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

