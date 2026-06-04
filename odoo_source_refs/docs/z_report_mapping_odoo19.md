# Mapping Rapport Z → Odoo 19 CE — Kodomo Jouet
## Base de développement Claude Code — Module `l10n_ma_pos_legal`

> **Source de vérité :** inspection XML-RPC live sur `https://odoo.kodomo.ma` (base `kodomo`) le 03/06/2026 — Odoo `19.0-20251124`
> Le Rapport Z est le rapport de **clôture de session** : il fige définitivement les totaux, accompagne la fermeture de `pos.session` (`state = 'closed'`) et constitue la pièce fiscale/comptable de référence de la journée.

---

## Données réelles de l'instance (live)

```
Dernières sessions :
  id:24  Kodomo MHA/00019  state=opened   start=2026-06-03 09:25  stop=false   (actuelle)
  id:23  Kodomo MHA/00018  state=closed   start=2026-06-02 09:57  stop=2026-06-02 19:01
  id:22  Kodomo MHA/00017  state=closed   start=2026-05-24 09:14  stop=2026-05-24 19:00

Méthodes paiement : Espèces (id:1, cash), Carte (id:2, bank)
TVA               : 1 taux — 20%, price_include=true, name="20% 80"
Lien comptable    : session.move_id → account.move (écriture générée à la clôture)
```

---

## 1. En-tête

| Élément maquette | Modèle | Champ vérifié | Statut | Valeur réelle |
|---|---|---|---|---|
| Logo | `res.company` | `logo` (binary, computed) | ✅ | À injecter. |
| `POS NAME` | `pos.config` | `name` (char, stored) | ✅ | `"Kodomo MHA"` |
| `ICE` | `res.company` | `company_registry` (char, computed) | ✅ | `"003719751000038"` |
| `IF` | `res.company` | `l10n_ma_if` (custom) | à créer | Voir receipt_mapping. |
| `TP` | `res.company` | `l10n_ma_tp` (custom) | à créer | Voir receipt_mapping. |
| `Z Rapport` (titre) | — | libellé statique | — | Encadré double bordure (identique au X). |

---

## 2. Bloc Identité de session

| Élément maquette | Modèle | Champ vérifié | Statut | Remarque |
|---|---|---|---|---|
| `Session : 00042-001` | `pos.session` | `name` (char, stored) | ✅ | Ex réel : `"Kodomo MHA/00018"`. Afficher le nom de session. |
| `Ouverture : 01/06/2026 09:00` | `pos.session` | `start_at` (datetime, stored) | ✅ | Ex réel : `"2026-06-02 09:57:02"`. Formater `Africa/Casablanca`. |
| `Clôture : 01/06/2026 20:47` | `pos.session` | `stop_at` (datetime, stored) | ✅ | Ex réel : `"2026-06-02 19:01:20"`. **Figé** à la fermeture. |
| `Caissier(s) : user1 / user2` | `pos.session` | `user_id` (many2one → `res.users`, stored) | ✅ | Responsable de session = `user_id.name`. Si multi-employé, lister les `employee_id` distincts des commandes. |
| `Tickets émis : N° 0001 → 0042` | `pos.order` | `tracking_number` (char, stored) | ✅ | Min et max de `tracking_number` sur les commandes de la session. Label Odoo : "Order Number". |
| `Nb transactions : 42` | `pos.session` | `order_count` (integer, computed) | ✅ | Nombre de commandes payées de la session. |

**Calcul des bornes de tickets :**
```python
session = env['pos.session'].browse(session_id)
orders = env['pos.order'].search([
    ('session_id', '=', session_id),
    ('state', 'in', ['paid', 'done', 'invoiced'])
], order='id asc')
ticket_first = orders[0].tracking_number  if orders else '—'
ticket_last  = orders[-1].tracking_number if orders else '—'
```

---

## 3. Bloc Ventes

Source : agrégation **figée** des `pos.order` de la session. À persister dans `pos.report.z` (voir §7).

| Élément maquette | Source ORM | Champs vérifiés | Statut | Calcul |
|---|---|---|---|---|
| `Total HT` | `pos.order` | `amount_total`, `amount_tax` (stored) | ✅ | `sum(amount_total - amount_tax)` |
| `TVA 20%` | `pos.order` | `amount_tax` (stored) | ✅ | `sum(amount_tax)` |
| `TOTAL TTC` | `pos.order` | `amount_total` (stored) | ✅ | `sum(amount_total)` |

**Instance Kodomo — 1 seul taux TVA (20%, price_include=true) :**
```python
domain = [
    ('session_id', '=', session_id),
    ('state', 'in', ['paid', 'done', 'invoiced'])
]
result = env['pos.order'].read_group(domain, ['amount_total', 'amount_tax'], [])
total_ttc = result[0]['amount_total']
total_tax = result[0]['amount_tax']
total_ht  = total_ttc - total_tax
```

**Important :** ces totaux doivent être **persistés** au moment de la clôture dans `pos.report.z`. Une réimpression ne doit jamais recalculer.

---

## 4. Bloc Paiements

Source : `pos.payment` de la session groupés par `payment_method_id`. **Identique au X mais sur session clôturée.**

| Colonne maquette | Source ORM | Champ vérifié | Statut | Remarque |
|---|---|---|---|---|
| `Mode` | `pos.payment.method` | `name` (char, stored) | ✅ | `"Espèces"`, `"Carte"` |
| `Montant` | `pos.payment` | `amount` (monetary, stored) | ✅ | `sum(amount)` par méthode |
| `Nb` | `pos.payment` | count | ✅ | Nb de paiements par méthode |
| `Total / nb_total` | — | somme globale | — | Total doit égaler `amount_total` des ventes |

```python
payments = env['pos.payment'].read_group(
    [('session_id', '=', session_id)],
    ['payment_method_id', 'amount'],
    ['payment_method_id']
)
```

---

## 5. Bloc Caisse espèces — Spécifique Z (avec comptage)

Tous les champs vérifiés sur `pos.session` :

| Élément maquette | Champ vérifié | Statut | Type | Stocké | Label Odoo |
|---|---|---|---|---|---|
| `Fond initial` | `cash_register_balance_start` | ✅ | `monetary` | stored | "Starting Balance" |
| `Entrées espèces` | `cash_real_transaction` | ✅ | `monetary` | stored | "Transaction" |
| `Retraits` | `statement_line_ids` filtré | ✅ | `one2many` | stored | "Cash Lines" |
| `Solde théorique` | `cash_register_balance_end` | ✅ | `monetary` | **computed** | "Theoretical Closing Balance" |
| `Solde compté` | `cash_register_balance_end_real` | ✅ | `monetary` | **stored** | "Ending Balance" |
| `Écart` | `cash_register_difference` | ✅ | `monetary` | **computed** | "Before Closing Difference" |

**Champs absents en v19 (ne pas utiliser) :**
```
cash_register_total_entry_encoding  → ❌ ABSENT
cash_real_expected                  → ❌ ABSENT
```

**Logique caisse complète :**
```python
session = env['pos.session'].browse(session_id)

# Champs stockés (figés à la clôture)
fond_initial         = session.cash_register_balance_start       # stored
solde_compte         = session.cash_register_balance_end_real    # stored (saisi par caissier)
total_transactions   = session.cash_real_transaction             # stored

# Champs calculés (à recalculer ou persister)
solde_theorique      = session.cash_register_balance_end         # computed
ecart                = session.cash_register_difference          # computed = solde_compte - solde_theorique

# Retraits/entrées manuels depuis statement_line_ids
cash_moves = session.statement_line_ids.filtered(
    lambda l: l.journal_id == session.cash_journal_id
)
retraits = sum(cash_moves.filtered(lambda l: l.amount < 0).mapped('amount'))
entrees  = sum(cash_moves.filtered(lambda l: l.amount > 0).mapped('amount'))
```

**Dans le Rapport Z uniquement :**
- `cash_register_balance_end_real` → solde compté physiquement par le caissier
- `cash_register_difference` → écart = compté − théorique (négatif = manquant, positif = excédent)
- Mettre en évidence si `abs(ecart) > seuil configurable`

---

## 6. Numérotation légale & code-barres Z

| Élément maquette | Modèle | Champ | Statut | Recommandation |
|---|---|---|---|---|
| Code-barres `Z-2026-00007` | `pos.report.z` | `name` / `l10n_ma_z_number` | à créer | Séquence légale **inviolable**. |
| `Document généré le 01/06/2026 à 20:47` | — | `stop_at` (date clôture) + `create_date` (date impression) | ✅ | Distinguer les deux : clôture est figée, impression est courante. |

**Séquence légale (ir.sequence) :**
```xml
<!-- data/ir_sequence_data.xml -->
<record id="seq_pos_report_z" model="ir.sequence">
    <field name="name">Rapport Z POS — Numéro Légal</field>
    <field name="code">pos.report.z</field>
    <field name="prefix">Z-%(year)s-</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
    <field name="number_increment">1</field>
    <!-- Ne jamais réinitialiser ce compteur -->
</record>
```

**Règles absolues sur le numéro Z :**
1. Attribué **une seule fois** à la clôture (transaction atomique)
2. **Jamais régénéré** à la réimpression
3. `readonly=True` dès attribution
4. Contrainte `unique` sur `session_id` dans `pos.report.z`

---

## 7. Modèle de persistance `pos.report.z` (obligatoire)

Le Z fiscal doit être un **snapshot persistant**. Les réimpressions lisent ce snapshot, jamais les données en live.

```python
# models/pos_report_z.py
from odoo import models, fields, api
from odoo.exceptions import UserError

class PosReportZ(models.Model):
    _name = 'pos.report.z'
    _description = 'Rapport Z — Clôture de session POS'
    _order = 'id desc'

    # Identification
    name             = fields.Char('Numéro Z', readonly=True, copy=False, index=True)
    session_id       = fields.Many2one('pos.session', 'Session', readonly=True,
                                       ondelete='restrict', required=True)
    company_id       = fields.Many2one('res.company', readonly=True)
    config_id        = fields.Many2one('pos.config', readonly=True)

    # Horodatages figés
    date_open        = fields.Datetime('Ouverture', readonly=True)
    date_close       = fields.Datetime('Clôture', readonly=True)
    date_printed     = fields.Datetime('Date impression', default=fields.Datetime.now)

    # Snapshot ventes
    amount_total_ht  = fields.Monetary('Total HT', readonly=True, currency_field='currency_id')
    amount_tax       = fields.Monetary('Total TVA', readonly=True, currency_field='currency_id')
    amount_total_ttc = fields.Monetary('Total TTC', readonly=True, currency_field='currency_id')
    currency_id      = fields.Many2one('res.currency', readonly=True)

    # Snapshot caisse
    cash_start       = fields.Monetary('Fond initial', readonly=True, currency_field='currency_id')
    cash_transaction = fields.Monetary('Entrées espèces', readonly=True, currency_field='currency_id')
    cash_out         = fields.Monetary('Retraits', readonly=True, currency_field='currency_id')
    cash_theoretical = fields.Monetary('Solde théorique', readonly=True, currency_field='currency_id')
    cash_counted     = fields.Monetary('Solde compté', readonly=True, currency_field='currency_id')
    cash_difference  = fields.Monetary('Écart', readonly=True, currency_field='currency_id')

    # Snapshot tickets
    order_ref_first  = fields.Char('1er ticket', readonly=True)
    order_ref_last   = fields.Char('Dernier ticket', readonly=True)
    order_count      = fields.Integer('Nb transactions', readonly=True)

    # Lignes TVA (JSON)
    tax_details      = fields.Json('Détail TVA', readonly=True)
    # Lignes paiements (JSON)
    payment_details  = fields.Json('Détail paiements', readonly=True)

    # Caissiers
    user_ids         = fields.Many2many('res.users', string='Caissiers', readonly=True)

    # État
    state            = fields.Selection([
        ('draft', 'Brouillon'),
        ('done', 'Émis')
    ], default='draft', readonly=True)
    is_reprint       = fields.Boolean('Réimpression', default=False)

    _sql_constraints = [
        ('session_unique', 'unique(session_id)', 'Un seul Rapport Z par session.')
    ]

    def action_print(self):
        """Verrouiller après première impression."""
        self.ensure_one()
        if self.state == 'done':
            self.is_reprint = True
        else:
            self.state = 'done'
        return self.env.ref('l10n_ma_pos_legal.action_report_z').report_action(self)

    @api.model
    def create_from_session(self, session_id):
        """Appeler à la clôture de session. Atomique."""
        session = self.env['pos.session'].browse(session_id)
        if self.search([('session_id', '=', session_id)], limit=1):
            raise UserError('Un Rapport Z existe déjà pour cette session.')

        orders = self.env['pos.order'].search([
            ('session_id', '=', session_id),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ], order='id asc')

        sales = self.env['pos.order'].read_group(
            [('session_id', '=', session_id), ('state', 'in', ['paid', 'done', 'invoiced'])],
            ['amount_total', 'amount_tax'], []
        )
        total_ttc = sales[0]['amount_total'] if sales else 0.0
        total_tax = sales[0]['amount_tax']   if sales else 0.0

        payments = self.env['pos.payment'].read_group(
            [('session_id', '=', session_id)],
            ['payment_method_id', 'amount'], ['payment_method_id']
        )

        cash_moves = session.statement_line_ids.filtered(
            lambda l: l.journal_id == session.cash_journal_id
        )
        cash_out = sum(cash_moves.filtered(lambda l: l.amount < 0).mapped('amount'))

        return self.create({
            'name':             self.env['ir.sequence'].next_by_code('pos.report.z'),
            'session_id':       session.id,
            'company_id':       session.company_id.id,
            'config_id':        session.config_id.id,
            'date_open':        session.start_at,
            'date_close':       session.stop_at,
            'amount_total_ht':  total_ttc - total_tax,
            'amount_tax':       total_tax,
            'amount_total_ttc': total_ttc,
            'currency_id':      session.currency_id.id,
            'cash_start':       session.cash_register_balance_start,
            'cash_transaction': session.cash_real_transaction,
            'cash_out':         cash_out,
            'cash_theoretical': session.cash_register_balance_end,
            'cash_counted':     session.cash_register_balance_end_real,
            'cash_difference':  session.cash_register_difference,
            'order_ref_first':  orders[0].tracking_number  if orders else '',
            'order_ref_last':   orders[-1].tracking_number if orders else '',
            'order_count':      len(orders),
            'payment_details':  [{
                'method': p['payment_method_id'][1],
                'amount': p['amount'],
                'count':  p['payment_method_id_count']
            } for p in payments],
            'user_ids':         [(6, 0, [session.user_id.id])],
            'state':            'draft',
        })
```

---

## 8. Hook clôture de session

```python
# models/pos_session.py
from odoo import models

class PosSession(models.Model):
    _inherit = 'pos.session'

    def action_pos_session_close(self, bank_payment_method_diffs=None):
        """Générer le Rapport Z à la clôture."""
        res = super().action_pos_session_close(bank_payment_method_diffs)
        for session in self:
            if session.state == 'closed':
                self.env['pos.report.z'].create_from_session(session.id)
        return res
```

---

## 9. Récapitulatif champs vérifiés Rapport Z

| Champ | Modèle | Présent | Stocké | Utilisation Z |
|---|---|---|---|---|
| `name` | `pos.session` | ✅ | stored | Identifiant session |
| `start_at` | `pos.session` | ✅ | stored | Date ouverture (figée) |
| `stop_at` | `pos.session` | ✅ | stored | Date clôture (figée) |
| `state` | `pos.session` | ✅ | stored | Vérification `closed` |
| `user_id` | `pos.session` | ✅ | stored | Caissier responsable |
| `order_ids` | `pos.session` | ✅ | stored | Commandes |
| `order_count` | `pos.session` | ✅ | computed | Nb transactions |
| `move_id` | `pos.session` | ✅ | stored | Écriture comptable liée |
| `cash_register_balance_start` | `pos.session` | ✅ | stored | Fond initial |
| `cash_register_balance_end` | `pos.session` | ✅ | computed | Solde théorique |
| `cash_register_balance_end_real` | `pos.session` | ✅ | stored | **Solde compté** (spécifique Z) |
| `cash_register_difference` | `pos.session` | ✅ | computed | **Écart** (spécifique Z) |
| `cash_real_transaction` | `pos.session` | ✅ | stored | Total espèces encaissées |
| `statement_line_ids` | `pos.session` | ✅ | stored | Mouvements caisse manuels |
| `tracking_number` | `pos.order` | ✅ | stored | Bornes N° tickets |
| `amount_total` | `pos.order` | ✅ | stored | Total TTC |
| `amount_tax` | `pos.order` | ✅ | stored | Total taxes |
| `amount` | `pos.payment` | ✅ | stored | Montant paiement |
| `payment_method_id` | `pos.payment` | ✅ | stored | Méthode paiement |
| `company_registry` | `res.company` | ✅ | computed | ICE |
| `cash_register_total_entry_encoding` | `pos.session` | ❌ ABSENT | — | Ne pas utiliser |
| `cash_real_expected` | `pos.session` | ❌ ABSENT | — | Ne pas utiliser |
| `sequence_number` | `pos.session` | ❌ ABSENT | — | Ne pas utiliser pour les bornes tickets |
