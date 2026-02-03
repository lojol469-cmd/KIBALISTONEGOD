#!/usr/bin/env python3
"""
Configuration de la licence SETRAF
Permet de contrôler le mode de vérification de la licence
"""

# ===== MODES DE LICENCE =====
# "strict"   : La licence est liée à l'empreinte machine (défaut)
# "portable" : La licence peut être utilisée sur plusieurs machines
# "dev"      : Mode développement - pas de vérification
LICENSE_MODE = "strict"

# ===== CONFIGURATION EMAIL =====
ADMIN_EMAIL = "nyundumathryme@gmail.com"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# ===== OPTIONS DE LICENCE PORTABLE =====
# Si LICENSE_MODE = "portable", permet de définir:
PORTABLE_OPTIONS = {
    # Nombre maximum de machines autorisées (None = illimité)
    "max_machines": None,
    
    # Vérifier uniquement l'email de l'utilisateur
    "check_email_only": True,
    
    # Autoriser le transfert de licence
    "allow_transfer": True,
    
    # Durée de validité de la licence (en jours, None = illimité)
    "validity_days": None
}

# ===== MODE DÉVELOPPEMENT =====
DEV_MODE = False  # Mettre à True pour désactiver toutes les vérifications
