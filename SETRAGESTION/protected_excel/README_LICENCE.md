# 🔐 SYSTÈME DE LICENCE SETRAF - GUIDE COMPLET

## 📋 RÉSUMÉ DU PROBLÈME

Le message **"l'environnement Python n'est pas disponible"** que vous rencontrez est causé par **deux problèmes distincts** :

### 1. ❌ Problème d'Environnement Python
L'environnement virtuel (`venv`) contient des chemins absolus vers votre ordinateur d'origine qui n'existent pas sur le nouvel ordinateur.

### 2. ❌ Problème de Licence
Le système de licence vérifie l'empreinte machine, donc la licence créée sur un ordinateur ne fonctionne pas sur un autre.

---

## ✅ SOLUTIONS COMPLÈTES

### **SOLUTION RAPIDE - Mode Portable**

#### Étape 1 : Activer le mode portable de la licence

Sur votre **ordinateur d'origine** (celui où l'application fonctionne) :

1. Allez dans : `SETRAGESTION\protected_excel\`
2. Exécutez : `CONFIGURER_LICENCE.bat`
3. Choisissez l'option **2. PORTABLE**
4. La configuration sera mise à jour

#### Étape 2 : Préparer les fichiers pour le transfert

Copiez ces fichiers sur votre SSD :
```
SETRAGESTION\
├── protected_excel\
│   ├── license.key          ← Important!
│   ├── license.dat          ← Important!
│   ├── license_config.py    ← Important!
│   └── (tous les autres fichiers)
└── Lanceur_SETRAF_Portable.bat
```

#### Étape 3 : Sur le nouvel ordinateur

1. **Copiez le dossier Python portable** à côté de SETRAGESTION :
   ```
   [SSD]\
   ├── python311\           ← Copiez depuis l'ordinateur source
   └── SETRAGESTION\
   ```

2. **Allez dans** : `SETRAGESTION\protected_excel\`

3. **Recréez l'environnement** :
   ```
   RECREER_ENVIRONNEMENT.bat
   ```

4. **Lancez l'application** :
   ```
   ..\Lanceur_SETRAF_Portable.bat
   ```

---

## 🔧 MODES DE LICENCE

### Mode STRICT (Par défaut)
- ✅ Sécurité maximale
- ✅ Licence liée à la machine
- ❌ Ne fonctionne pas sur d'autres ordinateurs

**Utiliser pour** : Installation permanente sur un seul ordinateur

### Mode PORTABLE
- ✅ Fonctionne sur plusieurs ordinateurs
- ✅ Vérification basée sur l'email utilisateur
- ⚠️  Moins sécurisé

**Utiliser pour** : Installation sur SSD portable, plusieurs postes

### Mode DEV (Développement)
- ✅ Pas de vérification de licence
- ⚠️  À utiliser uniquement pour le développement/test

**Utiliser pour** : Tests, développement, débogage

---

## 🛠️ OUTILS DISPONIBLES

### 1. `CONFIGURER_LICENCE.bat`
Change le mode de licence (strict/portable/dev)

**Utilisation** :
```bat
cd SETRAGESTION\protected_excel
CONFIGURER_LICENCE.bat
```

### 2. `RECREER_ENVIRONNEMENT.bat`
Recrée l'environnement Python virtuel

**Utilisation** :
```bat
cd SETRAGESTION\protected_excel
RECREER_ENVIRONNEMENT.bat
```

### 3. `Lanceur_SETRAF_Portable.bat`
Lance l'application en mode portable

**Utilisation** :
```bat
cd SETRAGESTION
Lanceur_SETRAF_Portable.bat
```

---

## 📦 STRUCTURE PORTABLE COMPLÈTE

Pour une portabilité totale, la structure doit être :

```
[SSD ou USB]\
│
├── python311\                          # Python portable
│   ├── python.exe
│   ├── Scripts\
│   └── Lib\
│
└── SETRAGESTION\
    │
    ├── Lanceur_SETRAF_Portable.bat    # ← Utiliser ce lanceur
    ├── GUIDE_PORTABILITE.md
    │
    └── protected_excel\
        ├── CONFIGURER_LICENCE.bat     # Configurer la licence
        ├── RECREER_ENVIRONNEMENT.bat  # Recréer l'environnement
        │
        ├── license_config.py           # Configuration de licence
        ├── license.key                 # Clé de licence
        ├── license.dat                 # Données de licence
        │
        ├── venv\                       # (sera recréé automatiquement)
        ├── app.py
        ├── launcher_all_servers.py
        ├── requirements.txt
        └── ...
```

---

## 🔄 PROCÉDURE COMPLÈTE DE DÉPLOIEMENT

### Sur l'ordinateur SOURCE (où ça fonctionne) :

1. **Passer en mode portable** :
   ```bat
   cd SETRAGESTION\protected_excel
   CONFIGURER_LICENCE.bat
   > Choisir option 2 (PORTABLE)
   ```

2. **Copier les fichiers essentiels** sur le SSD :
   - Tout le dossier `SETRAGESTION`
   - Le dossier `python311` (depuis `C:\Users\Admin\Desktop\logiciel\`)

### Sur l'ordinateur CIBLE (nouvel ordinateur) :

1. **Brancher le SSD**

2. **Supprimer l'ancien venv** (s'il existe) :
   ```bat
   cd [Lettre SSD]:\SETRAGESTION\protected_excel
   rmdir /s /q venv
   ```

3. **Recréer l'environnement** :
   ```bat
   RECREER_ENVIRONNEMENT.bat
   ```

4. **Lancer l'application** :
   ```bat
   cd ..
   Lanceur_SETRAF_Portable.bat
   ```

---

## 🎯 CHECKLIST DE DÉPLOIEMENT

- [ ] ✅ Mode licence configuré en PORTABLE
- [ ] ✅ Dossier SETRAGESTION copié
- [ ] ✅ Dossier python311 copié à côté
- [ ] ✅ Fichiers license.key et license.dat présents
- [ ] ✅ Fichier license_config.py présent
- [ ] ⚠️  Ancien venv supprimé sur le nouvel ordinateur
- [ ] ✅ RECREER_ENVIRONNEMENT.bat exécuté
- [ ] ✅ Application lancée avec Lanceur_SETRAF_Portable.bat

---

## 🆘 DÉPANNAGE

### Problème : "Python n'est pas installé"

**Cause** : Python portable absent ou mal placé

**Solution** :
1. Vérifier que `python311\python.exe` existe
2. Le placer au même niveau que SETRAGESTION

### Problème : "Impossible d'activer l'environnement virtuel"

**Cause** : Le venv contient des chemins obsolètes

**Solution** :
```bat
cd SETRAGESTION\protected_excel
rmdir /s /q venv
RECREER_ENVIRONNEMENT.bat
```

### Problème : "Licence non validée" en mode PORTABLE

**Cause** : Le fichier license_config.py n'a pas été copié ou n'est pas en mode portable

**Solution** :
```bat
cd SETRAGESTION\protected_excel
CONFIGURER_LICENCE.bat
> Choisir option 2 (PORTABLE)
```

### Problème : "Empreinte machine différente"

**Cause** : La licence est encore en mode STRICT

**Solution** : Passer en mode PORTABLE (voir ci-dessus)

---

## 📊 COMPARAISON DES MODES

| Caractéristique | STRICT | PORTABLE | DEV |
|----------------|--------|----------|-----|
| Sécurité | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ |
| Portabilité | ❌ | ✅ | ✅ |
| Multi-machines | ❌ | ✅ | ✅ |
| Vérification email | ❌ | ✅ | ❌ |
| Vérification machine | ✅ | ❌ | ❌ |
| Production | ✅ | ✅ | ❌ |
| Développement | ❌ | ❌ | ✅ |

---

## 💡 RECOMMANDATIONS

### Pour un usage en entreprise (poste fixe) :
👉 **Mode STRICT** - Sécurité maximale

### Pour un usage mobile (SSD/USB) :
👉 **Mode PORTABLE** - Flexibilité

### Pour le développement :
👉 **Mode DEV** - Pas de contraintes

---

## 📞 SUPPORT

**Email** : nyundumathryme@gmail.com

**Fichiers de log** :
- `logs_audit\` - Logs d'utilisation
- Console de lancement - Erreurs Python

---

## 🔒 SÉCURITÉ

### Mode STRICT :
- Empreinte machine unique (CPU, MAC, hostname)
- Licence cryptée et signée
- Validation par email OTP

### Mode PORTABLE :
- Vérification par email utilisateur
- Moins de contraintes matérielles
- Licence transférable

---

## 📝 NOTES TECHNIQUES

### Fichiers de licence :

**license.key** : Contient le code de licence OTP
**license.dat** : JSON avec les métadonnées
```json
{
    "fingerprint": "sha256_hash",
    "license_code": "12345678",
    "user_email": "user@example.com",
    "user_name": "Nom Utilisateur",
    "created": "2026-02-02T...",
    "validated": true
}
```

**license_config.py** : Configuration du mode de vérification

### Environnement virtuel :

**venv/pyvenv.cfg** : Configuration de l'environnement
- Contient les chemins vers Python de base
- Recréé automatiquement sur chaque machine

---

## ✨ AMÉLIORATIONS FUTURES POSSIBLES

1. ✅ **Installateur automatique** - Un seul clic pour tout installer
2. ✅ **Serveur de licence centralisé** - Gestion depuis un portail web
3. ✅ **Licences temporaires** - Avec date d'expiration
4. ✅ **Licences flottantes** - Pool de licences partagées
5. ✅ **Télémétrie** - Suivi des installations actives

**Souhaitez-vous que je développe l'une de ces fonctionnalités ?**
