from odoo import models, fields, api

class BBSHorseCareLog(models.Model):
    _name = 'bbs.horse.care.log'
    _description = 'Logbook Perawatan & Aktivitas Kuda BBS'
    _inherit = ['mail.thread']
    _order = 'date desc, id desc'

    name = fields.Char(string='No. Log', required=True, copy=False, readonly=True, default='New')
    horse_id = fields.Many2one('bbs.horse', string='Kuda', required=True, tracking=True)
    groomer_id = fields.Many2one(
        'hr.employee', 
        string='Petugas / Groomer', 
        default=lambda self: self.env.user.employee_id, 
        required=True, 
        tracking=True
    )
    date = fields.Datetime(string='Waktu Pelaksanaan', default=fields.Datetime.now, required=True, tracking=True)
    
    activity_type = fields.Selection([
        ('hoof_care', 'Perawatan Kaki & Kuku (Hoof Care)'),
        ('grooming', 'Grooming & Mandi'),
        ('exercise', 'Latihan / Lunging / Riding Member'),
        ('medical', 'Medis / Vitamin / Obat Cacing'),
        ('vet_check', 'Pemeriksaan Dokter Hewan (Vet)'),
        ('other', 'Lainnya'),
    ], string='Jenis Aktivitas', required=True, default='hoof_care', tracking=True)

    description = fields.Text(string='Catatan / Temuan Lapangan', required=True)
    state = fields.Selection([
        ('draft', 'Rencana / Draft'),
        ('done', 'Selesai Dilakukan'),
    ], string='Status', default='draft', tracking=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('bbs.horse.care.log') or 'LOG-' + fields.Date.today().strftime('%Y%m%d')
        return super().create(vals_list)

    def action_set_done(self):
        for record in self:
            record.state = 'done'

    def action_set_draft(self):
        for record in self:
            record.state = 'draft'
