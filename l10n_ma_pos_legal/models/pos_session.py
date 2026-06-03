# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)


class PosSession(models.Model):
    _inherit = 'pos.session'

    # ── Hook clôture : générer le Rapport Z ──────────────────────────────────
    def action_pos_session_close(self, bank_payment_method_diffs=None):
        """Générer le Rapport Z à la clôture de session."""
        res = super().action_pos_session_close(bank_payment_method_diffs)
        for session in self:
            if session.state == 'closed':
                try:
                    self.env['pos.report.z'].create_from_session(session.id)
                except Exception as e:
                    _logger.error(
                        'Erreur génération Rapport Z pour session %s : %s',
                        session.name, str(e)
                    )
        return res

    # ── Données Rapport X (appelé depuis le POS via RPC) ─────────────────────
    def get_x_report_data(self):
        """Retourne les données du Rapport X pour la session en cours."""
        self.ensure_one()

        if self.state != 'opened':
            return {'error': 'Session non ouverte. Utiliser le Rapport Z.'}

        from datetime import datetime, timezone

        domain_orders = [
            ('session_id', '=', self.id),
            ('state', 'in', ['paid', 'done', 'invoiced']),
        ]

        # ── Totaux ventes ────────────────────────────────────────────────────
        sales = self.env['pos.order'].read_group(
            domain_orders, ['amount_total', 'amount_tax'], []
        )
        total_ttc = sales[0]['amount_total'] if sales else 0.0
        total_tax = sales[0]['amount_tax']   if sales else 0.0
        total_ht  = total_ttc - total_tax

        # ── Nb articles vendus ───────────────────────────────────────────────
        lines = self.env['pos.order.line'].read_group(
            [('order_id.session_id', '=', self.id),
             ('order_id.state', 'in', ['paid', 'done', 'invoiced'])],
            ['qty'], []
        )
        nb_articles = lines[0]['qty'] if lines else 0

        # ── Paiements par méthode ────────────────────────────────────────────
        payments_raw = self.env['pos.payment'].read_group(
            [('session_id', '=', self.id)],
            ['payment_method_id', 'amount'],
            ['payment_method_id']
        )
        payments = [{
            'method_name':  p['payment_method_id'][1] if p['payment_method_id'] else '—',
            'amount':       p['amount'],
            'count':        p['payment_method_id_count'],
        } for p in payments_raw]

        # ── Caisse espèces ───────────────────────────────────────────────────
        # Mouvements manuels de caisse
        cash_moves = self.statement_line_ids.filtered(
            lambda l: l.journal_id == self.cash_journal_id
        )
        retraits = sum(cash_moves.filtered(lambda l: l.amount < 0).mapped('amount'))

        return {
            'type':              'X',
            'printed_at':        datetime.now(timezone.utc).isoformat(),
            'session_name':      self.name,
            'session_start':     self.start_at.isoformat() if self.start_at else None,
            'cashier':           self.user_id.name or '',
            'order_count':       self.order_count,
            # Ventes
            'total_ht':          total_ht,
            'total_tax':         total_tax,
            'total_ttc':         total_ttc,
            'nb_articles':       nb_articles,
            # Paiements
            'payments':          payments,
            # Caisse
            'cash_start':        self.cash_register_balance_start,
            'cash_transaction':  self.cash_real_transaction,
            'cash_retraits':     retraits,
            'cash_theoretical':  self.cash_register_balance_end,
            # Société
            'company': {
                'name':       self.config_id.name,
                'ice':        self.company_id.company_registry or '',
                'l10n_ma_if': self.company_id.l10n_ma_if or '',
                'l10n_ma_tp': self.company_id.l10n_ma_tp or '',
            },
        }
