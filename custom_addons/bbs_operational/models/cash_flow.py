from odoo import models, fields, api

class BBS_Cash_Flow(models.Model):
    _name = 'bbs.cash.flow'
    _description = 'Buku Kas Operasional Harian BBS'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, id desc'

    name = fields.Char(string="Keterangan Transaksi", required=True, tracking=True)
    date = fields.Date(string="Tanggal", default=fields.Date.today, required=True, tracking=True)
    transaction_type = fields.Selection([
        ('in', 'Uang Masuk (Pemasukan)'),
        ('out', 'Uang Keluar (Pengeluaran)'),
    ], string='Tipe Transaksi', default='out', required=True, tracking=True)

    category = fields.Selection([
        # Pos Pemasukan
        ('pemasukan_drop', 'Pemasukan: Drop Kas BBS (Owner)'),
        ('pemasukan_tiket', 'Pemasukan: Tiket Daily Riding / Member'),
        ('pemasukan_lain', 'Pemasukan: Saldo Awal / Penggantian Kas'),
        # Pos Pengeluaran Standar Operasional BBS
        ('operasional_bulanan', 'Operasional Bulanan (Serbuk, Keperluan Kandang, dsb)'),
        ('operasional_kendaraan', 'Operasional Kendaraan & Transport (BBM)'),
        ('listrik', 'Listrik Kandang'),
        ('internet', 'Internet & Komunikasi (WiFi / Paket Data)'),
        ('konsumsi', 'Konsumsi & Rapat'),
        ('admin_bank', 'Biaya Admin Bank BCA'),
        ('lain', 'Lain-lain / Perlengkapan Lapangan'),
        # Backward compatibility
        ('drop_dana', 'Drop Kas Operasional (dari BBS/Owner)'),
        ('daily_riding', 'Tiket Daily Riding / Member'),
        ('serbuk', 'Stok Serbuk Kayu'),
        ('peralatan', 'Peralatan & Perbaikan Lapangan'),
        ('kendaraan', 'Operasional Kendaraan / BBM'),
        ('talangan', 'Talangan / Penggantian Kas'),
    ], string='Kategori', required=True, default='operasional_bulanan', tracking=True)

    amount = fields.Float(string='Nominal (Rp.)', required=True, tracking=True)
    amount_in = fields.Float(string='Kas Masuk (Rp)', compute='_compute_amount_types', store=True)
    amount_out = fields.Float(string='Kas Keluar (Rp)', compute='_compute_amount_types', store=True)
    amount_net = fields.Float(string='Net / Saldo (Rp)', compute='_compute_amount_types', store=True)
    currency_id = fields.Many2one('res.currency', string='Mata Uang', default=lambda self: self.env.company.currency_id)

    @api.depends('amount', 'transaction_type')
    def _compute_amount_types(self):
        for rec in self:
            if rec.transaction_type == 'in':
                rec.amount_in = rec.amount
                rec.amount_out = 0.0
                rec.amount_net = rec.amount
            else:
                rec.amount_in = 0.0
                rec.amount_out = rec.amount
                rec.amount_net = -rec.amount

    pic_type = fields.Selection([
        ('tiara', 'Tiara'),
        ('ikhsan', 'Ikhsan'),
        ('nanda', 'Nanda'),
        ('dheny', 'Dheny'),
        ('bbs', 'BBS / Pusat'),
    ], string='PIC Transaksi', default='tiara', tracking=True)

    payment_method = fields.Selection([
        ('transfer', 'Transfer Bank'),
        ('cash', 'Tunai (Cash on Hand)'),
        ('qris', 'QRIS'),
    ], string='Metode Pembayaran', default='transfer', tracking=True)

    ref = fields.Char(string='No. Referensi', required=True, copy=False, readonly=True, default='New')
    rab_id = fields.Many2one('bbs.rab', string='Alokasi RAB', tracking=True, help='Tautkan transaksi ini ke dokumen RAB bulanan.')
    company_id = fields.Many2one('res.company', string='Perusahaan', default=lambda self: self.env.company)
    
    # Otomatisasi Biaya Admin Bank (BCA)
    auto_admin_fee = fields.Boolean(
        string='Catat Admin BCA Otomatis?', 
        default=False, 
        help='Centang opsi ini untuk otomatis membuat baris pengeluaran biaya admin bank BCA.'
    )
    admin_fee_amount = fields.Float(
        string='Nominal Admin BCA (Rp)', 
        default=2500.0,
        help='Biaya transfer BI-FAST (Rp 2.500) atau transfer online lainnya. Dapat diubah per transaksi.'
    )
    parent_cf_id = fields.Many2one('bbs.cash.flow', string='Transaksi Asal', ondelete='cascade', copy=False)
    child_cf_ids = fields.One2many('bbs.cash.flow', 'parent_cf_id', string='Biaya Admin Terkait')
    has_child_fee = fields.Boolean(compute='_compute_has_child_fee', string='Sudah Ada Admin BCA')

    receipt_image = fields.Binary(string='Bukti Transfer', attachment=True)
    notes = fields.Text(string='Catatan Tambahan')

    @api.depends('child_cf_ids')
    def _compute_has_child_fee(self):
        for rec in self:
            rec.has_child_fee = bool(rec.child_cf_ids)

    def action_quick_add_admin_fee(self):
        self.ensure_one()
        fee = self.admin_fee_amount or self.env.company.default_admin_bank_fee or 2500.0
        prefix = "KAS/OUT/"
        sequence = self.env['ir.sequence'].next_by_code('bbs.cash.flow') or fields.Date.today().strftime('%Y%m%d%H%M')
        child = self.env['bbs.cash.flow'].create({
            'ref': f"{prefix}{sequence}",
            'name': 'Admin BCA',
            'date': self.date,
            'transaction_type': 'out',
            'category': 'admin_bank',
            'amount': fee,
            'pic_type': self.pic_type,
            'payment_method': 'transfer',
            'rab_id': self.rab_id.id if self.rab_id else False,
            'parent_cf_id': self.id,
            'notes': f"Biaya transfer otomatis dari: {self.ref} - {self.name}",
        })
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'Biaya Admin BCA Berhasil Dicatat!',
                'message': f'Transaksi Admin BCA senilai Rp {fee:,.0f} berhasil dibuat ({child.ref}).',
                'type': 'success',
                'sticky': False,
            }
        }

    def action_view_admin_fee(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("bbs_operational.action_bbs_cash_flow")
        if len(self.child_cf_ids) == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.child_cf_ids[0].id
        else:
            action['domain'] = [('id', 'in', self.child_cf_ids.ids)]
        return action

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

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('ref', 'New') == 'New':
                prefix = 'KAS/IN/' if vals.get('transaction_type') == "in" else "KAS/OUT/"
                sequence = self.env['ir.sequence'].next_by_code('bbs.cash.flow') or fields.Date.today().strftime('%Y%m%d%H%M')
                vals['ref'] = f"{prefix}{sequence}"
        records = super().create(vals_list)

        admin_cfs_to_create = []
        for rec, vals in zip(records, vals_list):
            if vals.get('auto_admin_fee') and rec.transaction_type == 'out' and rec.payment_method == 'transfer' and rec.category != 'admin_bank':
                fee = vals.get('admin_fee_amount') or self.env.company.default_admin_bank_fee or 2500.0
                if fee > 0:
                    prefix = "KAS/OUT/"
                    sequence = self.env['ir.sequence'].next_by_code('bbs.cash.flow') or fields.Date.today().strftime('%Y%m%d%H%M')
                    admin_cfs_to_create.append({
                        'ref': f"{prefix}{sequence}",
                        'name': 'Admin BCA',
                        'date': rec.date,
                        'transaction_type': 'out',
                        'category': 'admin_bank',
                        'amount': fee,
                        'pic_type': rec.pic_type,
                        'payment_method': 'transfer',
                        'rab_id': rec.rab_id.id if rec.rab_id else False,
                        'parent_cf_id': rec.id,
                        'notes': f"Biaya transfer BI-FAST otomatis dari {rec.ref} - {rec.name}",
                    })
        if admin_cfs_to_create:
            super().create(admin_cfs_to_create)

        return records