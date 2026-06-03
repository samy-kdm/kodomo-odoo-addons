# -*- coding: utf-8 -*-
from odoo import models, fields, api


class ResCompany(models.Model):
    _inherit = 'res.company'

    # ── Champs légaux Maroc ───────────────────────────────────────────────────
    # ICE : réutiliser company_registry (déjà renseigné = "003719751000038")
    # Pas de champ custom ICE nécessaire.

    l10n_ma_if = fields.Char(
        string='Identifiant Fiscal (IF)',
        size=20,
        help='Identifiant Fiscal marocain — apparaît sur le ticket POS et les rapports X/Z',
    )
    l10n_ma_tp = fields.Char(
        string='Taxe Professionnelle (TP)',
        size=20,
        help='Numéro de Taxe Professionnelle marocaine — apparaît sur le ticket POS et les rapports X/Z',
    )

    # ── Injection dans le payload POS (chargé au démarrage de session) ───────
    def _get_pos_legal_fields(self):
        """Retourne les champs légaux pour le payload POS."""
        self.ensure_one()
        return {
            'ice':       self.company_registry or '',   # champ natif
            'l10n_ma_if': self.l10n_ma_if or '',
            'l10n_ma_tp': self.l10n_ma_tp or '',
            'name':      self.name or '',
            'phone':     self.phone or '',
            'email':     self.email or '',
        }
