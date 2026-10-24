from odoo import models, fields, api
import qrcode
import io
import base64
import os

class AccountMove(models.Model):
    _inherit = 'account.move'

    bbs_qr_code = fields.Binary(
        string='QR Code Validasi Faktur',
        compute='_compute_bbs_qr_code',
        store=False
    )

    bbs_logo_image = fields.Binary(
        string='Logo BBS',
        compute='_compute_bbs_logo_image',
        store=False
    )

    def _compute_bbs_logo_image(self):
        b64_logo = False
        logo_path = '/mnt/extra-addons/custom_addons/bbs_invoice/static/src/img/bbs_logo.jpg'
        if os.path.exists(logo_path):
            try:
                with open(logo_path, 'rb') as f:
                    b64_logo = base64.b64encode(f.read())
            except Exception:
                pass
        for rec in self:
            rec.bbs_logo_image = rec.company_id.logo or b64_logo

    # Info Rekening Pembayaran Khusus Faktur Ini
    bbs_payment_bank_name = fields.Char(
        string='Nama Bank Pembayaran',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )
    bbs_payment_bank_account_name = fields.Char(
        string='Atas Nama Rekening',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )
    bbs_payment_bank_account_number = fields.Char(
        string='Nomor Rekening',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )

    # Otorisasi TTD
    bbs_signer_city = fields.Char(
        string='Kota Cetak',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )
    bbs_signer_name = fields.Char(
        string='Nama Penandatangan',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )
    bbs_signer_title = fields.Char(
        string='Jabatan Penandatangan',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False
    )
    bbs_signature_image = fields.Binary(
        string='TTD & Stempel Khusus Faktur Ini',
        compute='_compute_bbs_defaults',
        store=True,
        readonly=False,
        attachment=True
    )
    bbs_show_signature = fields.Boolean(
        string='Tampilkan TTD & Stempel Elektronik?',
        default=True
    )

    @api.depends('company_id')
    def _compute_bbs_defaults(self):
        for rec in self:
            comp = rec.company_id
            if comp:
                if not rec.bbs_payment_bank_name:
                    rec.bbs_payment_bank_name = comp.bbs_invoice_bank_name or 'Bank Central Asia (BCA)'
                if not rec.bbs_payment_bank_account_name:
                    rec.bbs_payment_bank_account_name = comp.bbs_invoice_bank_account_name or 'BORNEO BERKUDA STABLE'
                if not rec.bbs_payment_bank_account_number:
                    rec.bbs_payment_bank_account_number = comp.bbs_invoice_bank_account_number or '037-901-111-3333'
                if not rec.bbs_signer_city:
                    rec.bbs_signer_city = comp.bbs_invoice_signer_city or 'Balikpapan'
                if not rec.bbs_signer_name:
                    rec.bbs_signer_name = comp.bbs_invoice_signer_name or 'Wawan Bagus Winarko'
                if not rec.bbs_signer_title:
                    rec.bbs_signer_title = comp.bbs_invoice_signer_title or 'Direktur'
                if not rec.bbs_signature_image and comp.bbs_invoice_signature_image:
                    rec.bbs_signature_image = comp.bbs_invoice_signature_image

    @api.depends('name', 'partner_id', 'amount_total', 'invoice_date')
    def _compute_bbs_qr_code(self):
        for rec in self:
            try:
                inv_no = rec.name or 'DRAFT'
                partner = rec.partner_id.name or '-'
                total = f"Rp {rec.amount_total:,.2f}"
                date = str(rec.invoice_date or fields.Date.today())
                qr_content = f"FAKTUR RESMI BORNEO BERKUDA STABLE\nNo. Invoice: {inv_no}\nKlien: {partner}\nTotal: {total}\nTanggal: {date}\nValidasi Sistem Odoo BBS"
                
                qr = qrcode.QRCode(version=1, box_size=3, border=1)
                qr.add_data(qr_content)
                qr.make(fit=True)
                img = qr.make_image(fill_color="#1b4d3e", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                rec.bbs_qr_code = base64.b64encode(buffer.getvalue())
            except Exception:
                rec.bbs_qr_code = False
