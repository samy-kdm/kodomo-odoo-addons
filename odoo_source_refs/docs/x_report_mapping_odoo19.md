# Mapping Rapport X → Odoo 19 CE — Kodomo Jouet
## Base de développement Claude Code — Module `l10n_ma_pos_legal`

> **Source de vérité :** inspection XML-RPC live sur `https://odoo.kodomo.ma` (base `kodomo`) le 03/06/2026 — Odoo `19.0-20251124`
> Le Rapport X est une **lecture en temps réel de la session ouverte**, sans clôture. Jamais d'écriture.

---

## Données réelles de l'instance (live)

```
Config POS      : Kodomo MHA (id:1)
Session active  : Kodomo MHA/00019 (id:24), state="opened"
  start_at      : 2026-06-03 09:25:31
  stop_at       : false (session en cours)
  user_id       : Salwa Houssni (id:5)
Méthodes paiement disponibles : Espèces (id:1), Carte (id:2)
TVA             : 20% (price_include=true)
```

---

## Concept Rapport X

| | Rapport X | Rapport Z |
|---|---|---|
| Moment | En cours de journée | À la clôture |
| Effet sur session | Aucun — lecture seule | Clôture la session |
| Source | `pos.session` state=`opened` | `pos.session` state=`closed` |
| Répétable | Oui | Non (1 seul Z par session) |
| Écart caisse | Non affiché | Affiché |
| Numérotation | Compteur applicatif libre | Séquence légale inviolable |

**Règle absolue :** le Rapport X ne doit jamais appeler `action_pos_session_closing_control` ni modifier aucune donnée.

---

## 1. En-tête (identique au ticket)

| Élément maquette | Modèle | Champ vérifié | Statut | Valeur réelle |
|---|---|---|---|---|
| Logo | `res.company` | `logo` (binary, computed) | ✅ | À injecter dans le template. |
| `POS NAME` | `pos.config` | `name` (char, stored) | ✅ | `"Kodomo MHA"` via `session.config_id.name`. |
| `ICE` | `res.company` | `company_registry` (char, computed) | ✅ | `"003719751000038"` — champ natif réutilisé. |
| `IF` | `res.company` | `l10n_ma_if` (custom) | à créer | Voir receipt_mapping. |
| `TP` | `res.company` | `l10n_ma_tp` (custom) | à créer | Voir receipt_mapping. |
| `X Rapport` (titre) | — | libellé statique | — | Encadré double bordure dans la maquette. |
| `Lecture seule — session non clôturée` | — | libellé statique conditionnel | — | Afficher tant que `session.state != 'closed'`. |

---

## 2. Bloc Informations

| Élément maquette | Modèle | Champ vérifié | Statut | Remarque |
|---|---|---|---|---|
| `Tiré le : 01/06/2026 14:32` | — | `fields.Datetime.now()` au moment du tirage | — | **Horodatage du tirage**, pas de la session. Ne pas utiliser `start_at`. |
| `Caissier : username` | `pos.session` | `user_id` (many2one → `res.users`, stored) | ✅ | Valeur réelle : `Salwa Houssni` (id:5). Utilisateur responsable de la session. |
| `Session : 00042-001` | `pos.session` | `name` (char, stored) | ✅ | Valeur réelle : `"Kodomo MHA/00019"`. Adapter l'affichage au format de la maquette. |
| `Ouverture session : 09:00` | `pos.session` | `start_at` (datetime, stored) | ✅ | Valeur réelle : `2026-06-03 09:25:31`. Afficher heure seule (format `HH:MM`). |
| `Transactions : 27 / 42` | `pos.session` | `order_count` (integer, computed) | ✅ | Afficher uniquement `order_count` (commandes payées). Le dénominateur `/ 42` n'a pas de source ORM → ne pas implémenter. |

**Requête pour `order_count` :**
```python
# Dans le contrôleur du Rapport X
session = request.env['pos.session'].browse(session_id)
order_count = session.order_count  # computed, filtre les commandes paid/done
# Ou plus précis :
order_count = request.env['pos.order'].search_count([
    ('session_id', '=', session_id),
    ('state', 'in', ['paid', 'done', 'invoiced'])
])
```

---

## 3. Bloc Ventes (en cours)

Source : agrégation des `pos.order` de la session (états `paid`, `done`, `invoiced`).

| Élément maquette | Source ORM | Champs vérifiés | Statut | Calcul |
|---|---|---|---|---|
| `Total HT` | `pos.order` | `amount_total`, `amount_tax` (stored) | ✅ | `sum(amount_total - amount_tax)` |
| `TVA 20%` | `pos.order` | `amount_tax` (stored) | ✅ | `sum(amount_tax)` — 1 seul taux (20%) sur l'instance |
| `TOTAL TTC` | `pos.order` | `amount_total` (stored) | ✅ | `sum(amount_total)` |
| `Nb articles vendus` | `pos.order.line` | `qty` (stored) | ✅ | `sum(line.qty)` sur toutes les lignes des commandes de la session |

**Requête Python (read_group) :**
```python
# Agrégation efficace en une seule requête
domain = [
    ('session_id', '=', session_id),
    ('state', 'in', ['paid', 'done', 'invoiced'])
]
result = env['pos.order'].read_group(
    domain, ['amount_total', 'amount_tax'], []
)
total_ttc = result[0]['amount_total'] if result else 0.0
total_tax = result[0]['amount_tax']   if result else 0.0
total_ht  = total_ttc - total_tax

# Nb articles : requête séparée sur les lignes
lines_result = env['pos.order.line'].read_group(
    [('order_id.session_id', '=', session_id),
     ('order_id.state', 'in', ['paid', 'done', 'invoiced'])],
    ['qty'], []
)
nb_articles = lines_result[0]['qty'] if lines_result else 0
```

**Note :** Avec `price_include=true` (TVA incluse), les remboursements ont `amount_total < 0`. Décider si le X montre le net (ventes − retours) ou le brut → recommandé : **net** pour la cohérence avec la caisse.

---

## 4. Bloc Paiements

Source : `pos.payment` des commandes de la session, groupés par `payment_method_id`.

| Colonne maquette | Source ORM | Champ vérifié | Statut | Remarque |
|---|---|---|---|---|
| `Mode` (Espèces, Carte) | `pos.payment.method` | `name` (char, stored) | ✅ | Valeurs réelles : `"Espèces"`, `"Carte"` |
| `Montant` | `pos.payment` | `amount` (monetary, stored) | ✅ | `sum(amount)` groupé par méthode |
| `Nb` | `pos.payment` | `id` (count) | ✅ | `count(payment)` par méthode |
| `Total` | — | somme globale | — | Doit égaler le `TOTAL TTC` des ventes (contrôle de cohérence) |

**Requête Python :**
```python
payments = env['pos.payment'].read_group(
    [('session_id', '=', session_id)],
    ['payment_method_id', 'amount'],
    ['payment_method_id']
)
# Résultat : [{payment_method_id: [id, name], amount: float, payment_method_id_count: int}]
```

**Méthodes configurées sur l'instance :**
```
Espèces  (id:1) is_cash_count=true   → inclus dans caisse espèces
Carte    (id:2) is_cash_count=false  → hors caisse espèces
```

---

## 5. Bloc Caisse espèces

Champs vérifiés sur `pos.session` (id:24 actuel) :

| Élément maquette | Champ vérifié | Statut | Type | Stocké | Label Odoo |
|---|---|---|---|---|---|
| `Fond initial` | `cash_register_balance_start` | ✅ | `monetary` | stored | "Starting Balance" |
| `Entrées espèces` | `cash_real_transaction` | ✅ | `monetary` | stored | "Transaction" |
| `Retraits` | `statement_line_ids` (filtré) | ✅ | `one2many` → `account.bank.statement.line` | stored | "Cash Lines" |
| `Solde théorique` | `cash_register_balance_end` | ✅ | `monetary` | **computed** | "Theoretical Closing Balance" |

**Champs absents (ne pas utiliser) :**
```
cash_register_total_entry_encoding  → ❌ ABSENT en v19
cash_real_expected                  → ❌ ABSENT en v19
sequence_number                     → ❌ ABSENT en v19
```

**Calcul du solde théorique (vérification) :**
```python
session = env['pos.session'].browse(session_id)

fond_initial   = session.cash_register_balance_start  # stored
transactions   = session.cash_real_transaction         # stored (total ventes espèces)
solde_theorique = session.cash_register_balance_end    # computed

# Pour les retraits/entrées manuels de caisse :
cash_moves = session.statement_line_ids.filtered(
    lambda l: l.journal_id == session.cash_journal_id
)
entrees   = sum(cash_moves.filtered(lambda l: l.amount > 0).mapped('amount'))
retraits  = sum(cash_moves.filtered(lambda l: l.amount < 0).mapped('amount'))
```

**Dans le Rapport X :** ne jamais afficher `cash_register_balance_end_real` (solde compté) ni `cash_register_difference` (écart) — ces données appartiennent au Rapport Z et nécessitent un comptage physique.

---

## 6. Code-barres & numérotation X

| Élément maquette | Source | Remarque |
|---|---|---|
| Code-barres `X-2026-00003` | compteur applicatif | Séquence libre (pas légale). Créer `ir.sequence` `pos.report.x` si traçabilité souhaitée, ou simple compteur sur la session. |
| `Rapport X — ne constitue pas une clôture` | libellé statique | Mention obligatoire dans la maquette. |

**Séquence optionnelle :**
```xml
<!-- data/ir_sequence_data.xml -->
<record id="seq_pos_report_x" model="ir.sequence">
    <field name="name">Rapport X POS</field>
    <field name="code">pos.report.x</field>
    <field name="prefix">X-%(year)s-</field>
    <field name="padding">5</field>
    <field name="number_next">1</field>
</record>
```

---

## 7. Structure du contrôleur Rapport X

```python
# controllers/report_x.py
from odoo import http
from odoo.http import request
from datetime import datetime

class PosReportX(http.Controller):

    @http.route('/pos/report/x/<int:session_id>', type='json', auth='user')
    def get_x_report_data(self, session_id, **kwargs):
        session = request.env['pos.session'].browse(session_id)
        if not session.exists():
            return {'error': 'Session introuvable'}
        if session.state != 'opened':
            return {'error': 'Session non ouverte — utiliser le Rapport Z'}

        domain_orders = [
            ('session_id', '=', session_id),
            ('state', 'in', ['paid', 'done', 'invoiced'])
        ]

        # Totaux ventes
        sales = request.env['pos.order'].read_group(
            domain_orders, ['amount_total', 'amount_tax'], []
        )
        total_ttc = sales[0]['amount_total'] if sales else 0.0
        total_tax = sales[0]['amount_tax']   if sales else 0.0

        # Paiements par méthode
        payments = request.env['pos.payment'].read_group(
            [('session_id', '=', session_id)],
            ['payment_method_id', 'amount'],
            ['payment_method_id']
        )

        # Nb articles
        lines = request.env['pos.order.line'].read_group(
            [('order_id.session_id', '=', session_id),
             ('order_id.state', 'in', ['paid', 'done', 'invoiced'])],
            ['qty'], []
        )

        return {
            'printed_at':      datetime.now().isoformat(),
            'session_name':    session.name,
            'session_start':   session.start_at.isoformat() if session.start_at else None,
            'cashier':         session.user_id.name,
            'order_count':     session.order_count,
            'total_ht':        total_ttc - total_tax,
            'total_tax':       total_tax,
            'total_ttc':       total_ttc,
            'nb_articles':     lines[0]['qty'] if lines else 0,
            'payments':        payments,
            'cash_start':      session.cash_register_balance_start,
            'cash_transaction': session.cash_real_transaction,
            'cash_theoretical': session.cash_register_balance_end,
            'company': {
                'name':             session.config_id.name,
                'ice':              session.company_id.company_registry,
                'l10n_ma_if':       session.company_id.l10n_ma_if,
                'l10n_ma_tp':       session.company_id.l10n_ma_tp,
            }
        }
```

---

## 8. Récapitulatif champs vérifiés Rapport X

| Champ | Modèle | Présent | Utilisation |
|---|---|---|---|
| `name` | `pos.session` | ✅ | Nom de session |
| `start_at` | `pos.session` | ✅ | Heure ouverture |
| `state` | `pos.session` | ✅ | Vérification session ouverte |
| `user_id` | `pos.session` | ✅ | Caissier responsable |
| `order_ids` | `pos.session` | ✅ | Commandes de la session |
| `order_count` | `pos.session` | ✅ | Nb commandes (computed) |
| `cash_register_balance_start` | `pos.session` | ✅ | Fond initial |
| `cash_register_balance_end` | `pos.session` | ✅ | Solde théorique (computed) |
| `cash_real_transaction` | `pos.session` | ✅ | Total transactions espèces |
| `statement_line_ids` | `pos.session` | ✅ | Mouvements caisse manuels |
| `config_id` | `pos.session` | ✅ | Config POS |
| `amount_total` | `pos.order` | ✅ | Total TTC commande |
| `amount_tax` | `pos.order` | ✅ | Total taxes |
| `amount` | `pos.payment` | ✅ | Montant paiement |
| `payment_method_id` | `pos.payment` | ✅ | Méthode |
| `is_cash_count` | `pos.payment.method` | ✅ | Détecte espèces |
| `company_registry` | `res.company` | ✅ | ICE |
| `cash_register_total_entry_encoding` | `pos.session` | ❌ ABSENT | Ne pas utiliser |
| `cash_real_expected` | `pos.session` | ❌ ABSENT | Ne pas utiliser |
| `sequence_number` | `pos.session` | ❌ ABSENT | Ne pas utiliser |
| `cash_register_balance_end_real` | `pos.session` | ✅ | **X seulement** : NE PAS AFFICHER |
| `cash_register_difference` | `pos.session` | ✅ | **X seulement** : NE PAS AFFICHER |
