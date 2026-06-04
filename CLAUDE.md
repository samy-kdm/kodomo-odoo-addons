# CLAUDE.md — Module `l10n_ma_pos_legal` — Kodomo Jouet

> Ce fichier est lu automatiquement par Claude Code au démarrage.
> Il contient tout le contexte nécessaire pour développer le module sans aller-retour.

---

## Contexte projet

Tu développes un module Odoo 19 CE custom pour **Kodomo Jouet** (société KDM SMART HUB),
un magasin de jouets à Mohammedia, Maroc, opérant sur `https://odoo.kodomo.ma`.

Le module s'appelle `l10n_ma_pos_legal`. Il ajoute au Point of Sale Odoo :
1. Un **ticket POS** avec les mentions légales marocaines (ICE, IF, TP)
2. Un **Rapport Z** (clôture de session) accessible depuis la caisse,
   avec snapshot persistant et numérotation légale

---

## Structure du projet

```
kodomo_pos_module/
├── CLAUDE.md                        ← tu lis ce fichier
├── l10n_ma_pos_legal/               ← le module à compléter
│   ├── __manifest__.py              ✅ complet
│   ├── __init__.py                  ✅ complet
│   ├── models/
│   │   ├── __init__.py              ✅ complet
│   │   ├── res_company.py           ✅ complet — champs IF, TP
│   │   ├── pos_order.py             ✅ complet — injection champs légaux POS
│   │   ├── pos_session.py           ✅ complet — hook clôture
│   │   └── pos_report_z.py          ✅ complet — modèle snapshot Z
│   ├── security/
│   │   └── ir.model.access.csv      ✅ complet
│   ├── data/
│   │   └── ir_sequence_data.xml     ✅ complet — séquence Z
│   ├── views/
│   │   ├── pos_report_z_views.xml   ✅ complet — back-office liste/form Z
│   │   └── pos_report_z_menu.xml    ✅ complet — menu back-office
│   └── static/src/app/
│       ├── overrides/
│       │   ├── order_receipt_override.xml   ⬜ PLACEHOLDER — à implémenter
│       │   └── pos_order_override.js        ⬜ PLACEHOLDER — à implémenter
│       ├── components/navbar/z_report_button/
│       │   └── z_report_button.js           ⬜ PLACEHOLDER — à implémenter
│       │   └── z_report_button.xml          ⬜ À CRÉER
│       └── screens/z_report_screen/
│           ├── z_report_screen.js           ⬜ PLACEHOLDER — à implémenter
│           └── z_report_screen.xml          ⬜ PLACEHOLDER — à implémenter
│
├── odoo_source_refs/                ← fichiers source Odoo 19 — NE PAS MODIFIER
│   ├── pos_models/
│   │   ├── pos_order.py             ← modèle Python pos.order natif
│   │   ├── pos_session.py           ← modèle Python pos.session natif
│   │   └── pos_config.py            ← modèle Python pos.config natif
│   └── pos_owl/
│       ├── receipt/
│       │   ├── order_receipt.js     ← composant OWL ticket natif ⭐ LIRE EN PREMIER
│       │   ├── order_receipt.xml    ← template OWL ticket natif ⭐ LIRE EN PREMIER
│       │   ├── receipt_header.js
│       │   ├── receipt_header.xml
│       │   ├── receipt_screen.js
│       │   └── receipt_screen.xml
│       ├── services/
│       │   ├── pos_store.js         ← store global POS (accès company, session, config)
│       │   ├── pos_printer_service.js ← service impression thermique
│       │   └── report_service.js    ← service rapport
│       ├── models/
│       │   ├── pos_order.js         ← modèle JS pos.order (export_for_printing ici) ⭐
│       │   ├── pos_order_line.js
│       │   └── pos_config.js
│       └── navbar/
│           ├── sale_details_button.js  ← référence pattern bouton navbar ⭐
│           ├── sale_details_button.xml ← référence template bouton navbar ⭐
│           └── sales_detail_report.xml ← référence template rapport navbar ⭐
│
├── receipt_mapping_odoo19.md        ← spec ticket — champs vérifiés live
├── z_report_mapping_odoo19.md       ← spec rapport Z — champs vérifiés live
├── receipt_mockup.html              ← maquette visuelle ticket 80mm
└── z_report_mockup.html             ← maquette visuelle rapport Z 80mm
```

---

## Instance Odoo — données réelles

```
URL             : https://odoo.kodomo.ma
Version         : 19.0-20251124
Base            : kodomo
Société         : KDM SMART HUB
Config POS      : Kodomo MHA (id:1)
Devise          : MAD (id:109) — afficher "DH" sur les documents
Fuseau horaire  : Africa/Casablanca

Modules installés pertinents :
  ✅ point_of_sale
  ✅ pos_hr        → employee_id actif sur pos.order
  ✅ account
  ✅ hr

Méthodes de paiement configurées :
  id=1  Espèces       is_cash_count=True   type="cash"
  id=2  Carte         is_cash_count=False  type="bank"
  id=3  Compte client is_cash_count=False  type="pay_later"

TVA configurée : 1 seule taxe "20% 80", amount=20.0, price_include=True
  → Tous les prix sont TTC. price_unit s'affiche directement.
  → Base HT = amount_total / 1.20

Footer ticket actuel (pos.config.receipt_footer) :
  "رقم 1، شارع سبتة، مجموعة ياسمين عمارة 6
   1, Bd Sebta, Groupe Yasmine, Imm. 6
   Mohammedia - المحمدية
   WhatsApp 07 23 84 20 00"

Champs légaux société :
  ICE : company_registry = "003719751000038"  (champ natif, déjà renseigné)
  IF  : l10n_ma_if → champ custom à créer (dans res_company.py ✅ déjà fait)
  TP  : l10n_ma_tp → champ custom à créer (dans res_company.py ✅ déjà fait)
```

---

## Décisions de design validées

| # | Sujet | Décision |
|---|---|---|
| 1 | Déclenchement Z | Bouton dans l'interface POS (OWL), sans quitter la caisse |
| 2 | Numéro légal ticket | `tracking_number` natif Odoo (`00042-001-0001`) — pas de séquence custom |
| 3 | Séquence numéro Z | Standard Odoo `ir.sequence` format `Z/2026/00001` |
| 4 | Caissiers sur le Z | Tous les `employee_id` distincts des commandes de la session |
| 5 | Alerte écart caisse | Affichage rouge si `abs(cash_register_difference) > 5` DH |
| 6 | Réimpression Z | Mention `DUPLICATA` en rouge en haut + date d'impression courante |

---

## Champs ORM vérifiés live — points critiques

```
✅ pos.order.date_order          → datetime, stored  (PAS creation_date ❌)
✅ pos.order.employee_id         → many2one hr.employee (mode pos_hr actif)
✅ pos.order.tracking_number     → char, stored = numéro ticket
✅ pos.order.amount_total        → monetary, stored = TTC
✅ pos.order.amount_tax          → monetary, stored = taxes
✅ pos.order.amount_return       → monetary, stored = rendu monnaie
✅ pos.order.line.full_product_name → char, stored (inclut variantes)
✅ pos.order.line.price_subtotal_incl → monetary, stored = total TTC ligne
✅ pos.session.cash_register_balance_start     → monetary, stored
✅ pos.session.cash_register_balance_end       → monetary, COMPUTED
✅ pos.session.cash_register_balance_end_real  → monetary, stored (solde compté)
✅ pos.session.cash_register_difference        → monetary, COMPUTED (écart)
✅ pos.session.cash_real_transaction           → monetary, stored
✅ pos.session.statement_line_ids              → one2many account.bank.statement.line
✅ pos.payment.method.is_cash_count            → boolean, stored

❌ cash_register_total_entry_encoding → ABSENT en v19 — ne pas utiliser
❌ cash_real_expected                 → ABSENT en v19 — ne pas utiliser
❌ sequence_number sur pos.session    → ABSENT en v19 — ne pas utiliser
❌ creation_date sur pos.order        → ABSENT en v19 — ne pas utiliser
```

---

## Instructions par fichier à implémenter

### Ordre d'implémentation recommandé

```
1. order_receipt_override.xml   → ticket (le plus visible, facile à tester)
2. pos_order_override.js        → injection données dans export_for_printing
3. z_report_button.js/.xml     → bouton navbar
4. z_report_screen.js/.xml     → écran Rapport Z
```

---

### 1. `order_receipt_override.xml`

**Objectif :** Hériter du template `point_of_sale.OrderReceipt` pour ajouter
les mentions légales marocaines dans l'en-tête du ticket.

**Lire avant de coder :**
- `odoo_source_refs/pos_owl/receipt/order_receipt.xml` — structure complète du ticket
- `odoo_source_refs/pos_owl/receipt/receipt_header.xml` — en-tête natif
- `receipt_mockup.html` — rendu visuel attendu
- `receipt_mapping_odoo19.md` — mapping complet des champs

**Ce que le template doit afficher (ordre de la maquette) :**
```
[LOGO société]
POS NAME (config.name = "Kodomo MHA")
ICE : 003719751000038    (company.company_registry)
TP : XXXXX   IF : XXXXX  (company.l10n_ma_tp / company.l10n_ma_if)
─────────────────────────
Date : JJ/MM/AAAA HH:MM  (order.date_order, fuseau Africa/Casablanca)
Caissier : Salwa Houssni  (order.employee_id.name)
─────────────────────────
Article          QTE   P.U    Total
Peluche Lapin     1   149,00  149,00
...
─────────────────────────
TOTAL TTC               597,00 DH
Nb Articles : 4
─────────────────────────
Paiement — Espèces :    600,00 DH
Rendu :                   3,00 DH
─────────────────────────
TVA    Base HT   TVA    TTC
20%    497,50    99,50  597,00
─────────────────────────
** Merci de votre visite **
[footer de pos.config.receipt_footer]
[CODE-BARRES tracking_number]
00042-001-0001
```

**Données disponibles dans le template OWL :**
Les données sont dans `receiptInfo` (objet retourné par `export_for_printing()`).
Après notre override JS, `receiptInfo.company` contiendra :
`ice`, `l10n_ma_if`, `l10n_ma_tp` en plus des champs natifs.

---

### 2. `pos_order_override.js`

**Objectif :** Patcher `export_for_printing()` pour injecter ICE, IF, TP
dans le payload du ticket.

**Lire avant de coder :**
- `odoo_source_refs/pos_owl/models/pos_order.js` — trouver le nom exact
  de la classe et la signature de `export_for_printing()`
- `odoo_source_refs/pos_owl/services/pos_store.js` — accès à `company`

**Pattern attendu :**
```javascript
import { patch } from "@web/core/utils/patch";
import { [NomExactClasse] } from "@point_of_sale/app/models/pos_order";

patch([NomExactClasse].prototype, {
    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        // Injecter depuis this.session.company ou this.config.company
        // (vérifier le chemin exact dans pos_order.js source)
        result.company.ice        = ... || "";
        result.company.l10n_ma_if = ... || "";
        result.company.l10n_ma_tp = ... || "";
        return result;
    }
});
```

---

### 3. `z_report_button.js` + `z_report_button.xml` (fichier XML à créer)

**Objectif :** Ajouter un bouton Rapport Z dans la navbar du POS.

**Lire avant de coder :**
- `odoo_source_refs/pos_owl/navbar/sale_details_button.js` — pattern exact à suivre
- `odoo_source_refs/pos_owl/navbar/sale_details_button.xml` — template bouton
- `odoo_source_refs/pos_owl/navbar/sales_detail_report.xml` — template rapport navbar

**Comportement :**
```
Bouton "Rapport Z" :
  → appel RPC : orm.call("pos.session", "get_z_report_data_for_pos", [session.id])
  → navigate vers ZReportScreen avec les données reçues
  → (la création du snapshot Z se fait côté serveur à la vraie clôture,
     ici on affiche juste un aperçu pour impression)
```

**Note :** Ajouter `get_z_report_data_for_pos()` dans `pos_session.py`.

---

### 4. `z_report_screen.js` + `z_report_screen.xml`

**Objectif :** Écran POS affichant le Rapport Z formaté, avec gestion
DUPLICATA et alerte écart.

**Lire avant de coder :**
- `z_report_mockup.html` — rendu visuel exact attendu
- `z_report_mapping_odoo19.md` — spec complète

**Structure de `props.data` reçu :**
```javascript
{
  type: 'Z',
  name,              // "Z/2026/00007"
  is_reprint,        // boolean → afficher bandeau DUPLICATA rouge
  date_open, date_close, date_printed,
  session_name,
  order_ref_first,   // "00001-001-0001"
  order_ref_last,    // "00042-001-0042"
  order_count,       // 42
  employees: ['Salwa Houssni', ...],
  total_ht, total_tax, total_ttc,
  payments: [{ method_name, amount, count }],
  cash_start, cash_transaction, cash_out,
  cash_theoretical,
  cash_counted,      // solde compté physiquement
  cash_difference,   // écart = compté - théorique
  cash_difference_alert, // boolean → true si |écart| > 5 DH → afficher en ROUGE
  company: { name, ice, l10n_ma_if, l10n_ma_tp }
}
```

---

## Règles générales de développement

### Python (côté serveur)
- Toujours hériter avec `_inherit` — jamais réécrire un modèle natif
- Appeler `super()` avant d'ajouter la logique custom
- Logger les erreurs avec `_logger.error()` — ne jamais avaler silencieusement
- Transactions atomiques pour la création du Z (déjà géré dans `create_from_session`)

### JavaScript OWL (côté frontend)
- Utiliser `patch()` de `@web/core/utils/patch` pour les overrides
- Utiliser `useService("orm")` pour les appels RPC
- Utiliser `useService("printer")` pour l'impression thermique
- Enregistrer les écrans avec `registry.category("pos_screens").add()`
- Tous les imports depuis `@point_of_sale/...` ou `@web/...`
- **Ne jamais** utiliser `require()` — uniquement `import`

### XML OWL
- Héritage template : `t-inherit="point_of_sale.OrderReceipt" t-inherit-mode="extension"`
- XPath basé sur les classes CSS ou les attributs — pas sur la position
- Tester chaque xpath contre le fichier source `order_receipt.xml`

### Formatage devise
```javascript
// Dans les templates OWL, utiliser :
this.env.utils.formatCurrency(amount)
// Ou depuis le composant :
formatCurrency(amount) {
    return this.pos.env.utils.formatCurrency(amount);
}
```

### Formatage date (fuseau Casablanca)
```javascript
import { formatDateTime } from "@web/core/l10n/dates";
// Ou utiliser luxon directement
import { DateTime } from "luxon";
DateTime.fromISO(isoString).setZone("Africa/Casablanca").toFormat("dd/MM/yyyy HH:mm");
```

---

## Déploiement sur le VPS après développement

```bash
# 1. Copier le module sur le VPS
scp -r l10n_ma_pos_legal/ root@odoo.kodomo.ma:/opt/odoo/custom_addons/

# 2. Ajouter le chemin dans odoo.conf (une seule fois)
# addons_path = /usr/lib/python3/dist-packages/odoo/addons,/opt/odoo/custom_addons

# 3. Redémarrer Odoo
sudo systemctl restart odoo

# 4. Installer le module depuis le back-office
# Paramètres → Apps → Rechercher "l10n_ma_pos_legal" → Installer

# 5. Mettre à jour après modification
sudo -u odoo odoo -c /etc/odoo/odoo.conf -u l10n_ma_pos_legal -d kodomo --stop-after-init
```

---

## Démarrage — première tâche

**Commence par lire ces fichiers dans cet ordre :**

1. `odoo_source_refs/pos_owl/receipt/order_receipt.xml`
2. `odoo_source_refs/pos_owl/receipt/order_receipt.js`
3. `odoo_source_refs/pos_owl/models/pos_order.js`
4. `receipt_mockup.html`
5. `receipt_mapping_odoo19.md`

**Puis implémente `order_receipt_override.xml` et `pos_order_override.js`.**

Une fois le ticket validé visuellement, passe au bouton Z puis à l'écran Z.

Pose une question si un chemin d'accès dans les fichiers source
ne correspond pas à ce que tu attends — ne jamais supposer.
