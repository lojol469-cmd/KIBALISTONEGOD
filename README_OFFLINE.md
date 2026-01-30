# Mode Hors Ligne - Documentation

## Vue d'ensemble

L'application Excel de gestion prend désormais en charge un mode hors ligne complet, permettant le fonctionnement sans connexion internet. Le mode est automatiquement détecté et les fonctionnalités sont adaptées en conséquence.

## Détection du mode

L'application détecte automatiquement le mode de fonctionnement en vérifiant :
- La connectivité internet (test de connexion à `google.com`)
- La disponibilité du backend Node.js (test de connexion à `localhost:3000`)

### États possibles
- **🟢 Mode en ligne** : Toutes les fonctionnalités disponibles
- **🔴 Mode hors ligne** : Fonctionnalités limitées, services externes désactivés

## Fonctionnalités en mode hors ligne

### ✅ Fonctionnalités disponibles
- Gestion complète des données (véhicules, achats, anomalies, habilitations)
- Sauvegarde et chargement depuis la base SQLite locale
- Export PDF des rapports
- Toutes les opérations CRUD sur les données
- Interface utilisateur complète

### ❌ Fonctionnalités désactivées
- Upload d'images vers Cloudinary
- Envoi d'emails de notification
- Authentification OTP par email
- Services externes dépendant d'internet

## Indicateur visuel

Un indicateur de mode est affiché dans la sidebar :
- **🟢 MODE EN LIGNE** - Toutes les fonctionnalités disponibles
- **🔴 MODE HORS LIGNE** - Certaines fonctionnalités sont limitées

## Persistance des données

En mode hors ligne, les données sont automatiquement sauvegardées dans une base SQLite locale (`data.db`) avec un système de fallback robuste.

## Messages d'erreur

Les fonctions utilisant internet retournent des messages d'erreur explicites :
- `"Mode hors ligne: Service d'authentification non disponible"`
- `"Mode hors ligne: Upload Cloudinary ignoré"`
- `"Mode hors ligne: Notification email ignorée"`

## Reconnexion automatique

L'application détecte automatiquement le retour de la connectivité internet et réactive les fonctionnalités correspondantes lors du prochain redémarrage ou rechargement de page.

## Tests

Le mode hors ligne a été testé avec simulation de déconnexion réseau, confirmant :
- Détection correcte du mode offline
- Désactivation appropriée des services internet
- Persistance des données en SQLite
- Messages d'erreur explicites

## Configuration

Aucune configuration supplémentaire n'est requise. Le mode hors ligne est entièrement automatique et transparent pour l'utilisateur.