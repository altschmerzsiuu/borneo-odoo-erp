from datetime import date
from odoo import models, fields, api

class BBSHorse(models.Model):
    _name = 'bbs.horse'
    _description = 'Master Data Kuda Borneo Berkuda Stable'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name asc'

    name = fields.Char(string='Nama Kuda', required=True, tracking=True)
    image_1920 = fields.Image(string='Foto Kuda', max_width=1920, max_height=1920)
    
    gender = fields.Selection([
        ('stallion', 'Jantan (Stallion)'),
        ('mare', 'Betina (Mare)'),
        ('gelding', 'Kebiri (Gelding)'),
    ], string='Jenis Kelamin', default='stallion', required=True, tracking=True)

    breed = fields.Char(string='Ras / Breed', tracking=True, help='Contoh: Thoroughbred, Warmblood, Sandalwood, G1, G2')
    color = fields.Char(string='Warna Bulu', help='Contoh: Bay, Chestnut, Black, Grey, Palomino')
    date_of_birth = fields.Date(string='Tanggal Lahir')
    age = fields.Integer(string='Usia (Tahun)', compute='_compute_age', store=True)

    stable_box = fields.Char(string='Nomor Box / Kandang', tracking=True, help='Contoh: Box A-01, Box B-03')
    
    owner_id = fields.Many2one('res.partner', string='Pemilik (Owner)', tracking=True, help='Pemilik kuda (BBS atau member titip rawat)')
    primary_groomer_id = fields.Many2one('hr.employee', string='Groomer Utama', tracking=True, help='Staf groomer penanggung jawab utama')

    care_log_ids = fields.One2many('bbs.horse.care.log', 'horse_id', string='Riwayat Perawatan')
    care_log_count = fields.Integer(string='Total Log', compute='_compute_care_log_count')

    notes = fields.Html(string='Catatan Karakter / Diet Kuda')
    active = fields.Boolean(string='Aktif', default=True)

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = date.today()
        for record in self:
            if record.date_of_birth:
                born = record.date_of_birth
                record.age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
            else:
                record.age = 0

    @api.depends('care_log_ids')
    def _compute_care_log_count(self):
        for record in self:
            record.care_log_count = len(record.care_log_ids)

    def action_view_care_logs(self):
        self.ensure_one()
        return {
            'name': f'Log Perawatan: {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'bbs.horse.care.log',
            'view_mode': 'tree,form',
            'domain': [('horse_id', '=', self.id)],
            'context': {'default_horse_id': self.id},
        }
