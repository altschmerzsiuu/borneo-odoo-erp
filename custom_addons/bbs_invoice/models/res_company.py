from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    # Informasi Rekening Bank untuk Faktur BBS
    bbs_invoice_bank_name = fields.Char(
        string='Nama Bank Pembayaran',
        default='Bank Central Asia (BCA)',
        help='Nama bank yang akan tercantum di instruksi pembayaran invoice.'
    )
    bbs_invoice_bank_account_name = fields.Char(
        string='Atas Nama Rekening',
        default='BORNEO BERKUDA STABLE',
        help='Nama pemilik rekening yang tertera di invoice.'
    )
    bbs_invoice_bank_account_number = fields.Char(
        string='Nomor Rekening',
        default='037-901-111-3333',
        help='Nomor rekening bank penampung tagihan invoice.'
    )

    # Identitas & Kontak Kop Surat
    bbs_invoice_address_header = fields.Char(
        string='Alamat Kop Surat',
        default='Jl. Ruhui Rahayu, Sepinggan Pratama, Balikpapan Selatan, Balikpapan, Kalimantan Timur'
    )
    bbs_invoice_phone = fields.Char(
        string='No. Telepon / WhatsApp',
        default='0851-7314-0965'
    )
    bbs_invoice_email = fields.Char(
        string='Email Penagihan',
        default='operasional@borneoberkuda.co.id'
    )

    # Otorisasi & Tanda Tangan Elektronik
    bbs_invoice_signer_city = fields.Char(
        string='Kota Penandatanganan',
        default='Balikpapan'
    )
    bbs_invoice_signer_name = fields.Char(
        string='Nama Penandatangan',
        default='Manajemen Operasional'
    )
    bbs_invoice_signer_title = fields.Char(
        string='Jabatan Penandatangan',
        default='Borneo Berkuda Stable'
    )
    bbs_invoice_signature_image = fields.Binary(
        string='Gambar TTD & Stempel Resmi',
        attachment=True,
        help='Unggah file scan tanda tangan dan/atau stempel resmi BBS transparan (PNG).'
    )
