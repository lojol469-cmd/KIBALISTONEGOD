---
title: Server App
emoji: 🐳
colorFrom: blue
colorTo: red
sdk: docker
sdk_version: python:3.9
app_file: app.py
pinned: false
---

# Server App

This is a combined Node.js and Python Streamlit application for data analysis and management.

## Features

- User authentication via email OTP
- Data visualization with Streamlit
- Cloudinary integration for file storage
- Email notifications

## How to run locally

### 🚀 Option 1: Démarrage complet automatique (Recommandé)

Double-cliquez simplement sur `start_all_servers.bat` pour lancer tous les services :

**Avantages :**
- Lance MariaDB, Node.js et Streamlit en séquence
- Vérifie que chaque service démarre correctement
- Utilise les chemins corrects vers les scripts MariaDB
- Arrêt automatique de tous les services

**Ou utilisez `start_all_servers_separate.bat` pour des fenêtres séparées :**
- Fenêtre dédiée pour chaque service
- Meilleure visibilité des logs
- Contrôle individuel possible

### Architecture des services

L'application utilise 3 services principaux :

1. **MariaDB** (Port 3306) : Base de données principale
2. **Node.js Server** (Port 3000) : API REST, authentification OTP, envoi d'emails  
3. **Streamlit App** (Port 8501) : Interface utilisateur (accessible sur `localhost:8501`)

### Option 2: Démarrage automatique avec MariaDB

1. Assurez-vous que MariaDB portable est configuré (voir MARIADB_README.md)

2. Lancez l'application complète :
   ```bash
   start_app_with_mariadb.bat
   ```

   Ce script :
   - Démarre MariaDB automatiquement
   - Attend que la base de données soit prête
   - Lance l'application Streamlit
   - Arrête MariaDB à la fermeture de l'app

### Option 3: Démarrage manuel

1. Démarrez MariaDB séparément :
   ```bash
   start_mariadb.bat
   ```

2. Attendez 10-15 secondes que MariaDB soit complètement démarré

3. Lancez l'application Streamlit :
   ```bash
   streamlit run app.py
   ```

### ⚠️ Prérequis

Assurez-vous que :
- MariaDB est installé dans `../mariadb/` (répertoire parent)
- Le script `../start_mariadb.bat` existe et fonctionne
- Les variables d'environnement sont configurées dans `.env`

## Fonctionnalités

- Authentification utilisateur via OTP email
- Visualisation de données avec Streamlit
- Intégration Cloudinary pour le stockage de fichiers
- Notifications par email
- Base de données MariaDB avec fallback SQLite
- Logs d'audit complets
- Système de corbeille pour la récupération de données

## 🔧 Dépannage

### Problèmes d'ordre de lancement (CORRIGE)

**Problème résolu :** L'application Streamlit ne se lançait pas car elle tentait de se connecter à MariaDB et au serveur Node.js avant qu'ils ne soient prêts.

**Solutions appliquées :**
- ✅ Attente prolongée pour MariaDB (15 secondes au lieu de 5-10)
- ✅ Vérifications avec retry automatique (5 tentatives pour MariaDB)
- ✅ Vérification de disponibilité du serveur Node.js avant lancement Streamlit
- ✅ Utilisation de `python -m streamlit run` au lieu de `streamlit run` direct

**Ordre de lancement corrigé :**
1. **MariaDB** → Démarrage + 15s attente + vérification avec retry
2. **Node.js** → Démarrage + 8s attente + vérification HTTP
3. **Streamlit** → Lancement seulement si les services précédents sont OK

### Autres problèmes courants

Si Streamlit ne se lance toujours pas :
1. Testez les services avec `test_services.bat`
2. Vérifiez Python : `python -c "import streamlit"`
3. Réinstallez les dépendances : `pip install -r requirements.txt`
4. Vérifiez les logs d'erreur dans les fenêtres de commande

### Scripts de diagnostic

- `test_streamlit.bat` : Diagnostic complet de Streamlit
- `test_services.bat` : Test rapide de tous les services
- `diagnostic_streamlit.bat` : Diagnostic étape par étape

## Deployment

This app is containerized with Docker for deployment on Hugging Face Spaces.