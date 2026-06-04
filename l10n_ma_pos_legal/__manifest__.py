# -*- coding: utf-8 -*-
{
    'name': 'Kodomo — POS Légal Maroc',
    'version': '19.0.1.0.0',
    'summary': 'Ticket et Rapport Z conformes à la réglementation marocaine',
    'description': """
        Module custom pour Kodomo Jouet (KDM SMART HUB).
        - Ticket POS avec ICE, IF, TP, adresse bilingue
        - Rapport Z (clôture de session) déclenché depuis la caisse
          avec snapshot persistant, numérotation légale et alerte écart > 5 DH
    """,
    'author': 'Kodomo Jouet',
    'website': 'https://kodomo.ma',
    'category': 'Point of Sale',
    'license': 'LGPL-3',

    # ── Dépendances ──────────────────────────────────────────────────────────
    # point_of_sale : module POS de base
    # account       : account.tax, account.move (écriture clôture)
    # hr            : hr.employee (multi-caissiers — pos_hr installé)
    # pos_hr        : employee_id sur pos.order, écran login employé
    'depends': [
        'point_of_sale',
        'account',
        'hr',
        'pos_hr',
    ],

    # ── Fichiers de données (chargés dans cet ordre) ─────────────────────────
    'data': [
        # Sécurité
        'security/ir.model.access.csv',

        # Séquence légale Z
        'data/ir_sequence_data.xml',

        # Vues back-office (liste des Z, formulaire)
        'views/pos_report_z_views.xml',

        # Actions menu back-office (optionnel)
        'views/pos_report_z_menu.xml',
    ],

    # ── Assets frontend OWL ──────────────────────────────────────────────────
    'assets': {
        'point_of_sale._assets_pos': [
            # Override ticket POS — mentions légales marocaines
            'l10n_ma_pos_legal/static/src/app/overrides/pos_order_override.js',
            'l10n_ma_pos_legal/static/src/app/overrides/order_receipt_override.xml',
        ],
    },

    'installable': True,
    'application': False,
    'auto_install': False,
}
