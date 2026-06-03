# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError

# Seuil d'alerte écart caisse (décision : 5 DH fixe)
CASH_DIFFERENCE_ALERT_THRESHOLD = 5.0


class PosReportZ(models.Model):
    _name = 'pos.report.z'
    _description = 'Rapport Z — Clôture de session POS (Kodomo Jouet)'
    _order = 'id desc'
    _rec_name = 'name'

    # ── Identification ────────────────────────────────────────────────────────
    name = fields.Char(
        string='Numéro Z',
        readonly=True,
        copy=False,
        index=True,
        help='Numéro légal séquentiel attribué à la clôture — jamais régénéré.',
    )
    session_id = fields.Many2one(
        'pos.session',
        string='Session',
        readonly=True,
        ondelete='restrict',
        required=True,
        index=True,
    )
    company_id = fields.Many2one('res.company', string='Société', readonly=True)
    config_id  = fields.Many2one('pos.config',  string='Point de vente', readonly=True)
    currency_id = fields.Many2one('res.currency', string='Devise', readonly=True)

    # ── Horodatages figés ─────────────────────────────────────────────────────
    date_open    = fields.Datetime('Ouverture session', readonly=True)
    date_close   = fields.Datetime('Clôture session',   readonly=True)
    date_printed = fields.Datetime(
        'Date impression',
        default=fields.Datetime.now,
        readonly=True,
    )

    # ── Snapshot ventes ───────────────────────────────────────────────────────
    amount_total_ht  = fields.Monetary(
        'Total HT', readonly=True, currency_field='currency_id'
    )
    amount_tax = fields.Monetary(
        'Total TVA 20%', readonly=True, currency_field='currency_id'
    )
    amount_total_ttc = fields.Monetary(
        'Total TTC', readonly=True, currency_field='currency_id'
    )

    # ── Snapshot caisse ───────────────────────────────────────────────────────
    cash_start       = fields.Monetary('Fond initial',      readonly=True, currency_field='currency_id')
    cash_transaction = fields.Monetary('Entrées espèces',   readonly=True, currency_field='currency_id')
    cash_out         = fields.Monetary('Retraits',          readonly=True, currency_field='currency_id')
    cash_theoretical = fields.Monetary('Solde théorique',   readonly=True, currency_field='currency_id')
    cash_counted     = fields.Monetary('Solde compté',      readonly=True, currency_field='currency_id')
    cash_difference  = fields.Monetary('Écart',             readonly=True, currency_field='currency_id')

    # Alerte écart (calculée depuis cash_difference)
    cash_difference_alert = fields.Boolean(
        'Alerte écart',
        compute='_compute_cash_difference_alert',
        help=f'True si |écart| > {CASH_DIFFERENCE_ALERT_THRESHOLD} DH',
    )

    # ── Snapshot tickets ──────────────────────────────────────────────────────
    order_ref_first = fields.Char('Premier ticket', readonly=True)
    order_ref_last  = fields.Char('Dernier ticket',  readonly=True)
    order_count     = fields.Integer('Nb transactions', readonly=True)

    # ── Détails TVA et paiements (JSON) ──────────────────────────────────────
    tax_details     = fields.Json('Détail TVA',       readonly=True)
    payment_details = fields.Json('Détail paiements', readonly=True)

    # ── Caissiers ─────────────────────────────────────────────────────────────
    # Tous les employés distincts ayant encaissé pendant la session
    employee_ids = fields.Many2many(
        'hr.employee',
        string='Caissiers',
        readonly=True,
    )

    # ── État ──────────────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft', 'Brouillon'),
        ('done',  'Émis'),
    ], string='État', default='draft', readonly=True)

    is_reprint = fields.Boolean(
        'Réimpression',
        default=False,
        readonly=True,
        help='True si ce document est une réimpression — mention DUPLICATA affichée.',
    )

    # ── Contrainte : 1 seul Z par session ────────────────────────────────────
    _sql_constraints = [
        ('session_unique', 'unique(session_id)',
         'Un Rapport Z existe déjà pour cette session.'),
    ]

    # ── Compute ───────────────────────────────────────────────────────────────
    @api.depends('cash_difference')
    def _compute_cash_difference_alert(self):
        for rec in self:
            rec.cash_difference_alert = (
                abs(rec.cash_difference or 0.0) > CASH_DIFFERENCE_ALERT_THRESHOLD
            )

    # ── Action impression ─────────────────────────────────────────────────────
    def action_print(self):
        """Imprimer le Rapport Z. Marquer DUPLICATA si déjà émis."""
        self.ensure_one()
        if self.state == 'done':
            self.write({
                'is_reprint':    True,
                'date_printed':  fields.Datetime.now(),
            })
        else:
            self.write({'state': 'done'})
        # Retourner l'action d'impression QWeb (à définir dans report/)
        return self.env.ref(
            'l10n_ma_pos_legal.action_report_pos_z'
        ).report_action(self)

    def get_z_report_data(self):
        """Retourne le dict de données pour le rendu OWL depuis le POS."""
        self.ensure_one()
        return {
            'type':               'Z',
            'name':               self.name,
            'is_reprint':         self.is_reprint,
            'date_open':          self.date_open.isoformat() if self.date_open else None,
            'date_close':         self.date_close.isoformat() if self.date_close else None,
            'date_printed':       self.date_printed.isoformat() if self.date_printed else None,
            'session_name':       self.session_id.name,
            'order_ref_first':    self.order_ref_first,
            'order_ref_last':     self.order_ref_last,
            'order_count':        self.order_count,
            'employees':          self.employee_ids.mapped('name'),
            # Ventes
            'total_ht':           self.amount_total_ht,
            'total_tax':          self.amount_tax,
            'total_ttc':          self.amount_total_ttc,
            # Caisse
            'cash_start':         self.cash_start,
            'cash_transaction':   self.cash_transaction,
            'cash_out':           self.cash_out,
            'cash_theoretical':   self.cash_theoretical,
            'cash_counted':       self.cash_counted,
            'cash_difference':    self.cash_difference,
            'cash_difference_alert': self.cash_difference_alert,
            # Paiements
            'payments':           self.payment_details or [],
            # Société
            'company': {
                'name':       self.config_id.name,
                'ice':        self.company_id.company_registry or '',
                'l10n_ma_if': self.company_id.l10n_ma_if or '',
                'l10n_ma_tp': self.company_id.l10n_ma_tp or '',
            },
        }

    # ── Création depuis la session (appelé à la clôture) ─────────────────────
    @api.model
    def create_from_session(self, session_id):
        """
        Créer le snapshot Z à la clôture.
        Atomique — appelé depuis pos.session.action_pos_session_close().
        """
        session = self.env['pos.session'].browse(session_id)

        # Vérification unicité
        if self.search([('session_id', '=', session_id)], limit=1):
            raise UserError(
                f'Un Rapport Z existe déjà pour la session {session.name}.'
            )

        domain_orders = [
            ('session_id', '=', session_id),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]

        # ── Totaux ventes ────────────────────────────────────────────────────
        sales = self.env['pos.order'].read_group(
            domain_orders, ['amount_total', 'amount_tax'], []
        )
        total_ttc = sales[0]['amount_total'] if sales else 0.0
        total_tax = sales[0]['amount_tax']   if sales else 0.0

        # ── Bornes tickets ───────────────────────────────────────────────────
        orders = self.env['pos.order'].search(
            domain_orders, order='id asc'
        )
        ticket_first = orders[0].tracking_number  if orders else ''
        ticket_last  = orders[-1].tracking_number if orders else ''

        # ── Employés distincts ───────────────────────────────────────────────
        employee_ids = orders.mapped('employee_id').ids

        # ── Paiements par méthode ────────────────────────────────────────────
        payments_raw = self.env['pos.payment'].read_group(
            [('session_id', '=', session_id)],
            ['payment_method_id', 'amount'],
            ['payment_method_id']
        )
        payment_details = [{
            'method_name': p['payment_method_id'][1] if p['payment_method_id'] else '—',
            'amount':      p['amount'],
            'count':       p['payment_method_id_count'],
        } for p in payments_raw]

        # ── Caisse — mouvements manuels ──────────────────────────────────────
        cash_moves = session.statement_line_ids.filtered(
            lambda l: l.journal_id == session.cash_journal_id
        )
        cash_out = sum(cash_moves.filtered(lambda l: l.amount < 0).mapped('amount'))

        # ── Numéro légal Z (séquence standard Odoo) ──────────────────────────
        z_number = self.env['ir.sequence'].next_by_code('pos.report.z') or '/'

        return self.create({
            'name':             z_number,
            'session_id':       session.id,
            'company_id':       session.company_id.id,
            'config_id':        session.config_id.id,
            'currency_id':      session.currency_id.id,
            'date_open':        session.start_at,
            'date_close':       session.stop_at,
            # Ventes
            'amount_total_ht':  total_ttc - total_tax,
            'amount_tax':       total_tax,
            'amount_total_ttc': total_ttc,
            # Caisse
            'cash_start':       session.cash_register_balance_start,
            'cash_transaction': session.cash_real_transaction,
            'cash_out':         cash_out,
            'cash_theoretical': session.cash_register_balance_end,
            'cash_counted':     session.cash_register_balance_end_real,
            'cash_difference':  session.cash_register_difference,
            # Tickets
            'order_ref_first':  ticket_first,
            'order_ref_last':   ticket_last,
            'order_count':      len(orders),
            # Détails
            'payment_details':  payment_details,
            # Caissiers (tous les employés distincts)
            'employee_ids':     [(6, 0, employee_ids)],
            'state':            'draft',
        })
