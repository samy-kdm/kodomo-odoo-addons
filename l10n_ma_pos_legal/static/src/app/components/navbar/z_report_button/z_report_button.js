/** @odoo-module **/
/**
 * z_report_button.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Bouton Rapport Z dans la navbar du POS.
 * Référence : sale_details_button.js (même pattern)
 *
 * Ce fichier est un PLACEHOLDER — Claude Code doit implémenter :
 *
 * 1. Importer Component, useService depuis @odoo/owl
 * 2. Créer le composant ZReportButton héritant de Component
 * 3. Ajouter un bouton dans le template :
 *    - "Rapport Z" → appel RPC pos.session.get_z_report_data_for_pos()
 *                  → naviguer vers ZReportScreen avec les données reçues
 * 4. Patch de la navbar pour ajouter le bouton
 *
 * Pattern à suivre (depuis sale_details_button.js) :
 * ─────────────────────────────────────────────────
 * import { Component } from "@odoo/owl";
 * import { usePos } from "@point_of_sale/app/hooks/pos_hook";
 * import { useService } from "@web/core/utils/hooks";
 *
 * export class ZReportButton extends Component {
 *     static template = "l10n_ma_pos_legal.ZReportButton";
 *     setup() {
 *         this.pos = usePos();
 *         this.orm = useService("orm");
 *         this.printer = useService("printer");
 *     }
 *     async printZReport() {
 *         const data = await this.orm.call(
 *             "pos.session",
 *             "get_z_report_data_for_pos",
 *             [this.pos.session.id]
 *         );
 *         // Naviguer vers ZReportScreen
 *     }
 * }
 *
 * Enregistrement dans la navbar :
 * import { Navbar } from "@point_of_sale/app/components/navbar/navbar";
 * import { patch } from "@web/core/utils/patch";
 * patch(Navbar, { components: { ...Navbar.components, ZReportButton } });
 */

// TODO : Claude Code implémente ce fichier
