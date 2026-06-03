# Mapping Ticket POS → Odoo 19 CE — Kodomo Jouet
## Base de développement Claude Code — Module `l10n_ma_pos_legal`

> **Source de vérité :** inspection XML-RPC live sur `https://odoo.kodomo.ma` (base `kodomo`) le 03/06/2026 — Odoo `19.0-20251124`
> Tous les champs marqués ✅ sont **confirmés présents** sur cette instance. Les ❌ sont absents.
> Le ticket POS est rendu **côté frontend OWL** via `export_for_printing()` — pas par un rapport QWeb serveur.

---

## Données réelles de l'instance (live)

```
Société         : KDM SMART HUB
Config POS      : Kodomo MHA
Session active  : Kodomo MHA/00019 (ouverte)
Caissière       : Salwa Houssni
Devise          : MAD (id: 109)
ICE actuel      : company_registry = "003719751000038" (champ natif)
VAT             : false (non renseigné)
Méthodes paiement :
  - Espèces  (id:1) is_cash_count=true,  type="cash"
  - Carte    (id:2) is_cash_count=false, type="bank"
  - Compte client (id:3) is_cash_count=false, type="pay_later"
TVA configurée  : 1 seule taxe — "20% 80", amount=20.0, price_include=true, type_tax_use="sale"
Footer ticket   : "رقم 1، شارع سبتة، مجموعة ياسمين عمارة 6\n1, Bd Sebta, Groupe Yasmine, Imm. 6\nMohammedia - المحمدية\nWhatsApp 07 23 84 20 00"
Header ticket   : false (non configuré)
```

---

## 1. En-tête

| Élément maquette | Modèle | Champ ORM vérifié | Statut | Accès JS / remarque |
|---|---|---|---|---|
| Logo | `res.company` | `logo` (binary, computed) | ✅ | Non affiché par défaut en POS OWL → à ajouter au template hérité. |
| `POS NAME` (nom caisse) | `pos.config` | `name` (char, stored) | ✅ | Valeur réelle : `"Kodomo MHA"`. Accès via `session.config_id.name`. Préférer `pos.config.name` à `res.company.name` (multi-caisse). |
| `ICE : 003719751000038` | `res.company` | `company_registry` (char, computed) | ✅ | **Décision :** réutiliser `company_registry` qui contient déjà l'ICE réel. Pas besoin de champ custom `l10n_ma_ice` — valeur déjà présente. |
| `IF : 66288862` | `res.company` | `vat` (char, computed) | ❌ vide | `vat` est `false` sur cette instance. Créer champ custom `l10n_ma_if` (Char). |
| `TP : 39503002` | `res.company` | aucun champ natif | ❌ absent | Créer champ custom `l10n_ma_tp` (Char). |

**Champs custom à créer sur `res.company` :**
```python
# Dans models/res_company.py
l10n_ma_if = fields.Char('Identifiant Fiscal', size=20)
l10n_ma_tp = fields.Char('Taxe Professionnelle', size=20)
# ICE → réutiliser company_registry (déjà renseigné)
```

---

## 2. Métadonnées de la transaction

| Élément maquette | Modèle | Champ ORM vérifié | Statut | Accès JS / remarque |
|---|---|---|---|---|
| `Date : 01/06/2026 14:32` | `pos.order` | `date_order` (datetime, stored) | ✅ | Formater en `Africa/Casablanca`. `creation_date` ❌ ABSENT — ne pas utiliser. |
| `Caissier : username` | `pos.order` | `employee_id` (many2one → `hr.employee`, stored) | ✅ | Valeur réelle : Salwa Houssni. `employee_id` est le bon champ (mode multi-employé actif). `user_id` existe aussi mais `employee_id` a le label "Cashier" dans le code. Afficher `employee_id.name` en priorité, fallback `user_id.name`. |

---

## 3. Lignes d'articles

Source : `pos.order.line` — relation `lines` (one2many, stored) sur `pos.order`.

| Colonne maquette | Modèle | Champ ORM vérifié | Statut | Remarque |
|---|---|---|---|---|
| Nom article (`Peluche Lapin 30cm`) | `pos.order.line` | `full_product_name` (char, stored) | ✅ | Inclut les variantes. Accès JS : `line.full_product_name`. |
| `QTE` | `pos.order.line` | `qty` (float, stored) | ✅ | Entiers pour Kodomo. |
| `P.U` (prix unitaire TTC) | `pos.order.line` | `price_unit` (float, stored) | ✅ | **Attention :** `price_unit` est HT. La taxe configurée (`20% 80`) a `price_include=true` → les prix sont **déjà TTC** dans la liste de prix. Afficher directement `price_unit`. |
| `Total` ligne | `pos.order.line` | `price_subtotal_incl` (monetary, stored) | ✅ | Total TTC de la ligne. Label Odoo : "Tax Incl.". |
| Remise (si > 0) | `pos.order.line` | `discount` (float, stored) | ✅ | Afficher uniquement si `discount > 0`. |
| Note client | `pos.order.line` | `customer_note` (char, stored) | ✅ | Optionnel. `note` (char, stored) également disponible ("Product Note"). |

**Champs complémentaires disponibles sur `pos.order.line` :**
```
price_subtotal      → monetary, stored  — montant HT ligne
tax_ids             → many2many → account.tax — taxes appliquées
price_type          → selection, stored
extra_tax_data      → json, stored      — données taxes supplémentaires
refunded_qty        → float, computed   — qté remboursée
```

---

## 4. Totaux

| Élément maquette | Modèle | Champ ORM vérifié | Statut | Remarque |
|---|---|---|---|---|
| `TOTAL TTC 597,00 DH` | `pos.order` | `amount_total` (monetary, stored) | ✅ | Total TTC de la commande. |
| Total HT (pour bloc TVA) | `pos.order` | `amount_total - amount_tax` | calc. | `amount_tax` (monetary, stored) ✅ |
| `Nb Articles : 4` | `pos.order.line` | `sum(line.qty)` | calc. | Somme des quantités (≠ nb de lignes). Ex : 1+1+2=4. |
| Devise `DH` | `res.currency` | `currency_id` (MAD, id:109) | ✅ | Symbole : `MAD`. Afficher `DH` côté template. |

**Champs complémentaires sur `pos.order` :**
```
amount_paid         → monetary, stored  — montant encaissé
amount_difference   → monetary, stored  — différence
amount_return       → monetary, stored  — rendu monnaie ✅
tip_amount          → monetary, stored  — pourboire
```

---

## 5. Bloc TVA

Source : agrégation des taxes par taux depuis `pos.order.line.tax_ids`.

| Colonne maquette | Source ORM | Statut | Remarque |
|---|---|---|---|
| `TVA 20%` | `account.tax.amount` = 20.0, `name` = "20% 80" | ✅ | 1 seule taxe configurée sur l'instance. `price_include=true` → base HT = TTC / 1.20. |
| `Base HT 497,50` | `price_subtotal` sur `pos.order.line` | ✅ | Ou calculer : `amount_total / 1.20`. |
| `TVA 99,50` | `amount_tax` sur `pos.order` | ✅ | Ou `amount_total - (amount_total / 1.20)`. |
| `TTC 597,00` | `amount_total` sur `pos.order` | ✅ | |

**Note TVA :** Avec `price_include=true`, tous les prix affichés sont déjà TTC. La ventilation TVA se calcule ainsi :
```python
base_ht  = amount_total / 1.20   # → 497.50
tva      = amount_total - base_ht # → 99.50
ttc      = amount_total            # → 597.00
```
Accès JS : `order.get_tax_details()` ou agrégation depuis `order.lines` groupé par `tax_ids`.

---

## 6. Paiements

Source : `pos.payment` — relation `payment_ids` (one2many, stored) sur `pos.order`.

| Élément maquette | Modèle | Champ ORM vérifié | Statut | Remarque |
|---|---|---|---|---|
| `Paiement — Espèces : 600,00` | `pos.payment` | `amount` (monetary, stored) | ✅ | Libellé : `payment_method_id.name` = "Espèces". |
| Mode de paiement | `pos.payment` | `payment_method_id` (many2one → `pos.payment.method`, stored) | ✅ | |
| `Rendu : 3,00 DH` | `pos.order` | `amount_return` (monetary, stored) | ✅ | Afficher uniquement si `amount_return > 0` ET méthode Espèces. |
| Détection cash | `pos.payment.method` | `is_cash_count` (boolean, stored) | ✅ | Espèces : `is_cash_count=true`. Carte : `is_cash_count=false`. |

**Méthodes configurées sur l'instance :**
```
id=1  Espèces       is_cash_count=true   type="cash"     → calcul rendu actif
id=2  Carte         is_cash_count=false  type="bank"     → pas de rendu
id=3  Compte client is_cash_count=false  type="pay_later"→ pas de rendu
```

---

## 7. Message de bas de page

| Élément maquette | Modèle | Champ ORM vérifié | Statut | Valeur réelle |
|---|---|---|---|---|
| `** Merci de votre visite **` | `pos.config` | `receipt_footer` (text, stored) | ✅ | Valeur actuelle : adresse bilingue + WhatsApp. `receipt_header` = false. |

Le footer est configurable depuis l'interface POS sans toucher au code.

---

## 8. Code-barres & numérotation

| Élément maquette | Champ | Statut | Recommandation |
|---|---|---|---|
| Code-barres SVG | généré JS | — | Utiliser lib `JsBarcode` côté OWL. Encoder `pos_reference` ou `l10n_ma_legal_number`. |
| `00042-001-0001` (lisible) | `pos.order.tracking_number` (char, stored) | ✅ | Label Odoo : "Order Number". Format natif proche de la maquette. |
| `TK-2026-XXXXX` (format légal) | `l10n_ma_legal_number` (custom) | à créer | Séquence continue non réinitialisable. Attribuée à la validation de commande. |

**Champ custom à créer sur `pos.order` :**
```python
# Dans models/pos_order.py
l10n_ma_legal_number = fields.Char(
    'N° pièce légal', readonly=True, copy=False, index=True
)
```

---

## 9. Architecture d'implémentation OWL

```
Fichiers à créer dans le module l10n_ma_pos_legal :
├── models/
│   ├── res_company.py          # champs l10n_ma_if, l10n_ma_tp
│   └── pos_order.py            # champ l10n_ma_legal_number + ir.sequence
├── static/src/
│   ├── overrides/
│   │   └── models/
│   │       └── pos_order.js    # surcharge export_for_printing()
│   └── xml/
│       └── receipt.xml         # héritage point_of_sale.OrderReceipt
└── data/
    └── ir_sequence_data.xml    # séquence légale pos.ticket.legal
```

**Surcharge JS minimale :**
```javascript
// Injecter les champs légaux dans le payload du ticket
patch(Order.prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.company.l10n_ma_if = this.company.l10n_ma_if;
        result.company.l10n_ma_tp = this.company.l10n_ma_tp;
        result.company.ice        = this.company.company_registry;
        result.l10n_ma_legal_number = this.l10n_ma_legal_number;
        return result;
    }
});
```

---

## 10. Récapitulatif champs vérifiés

| Champ | Modèle | Présent | Notes |
|---|---|---|---|
| `date_order` | `pos.order` | ✅ | Utiliser — `creation_date` ❌ absent |
| `employee_id` | `pos.order` | ✅ | Caissier principal |
| `user_id` | `pos.order` | ✅ | Fallback si pas d'employé |
| `pos_reference` | `pos.order` | ✅ | "Receipt Number" |
| `tracking_number` | `pos.order` | ✅ | "Order Number" |
| `amount_total` | `pos.order` | ✅ | Total TTC |
| `amount_tax` | `pos.order` | ✅ | Total taxes |
| `amount_return` | `pos.order` | ✅ | Rendu monnaie |
| `lines` | `pos.order` | ✅ | one2many vers `pos.order.line` |
| `payment_ids` | `pos.order` | ✅ | one2many vers `pos.payment` |
| `full_product_name` | `pos.order.line` | ✅ | Nom avec variantes |
| `qty` | `pos.order.line` | ✅ | Quantité |
| `price_unit` | `pos.order.line` | ✅ | Prix unitaire (TTC ici car price_include) |
| `price_subtotal_incl` | `pos.order.line` | ✅ | Total TTC ligne |
| `price_subtotal` | `pos.order.line` | ✅ | Total HT ligne |
| `discount` | `pos.order.line` | ✅ | Remise % |
| `tax_ids` | `pos.order.line` | ✅ | Taxes appliquées |
| `amount` | `pos.payment` | ✅ | Montant paiement |
| `payment_method_id` | `pos.payment` | ✅ | Méthode |
| `is_cash_count` | `pos.payment.method` | ✅ | Détecte Espèces |
| `company_registry` | `res.company` | ✅ | Contient l'ICE réel |
| `receipt_footer` | `pos.config` | ✅ | Footer configuré (adresse + tel) |
| `creation_date` | `pos.order` | ❌ | Ne pas utiliser |
