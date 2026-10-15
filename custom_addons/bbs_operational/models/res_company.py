from odoo import models, fields, api

class ResCompany(models.Model):
    _inherit = 'res.company'

    default_admin_bank_fee = fields.Float(
        string='Default Biaya Admin BCA / Bank (Rp)', 
        default=2500.0,
        help='Biaya standar transfer per transaksi (misal BI-FAST Rp 2.500) untuk otomatisasi pencatatan kas.'
    )

class BBSCashConfig(models.TransientModel):
    _name = 'bbs.cash.config'
    _description = 'Pengaturan Biaya Operasional BBS'

    company_id = fields.Many2one('res.company', string='Perusahaan', default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', string='Mata Uang')
    default_admin_bank_fee = fields.Float(
        string="Default Biaya Admin BCA / Bank (Rp)",
        related='company_id.default_admin_bank_fee',
        readonly=False,
        help="Biaya standar transfer per transaksi (misal BI-FAST Rp 2.500) untuk otomatisasi pencatatan kas."
    )

    def action_save(self):
        return {'type': 'ir.actions.act_window_close'}
