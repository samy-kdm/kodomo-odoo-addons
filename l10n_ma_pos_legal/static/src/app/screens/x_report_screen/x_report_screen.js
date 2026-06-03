/** @odoo-module **/
/**
 * x_report_screen.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Écran Rapport X dans le POS OWL.
 *
 * Ce fichier est un PLACEHOLDER — Claude Code doit implémenter :
 *
 * 1. Composant XReportScreen héritant de Component
 * 2. Props : { data } (reçu depuis XZReportButton via navigate)
 * 3. Template : affichage du rapport X formaté (voir x_report_screen.xml)
 * 4. Bouton "Imprimer" → utiliser useService("printer") ou pos_printer_service
 * 5. Bouton "Fermer" → retour à l'écran précédent
 *
 * Données disponibles dans this.props.data :
 * ───────────────────────────────────────────
 * {
 *   type: 'X',
 *   printed_at, session_name, session_start,
 *   cashier, order_count,
 *   total_ht, total_tax, total_ttc, nb_articles,
 *   payments: [{method_name, amount, count}],
 *   cash_start, cash_transaction, cash_retraits, cash_theoretical,
 *   company: {name, ice, l10n_ma_if, l10n_ma_tp}
 * }
 *
 * Pattern d'enregistrement de l'écran :
 * ──────────────────────────────────────
 * import { registry } from "@web/core/registry";
 * registry.category("pos_screens").add("XReportScreen", XReportScreen);
 */

// TODO : Claude Code implémente ce fichier
