/** @odoo-module **/
/**
 * z_report_screen.js
 * ─────────────────────────────────────────────────────────────────────────────
 * Écran Rapport Z dans le POS OWL.
 *
 * Ce fichier est un PLACEHOLDER — Claude Code doit implémenter :
 *
 * 1. Composant ZReportScreen héritant de Component
 * 2. Props : { data } (reçu depuis XZReportButton)
 * 3. Template : affichage du rapport Z formaté (voir z_report_screen.xml)
 * 4. Alerte écart : si data.cash_difference_alert → afficher écart en rouge
 * 5. DUPLICATA : si data.is_reprint → afficher bandeau DUPLICATA en rouge
 * 6. Bouton "Imprimer" → printer service
 * 7. Bouton "Fermer"
 *
 * Données disponibles dans this.props.data :
 * ───────────────────────────────────────────
 * {
 *   type: 'Z',
 *   name,           // numéro Z ex: Z/2026/00007
 *   is_reprint,     // boolean → afficher DUPLICATA
 *   date_open, date_close, date_printed,
 *   session_name,
 *   order_ref_first, order_ref_last, order_count,
 *   employees: ['Salwa Houssni', ...],
 *   total_ht, total_tax, total_ttc,
 *   payments: [{method_name, amount, count}],
 *   cash_start, cash_transaction, cash_out,
 *   cash_theoretical, cash_counted, cash_difference,
 *   cash_difference_alert,  // boolean → écart > 5 DH
 *   company: {name, ice, l10n_ma_if, l10n_ma_tp}
 * }
 */

// TODO : Claude Code implémente ce fichier
