{
    'name': 'Borneo Berkuda Stable (BBS)',
    'version': '17.0.1.0.0',
    'category': 'Operations',
    'summary': 'Manajemen Data Kuda & Log Harian Perawatan Kandang BBS',
    'description': """
Modul Operasional Borneo Berkuda Stable (BBS)
=============================================
Fitur:
- Database Master Kuda (Ras, Jenis Kelamin, Usia, Pemilik, Groomer Utama, Foto).
- Logbook Harian Perawatan Kuda (Perawatan Kuku/Kaki, Grooming/Mandi, Latihan Member, Obat/Vitamin).
- Hak Akses Berjenjang (BBS Groomer vs BBS Manager).
    """,
    'author': 'Borneo Berkuda Stable',
    'website': 'https://borneoberkuda.com',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'mail',
        'hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/horse_views.xml',
        'views/horse_care_log_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
