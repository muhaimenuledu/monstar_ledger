{
    'name': 'Monstar Ledger',
    'version': '1.0',
    'category': 'Accounting',
    'author' : 'Pranto',
    'depends': ['account',
                'account_reports'],
    'data': [
        'views/account_report_view.xml',
        'views/account_move_line_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
