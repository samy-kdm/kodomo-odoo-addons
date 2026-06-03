/** @odoo-module **/
/**
 * x_z_report_button.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Bouton X/Z dans la navbar du POS.
 * Référence : sale_details_button.js (même pattern)
 *
 * Ce fichier est un PLACEHOLDER — Claude Code doit implémenter :
 *
 * 1. Importer Component, useState, useService depuis @odoo/owl
 * 2. Créer le composant XZReportButton héritant de Component
 * 3. Ajouter deux boutons dans le template :
 *    - "Rapport X" → appel RPC pos.session.get_x_report_data()
 *                  → naviguer vers XReportScreen avec les données
 *    - "Rapport Z" → visible uniquement si session peut être clôturée
 *                  → récupérer pos.report.z.get_z_report_data()
 *                  → naviguer vers ZReportScreen avec les données
 * 4. Patch de la navbar pour ajouter le bouton
 *
 * Pattern à suivre (depuis sale_details_button.js) :
 * ─────────────────────────────────────────────────
 * import { Component } from "@odoo/owl";
 * import { usePos } from "@point_of_sale/app/hooks/pos_hook";
 * import { useService } from "@web/core/utils/hooks";
 *
 * export class XZReportButton extends Component {
 *     static template = "l10n_ma_pos_legal.XZReportButton";
 *     setup() {
 *         this.pos = usePos();
 *         this.orm = useService("orm");
 *         this.printer = useService("printer");
 *     }
 *     async printXReport() {
 *         const data = await this.orm.call(
 *             "pos.session",
 *             "get_x_report_data",
 *             [this.pos.session.id]
 *         );
 *         // Naviguer vers XReportScreen ou imprimer directement
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
 * patch(Navbar, { components: { ...Navbar.components, XZReportButton } });
 */

// TODO : Claude Code implémente ce fichier
