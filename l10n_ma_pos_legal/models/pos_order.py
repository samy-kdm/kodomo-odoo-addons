# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # ── Champ numéro légal (utilise tracking_number natif) ───────────────────
    # Décision : on utilise tracking_number natif Odoo (format 00042-001-0001)
    # Pas de séquence custom nécessaire pour le ticket.

    # ── Injection des champs légaux dans le payload du POS ───────────────────
    # Ces champs sont chargés via _load_pos_data_fields au démarrage de session.

    @api.model
    def _load_pos_data_fields(self, config_id):
        """Ajouter les champs nécessaires au chargement POS."""
        result = super()._load_pos_data_fields(config_id)
        # tracking_number est déjà chargé nativement
        return result


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_res_company(self):
        """Injecter les champs légaux dans le chargement de la société."""
        result = super()._loader_params_res_company()
        # Ajouter nos champs custom à la liste des champs chargés
        if 'fields' in result.get('search_params', {}):
            result['search_params']['fields'] += [
                'l10n_ma_if',
                'l10n_ma_tp',
                'company_registry',  # = ICE
                'phone',
                'email',
            ]
        return result
