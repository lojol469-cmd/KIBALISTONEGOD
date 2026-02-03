# 📦 PRÉPARATION DU PACKAGE 100% PORTABLE

## 🎯 Objectif
Créer un dossier SETRAGESTION complètement autonome qui fonctionne sur **n'importe quel ordinateur Windows** sans aucune installation.

---

## ⚙️ ÉTAPES DE PRÉPARATION (À FAIRE UNE SEULE FOIS)

### 1️⃣ Installer les dépendances Python portables

```batch
cd protected_excel
INSTALLER_DEPENDANCES_PORTABLE.bat
```

**Ce script installe dans `python311\`:**
- python-dotenv
- requests  
- streamlit
- pandas
- plotly
- cloudinary
- Toutes les dépendances du projet

### 2️⃣ Télécharger Node.js portable

```batch
cd protected_excel
TELECHARGER_NODEJS_PORTABLE.bat
```

**Ce script télécharge automatiquement:**
- Node.js v24.13.0 (±80 MB)
- Extrait dans `protected_excel\nodejs\`
- Pas besoin d'installation système

### 3️⃣ Installer les dépendances Node.js

```batch
cd protected_excel
nodejs\npm.cmd install
```

**Installe les modules:**
- express
- nodemailer
- dotenv
- body-parser
- cors

### 4️⃣ Vérifier la structure

```
SETRAGESTION/
├── Lanceur_SETRAF_Portable.bat  ← Lance l'application
├── protected_excel/
│   ├── python311/               ← Python portable + dépendances
│   │   ├── python.exe
│   │   └── Lib/ (avec dotenv, streamlit, etc.)
│   ├── nodejs/                  ← Node.js portable
│   │   ├── node.exe
│   │   └── npm.cmd
│   ├── node_modules/            ← Modules Node.js
│   ├── license_server.js
│   ├── license_check.py
│   ├── launcher_all_servers.py
│   └── ...
```

---

## 🚀 DISTRIBUTION

### Copier le dossier complet

**Sur la même machine:**
```batch
xcopy /E /I /H /Y "C:\...\SETRAGESTION" "D:\SETRAGESTION"
```

**Sur clé USB ou réseau:**
- Copier tout le dossier SETRAGESTION
- Taille finale: ~300-500 MB (selon dépendances)

### Sur le nouvel ordinateur

1. Copier le dossier SETRAGESTION n'importe où (C:\, D:\, E:\, clé USB...)
2. Double-cliquer sur **`Lanceur_SETRAF_Portable.bat`**
3. C'est tout ! 🎉

---

## ✅ AVANTAGES DE CETTE APPROCHE

- ✅ **Aucune installation** requise sur la machine cible
- ✅ **Python portable** avec toutes les dépendances
- ✅ **Node.js portable** inclus
- ✅ **Fonctionne depuis n'importe quel lecteur** (C:, D:, E:, USB...)
- ✅ **Licence automatique** via serveur intégré
- ✅ **0 dépendance système** (sauf Windows)

---

## 🔧 DÉPANNAGE

### Erreur "ModuleNotFoundError: No module named 'dotenv'"
➡️ Exécutez `INSTALLER_DEPENDANCES_PORTABLE.bat`

### Erreur "Node.js introuvable"
➡️ Exécutez `TELECHARGER_NODEJS_PORTABLE.bat`

### Erreur "npm install" échoue
➡️ Vérifiez que `nodejs\npm.cmd` existe
➡️ Exécutez manuellement: `nodejs\npm.cmd install`

---

## 📋 CHECKLIST FINALE AVANT DISTRIBUTION

- [ ] `INSTALLER_DEPENDANCES_PORTABLE.bat` exécuté
- [ ] `TELECHARGER_NODEJS_PORTABLE.bat` exécuté  
- [ ] `nodejs\npm.cmd install` exécuté
- [ ] Test sur une autre machine (D:\ ou E:\)
- [ ] Vérifier que `python311\` contient dotenv, streamlit, etc.
- [ ] Vérifier que `nodejs\` contient node.exe et npm.cmd
- [ ] Vérifier que `node_modules\` contient express, nodemailer, etc.
- [ ] (Optionnel) Exécuter `VERROUILLER_FICHIERS.bat` pour protection

---

## 🎁 PACKAGE FINAL

Vous obtenez un dossier **SETRAGESTION** complètement autonome:

✅ Python 3.11.8 portable  
✅ Node.js v24.13.0 portable  
✅ Toutes les dépendances incluses  
✅ Système de licence intégré  
✅ Serveurs backend inclus  
✅ Base de données SQLite embarquée  

**Taille totale:** ~400 MB  
**Compatibilité:** Windows 10/11 (64-bit)  
**Installation requise:** AUCUNE ✅
