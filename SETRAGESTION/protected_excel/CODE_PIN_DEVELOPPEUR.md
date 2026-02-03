# 🔒 PROTECTION DES FICHIERS SENSIBLES

## ⚠️ IMPORTANT - POUR LE DÉVELOPPEUR

Le dossier `protected_excel` contient des fichiers sensibles qui sont maintenant protégés.

### 🔐 Code PIN Développeur

**Code par défaut : `12345`**

⚠️ **IMPORTANT** : Ce code doit être changé dans les fichiers suivants :
- `verrouiller_fichiers.py`
- `deverrouiller_fichiers.py`

Pour changer le code, remplacez la ligne :
```python
DEV_PIN_HASH = "8cb2237d0679ca88db6464eac60da96345513964"
```

Par le hash SHA1 de votre nouveau code PIN (5 chiffres).

### 📝 Comment générer un nouveau hash :

```python
import hashlib
nouveau_code = "67890"  # Votre nouveau code
hash = hashlib.sha1(nouveau_code.encode()).hexdigest()
print(hash)
```

## 🛡️ Utilisation

### Verrouiller les fichiers (avant distribution)

1. Double-cliquez sur `VERROUILLER_FICHIERS.bat`
2. Confirmez l'opération
3. Les fichiers sensibles seront cachés et protégés

### Déverrouiller les fichiers (développement)

1. Double-cliquez sur `DEVERROUILLER_FICHIERS.bat`
2. Entrez le code PIN développeur (5 chiffres)
3. Les fichiers sensibles seront restaurés

## 📋 Fichiers protégés

- `license_check.py` - Vérification des licences
- `license_manager.py` - Gestion des licences
- `license_config.py` - Configuration licence
- `license_server.js` - Serveur de licences
- `server.js` - Serveur principal
- `.env` - Variables d'environnement
- `integrity_checker.py` - Vérification d'intégrité
- `config_licence.py` - Configuration
- Autres fichiers de build

## 🚀 Workflow de distribution

1. **Développement** :
   - Fichiers déverrouillés
   - Vous pouvez modifier tout

2. **Avant distribution** :
   - Exécutez `VERROUILLER_FICHIERS.bat`
   - Les fichiers sont protégés
   - L'utilisateur ne peut pas les modifier

3. **Après distribution** :
   - Si besoin de maintenance, utilisez `DEVERROUILLER_FICHIERS.bat`
   - Entrez le code PIN
   - Effectuez vos modifications
   - Re-verrouillez avant de redistribuer

## ⚡ Sécurité

- Les fichiers sont encodés en Base64 (obfuscation)
- Le code PIN est hashé en SHA1
- Les fichiers protégés sont dans un dossier caché `.protected_files`
- Un fichier placeholder remplace les originaux

⚠️ **Note** : Ce n'est pas un chiffrement militaire, mais suffisant pour empêcher un utilisateur lambda de modifier les fichiers sensibles.
