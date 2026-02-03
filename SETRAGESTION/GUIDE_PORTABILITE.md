# 🚀 GUIDE DE PORTABILITÉ SETRAF

## ❌ **PROBLÈME IDENTIFIÉ**

Le message **"l'environnement Python n'est pas disponible"** apparaît car :

### Cause principale :
L'environnement virtuel Python (`venv`) contient des **chemins absolus** qui pointent vers l'ordinateur d'origine :

```
venv/pyvenv.cfg:
  home = C:\Program Files\Epic Games\UE_5.7\Engine\Binaries\ThirdParty\Python3\Win64
  
venv/excel_env/pyvenv.cfg:
  home = C:\Users\Admin\Desktop\logiciel\python311
```

Quand vous copiez sur un autre ordinateur, **ces chemins n'existent pas** → Python refuse de démarrer.

---

## ✅ **SOLUTIONS**

### **Solution 1 : Recréer l'environnement sur le nouvel ordinateur** (Rapide)

**Sur le nouvel ordinateur :**

1. **Copiez tout le dossier SETRAGESTION sur votre SSD**

2. **Allez dans le dossier** :
   ```
   C:\[Votre SSD]\SETRAGESTION\protected_excel\
   ```

3. **Exécutez** :
   ```
   RECREER_ENVIRONNEMENT.bat
   ```

4. **Lancez l'application** :
   ```
   ..\Lanceur_SETRAF_Portable.bat
   ```

---

### **Solution 2 : Version 100% Portable** (Recommandé)

Pour rendre l'application **vraiment portable sans dépendances** :

#### Étape 1 : Copier Python portable

1. **Sur l'ordinateur source**, copiez le dossier :
   ```
   C:\Users\Admin\Desktop\logiciel\python311\
   ```

2. **Placez-le à côté de SETRAGESTION** :
   ```
   [SSD]\
   ├── SETRAGESTION\
   └── python311\          ← Copiez ici
   ```

#### Étape 2 : Supprimer l'ancien venv

**Sur le nouvel ordinateur** :
```bat
cd C:\[Votre SSD]\SETRAGESTION\protected_excel
rmdir /s /q venv
```

#### Étape 3 : Recréer avec Python portable

**Exécutez** :
```bat
RECREER_ENVIRONNEMENT.bat
```

#### Étape 4 : Lancer avec le nouveau script

**Utilisez maintenant** :
```bat
Lanceur_SETRAF_Portable.bat
```

Ce nouveau lanceur :
- ✅ Détecte automatiquement Python portable
- ✅ Recrée le venv si nécessaire
- ✅ Vérifie la licence
- ✅ Lance l'application

---

## 🔐 **GESTION DE LA LICENCE**

### Problème de licence sur nouvel ordinateur

La licence est liée à l'**empreinte machine** (Machine Fingerprint) qui change d'un ordinateur à l'autre.

**Fichiers de licence** :
- `license.key` - Code de licence
- `license.dat` - Données de licence (contient l'empreinte machine)

### Solution :

**Option A : Licence par machine**
- Chaque ordinateur doit demander sa propre licence
- Exécutez `python license_check.py` pour demander une nouvelle licence

**Option B : Modifier le système de licence** (pour multi-postes)

Je peux modifier `license_check.py` pour :
1. ✅ Ignorer la vérification de l'empreinte machine
2. ✅ Utiliser une licence basée sur le nom d'utilisateur
3. ✅ Ajouter une licence "flottante" pour plusieurs machines

**Voulez-vous que je modifie le système de licence ?**

---

## 📋 **CHECKLIST DE DÉPLOIEMENT**

Pour déployer sur un nouvel ordinateur :

- [ ] Copier tout le dossier SETRAGESTION
- [ ] Copier le dossier python311 (si version portable)
- [ ] Exécuter RECREER_ENVIRONNEMENT.bat
- [ ] Demander une nouvelle licence (si nécessaire)
- [ ] Lancer avec Lanceur_SETRAF_Portable.bat

---

## 🔧 **STRUCTURE PORTABLE IDÉALE**

```
[SSD]\
├── python311\                    # Python portable
│   ├── python.exe
│   ├── Scripts\
│   └── Lib\
│
└── SETRAGESTION\
    ├── Lanceur_SETRAF_Portable.bat    # ← Utiliser celui-ci
    │
    └── protected_excel\
        ├── RECREER_ENVIRONNEMENT.bat   # Recréer venv
        ├── venv\                        # Sera recréé localement
        ├── license_check.py
        ├── launcher_all_servers.py
        ├── app.py
        ├── requirements.txt
        └── ...
```

---

## 🆘 **DÉPANNAGE**

### Erreur : "Python n'est pas installé"
**Solution** : Copiez python311 à côté de SETRAGESTION

### Erreur : "Impossible d'activer l'environnement virtuel"
**Solution** : Exécutez RECREER_ENVIRONNEMENT.bat

### Erreur : "Licence non validée"
**Solution** : 
1. Le système détecte un changement de machine
2. Vous devez demander une nouvelle licence
3. Ou je modifie le système pour accepter plusieurs machines

### Erreur : "Module xyz not found"
**Solution** : 
```bat
cd protected_excel
call venv\Scripts\activate.bat
pip install -r requirements.txt
```

---

## 💡 **AMÉLIORATION RECOMMANDÉE**

Je peux créer un **installateur automatique** qui :
1. ✅ Détecte l'environnement
2. ✅ Configure automatiquement Python
3. ✅ Crée l'environnement virtuel
4. ✅ Installe les dépendances
5. ✅ Gère la licence de façon transparente
6. ✅ Crée un raccourci sur le bureau

**Voulez-vous que je crée cet installateur ?**

---

## 📞 **BESOIN D'AIDE ?**

Contactez : nyundumathryme@gmail.com
