# 🌐 Guide d'Accès Réseau - SETRAGESTION

## 🎯 Problème Résolu

**Avant :** L'application s'ouvrait mais n'affichait rien sur les autres ordinateurs  
**Cause :** Streamlit écoutait uniquement sur `localhost` (127.0.0.1)  
**Solution :** Configuration pour écouter sur `0.0.0.0` (toutes les interfaces réseau)

---

## ✅ Corrections Appliquées

### 1. **Configuration Serveur**
- Streamlit écoute maintenant sur `0.0.0.0` au lieu de `localhost`
- Permet les connexions depuis d'autres machines du réseau
- Détection automatique de l'adresse IP locale

### 2. **Détection IP Automatique**
- Fonction `get_local_ip()` ajoutée
- Détecte automatiquement l'IP de la machine serveur
- Affiche les adresses d'accès pour partage

### 3. **Fichiers Modifiés**
- ✅ `launcher_all_servers.py` - Lanceur principal
- ✅ `launch.py` - Lanceur simple

---

## 🚀 Utilisation Multi-Utilisateurs

### **Sur la Machine Serveur (Hébergeur)**

1. **Lancez l'application** avec `Lanceur_SETRAF_Portable.bat`

2. **Notez l'adresse IP affichée** dans le terminal :
```
🌐 ADRESSES D'ACCÈS:

📱 Depuis CET ordinateur:
   • Application Excel: http://localhost:8501

🌍 Depuis UN AUTRE ordinateur sur le réseau:
   • Application Excel: http://192.168.1.100:8501

📍 Adresse IP de cette machine: 192.168.1.100
```

3. **Partagez l'adresse IP** avec les autres utilisateurs

---

### **Sur les Autres Ordinateurs (Clients)**

1. **Ouvrez un navigateur web** (Chrome, Firefox, Edge)

2. **Tapez l'adresse** fournie par le serveur :
   ```
   http://192.168.1.100:8501
   ```
   *(Remplacez par l'IP réelle affichée)*

3. **✅ L'application s'affiche** et fonctionne normalement

---

## 📋 Configuration Réseau Requise

### **Prérequis**

✅ Tous les ordinateurs doivent être sur le **même réseau local** (WiFi ou Ethernet)  
✅ Le **pare-feu Windows** doit autoriser les connexions sur les ports :
   - **8501** - Application Streamlit
   - **3000** - API Backend Node.js
   - **4000** - Serveur de Licence

### **Vérification Réseau**

1. **Tester la connectivité** depuis un autre ordinateur :
   ```bash
   ping 192.168.1.100
   ```
   *(Remplacez par l'IP du serveur)*

2. **Si le ping fonctionne** → Le réseau est OK
3. **Si le ping échoue** → Problème de réseau ou pare-feu

---

## 🛡️ Configuration du Pare-feu Windows

### **Méthode Automatique (Recommandée)**

Au premier lancement, Windows peut demander l'autorisation :
```
Windows Defender - Pare-feu
Autoriser Python à communiquer sur ces réseaux ?
☑ Réseaux privés (domicile ou bureau)
☐ Réseaux publics
```
✅ **Cochez "Réseaux privés"** et cliquez **"Autoriser l'accès"**

### **Méthode Manuelle**

1. Ouvrez **Panneau de configuration** > **Pare-feu Windows**
2. Cliquez **"Paramètres avancés"**
3. Créez une **nouvelle règle entrante** :
   - Type : **Port**
   - Protocole : **TCP**
   - Ports : **8501, 3000, 4000**
   - Action : **Autoriser la connexion**
   - Profil : **Privé, Domaine**
   - Nom : **SETRAGESTION**

---

## 🎯 Cas d'Usage

### **Scénario 1 : Bureau avec plusieurs ordinateurs**

```
Ordinateur 1 (Serveur)
   ↓ lance SETRAGESTION
   ↓ IP: 192.168.1.100
   
Ordinateur 2, 3, 4... (Clients)
   ↓ ouvrent http://192.168.1.100:8501
   ↓ utilisent l'application
```

### **Scénario 2 : Travail à distance (même réseau)**

```
Laptop (Serveur)
   ↓ lance SETRAGESTION via WiFi bureau
   ↓ IP: 192.168.10.50
   
Desktop (Client)
   ↓ connecté au même WiFi
   ↓ accède via http://192.168.10.50:8501
```

---

## 🔧 Dépannage

### **Problème 1 : "Impossible d'accéder au site"**

**Causes possibles :**
- ❌ Pas sur le même réseau
- ❌ Mauvaise adresse IP
- ❌ Pare-feu bloque la connexion
- ❌ Application non lancée sur le serveur

**Solutions :**
1. Vérifiez que les deux ordinateurs sont sur le même réseau
2. Vérifiez l'adresse IP exacte (peut changer après redémarrage)
3. Désactivez temporairement le pare-feu pour tester
4. Relancez l'application sur le serveur

### **Problème 2 : "La page charge mais n'affiche rien"**

**Solution :** ✅ **RÉSOLU** avec cette mise à jour !
- L'application écoute maintenant sur `0.0.0.0`
- Les connexions réseau sont acceptées

### **Problème 3 : "L'IP change tout le temps"**

**Cause :** IP dynamique attribuée par le routeur

**Solutions :**
1. **IP statique** : Configurez une IP fixe dans les paramètres réseau Windows
2. **Réservation DHCP** : Configurez le routeur pour toujours attribuer la même IP
3. **Hostname** : Utilisez le nom de l'ordinateur au lieu de l'IP

### **Problème 4 : "Connexion lente depuis d'autres ordinateurs"**

**Causes possibles :**
- Réseau WiFi saturé
- Machine serveur insuffisante

**Solutions :**
- Utilisez une connexion Ethernet pour le serveur
- Augmentez la RAM du serveur
- Limitez le nombre de clients simultanés

---

## 📊 Performances Réseau

### **Recommandations**

| Type de Réseau | Vitesse | Utilisateurs Simultanés | Performance |
|----------------|---------|-------------------------|-------------|
| **Ethernet Gigabit** | 1000 Mbps | 10-20 | ⭐⭐⭐⭐⭐ Excellent |
| **WiFi 5 (802.11ac)** | 300-600 Mbps | 5-10 | ⭐⭐⭐⭐ Très bon |
| **WiFi 4 (802.11n)** | 100-300 Mbps | 3-5 | ⭐⭐⭐ Bon |
| **WiFi ancien** | < 100 Mbps | 1-2 | ⭐⭐ Moyen |

---

## 🔐 Sécurité

### **Bonnes Pratiques**

✅ **Utilisez uniquement sur des réseaux de confiance** (bureau, domicile)  
✅ **Ne partagez pas l'adresse sur Internet public**  
✅ **Activez le système de licence** (déjà implémenté)  
⚠️ **Évitez les réseaux publics** (cafés, aéroports)

### **Protection Pare-feu**

- Autorisez uniquement les **réseaux privés**
- N'autorisez **PAS** les réseaux publics
- Les ports sont accessibles uniquement sur le réseau local

---

## 📱 Accès depuis Téléphone/Tablette

**Oui, c'est possible !**

1. Connectez votre téléphone/tablette au **même WiFi**
2. Ouvrez le navigateur mobile (Chrome, Safari, Firefox)
3. Entrez l'adresse : `http://192.168.1.100:8501`
4. ✅ L'interface s'adapte automatiquement

> **Note :** L'interface Streamlit est responsive et fonctionne sur mobile

---

## 🎉 Résumé des Avantages

✅ **Accès multi-utilisateurs** - Plusieurs personnes en même temps  
✅ **Aucune installation** sur les clients - Juste un navigateur web  
✅ **Données centralisées** - Une seule base de données SQLite  
✅ **Compatible mobile** - Smartphones et tablettes  
✅ **Portable** - Fonctionne sur clé USB avec accès réseau  
✅ **Sécurisé** - Système de licence par machine  

---

## 📞 Support Technique

**Si vous rencontrez des problèmes :**

1. Vérifiez le terminal sur la machine serveur (messages d'erreur)
2. Testez avec `ping` la connectivité réseau
3. Vérifiez le pare-feu Windows
4. Redémarrez l'application
5. Contactez l'administrateur système

---

**Date :** 2 février 2026  
**Version :** SETRAF 2026 - Accès Réseau Activé  
**Statut :** ✅ **FONCTIONNEL MULTI-UTILISATEURS**
