{
    'name': 'Borneo Berkuda - Custom Invoicing & Faktur',
    'version': '17.0.1.0.0',
    'category': 'Accounting/Invoicing',
    'summary': 'Template Faktur Resmi Borneo Berkuda Stable (ATM Format KMS) dengan Kop Surat & TTD Elektronik',
    'author': 'Borneo Berkuda Stable',
    'license': 'LGPL-3',
    'depends': [
        'account',
        'base',
        'web',
    ],
    'data': [
        'views/res_company_views.xml',
        'views/account_move_views.xml',
        'reports/invoice_report_templates.xml',
        'reports/invoice_reports.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
