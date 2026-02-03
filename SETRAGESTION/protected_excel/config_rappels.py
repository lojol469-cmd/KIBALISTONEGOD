# Configuration des rappels automatiques d'habilitations

# Fréquence de vérification (en jours)
# 1 = tous les jours
# 3 = tous les 3 jours
# 7 = toutes les semaines
FREQUENCE_RAPPEL_JOURS = 3

# Nombre de jours avant expiration pour envoyer un rappel
JOURS_AVANT_EXPIRATION_RAPPEL = 30

# Niveaux d'urgence
JOURS_URGENT = 7  # Moins de 7 jours = URGENT
JOURS_ATTENTION = 15  # Moins de 15 jours = ATTENTION
JOURS_SURVEILLER = 30  # Moins de 30 jours = À SURVEILLER

# Activer les rappels automatiques au démarrage
RAPPELS_AUTOMATIQUES_ACTIFS = True

# Email du super admin (reçoit tous les rappels)
SUPER_ADMIN_EMAIL = "nyundumathryme@gmail.com"
