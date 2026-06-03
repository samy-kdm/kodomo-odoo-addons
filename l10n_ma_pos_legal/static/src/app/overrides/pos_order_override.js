/** @odoo-module **/
/**
 * pos_order_override.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Override du modèle JS pos.order pour injecter les champs légaux
 * dans le payload export_for_printing().
 *
 * Ce fichier est un PLACEHOLDER — Claude Code doit implémenter :
 *
 * 1. Importer patch depuis @web/core/utils/patch
 * 2. Importer Order depuis @point_of_sale/app/models/pos_order
 * 3. Patcher Order.prototype.export_for_printing pour ajouter :
 *    - result.company.ice        = this.company.company_registry
 *    - result.company.l10n_ma_if = this.company.l10n_ma_if
 *    - result.company.l10n_ma_tp = this.company.l10n_ma_tp
 *
 * Pattern :
 * ─────────
 * import { patch } from "@web/core/utils/patch";
 * import { PosOrder } from "@point_of_sale/app/models/pos_order";
 *
 * patch(PosOrder.prototype, {
 *     export_for_printing() {
 *         const result = super.export_for_printing(...arguments);
 *         const company = this.config.company;
 *         result.company.ice        = company.company_registry || "";
 *         result.company.l10n_ma_if = company.l10n_ma_if || "";
 *         result.company.l10n_ma_tp = company.l10n_ma_tp || "";
 *         return result;
 *     }
 * });
 *
 * IMPORTANT : vérifier le nom exact de la classe dans pos_order.js source
 * (peut être PosOrder ou Order selon la version).
 * Vérifier aussi le chemin d'accès à company depuis this (this.config, this.pos, etc.)
 */

// TODO : Claude Code implémente ce fichier
