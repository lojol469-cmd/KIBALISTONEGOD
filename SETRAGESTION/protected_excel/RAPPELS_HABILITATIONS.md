# 🔔 SYSTÈME DE RAPPEL AUTOMATIQUE DES HABILITATIONS

## ✅ Fonctionnalités implémentées

### 1. Vérification automatique au démarrage
- ✅ Vérifie toutes les habilitations de tous les utilisateurs
- ✅ Détecte les habilitations qui expirent dans les 30 jours
- ✅ Détecte les habilitations déjà expirées
- ✅ S'exécute automatiquement à chaque démarrage de l'application

### 2. Niveaux d'urgence
- 🔴 **URGENT** - Expire dans 7 jours ou moins
- 🟡 **ATTENTION** - Expire dans 8 à 15 jours
- 🟢 **À SURVEILLER** - Expire dans 16 à 30 jours
- ⚫ **EXPIRÉE** - Date d'expiration dépassée

### 3. Notifications par email

#### Pour le super admin (nyundumathryme@gmail.com):
- ✅ Reçoit un récapitulatif complet de toutes les habilitations à expirer
- ✅ Liste par utilisateur avec niveau d'urgence
- ✅ Nombre total d'habilitations critiques

#### Pour chaque utilisateur concerné:
- ✅ Reçoit uniquement ses propres habilitations à expirer
- ✅ Liste détaillée avec jours restants
- ✅ Indication claire des actions à entreprendre

### 4. Vérification manuelle (Super Admin)
- ✅ Bouton "🔔 Vérifier les habilitations à expirer" dans le panneau Super Admin
- ✅ Permet de déclencher manuellement la vérification
- ✅ Affiche le résultat immédiatement

## 📧 Format des emails de rappel

### Email Super Admin:
```
[RAPPEL AUTOMATIQUE] Habilitations - X habilitation(s)

=== HABILITATIONS À RENOUVELER ===

🔴 EXPIRÉES:
  • Jean DUPONT - CACES (CAC-2024-001) - Expiré depuis 5 jours - Utilisateur: user1@example.com
  • Marie MARTIN - SST (SST-2024-002) - Expiré depuis 12 jours - Utilisateur: user2@example.com

⚠️ À EXPIRER PROCHAINEMENT:
  • 🔴 URGENT Pierre DURAND - Habilitation électrique (HE-2024-003) - 3 jour(s) - Utilisateur: user3@example.com
  • 🟡 ATTENTION Sophie BERNARD - Travail en hauteur (TH-2024-004) - 12 jour(s) - Utilisateur: user1@example.com
  • 🟢 À SURVEILLER Luc PETIT - Conduite PL (PL-2024-005) - 25 jour(s) - Utilisateur: user4@example.com
```

### Email Utilisateur:
```
[RAPPEL] Vos habilitations - 2 habilitation(s)

Vos habilitations nécessitent votre attention:

🔴 EXPIRÉE: Jean DUPONT - CACES - Expiré depuis 5 jours
⚠️ EXPIRE BIENTÔT: Sophie BERNARD - Travail en hauteur - 12 jour(s) restant(s)
```

## 🔧 Configuration

### Fichier: config_rappels.py

```python
# Fréquence de vérification (en jours)
FREQUENCE_RAPPEL_JOURS = 3  # Tous les 3 jours

# Nombre de jours avant expiration pour envoyer un rappel
JOURS_AVANT_EXPIRATION_RAPPEL = 30

# Niveaux d'urgence
JOURS_URGENT = 7
JOURS_ATTENTION = 15
JOURS_SURVEILLER = 30

# Activer/désactiver les rappels automatiques
RAPPELS_AUTOMATIQUES_ACTIFS = True
```

## 🚀 Utilisation

### Automatique:
1. **Lancez l'application** avec `Lanceur_SETRAF_Portable.bat`
2. **La vérification se fait automatiquement** au démarrage
3. **Les emails sont envoyés** si des habilitations expirent bientôt
4. **Consultez vos emails** pour voir les rappels

### Manuel (Super Admin uniquement):
1. Connectez-vous avec **nyundumathryme@gmail.com**
2. Allez dans **"🔐 Super Admin"**
3. Cliquez sur **"🔔 Vérifier les habilitations à expirer"**
4. Consultez vos emails

## 📊 Logs de la console

Lors de la vérification, vous verrez dans la console:

```
🔔 Vérification des habilitations à expirer...
⚠️ 5 habilitation(s) à expirer, 2 expirée(s)
Email envoyé avec succès: [RAPPEL AUTOMATIQUE] Habilitations - 7 habilitation(s)
Email envoyé avec succès: [RAPPEL] Vos habilitations - 2 habilitation(s)
Email envoyé avec succès: [RAPPEL] Vos habilitations - 3 habilitation(s)
✅ Rappels envoyés à 3 utilisateur(s) + super admin
```

Ou si rien à signaler:
```
🔔 Vérification des habilitations à expirer...
✅ Aucune habilitation à expirer dans les 30 jours
```

## 🎯 Avantages

1. **Proactif** - Détecte les problèmes avant qu'ils ne surviennent
2. **Automatique** - Pas besoin de vérifier manuellement
3. **Ciblé** - Chaque utilisateur reçoit uniquement ses propres alertes
4. **Centralisé** - Le super admin a une vue globale
5. **Configurable** - Fréquence et seuils ajustables dans config_rappels.py

## ⚙️ Pour modifier la fréquence

### Pour rappels quotidiens:
```python
FREQUENCE_RAPPEL_JOURS = 1  # dans config_rappels.py
```

### Pour rappels hebdomadaires:
```python
FREQUENCE_RAPPEL_JOURS = 7
```

**Note:** Actuellement, la vérification se fait à chaque démarrage de l'application. Pour une vérification automatique tous les X jours même sans démarrer l'app, il faudrait créer une tâche planifiée Windows.

## 📅 Planification Windows (optionnel)

Pour créer une tâche planifiée qui vérifie les habilitations tous les jours à 8h00:

1. Créez `verifier_habilitations.py`:
```python
from app import check_expiring_habilitations
check_expiring_habilitations()
```

2. Créez une tâche planifiée Windows:
   - Ouvrez "Planificateur de tâches"
   - Créez une tâche de base
   - Déclencheur: Tous les jours à 8h00
   - Action: Démarrer un programme
   - Programme: `C:\...\python311\python.exe`
   - Argument: `verifier_habilitations.py`
   - Répertoire: `C:\Users\Admin\Desktop\logiciel\SETRAGESTION\protected_excel`

---

**Système opérationnel!** Les rappels sont actifs et s'exécutent à chaque démarrage. 🎉
