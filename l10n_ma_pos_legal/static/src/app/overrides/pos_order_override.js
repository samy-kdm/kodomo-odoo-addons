/** @odoo-module **/
import { patch } from "@web/core/utils/patch";
import { PosOrder } from "@point_of_sale/app/models/pos_order";

// Injecte les champs légaux marocains dans le payload de sérialisation de commande.
// Les champs sont chargés au démarrage via _loader_params_res_company (pos_order.py).
patch(PosOrder.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        const company = this.company;
        if (result && result.company) {
            result.company.ice        = company?.company_registry || "";
            result.company.l10n_ma_if = company?.l10n_ma_if || "";
            result.company.l10n_ma_tp = company?.l10n_ma_tp || "";
        }
        return result;
    },
});
