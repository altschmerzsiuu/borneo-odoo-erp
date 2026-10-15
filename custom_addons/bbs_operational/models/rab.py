import string
from datetime import date
from odoo import models, fields, api

class BBS_RAB(models.Model):
    _name = 'bbs.rab'
    _description = 'Rencana Anggaran Biaya (RAB) Bulanan BBS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'year desc, month desc, id desc'

    name = fields.Char(string='Nama / Periode RAB', required=True, tracking=True)
    month = fields.Selection([
        ('1', 'Januari'),
        ('2', 'Februari'),
        ('3', 'Maret'),
        ('4', 'April'),
        ('5', 'Mei'),
        ('6', 'Juni'),
        ('7', 'Juli'),
        ('8', 'Agustus'),
        ('9', 'September'),
        ('10', 'Oktober'),
        ('11', 'November'),
        ('12', 'Desember'),
    ], string='Bulan', required=True, default=str(date.today().month), tracking=True)

    year = fields.Integer(string='Tahun', required=True, default=date.today().year, tracking=True)
    date_submission = fields.Date(string='Tanggal Pengajuan', default=fields.Date.today)

    line_ids = fields.One2many('bbs.rab.line', 'rab_id', string='Daftar Kebutuhan Belanja')
    total_amount = fields.Float(string='Total Anggaran (Rp.)', compute='_compute_total_amount', store=True, tracking=True)
    cash_flow_ids = fields.One2many('bbs.cash.flow', 'rab_id', string='Realisasi Transaksi Kas')
    saldo_awal = fields.Float(string='Saldo Awal Kas (Rp.)', compute='_compute_kas_summary', store=True)
    total_kas_masuk = fields.Float(string='Total Pemasukan (Rp.)', compute='_compute_kas_summary', store=True)
    total_kas_keluar = fields.Float(string='Total Pengeluaran (Rp.)', compute='_compute_kas_summary', store=True)
    balance = fields.Float(string='Saldo Akhir Kas (Rp.)', compute='_compute_kas_summary', store=True)
    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self:self.env.company.currency_id)
    notes = fields.Text(string='Catatan untuk Owner')
    state = fields.Selection([
        ('draft', 'Draft (Penyusunan)'),
        ('submitted', 'Diajukan ke Owner'),
        ('approved', 'Disetujui (Dana Cair)'),
        ('rejected', 'Ditolak / Revisi'),
    ], string='Status', default='draft', tracking=True)

    @api.depends('line_ids.subtotal')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = sum(line.subtotal for line in record.line_ids)
    
    @api.depends('cash_flow_ids.amount', 'cash_flow_ids.transaction_type', 'cash_flow_ids.name')
    def _compute_kas_summary(self):
        for record in self:
            total_in = sum(line.amount for line in record.cash_flow_ids if line.transaction_type == 'in')
            total_out = sum(line.amount for line in record.cash_flow_ids if line.transaction_type == 'out')
            
            # Deteksi Saldo Awal (transaksi dengan nama atau catatan 'Saldo Awal')
            saldo_awal_line = record.cash_flow_ids.filtered(lambda c: 'saldo awal' in (c.name or '').lower())
            record.saldo_awal = sum(saldo_awal_line.mapped('amount')) if saldo_awal_line else 0.0

            record.total_kas_masuk = total_in
            record.total_kas_keluar = total_out
            record.balance = total_in - total_out

    def get_cash_flow_category_summary(self):
        """Menghasilkan ringkasan total pengeluaran per kategori untuk laporan eksekutif PDF"""
        self.ensure_one()
        category_dict = dict(self.env['bbs.cash.flow']._fields['category'].selection)
        summary = {}
        total_expense = self.total_kas_keluar or 1.0
        for cf in self.cash_flow_ids.filtered(lambda c: c.transaction_type == 'out'):
            cat_label = category_dict.get(cf.category, cf.category)
            if cf.category not in summary:
                summary[cf.category] = {
                    'code': cf.category,
                    'name': cat_label,
                    'total': 0.0,
                    'count': 0,
                    'percentage': 0.0,
                }
            summary[cf.category]['total'] += cf.amount
            summary[cf.category]['count'] += 1

        res = list(summary.values())
        for r in res:
            r['percentage'] = (r['total'] / total_expense) * 100.0 if total_expense else 0.0
        return sorted(res, key=lambda x: x['total'], reverse=True)

    def action_submit(self):
        self.write({'state' : 'submitted'})

    def action_approve(self):
        self.write({'state' : 'approved'})

    def action_reject(self):
        self.write({'state' : 'rejected'})

    def action_draft(self):
        self.write({'state' : 'draft'})
    
class BBS_RAB_Line(models.Model):
    _name = 'bbs.rab.line'
    _description = 'Detail Kebutuhan Belanja BBS'

    rab_id = fields.Many2one('bbs.rab', string='RAB Reference', ondelete='cascade')
    name = fields.Char(string='Kebutuhan / Uraian', required=True)
    qty = fields.Float(string='Jumlah', default=1.0, required=True)
    uom = fields.Selection([
        ('pcs', 'Pcs'),
        ('bulan', 'Bulan'),
        ('karung', 'Karung'),
        ('zak', 'Zak'),
        ('meter', 'Meter'),
        ('liter', 'Liter'),
        ('kg', 'Kg'),
        ('box', 'Box'),
        ('roll', 'Roll'),
        ('batang', 'Batang'),
        ('paket', 'Paket'),
        ('unit', 'Unit'),
        ('lain', 'Lainnya'),
    ], string='Satuan', default='pcs', required=True)
    price_unit = fields.Float(string='Harga Satuan (Rp.)', required=True)
    subtotal = fields.Float(string='Total (Rp.)', compute='_compute_subtotal', store=True)

    category = fields.Selection([
        ('bpu', 'BPU (Biaya Pokok Utama)'),
        ('peralatan', 'Peralatan & Maintenance'),
        ('internet', 'Internet & Wifi'),
        ('uk40', 'UK 40 / Armada'),
        ('talangan', 'Ganti Talangan Staf'),
        ('lain', 'Lain-lain'),
    ], string='Keterangan / Kategori', default='bpu')

    is_talangan = fields.Boolean(string='Pos Talangan', help='Centang jika ini adalah penggantian uang staf')

    @api.depends('qty', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.subtotal = line.qty * line.price_unit

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            acronyms = {
                'bbm': 'BBM', 'bca': 'BCA', 'bri': 'BRI', 'bni': 'BNI', 'bbs': 'BBS', 
                'rab': 'RAB', 'bpu': 'BPU', 'qris': 'QRIS', 'wifi': 'WiFi', 'pic': 'PIC',
                'pdam': 'PDAM', 'pln': 'PLN', 'uk': 'UK', 'uk40': 'UK40', 'hp': 'HP',
                'bpjs': 'BPJS', 'pos': 'POS'
            }
            words = self.name.strip().split()
            formatted = []
            for w in words:
                w_lower = w.lower()
                if w_lower in acronyms:
                    formatted.append(acronyms[w_lower])
                elif w.isupper() and len(w) > 1:
                    formatted.append(w)
                else:
                    formatted.append(w.capitalize())
            self.name = ' '.join(formatted)