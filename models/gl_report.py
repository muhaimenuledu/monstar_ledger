from odoo import models
from odoo.tools.sql import SQL

class AccountGeneralLedger(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _get_query_amls(self, report, options, expanded_account_ids, offset=0, limit=None):
        from odoo.tools.sql import SQL  # Safe SQL wrapper

        additional_domain = [('account_id', 'in', expanded_account_ids)] if expanded_account_ids else None
        queries = []
        journal_name = self.env['account.journal']._field_to_sql('journal', 'name')

        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            query = report._get_report_query(group_options, domain=additional_domain, date_scope='strict_range')

            account_alias = query.join(
                lhs_alias='account_move_line', lhs_column='account_id',
                rhs_table='account_account', rhs_column='id', link='account_id'
            )
            account_code = self.env['account.account']._field_to_sql(account_alias, 'code', query)
            account_name = self.env['account.account']._field_to_sql(account_alias, 'name')
            account_type = self.env['account.account']._field_to_sql(account_alias, 'account_type')

            query = SQL('''
                SELECT
                    account_move_line.id,
                    account_move_line.date,
                    account_move_line.date_maturity,
                    account_move_line.name,
                    account_move_line.ref,
                    account_move_line.company_id,
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.partner_id,
                    account_move_line.currency_id,
                    account_move_line.amount_currency,
                    account_move_line.quantity      AS qty,
                    uom.name                        AS product_uom,
                    COALESCE(account_move_line.invoice_date, account_move_line.date) AS invoice_date,
                    %(debit_select)s               AS debit,
                    %(credit_select)s              AS credit,
                    %(balance_select)s             AS balance,
                    move.id                        AS move_id,
                    move.name                      AS move_name,
                    move.group                     AS move_group,
                    move.ref                       AS move_ref,
                    company.currency_id            AS company_currency_id,
                    partner.name                   AS partner_name,
                    move.move_type                 AS move_type,
                    %(account_code)s               AS account_code,
                    %(account_name)s               AS account_name,
                    %(account_type)s               AS account_type,
                    journal.code                   AS journal_code,
                    %(journal_name)s               AS journal_name,
                    full_rec.id                    AS full_rec_name,
                    %(column_group_key)s           AS column_group_key,
                    account_move_line.lead_reference AS lead_reference,
                    pt.name                        AS product_name
                FROM %(table_references)s
                JOIN account_move move           ON move.id = account_move_line.move_id
                %(currency_table_join)s
                LEFT JOIN res_company company    ON company.id = account_move_line.company_id
                LEFT JOIN res_partner partner    ON partner.id = account_move_line.partner_id
                LEFT JOIN account_journal journal ON journal.id = account_move_line.journal_id
                LEFT JOIN account_full_reconcile full_rec ON full_rec.id = account_move_line.full_reconcile_id
                LEFT JOIN product_product pp     ON pp.id = account_move_line.product_id
                LEFT JOIN product_template pt    ON pt.id = pp.product_tmpl_id
                LEFT JOIN uom_uom uom            ON uom.id = account_move_line.product_uom_id
                WHERE %(search_condition)s
                ORDER BY account_move_line.date, move.name, account_move_line.id
            ''',
            account_code=account_code,
            account_name=account_name,
            account_type=account_type,
            journal_name=journal_name,
            column_group_key=column_group_key,
            table_references=query.from_clause,
            currency_table_join=report._currency_table_aml_join(group_options),
            debit_select=report._currency_table_apply_rate(SQL("account_move_line.debit")),
            credit_select=report._currency_table_apply_rate(SQL("account_move_line.credit")),
            balance_select=report._currency_table_apply_rate(SQL("account_move_line.balance")),
            search_condition=query.where_clause,
            )
            queries.append(query)

        full_query = SQL(" UNION ALL ").join(SQL("(%s)", query) for query in queries)

        if offset:
            full_query = SQL('%s OFFSET %s', full_query, offset)
        if limit:
            full_query = SQL('%s LIMIT %s', full_query, limit)

        return full_query
