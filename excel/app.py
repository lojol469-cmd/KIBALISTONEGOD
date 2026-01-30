import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from pathlib import Path
import io
import os
import pymysql as mysql  # type: ignore
import sqlite3
import tempfile
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, PageBreak, Spacer
import matplotlib.pyplot as plt
from PIL import Image as PILImage
import cloudinary
import cloudinary.uploader
import tempfile
import requests
from cloudinary import api
from dotenv import load_dotenv
import socket

# Charger les variables d'environnement
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Debug backend: Afficher les variables d'environnement dans la console
print("Debug - CLOUDINARY_CLOUD_NAME:", os.environ.get('CLOUDINARY_CLOUD_NAME'))
api_key = os.environ.get('CLOUDINARY_API_KEY')
print("Debug - CLOUDINARY_API_KEY:", api_key[:10] + "..." if api_key else None)
api_secret = os.environ.get('CLOUDINARY_API_SECRET')
print("Debug - CLOUDINARY_API_SECRET:", api_secret[:10] + "..." if api_secret else None)

# Configuration backend
BACKEND_URL = 'http://localhost:3000'

# Configuration Cloudinary (optionnel en mode offline)
try:
    cloudinary.config(
        cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
        api_key=os.environ.get('CLOUDINARY_API_KEY'),
        api_secret=os.environ.get('CLOUDINARY_API_SECRET')
    )
    print("Debug - Cloudinary config set with cloud_name:", os.environ.get('CLOUDINARY_CLOUD_NAME'))
except Exception as e:
    print("Debug - Cloudinary config failed:", str(e))

# Configuration MySQL
# Les paramètres sont passés directement pour éviter les erreurs de type Pylance

# Database path for SQLite fallback
db_path = "data.db"

# Fonction pour détecter la connexion internet
def check_internet_connection():
    """Vérifie si l'application a accès à internet"""
    try:
        # Test de connexion rapide vers un service fiable
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

# Fonction pour vérifier la disponibilité du backend
def check_backend_available():
    """Vérifie si le serveur backend local est disponible"""
    try:
        response = requests.get(BACKEND_URL, timeout=2)
        return response.status_code == 200
    except:
        return False

# Fonction pour déterminer le mode de fonctionnement
def get_app_mode():
    """Détermine si l'application fonctionne en mode online, partial ou offline"""
    has_internet = check_internet_connection()
    backend_available = check_backend_available() if has_internet else False

    if has_internet and backend_available:
        return "online"
    elif has_internet and not backend_available:
        return "partial"  # Internet mais backend indisponible
    else:
        return "offline"

# Variable globale pour le mode
APP_MODE = get_app_mode()
print(f"Mode de fonctionnement détecté: {APP_MODE}")

# Fonction pour initialiser la base de données
def init_database():
    import time
    max_retries = 5
    retry_delay = 2  # secondes

    for attempt in range(max_retries):
        try:
            conn = mysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', ''),
                database=os.environ.get('MYSQL_DB', 'excel_app'),
                port=int(os.environ.get('MYSQL_PORT', '3306')),
                connect_timeout=5
            )
            cursor = conn.cursor()

            # Table pour les données de l'app
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_data (
                    `key` VARCHAR(255) PRIMARY KEY,
                    value TEXT
                )
            ''')

            # Table pour les logs d'audit
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    `timestamp` VARCHAR(255),
                    user_action VARCHAR(255),
                    entity_type VARCHAR(255),
                    entity_id VARCHAR(255),
                    action_type VARCHAR(255),
                    details TEXT,
                    user_info TEXT
                )
            ''')

            # Table pour la corbeille
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS corbeille (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    entity_type VARCHAR(255),
                    entity_data TEXT,
                    deleted_at VARCHAR(255),
                    deleted_by VARCHAR(255)
                )
            ''')

            # Migration : ajouter la colonne details si elle n'existe pas
            try:
                cursor.execute("SHOW COLUMNS FROM audit_logs LIKE 'details'")
                result = cursor.fetchone()
                if not result:
                    cursor.execute('ALTER TABLE audit_logs ADD COLUMN details TEXT')
                    print("Migration: Colonne details ajoutée à audit_logs")
            except mysql.Error as migration_err:
                print(f"Note: Migration details column: {migration_err}")

            conn.commit()
            conn.close()
            print("Debug - MySQL database initialized")
            return  # Succès, sortir de la fonction

        except mysql.Error as err:
            print(f"Tentative {attempt + 1}/{max_retries} - Erreur MySQL: {err}")
            if attempt < max_retries - 1:
                print(f"Attente de {retry_delay} secondes avant retry...")
                time.sleep(retry_delay)
            else:
                print("Toutes les tentatives ont échoué, passage en mode fallback SQLite")
                # Fallback to SQLite if MySQL fails
                init_sqlite_fallback()

# Fonction pour vérifier la santé de la connexion MySQL
def check_mysql_connection():
    try:
        conn = mysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'excel_app'),
            port=int(os.environ.get('MYSQL_PORT', '3306')),
            connect_timeout=5
        )
        conn.close()
        return True
    except mysql.Error:
        return False

# Fonction pour initialiser la base de données SQLite en fallback
def init_sqlite_fallback():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Table pour les données de l'app
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS app_data (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Table pour les logs d'audit
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            user_action TEXT,
            entity_type TEXT,
            entity_id TEXT,
            action_type TEXT,
            details TEXT,
            user_info TEXT
        )
    ''')

    # Table pour la corbeille
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS corbeille (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_type TEXT,
            entity_data TEXT,
            deleted_at TEXT,
            deleted_by TEXT
        )
    ''')

    conn.commit()
    conn.close()
    print("Debug - SQLite database initialized (fallback)")

# Appeler l'initialisation au démarrage
init_database()

# Fonctions d'authentification
def send_otp(email, action):
    app_mode = get_app_mode()
    if app_mode == "offline":
        return {'error': 'Mode hors ligne: Service d\'authentification non disponible'}
    
    try:
        response = requests.post(f'{BACKEND_URL}/{action}', json={'email': email})
        return response.json()
    except:
        return {'error': 'Erreur de connexion au serveur'}

def verify_otp(email, otp):
    app_mode = get_app_mode()
    if app_mode == "offline":
        return {'error': 'Mode hors ligne: Service d\'authentification non disponible'}
    
    try:
        response = requests.post(f'{BACKEND_URL}/verify', json={'email': email, 'otp': otp})
        return response.json()
    except:
        return {'error': 'Erreur de connexion au serveur'}

# Fonction pour envoyer des notifications par email
def send_email_notification(action_type, entity_type, entity_id="", details="", user_info="Utilisateur"):
    app_mode = get_app_mode()
    if app_mode == "offline":
        print(f"Mode hors ligne: Notification email ignorée - {action_type} {entity_type}")
        return
    
    try:
        subject = f"[{action_type}] {entity_type} - {entity_id}" if entity_id else f"[{action_type}] {entity_type}"
        
        # Construire le corps de l'email
        body = f"""
        <h2>Notification d'action - Système de Gestion</h2>
        
        <p><strong>Action:</strong> {action_type}</p>
        <p><strong>Type d'entité:</strong> {entity_type}</p>
        {f"<p><strong>ID de l'entité:</strong> {entity_id}</p>" if entity_id else ""}
        <p><strong>Utilisateur:</strong> {user_info}</p>
        <p><strong>Date/Heure:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        {f"<p><strong>Détails:</strong><br>{details}</p>" if details else ""}
        
        <hr>
        <p style="color: #666; font-size: 12px;">
        Cette notification a été générée automatiquement par le système de gestion.
        </p>
        """
        
        # Email de destination (à configurer selon les besoins)
        recipient_email = "admin@entreprise.com"  # À remplacer par l'email approprié
        
        # Appel au backend pour envoyer l'email
        email_data = {
            'to': recipient_email,
            'subject': subject,
            'html': body,
            'action_type': action_type,
            'entity_type': entity_type,
            'entity_id': entity_id,
            'user_info': user_info,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        response = requests.post(f'{BACKEND_URL}/send-notification', json=email_data)
        result = response.json()
        
        if 'error' in result:
            print(f"Erreur envoi email: {result['error']}")
        else:
            print(f"Email envoyé avec succès: {subject}")
            
    except Exception as e:
        print(f"Erreur lors de l'envoi de l'email: {str(e)}")

# Fonction pour mettre à jour les statuts des habilitations
# Page d'authentification
def auth_page():
    st.title("🔐 Authentification")
    
    tab1, tab2 = st.tabs(["Connexion", "Inscription"])
    
    with tab1:
        st.subheader("Connexion")
        email_login = st.text_input("Email", key="login_email")
        if st.button("Envoyer code de connexion"):
            if email_login:
                result = send_otp(email_login, 'login')
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success(result['message'])
                    st.session_state['otp_sent'] = True
                    st.session_state['action'] = 'login'
                    st.session_state['email'] = email_login
            else:
                st.error("Veuillez entrer un email")
    
    with tab2:
        st.subheader("Inscription")
        email_register = st.text_input("Email", key="register_email")
        if st.button("Envoyer code d'inscription"):
            if email_register:
                result = send_otp(email_register, 'register')
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success(result['message'])
                    st.session_state['otp_sent'] = True
                    st.session_state['action'] = 'register'
                    st.session_state['email'] = email_register
            else:
                st.error("Veuillez entrer un email")
    
    if st.session_state.get('otp_sent', False):
        st.subheader("Vérification du code")
        otp = st.text_input("Code OTP", key="otp")
        if st.button("Vérifier"):
            if otp:
                result = verify_otp(st.session_state['email'], otp)
                if 'error' in result:
                    st.error(result['error'])
                else:
                    st.success(result['message'])
                    st.session_state['authenticated'] = True
                    st.session_state['user_email'] = st.session_state['email']
                    st.session_state['last_activity'] = datetime.now()
                    del st.session_state['otp_sent']
                    del st.session_state['action']
                    del st.session_state['email']
                    st.rerun()
            else:
                st.error("Veuillez entrer le code OTP")
# Vérification d'authentification
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# Vérification du timeout de session (1 heure)
if st.session_state['authenticated'] and 'last_activity' in st.session_state:
    if datetime.now() - st.session_state['last_activity'] > timedelta(hours=1):
        st.session_state['authenticated'] = False
        st.session_state['user_email'] = None
        if 'last_activity' in st.session_state:
            del st.session_state['last_activity']
        st.warning("Session expirée après 1 heure d'inactivité. Veuillez vous reconnecter.")
        st.rerun()

if not st.session_state['authenticated']:
    auth_page()
    st.stop()

# Mise à jour de l'activité
st.session_state['last_activity'] = datetime.now()

# Configuration de la page
st.set_page_config(
    page_title="Système de Gestion Avancé",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styles CSS personnalisés
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+Pro:wght@300;400;600&display=swap');
    
    /* Variables CSS */
    :root {
        --primary-color: #1a3a52;
        --secondary-color: #2c5f7d;
        --accent-color: #4CAF50;
        --background-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        --hover-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
    }
    
    /* Styles globaux */
    .stApp {
                                        background-image: url("static/pexels-simberto-brauserich-3680746-5882869.jpg");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        min-height: 100vh;
    }
    
    /* Overlay pour améliorer la lisibilité */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.85);
        z-index: -1;
    }
    
    /* En-tête personnalisé */
    .main-header {
        background: rgba(255, 255, 255, 0.9);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        box-shadow: var(--card-shadow);
        animation: slideDown 0.6s ease-out;
    }
    
    .main-header h1 {
        font-family: 'Playfair Display', serif;
        color: white;
        font-size: 3rem;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        letter-spacing: 2px;
    }
    
    .main-header p {
        font-family: 'Source Sans Pro', sans-serif;
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        margin-top: 0.5rem;
    }
    
    /* Cartes */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: var(--card-shadow);
        transition: all 0.3s ease;
        border-left: 4px solid var(--accent-color);
        animation: fadeIn 0.8s ease-out;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--hover-shadow);
    }
    
    .metric-value {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
    }
    
    .metric-label {
        font-family: 'Source Sans Pro', sans-serif;
        font-size: 1rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.5rem;
    }
    
    /* Boutons personnalisés */
    .stButton>button {
        background: rgba(76, 175, 80, 0.9) !important;
        color: #1a3a52 !important;
        border: 2px solid #4CAF50 !important;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        letter-spacing: 0.5px;
    }
    
    .stButton>button:hover {
        background: rgba(255, 235, 59, 0.95) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Inputs personnalisés */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>div,
    .stDateInput>div>div>input,
    .stTextArea>div>div>textarea {
        background: rgba(76, 175, 80, 0.9) !important;
        color: #1a3a52 !important;
        border: 2px solid #4CAF50 !important;
        border-radius: 8px !important;
        padding: 0.5rem !important;
        font-family: 'Source Sans Pro', sans-serif !important;
        font-weight: 500 !important;
    }
    
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    .stSelectbox>div>div>div:focus,
    .stDateInput>div>div>input:focus,
    .stTextArea>div>div>textarea:focus {
        background: rgba(76, 175, 80, 0.95) !important;
        border-color: #388E3C !important;
        box-shadow: 0 0 0 2px rgba(76, 175, 80, 0.3) !important;
    }
    
    /* Labels des inputs */
    .stTextInput label,
    .stNumberInput label,
    .stSelectbox label,
    .stDateInput label,
    .stTextArea label {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.7) !important;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: var(--card-shadow);
        font-family: 'Source Sans Pro', sans-serif;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a3a52 0%, #2c5f7d 100%);
    }
    
    /* Animations */
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes slideDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Conteneur de formulaire */
    .form-container {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: var(--card-shadow);
        margin: 1rem 0;
    }
    
    /* Badges de statut */
    .status-badge {
        display: inline-block;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        font-family: 'Source Sans Pro', sans-serif;
        letter-spacing: 0.5px;
    }
    
    .status-ok {
        background: #d4edda;
        color: #155724;
    }
    
    .status-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    .status-danger {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Tabs personnalisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: var(--card-shadow);
    }
    
    .stTabs [data-baseweb="tab"] {
        font-family: 'Source Sans Pro', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
        padding: 1rem 2rem;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--background-gradient);
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Initialisation des données dans session_state
def init_session_state():
    """Initialise l'état de session de manière optimisée"""
    # Éviter les rechargements constants - ne charger que si nécessaire
    if 'data_loaded' not in st.session_state:
        print("🔄 Initialisation des données de session...")
        success = load_app_data()
        st.session_state.data_loaded = success

        # Log du résultat du chargement
        if success:
            print("✅ Données chargées avec succès")
        else:
            print("⚠️ Aucune donnée trouvée, initialisation avec des DataFrames vides")

    # S'assurer que toutes les sections sont initialisées avec des DataFrames valides
    # mais seulement si elles ne sont pas déjà présentes et valides
    sections = {
        'vehicules': ['Immatriculation', 'Marque', 'Modèle', 'Année', 'Type',
                     'Boîte_Pharmacie', 'Extincteur', 'Triangle_Panne', 'Cale',
                     'Etat_Propreté', 'Date_Inspection', 'Inspecteur', 'Statut'],
        'achats': ['Date', 'Article', 'Catégorie', 'Quantité', 'Prix_Unitaire',
                  'Prix_Total', 'Devise', 'Fournisseur', 'Responsable', 'Statut',
                  'Mode_Paiement', 'Référence', 'Notes'],
        'anomalies': ['Date_Signalement', 'Type', 'Description', 'Véhicule_Concerné',
                     'Priorité', 'Statut', 'Date_Résolution', 'Responsable', 'Actions_Prises',
                     'Nb_Documents', 'Documents'],
        'habilitations': ['Employé', 'Type_Habilitation', 'Numéro', 'Date_Obtention',
                         'Date_Expiration', 'Organisme', 'Statut', 'Vérifié_Par', 'Date_Vérification', 'Jours_Restants']
    }

    for section_name, columns in sections.items():
        if section_name not in st.session_state:
            st.session_state[section_name] = pd.DataFrame(columns=columns)
            print(f"🔄 {section_name}: DataFrame vide créé")
        elif not isinstance(st.session_state[section_name], pd.DataFrame):
            st.session_state[section_name] = pd.DataFrame(columns=columns)
            print(f"🔄 {section_name}: DataFrame recréé (type invalide)")

    # Vérifier et corriger les colonnes manquantes pour les achats (migration)
    if not st.session_state.achats.empty and 'Devise' not in st.session_state.achats.columns:
        st.session_state.achats['Devise'] = 'EUR (€)'
        print("Migration: Colonne Devise ajoutée aux achats existants")

    # Mettre à jour les statuts des habilitations au démarrage (une seule fois)
    if 'habilitations_updated' not in st.session_state:
        update_habilitations_status()
        st.session_state.habilitations_updated = True

    # Log final des données chargées (une seule fois)
    if 'init_logged' not in st.session_state:
        total_records = (len(st.session_state.vehicules) + len(st.session_state.achats) +
                        len(st.session_state.anomalies) + len(st.session_state.habilitations))
        print(f"📊 État final: {len(st.session_state.vehicules)} véhicules, {len(st.session_state.achats)} achats, "
              f"{len(st.session_state.anomalies)} anomalies, {len(st.session_state.habilitations)} habilitations "
              f"(Total: {total_records} enregistrements)")
        st.session_state.init_logged = True


# Fonction pour générer un PDF à partir d'un DataFrame
def generate_pdf_bytes(df, title):
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.units import inch
    import io

    buffer = io.BytesIO()

    # Utiliser le format A4 au lieu de letter
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                           rightMargin=30, leftMargin=30,
                           topMargin=30, bottomMargin=30)

    styles = getSampleStyleSheet()
    story = []

    # Titre stylisé
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Centré
        textColor=colors.darkblue
    )
    story.append(Paragraph(title, title_style))
    story.append(Spacer(1, 12))

    if title == "Habilitations et Certifications":
        temp_paths = []
        for idx, row in df.iterrows():
            hab_dict = row.to_dict()
            img_data, _ = generate_habilitation_image(hab_dict)
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(img_data)
                img_path = tmp.name
            temp_paths.append(img_path)
            img = Image(img_path, width=400, height=300)
            story.append(img)
            story.append(PageBreak())
        doc.build(story)
        for path in temp_paths:
            os.unlink(path)
    elif title == "Anomalies et Réclamations":
        # Générer des fiches de preuves individuelles
        for idx, row in df.iterrows():
            # Titre de la fiche
            fiche_title = f"Fiche de Preuve - Anomalie #{idx + 1}"
            story.append(Paragraph(fiche_title, title_style))
            story.append(Spacer(1, 12))
            
            # Informations détaillées
            info_style = ParagraphStyle(
                'InfoStyle',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6
            )
            
            story.append(Paragraph(f"<b>Date de signalement:</b> {row['Date_Signalement']}", info_style))
            story.append(Paragraph(f"<b>Type:</b> {row['Type']}", info_style))
            story.append(Paragraph(f"<b>Description:</b> {row['Description']}", info_style))
            story.append(Paragraph(f"<b>Véhicule concerné:</b> {row['Véhicule_Concerné'] or 'N/A'}", info_style))
            story.append(Paragraph(f"<b>Priorité:</b> {row['Priorité']}", info_style))
            story.append(Paragraph(f"<b>Statut:</b> {row['Statut']}", info_style))
            if pd.notna(row['Date_Résolution']):
                story.append(Paragraph(f"<b>Date de résolution:</b> {row['Date_Résolution']}", info_style))
            story.append(Paragraph(f"<b>Responsable:</b> {row['Responsable']}", info_style))
            if row['Actions_Prises']:
                story.append(Paragraph(f"<b>Actions prises:</b> {row['Actions_Prises']}", info_style))
            story.append(Spacer(1, 12))
            
            # Documents joints
            if 'Documents' in row and row['Documents']:
                doc_paths = str(row['Documents']).split(';')
                story.append(Paragraph("<b>Documents joints:</b>", info_style))
                for doc_path in doc_paths:
                    if os.path.exists(doc_path):
                        try:
                            if doc_path.lower().endswith(('.jpg', '.jpeg', '.png')):
                                # Insérer l'image
                                img = Image(doc_path, width=300, height=200)
                                story.append(img)
                                story.append(Spacer(1, 6))
                            elif doc_path.lower().endswith('.pdf'):
                                story.append(Paragraph(f"Document PDF: {os.path.basename(doc_path)}", info_style))
                            else:
                                story.append(Paragraph(f"Document: {os.path.basename(doc_path)}", info_style))
                        except Exception as e:
                            story.append(Paragraph(f"Erreur chargement document: {os.path.basename(doc_path)}", info_style))
                story.append(Spacer(1, 12))
            
            # Ligne de séparation
            story.append(PageBreak())
    
    else:
        if df.empty:
            story.append(Paragraph("Aucune donnée disponible.", styles['Normal']))
        else:
            # Convertir les NaN et None en chaînes vides pour éviter les erreurs
            df_clean = df.fillna('').copy()

            # Limiter le nombre de colonnes affichées pour éviter les coupures
            max_cols = 8  # Limiter à 8 colonnes maximum pour la lisibilité
            if len(df_clean.columns) > max_cols:
                # Sélectionner les colonnes les plus importantes
                priority_cols = ['Immatriculation', 'Marque', 'Modèle', 'Date', 'Article', 'Prix_Total', 'Type', 'Statut']
                selected_cols = []
                for col in priority_cols:
                    if col in df_clean.columns and len(selected_cols) < max_cols:
                        selected_cols.append(col)

                # Ajouter d'autres colonnes si nécessaire
                for col in df_clean.columns:
                    if col not in selected_cols and len(selected_cols) < max_cols:
                        selected_cols.append(col)

                df_clean = df_clean[selected_cols]

            # Préparer les données avec gestion des textes longs
            data = [df_clean.columns.tolist()] + df_clean.values.tolist()

            # Configuration améliorée pour les tableaux
            page_width = A4[0] - 60  # Largeur disponible (marges déduites)
            num_cols = len(df_clean.columns)

            # Largeurs de colonnes optimisées
            if num_cols <= 3:
                col_width = page_width / num_cols
                col_widths = [col_width] * num_cols
            elif num_cols <= 5:
                col_widths = [1.5 * inch] * num_cols
                # Ajuster si trop large
                total_width = sum(col_widths)
                if total_width > page_width:
                    col_widths = [page_width / num_cols] * num_cols
            else:
                # Pour beaucoup de colonnes, utiliser des largeurs fixes réduites
                col_widths = [1.0 * inch] * num_cols
                total_width = sum(col_widths)
                if total_width > page_width:
                    col_widths = [page_width / num_cols] * num_cols

            # Créer le tableau avec options améliorées pour éviter les coupures
            table = Table(data, colWidths=col_widths,
                         repeatRows=1,  # Répète l'en-tête sur chaque page
                         splitByRow=True,  # Permet la division sur plusieurs pages
                         hAlign='LEFT')  # Alignement à gauche

            # Style amélioré du tableau
            table_style = [
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),

                # Bordures
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),

                # Corps du tableau
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 4),
                ('TOPPADDING', (0, 1), (-1, -1), 4),
                ('LEFTPADDING', (0, 0), (-1, -1), 3),
                ('RIGHTPADDING', (0, 0), (-1, -1), 3),
            ]

            # Couleurs alternées pour le corps du tableau
            num_rows = len(data)
            for row_idx in range(1, num_rows):
                if row_idx % 2 == 1:
                    table_style.append(('BACKGROUND', (0, row_idx), (-1, row_idx), colors.lightgrey))

            table.setStyle(TableStyle(table_style))

            # Gestion améliorée des textes longs
            for i, row in enumerate(data):
                for j, cell in enumerate(row):
                    cell_str = str(cell)
                    if len(cell_str) > 30:  # Texte long
                        # Créer un paragraphe avec césure automatique
                        cell_style = ParagraphStyle(
                            'CellText',
                            fontSize=8,
                            leading=10,
                            wordWrap='CJK',
                            alignment=0,  # Gauche
                            spaceAfter=0,
                            spaceBefore=0
                        )
                        data[i][j] = Paragraph(cell_str, cell_style)
                    elif len(cell_str) > 15:  # Texte moyen
                        # Couper et ajouter des sauts de ligne manuels si nécessaire
                        words = cell_str.split()
                        lines = []
                        current_line = ""
                        for word in words:
                            if len(current_line + " " + word) > 15:
                                lines.append(current_line)
                                current_line = word
                            else:
                                current_line += " " + word if current_line else word

                        if current_line:
                            lines.append(current_line)

                        data[i][j] = "\n".join(lines)

            story.append(table)

            # Informations de résumé
            if len(df_clean) > 10:
                story.append(Spacer(1, 12))
                summary_style = ParagraphStyle(
                    'Summary',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=colors.darkgrey,
                    alignment=2
                )
                summary_text = f"Total d'enregistrements: {len(df_clean)} | Colonnes affichées: {num_cols} | Généré le: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
                story.append(Paragraph(summary_text, summary_style))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# Fonction pour générer une image de certificat d'habilitation
def generate_habilitation_image(hab_dict):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.text(0.5, 0.9, 'CERTIFICAT D\'HABILITATION', ha='center', va='center', fontsize=20, fontweight='bold')
    ax.text(0.1, 0.8, f'Employé: {hab_dict["Employé"]}', fontsize=12)
    ax.text(0.1, 0.7, f'Type: {hab_dict["Type_Habilitation"]}', fontsize=12)
    ax.text(0.1, 0.6, f'Numéro: {hab_dict["Numéro"]}', fontsize=12)
    ax.text(0.1, 0.5, f'Date d\'obtention: {hab_dict["Date_Obtention"]}', fontsize=12)
    ax.text(0.1, 0.4, f'Date d\'expiration: {hab_dict["Date_Expiration"]}', fontsize=12)
    ax.text(0.1, 0.3, f'Organisme: {hab_dict["Organisme"]}', fontsize=12)
    ax.text(0.1, 0.2, f'Statut: {hab_dict["Statut"]}', fontsize=12)
    ax.text(0.1, 0.1, f'Vérifié par: {hab_dict["Vérifié_Par"]} le {hab_dict["Date_Vérification"]}', fontsize=12)
    ax.axis('off')
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    img_bytes = buf.getvalue()
    # Upload to Cloudinary (uniquement en mode online)
    app_mode = get_app_mode()
    if app_mode == "online":
        try:
            result = cloudinary.uploader.upload(buf, folder="habilitations")
            img_url = result['secure_url']
            print(f"Image uploadée vers Cloudinary: {img_url}")
        except Exception as e:
            print(f"Erreur upload Cloudinary: {e}")
            img_url = None
    else:
        print("Mode offline: Upload Cloudinary ignoré")
        img_url = None
    plt.close(fig)
    return img_bytes, img_url

# Fonction pour sauvegarder les données dans MySQL
def save_data_to_mysql():
    data = {
        'vehicules': st.session_state.vehicules.to_dict('records'),
        'achats': st.session_state.achats.to_dict('records'),
        'anomalies': st.session_state.anomalies.to_dict('records'),
        'habilitations': st.session_state.habilitations.to_dict('records')
    }
    data_json = json.dumps(data)
    print(f"Saving data to MySQL, size: {len(data_json)} chars")
    print(f"Data preview: {data_json[:200]}...")
    try:
        conn = mysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'excel_app'),
            port=int(os.environ.get('MYSQL_PORT', '3306'))
        )
        cursor = conn.cursor()
        # Supprimer les anciennes données
        cursor.execute('DELETE FROM app_data')
        # Insérer les nouvelles données
        cursor.execute('INSERT INTO app_data (`key`, value) VALUES (%s, %s)', ('app_data', data_json))
        conn.commit()
        conn.close()
        print("Données sauvegardées dans MySQL")
        return True
    except mysql.Error as e:
        print(f"Erreur sauvegarde MySQL: {str(e)}")
        # Fallback to SQLite
        return save_data_to_sqlite()
    except Exception as e:
        print(f"Erreur générale sauvegarde: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def load_data_from_mysql():
    try:
        conn = mysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'excel_app'),
            port=int(os.environ.get('MYSQL_PORT', '3306'))
        )
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM app_data WHERE `key` = ?', ('app_data',))
        result = cursor.fetchone()
        conn.close()
        if result:
            data = json.loads(result[0])
            st.session_state.vehicules = pd.DataFrame(data.get('vehicules', []))
            st.session_state.achats = pd.DataFrame(data.get('achats', []))
            st.session_state.anomalies = pd.DataFrame(data.get('anomalies', []))
            st.session_state.habilitations = pd.DataFrame(data.get('habilitations', []))
            
            # Migration des données : ajouter la colonne Devise si elle n'existe pas
            if not st.session_state.achats.empty and 'Devise' not in st.session_state.achats.columns:
                st.session_state.achats['Devise'] = 'EUR (€)'
                print("Migration: Colonne Devise ajoutée aux achats existants")
            
            print("Données chargées depuis MySQL")
            # Enregistrer dans les logs d'audit
            total_loaded = len(st.session_state.vehicules) + len(st.session_state.achats) + len(st.session_state.anomalies) + len(st.session_state.habilitations)
            log_action("CHARGEMENT", "base_données", "MySQL", 
                      f"Données chargées - {len(st.session_state.vehicules)} véhicules, {len(st.session_state.achats)} achats, {len(st.session_state.anomalies)} anomalies, {len(st.session_state.habilitations)} habilitations")
            return True
        else:
            print("Aucune donnée trouvée dans MySQL")
            return False
    except mysql.Error as e:
        print(f"Erreur chargement MySQL: {str(e)}")
        # Fallback to SQLite
        return load_data_from_sqlite()
    except Exception as e:
        print(f"Erreur générale chargement: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Fonction pour synchroniser les données après sauvegarde
def sync_data_after_save():
    """Synchronise les données en mémoire avec celles de la base de données"""
    try:
        print("🔄 Synchronisation des données après sauvegarde...")

        # Recharger les données depuis la base
        mysql_data = None
        sqlite_data = None

        # Essayer de charger depuis MySQL
        if check_mysql_connection():
            try:
                conn = mysql.connect(
                    host=os.environ.get('MYSQL_HOST', 'localhost'),
                    user=os.environ.get('MYSQL_USER', 'root'),
                    password=os.environ.get('MYSQL_PASSWORD', ''),
                    database=os.environ.get('MYSQL_DB', 'excel_app'),
                    port=int(os.environ.get('MYSQL_PORT', '3306'))
                )
                cursor = conn.cursor()
                cursor.execute('SELECT value FROM app_data WHERE `key` = %s', ('app_data',))
                result = cursor.fetchone()
                conn.close()
                if result:
                    mysql_data = json.loads(result[0])
            except mysql.Error as e:
                print(f"⚠️ Erreur rechargement MySQL: {str(e)}")

        # Essayer de charger depuis SQLite
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            # Essayer d'abord la nouvelle structure
            cursor.execute('SELECT data FROM app_data ORDER BY id DESC LIMIT 1')
            result = cursor.fetchone()
            if result:
                sqlite_data = json.loads(result[0])
            else:
                # Essayer l'ancienne structure
                cursor.execute('SELECT value FROM app_data WHERE key = ?', ('app_data',))
                result = cursor.fetchone()
                if result:
                    sqlite_data = json.loads(result[0])
            conn.close()
        except Exception as e:
            print(f"⚠️ Erreur rechargement SQLite: {str(e)}")

        # Mettre à jour les DataFrames en session
        if mysql_data or sqlite_data:
            for key in ['vehicules', 'achats', 'anomalies', 'habilitations']:
                mysql_items = mysql_data.get(key, []) if mysql_data else []
                sqlite_items = sqlite_data.get(key, []) if sqlite_data else []

                if len(mysql_items) > 0:
                    st.session_state[key] = pd.DataFrame(mysql_items)
                elif len(sqlite_items) > 0:
                    st.session_state[key] = pd.DataFrame(sqlite_items)

            # Migration des colonnes
            if not st.session_state.achats.empty and 'Devise' not in st.session_state.achats.columns:
                st.session_state.achats['Devise'] = 'EUR (€)'
                print("Migration: Colonne Devise ajoutée aux achats existants")

            print("✅ Données synchronisées")
            return True
        else:
            print("⚠️ Aucune donnée trouvée pour la synchronisation")
            return False

    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation: {str(e)}")
        return False

# Fonction unifiée pour sauvegarder les données (MySQL + SQLite)
def save_app_data():
    """Sauvegarde les données dans MySQL (principal) et SQLite (sauvegarde)"""
    mysql_success = False
    sqlite_success = False

    # Sauvegarde MySQL (base principale)
    if check_mysql_connection():
        mysql_success = save_data_to_mysql()
        if mysql_success:
            print("✅ Données sauvegardées dans MySQL")
        else:
            print("❌ Échec sauvegarde MySQL")
    else:
        print("⚠️ MySQL non disponible")

    # Sauvegarde SQLite (sauvegarde secondaire)
    sqlite_success = save_data_to_sqlite()
    if sqlite_success:
        print("✅ Données sauvegardées dans SQLite")
    else:
        print("❌ Échec sauvegarde SQLite")

    # Synchronisation automatique après sauvegarde réussie
    if mysql_success or sqlite_success:
        print("🔄 Synchronisation automatique des données...")
        sync_success = sync_data_after_save()
        if sync_success:
            print("✅ Synchronisation terminée")
            # Marquer qu'une synchronisation a eu lieu pour forcer le rafraîchissement
            st.session_state.last_sync = datetime.now().isoformat()
            st.session_state.dashboard_needs_refresh = True
        else:
            print("⚠️ Synchronisation partielle")

    # Retourne True si au moins une sauvegarde a réussi
    return mysql_success or sqlite_success

# Fonction unifiée pour charger les données (MySQL prioritaire, SQLite fallback)
def load_app_data():
    """Charge les données depuis MySQL (principal) ou SQLite (fallback)"""
    mysql_data = None
    sqlite_data = None
    
    # Essayer de charger depuis MySQL
    if check_mysql_connection():
        try:
            conn = mysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', ''),
                database=os.environ.get('MYSQL_DB', 'excel_app'),
                port=int(os.environ.get('MYSQL_PORT', '3306'))
            )
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM app_data WHERE `key` = %s', ('app_data',))
            result = cursor.fetchone()
            conn.close()
            if result:
                mysql_data = json.loads(result[0])
                print("✅ Données chargées depuis MySQL")
        except mysql.Error as e:
            print(f"⚠️ Erreur chargement MySQL: {str(e)}")
    
    # Essayer de charger depuis SQLite
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        # Essayer d'abord la nouvelle structure (avec colonne 'data')
        cursor.execute('SELECT data FROM app_data ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            sqlite_data = json.loads(result[0])
            print("✅ Données chargées depuis SQLite (nouvelle structure)")
        else:
            # Essayer l'ancienne structure (avec colonnes 'key' et 'value')
            cursor.execute('SELECT value FROM app_data WHERE key = ?', ('app_data',))
            result = cursor.fetchone()
            if result:
                sqlite_data = json.loads(result[0])
                print("✅ Données chargées depuis SQLite (ancienne structure)")
        conn.close()
    except Exception as e:
        print(f"⚠️ Erreur chargement SQLite: {str(e)}")
        # Essayer une approche plus simple si la table n'existe pas
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM app_data LIMIT 1')
            result = cursor.fetchone()
            if result:
                print("ℹ️ Table app_data trouvée mais structure inconnue")
            conn.close()
        except Exception as e2:
            print(f"⚠️ Table app_data non trouvée ou corrompue: {str(e2)}")
    
    # Fusionner les données (MySQL prioritaire, compléter avec SQLite)
    if mysql_data or sqlite_data:
        final_data = {}
        for key in ['vehicules', 'achats', 'anomalies', 'habilitations']:
            mysql_items = mysql_data.get(key, []) if mysql_data else []
            sqlite_items = sqlite_data.get(key, []) if sqlite_data else []

            # Log pour déboguer
            print(f"Debug - {key}: MySQL={len(mysql_items)}, SQLite={len(sqlite_items)}")

            # Utiliser MySQL si disponible, sinon SQLite
            if len(mysql_items) > 0:
                final_data[key] = mysql_items
                print(f"✅ {key}: Chargé depuis MySQL ({len(mysql_items)} éléments)")
            elif len(sqlite_items) > 0:
                final_data[key] = sqlite_items
                print(f"ℹ️ {key}: Chargé depuis SQLite ({len(sqlite_items)} éléments)")
            else:
                final_data[key] = []
                print(f"⚠️ {key}: Aucune donnée trouvée")

        # Appliquer les données
        st.session_state.vehicules = pd.DataFrame(final_data.get('vehicules', []))
        st.session_state.achats = pd.DataFrame(final_data.get('achats', []))
        st.session_state.anomalies = pd.DataFrame(final_data.get('anomalies', []))
        st.session_state.habilitations = pd.DataFrame(final_data.get('habilitations', []))
        
        # Migration des données
        if not st.session_state.achats.empty and 'Devise' not in st.session_state.achats.columns:
            st.session_state.achats['Devise'] = 'EUR (€)'
            print("Migration: Colonne Devise ajoutée aux achats existants")
        
        total_loaded = len(st.session_state.vehicules) + len(st.session_state.achats) + len(st.session_state.anomalies) + len(st.session_state.habilitations)
        log_action("CHARGEMENT", "base_données", "MySQL+SQLite", 
                  f"Données fusionnées - {len(st.session_state.vehicules)} véhicules, {len(st.session_state.achats)} achats, {len(st.session_state.anomalies)} anomalies, {len(st.session_state.habilitations)} habilitations")
        
        # Vérifier l'intégrité des données
        data_integrity_check()
        
        return True
    else:
        print("❌ Aucune donnée trouvée dans les bases de données")
        # Même si aucune donnée n'est trouvée, on retourne True pour indiquer que le chargement s'est bien passé
        # Les DataFrames vides seront créés par init_session_state()
        return True

# Fonction pour vérifier l'intégrité des données
def data_integrity_check():
    """Vérifie que toutes les sections de données sont correctement initialisées"""
    sections = ['vehicules', 'achats', 'anomalies', 'habilitations']
    issues_found = []
    
    for section in sections:
        if section not in st.session_state:
            issues_found.append(f"{section}: variable manquante")
            continue
            
        df = st.session_state[section]
        if not isinstance(df, pd.DataFrame):
            issues_found.append(f"{section}: n'est pas un DataFrame")
            continue
            
        if df.empty:
            print(f"ℹ️ {section}: DataFrame vide ({len(df)} enregistrements)")
        else:
            print(f"✅ {section}: {len(df)} enregistrement(s)")
    
    if issues_found:
        print(f"⚠️ Problèmes d'intégrité détectés: {', '.join(issues_found)}")
        # Tenter de corriger automatiquement
        for issue in issues_found:
            section = issue.split(':')[0]
            if 'variable manquante' in issue:
                # Recréer le DataFrame manquant
                if section == 'vehicules':
                    st.session_state.vehicules = pd.DataFrame(columns=[
                        'Immatriculation', 'Marque', 'Modèle', 'Année', 'Type',
                        'Boîte_Pharmacie', 'Extincteur', 'Triangle_Panne', 'Cale',
                        'Etat_Propreté', 'Date_Inspection', 'Inspecteur', 'Statut'
                    ])
                elif section == 'achats':
                    st.session_state.achats = pd.DataFrame(columns=[
                        'Date', 'Article', 'Catégorie', 'Quantité', 'Prix_Unitaire',
                        'Prix_Total', 'Devise', 'Fournisseur', 'Responsable', 'Statut',
                        'Mode_Paiement', 'Référence', 'Notes'
                    ])
                elif section == 'anomalies':
                    st.session_state.anomalies = pd.DataFrame(columns=[
                        'Date_Signalement', 'Type', 'Description', 'Véhicule_Concerné',
                        'Priorité', 'Statut', 'Date_Résolution', 'Responsable', 'Actions_Prises',
                        'Nb_Documents', 'Documents'
                    ])
                elif section == 'habilitations':
                    st.session_state.habilitations = pd.DataFrame(columns=[
                        'Employé', 'Type_Habilitation', 'Numéro', 'Date_Obtention',
                        'Date_Expiration', 'Organisme', 'Statut', 'Vérifié_Par', 'Date_Vérification', 'Jours_Restants'
                    ])
                print(f"🔧 {section}: DataFrame recréé automatiquement")
    else:
        print("✅ Intégrité des données vérifiée")

# Fonction pour sauvegarder les données dans SQLite
def save_data_to_sqlite():
    data = {
        'vehicules': st.session_state.vehicules.to_dict('records'),
        'achats': st.session_state.achats.to_dict('records'),
        'anomalies': st.session_state.anomalies.to_dict('records'),
        'habilitations': st.session_state.habilitations.to_dict('records')
    }
    data_json = json.dumps(data)
    print(f"Saving data to SQLite, size: {len(data_json)} chars")
    print(f"Data preview: {data_json[:200]}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('DROP TABLE IF EXISTS app_data')
        cursor.execute('''
            CREATE TABLE app_data (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        cursor.execute('INSERT INTO app_data (data) VALUES (?)', (data_json,))
        conn.commit()
        conn.close()
        print("Données sauvegardées dans SQLite")
        return True
    except Exception as e:
        print(f"Erreur sauvegarde SQLite: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def load_data_from_sqlite():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_data (
                id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        cursor.execute('SELECT data FROM app_data ORDER BY id DESC LIMIT 1')
        result = cursor.fetchone()
        if result:
            data = json.loads(result[0])
            st.session_state.vehicules = pd.DataFrame(data.get('vehicules', []))
            st.session_state.achats = pd.DataFrame(data.get('achats', []))
            st.session_state.anomalies = pd.DataFrame(data.get('anomalies', []))
            st.session_state.habilitations = pd.DataFrame(data.get('habilitations', []))
            
            # Migration des données : ajouter la colonne Devise si elle n'existe pas
            if not st.session_state.achats.empty and 'Devise' not in st.session_state.achats.columns:
                st.session_state.achats['Devise'] = 'EUR (€)'
                print("Migration: Colonne Devise ajoutée aux achats existants")
            
            print("Données chargées depuis SQLite")
            # Enregistrer dans les logs d'audit
            total_loaded = len(st.session_state.vehicules) + len(st.session_state.achats) + len(st.session_state.anomalies) + len(st.session_state.habilitations)
            log_action("CHARGEMENT", "base_données", "SQLite", 
                      f"Données chargées - {len(st.session_state.vehicules)} véhicules, {len(st.session_state.achats)} achats, {len(st.session_state.anomalies)} anomalies, {len(st.session_state.habilitations)} habilitations")
            return True
        else:
            print("Aucune donnée trouvée dans SQLite")
            return False
    except Exception as e:
        print(f"Erreur chargement SQLite: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

# Fonction pour charger les données depuis Cloudinary

# Fonction pour initialiser la table des logs d'audit
def init_audit_logs():
    try:
        conn = mysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'excel_app'),
            port=int(os.environ.get('MYSQL_PORT', '3306'))
        )
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp VARCHAR(255),
                user_action VARCHAR(255),
                entity_type VARCHAR(255),
                entity_id VARCHAR(255),
                action_type VARCHAR(255),
                details TEXT,
                user_info TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    except mysql.Error as err:
        print(f"Erreur MySQL init_audit_logs: {err}")
        # Fallback to SQLite if MySQL fails
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                user_action TEXT,
                entity_type TEXT,
                entity_id TEXT,
                action_type TEXT,
                details TEXT,
                user_info TEXT
            )
        ''')
        
        conn.commit()
        conn.close()

# Fonction pour enregistrer une action dans les logs
def log_action(action_type, entity_type, entity_id="", details="", user_info="Utilisateur"):
    try:
        init_audit_logs()  # S'assurer que la table existe

        # Vérifier la santé de MySQL
        if check_mysql_connection():
            conn = mysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', ''),
                database=os.environ.get('MYSQL_DB', 'excel_app'),
                port=int(os.environ.get('MYSQL_PORT', '3306'))
            )
            cursor = conn.cursor()

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute('''
                INSERT INTO audit_logs (timestamp, user_action, entity_type, entity_id, action_type, details, user_info)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            ''', (timestamp, f"{action_type} {entity_type}", entity_type, entity_id, action_type, details, user_info))

            conn.commit()
            conn.close()
        else:
            # Fallback vers SQLite
            log_action_sqlite(action_type, entity_type, entity_id, details, user_info)
            print("Debug - Log enregistré dans SQLite (MySQL indisponible)")

        # Sauvegarder automatiquement dans un fichier local
        save_logs_to_file()

        # Envoyer une notification par email seulement pour les nouveaux enregistrements
        if action_type == "AJOUT":
            send_email_notification(action_type, entity_type, entity_id, details, user_info)

    except Exception as e:
        print(f"Erreur lors de l'enregistrement du log: {str(e)}")
        # En cas d'erreur, essayer SQLite
        try:
            log_action_sqlite(action_type, entity_type, entity_id, details, user_info)
        except Exception as sqlite_e:
            print(f"Erreur SQLite également: {str(sqlite_e)}")

# Fonction de fallback pour enregistrer les logs dans SQLite
def log_action_sqlite(action_type, entity_type, entity_id="", details="", user_info="Utilisateur"):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute('''
            INSERT INTO audit_logs (timestamp, user_action, entity_type, entity_id, action_type, details, user_info)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, f"{action_type} {entity_type}", entity_type, entity_id, action_type, details, user_info))

        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erreur lors de l'enregistrement du log SQLite: {str(e)}")

# Fonctions de gestion de la corbeille
def add_to_corbeille(entity_type, entity_data, deleted_by="Utilisateur"):
    """Ajoute un élément supprimé à la corbeille"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO corbeille (entity_type, entity_data, deleted_at, deleted_by)
            VALUES (?, ?, ?, ?)
        ''', (entity_type, json.dumps(entity_data), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), deleted_by))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Erreur ajout à la corbeille: {str(e)}")
        return False

def get_corbeille_items():
    """Récupère tous les éléments de la corbeille"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, entity_type, entity_data, deleted_at, deleted_by
            FROM corbeille
            ORDER BY deleted_at DESC
        ''')
        
        items = cursor.fetchall()
        conn.close()
        
        # Convertir en liste de dictionnaires
        corbeille_items = []
        for item in items:
            corbeille_items.append({
                'id': item[0],
                'entity_type': item[1],
                'entity_data': json.loads(item[2]),
                'deleted_at': item[3],
                'deleted_by': item[4]
            })
        
        return corbeille_items
    except Exception as e:
        print(f"Erreur récupération corbeille: {str(e)}")
        return []

def restore_from_corbeille(item_id, user_info="Utilisateur"):
    """Restaure un élément de la corbeille"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Récupérer l'élément de la corbeille
        cursor.execute('SELECT entity_type, entity_data FROM corbeille WHERE id = ?', (item_id,))
        item = cursor.fetchone()
        
        if not item:
            conn.close()
            return False, "Élément non trouvé dans la corbeille"
        
        entity_type, entity_data = item
        data = json.loads(entity_data)
        
        # Ajouter l'élément à la bonne DataFrame selon le type
        if entity_type == 'véhicule':
            if st.session_state.vehicules.empty:
                st.session_state.vehicules = pd.DataFrame([data])
            else:
                st.session_state.vehicules = pd.concat([st.session_state.vehicules, pd.DataFrame([data])], ignore_index=True)
        elif entity_type == 'achat':
            if st.session_state.achats.empty:
                st.session_state.achats = pd.DataFrame([data])
            else:
                st.session_state.achats = pd.concat([st.session_state.achats, pd.DataFrame([data])], ignore_index=True)
        elif entity_type == 'anomalie':
            if st.session_state.anomalies.empty:
                st.session_state.anomalies = pd.DataFrame([data])
            else:
                st.session_state.anomalies = pd.concat([st.session_state.anomalies, pd.DataFrame([data])], ignore_index=True)
        elif entity_type == 'habilitation':
            if st.session_state.habilitations.empty:
                st.session_state.habilitations = pd.DataFrame([data])
            else:
                st.session_state.habilitations = pd.concat([st.session_state.habilitations, pd.DataFrame([data])], ignore_index=True)
        
        # Supprimer de la corbeille
        cursor.execute('DELETE FROM corbeille WHERE id = ?', (item_id,))
        
        conn.commit()
        conn.close()
        
        # Sauvegarder les données
        save_app_data()
        
        # Logger l'action
        entity_id = data.get('Immatriculation', data.get('Article', data.get('Type', data.get('Employé', 'N/A'))))
        log_action("RESTAURATION", entity_type, entity_id, f"Restauré depuis la corbeille", user_info)
        
        return True, f"Élément {entity_type} restauré avec succès"
        
    except Exception as e:
        print(f"Erreur restauration corbeille: {str(e)}")
        return False, f"Erreur lors de la restauration: {str(e)}"

def empty_corbeille(user_info="Utilisateur"):
    """Vide complètement la corbeille"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les éléments avant suppression
        cursor.execute('SELECT COUNT(*) FROM corbeille')
        result = cursor.fetchone()
        count = result[0] if result else 0
        
        # Vider la corbeille
        cursor.execute('DELETE FROM corbeille')
        
        conn.commit()
        conn.close()
        
        # Logger l'action
        log_action("VIDAGE", "corbeille", "Tous les éléments", f"{count} éléments supprimés définitivement", user_info)
        
        return True, f"Corbeille vidée avec succès ({count} éléments supprimés)"
        
    except Exception as e:
        print(f"Erreur vidage corbeille: {str(e)}")
        return False, f"Erreur lors du vidage: {str(e)}"

# Fonctions de monitoring de la base de données
def get_database_stats():
    """Calcule les statistiques de stockage de la base de données"""
    try:
        # Taille du fichier de base de données
        db_size_bytes = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        db_size_mb = db_size_bytes / (1024 * 1024)
        
        # Stockage alloué par utilisateur (5 GB = 5120 MB)
        allocated_storage_mb = 5120
        remaining_storage_mb = allocated_storage_mb - db_size_mb
        
        # Statistiques des données
        vehicules_count = len(st.session_state.vehicules) if hasattr(st.session_state, 'vehicules') else 0
        achats_count = len(st.session_state.achats) if hasattr(st.session_state, 'achats') else 0
        anomalies_count = len(st.session_state.anomalies) if hasattr(st.session_state, 'anomalies') else 0
        habilitations_count = len(st.session_state.habilitations) if hasattr(st.session_state, 'habilitations') else 0
        
        # Statistiques de la corbeille
        corbeille_items = get_corbeille_items()
        corbeille_count = len(corbeille_items)
        
        # Statistiques des logs d'audit
        try:
            conn = mysql.connect(
                host=os.environ.get('MYSQL_HOST', 'localhost'),
                user=os.environ.get('MYSQL_USER', 'root'),
                password=os.environ.get('MYSQL_PASSWORD', ''),
                database=os.environ.get('MYSQL_DB', 'excel_app'),
                port=int(os.environ.get('MYSQL_PORT', '3306'))
            )
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM audit_logs')
            result = cursor.fetchone()
            audit_logs_count = result[0] if result else 0
            conn.close()
        except mysql.Error:
            # Fallback to SQLite if MySQL fails
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM audit_logs')
                result = cursor.fetchone()
                audit_logs_count = result[0] if result else 0
                conn.close()
            except:
                audit_logs_count = 0
        
        return {
            'db_size_mb': round(db_size_mb, 2),
            'allocated_storage_mb': allocated_storage_mb,
            'remaining_storage_mb': max(0, round(remaining_storage_mb, 2)),
            'usage_percentage': min(100, round((db_size_mb / allocated_storage_mb) * 100, 1)),
            'stats': {
                'vehicules': vehicules_count,
                'achats': achats_count,
                'anomalies': anomalies_count,
                'habilitations': habilitations_count,
                'corbeille': corbeille_count,
                'audit_logs': audit_logs_count
            }
        }
        
    except Exception as e:
        print(f"Erreur calcul statistiques DB: {str(e)}")
        return {
            'db_size_mb': 0,
            'allocated_storage_mb': 5120,
            'remaining_storage_mb': 5120,
            'usage_percentage': 0,
            'stats': {
                'vehicules': 0,
                'achats': 0,
                'anomalies': 0,
                'habilitations': 0,
                'corbeille': 0,
                'audit_logs': 0
            }
        }

def display_database_monitoring():
    """Affiche le monitoring de la base de données"""
    st.markdown("### 📊 Monitoring Base de Données")
    
    stats = get_database_stats()
    
    # Métriques principales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Stockage utilisé", 
            f"{stats['db_size_mb']} MB",
            help=f"Sur {stats['allocated_storage_mb']} MB alloués"
        )
    
    with col2:
        st.metric(
            "Espace restant", 
            f"{stats['remaining_storage_mb']} MB",
            help=f"{stats['usage_percentage']}% d'utilisation"
        )
    
    with col3:
        # Indicateur de couleur selon l'usage
        if stats['usage_percentage'] < 70:
            color = "🟢"
        elif stats['usage_percentage'] < 85:
            color = "🟡"
        else:
            color = "🔴"
        
        st.metric(
            "Utilisation", 
            f"{color} {stats['usage_percentage']}%"
        )
    
    # Barre de progression
    st.progress(min(1.0, stats['usage_percentage'] / 100))
    
    # Détails des données stockées
    st.markdown("#### 📋 Données stockées")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Entités principales:**")
        st.info(f"🚙 Véhicules: {stats['stats']['vehicules']}")
        st.info(f"🛒 Achats: {stats['stats']['achats']}")
        st.info(f"⚠️ Anomalies: {stats['stats']['anomalies']}")
        st.info(f"🎓 Habilitations: {stats['stats']['habilitations']}")
    
    with col2:
        st.markdown("**Système:**")
        st.info(f"🗑️ Corbeille: {stats['stats']['corbeille']}")
        st.info(f"📝 Logs d'audit: {stats['stats']['audit_logs']}")
        
        # Calcul du total
        total_entities = sum(stats['stats'].values())
        st.info(f"📊 Total: {total_entities} éléments")
    
    # Alertes de stockage
    if stats['usage_percentage'] > 90:
        st.error("🚨 **ALERTE:** Stockage presque plein! Considérez l'archivage ou la suppression de données.")
    elif stats['usage_percentage'] > 75:
        st.warning("⚠️ **ATTENTION:** Stockage utilisé à plus de 75%. Surveillez l'espace disponible.")
    
    # Informations techniques
    with st.expander("ℹ️ Informations techniques"):
        st.markdown(f"""
        - **Fichier DB:** `{db_path}`
        - **Taille exacte:** {stats['db_size_mb'] * 1024 * 1024:.0f} bytes
        - **Quota utilisateur:** {stats['allocated_storage_mb']} MB (5 GB)
        - **Mise à jour:** {datetime.now().strftime('%H:%M:%S')}
        """)

# Fonction pour récupérer les logs d'audit
def get_audit_logs(limit=100):
    try:
        init_audit_logs()
        
        conn = mysql.connect(
            host=os.environ.get('MYSQL_HOST', 'localhost'),
            user=os.environ.get('MYSQL_USER', 'root'),
            password=os.environ.get('MYSQL_PASSWORD', ''),
            database=os.environ.get('MYSQL_DB', 'excel_app'),
            port=int(os.environ.get('MYSQL_PORT', '3306'))
        )
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, user_action, entity_type, entity_id, action_type, details, user_info
            FROM audit_logs
            ORDER BY timestamp DESC
            LIMIT %s
        ''', (limit,))
        
        logs = cursor.fetchall()
        conn.close()
        
        return logs
    except mysql.Error as mysql_err:
        print(f"Erreur MySQL get_audit_logs: {mysql_err}")
        # Fallback to SQLite if MySQL fails
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT timestamp, user_action, entity_type, entity_id, action_type, details, user_info
                FROM audit_logs
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            logs = cursor.fetchall()
            conn.close()
            
            return logs
        except Exception as sqlite_err:
            print(f"Erreur SQLite get_audit_logs: {sqlite_err}")
            return []
    except Exception as e:
        print(f"Erreur lors de la récupération des logs: {str(e)}")
        return []

# Fonction pour sauvegarder les logs dans un fichier local
def save_logs_to_file():
    try:
        import os
        
        # Créer le dossier des logs s'il n'existe pas
        logs_dir = os.path.join(os.getcwd(), "logs_audit")
        os.makedirs(logs_dir, exist_ok=True)
        
        # Nom du fichier avec la date
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = os.path.join(logs_dir, f"audit_logs_{today}.txt")
        
        logs = get_audit_logs(1000)  # Récupérer les 1000 derniers logs
        
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("=== LOGS D'AUDIT - SYSTÈME DE GESTION ===\n")
            f.write(f"Généré le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            for log in logs:
                timestamp, user_action, entity_type, entity_id, action_type, details, user_info = log
                f.write(f"[{timestamp}] {user_action}\n")
                f.write(f"  Type: {entity_type} | ID: {entity_id} | Action: {action_type}\n")
                f.write(f"  Détails: {details}\n")
                f.write(f"  Utilisateur: {user_info}\n")
                f.write("-" * 50 + "\n")
        
        return log_file
    except Exception as e:
        print(f"Erreur lors de la sauvegarde des logs: {str(e)}")
        return None

# Fonction pour afficher les logs d'audit
def display_audit_logs():
    st.markdown("### 📋 Logs d'Audit")
    
    logs = get_audit_logs(50)  # Afficher les 50 derniers logs
    
    if logs:
        # Filtres
        col1, col2 = st.columns(2)
        with col1:
            filter_action = st.multiselect(
                "Filtrer par action",
                options=list(set([log[4] for log in logs])),  # action_type
                default=[]
            )
        with col2:
            filter_entity = st.multiselect(
                "Filtrer par entité",
                options=list(set([log[2] for log in logs])),  # entity_type
                default=[]
            )
        
        # Appliquer les filtres
        filtered_logs = logs
        if filter_action:
            filtered_logs = [log for log in filtered_logs if log[4] in filter_action]
        if filter_entity:
            filtered_logs = [log for log in filtered_logs if log[2] in filter_entity]
        
        # Afficher les logs
        if filtered_logs:
            for log in filtered_logs:
                timestamp, user_action, entity_type, entity_id, action_type, details, user_info = log
                
                # Déterminer la couleur selon le type d'action
                if action_type == "AJOUT":
                    color = "🟢"
                elif action_type == "MODIFICATION":
                    color = "🟡"
                elif action_type == "SUPPRESSION":
                    color = "🔴"
                else:
                    color = "🔵"
                
                st.markdown(f"""
                <div style="border-left: 4px solid {'#28a745' if action_type=='AJOUT' else '#ffc107' if action_type=='MODIFICATION' else '#dc3545' if action_type=='SUPPRESSION' else '#007bff'}; padding: 10px; margin: 5px 0; background-color: #f8f9fa; border-radius: 5px;">
                    <strong>{color} {user_action}</strong><br>
                    <small style="color: #666;">{timestamp} | {user_info}</small><br>
                    <small><strong>ID:</strong> {entity_id} | <strong>Détails:</strong> {details}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("Aucun log ne correspond aux filtres sélectionnés.")
        
        # Bouton pour exporter les logs
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📄 Générer rapport des logs", width='stretch'):
                log_file = save_logs_to_file()
                if log_file:
                    st.success(f"✅ Rapport généré: {log_file}")
                    
                    # Lire le fichier et permettre le téléchargement
                    with open(log_file, 'r', encoding='utf-8') as f:
                        log_content = f.read()
                    
                    st.download_button(
                        "📥 Télécharger le rapport",
                        log_content,
                        f"rapport_audit_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt",
                        "text/plain",
                        width='stretch'
                    )
                else:
                    st.error("❌ Erreur lors de la génération du rapport")
        
        with col2:
            if st.button("🗑️ Vider les logs", width='stretch', type="primary"):
                if st.session_state.get('confirm_clear_logs', False):
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute('DELETE FROM audit_logs')
                    conn.commit()
                    conn.close()
                    st.success("✅ Logs vidés avec succès!")
                    st.session_state.confirm_clear_logs = False
                    st.rerun()
                else:
                    st.session_state.confirm_clear_logs = True
                    st.warning("⚠️ Cliquez à nouveau pour confirmer la suppression de tous les logs")
        
        with col3:
            df_logs = pd.DataFrame(logs, columns=['Timestamp', 'Action', 'Entity', 'ID', 'Type', 'Details', 'User'])
            pdf_data = generate_pdf_bytes(df_logs, "Rapport d'Audit Complet")
            st.download_button("📄 Exporter PDF Complet", pdf_data, "rapport_audit_complet.pdf", "application/pdf", width='stretch')
        
        with col4:
            today = datetime.now().strftime('%Y-%m-%d')
            daily_logs = [log for log in logs if log[0].startswith(today)]
            if daily_logs:
                df_daily = pd.DataFrame(daily_logs, columns=['Timestamp', 'Action', 'Entity', 'ID', 'Type', 'Details', 'User'])
                pdf_data = generate_pdf_bytes(df_daily, f"Rapport d'Audit Journalier - {today}")
                st.download_button("📄 Exporter PDF Journalier", pdf_data, f"rapport_audit_{today}.pdf", "application/pdf", width='stretch')
            else:
                st.info("Aucun log pour aujourd'hui.")
    else:
        st.success("📝 Aucun log d'audit enregistré pour le moment.")

# Fonction pour sauvegarder les données (maintenue pour compatibilité)
def save_data():
    data = {
        'vehicules': st.session_state.vehicules.to_dict('records'),
        'achats': st.session_state.achats.to_dict('records'),
        'anomalies': st.session_state.anomalies.to_dict('records'),
        'habilitations': st.session_state.habilitations.to_dict('records')
    }
    return data

# Fonction pour charger les données
def load_data(data):
    st.session_state.vehicules = pd.DataFrame(data.get('vehicules', []))
    st.session_state.achats = pd.DataFrame(data.get('achats', []))
    st.session_state.anomalies = pd.DataFrame(data.get('anomalies', []))
    st.session_state.habilitations = pd.DataFrame(data.get('habilitations', []))

# En-tête de l'application
def display_header():
    # En-tête sans logo (logo déplacé dans la sidebar)
    st.markdown("""
    <div class="main-header">
        <h1 style="color: green;">Système de Gestion Avancé</h1>
        <p>Plateforme complète de gestion des véhicules, achats, anomalies et habilitations</p>
    </div>
    """, unsafe_allow_html=True)

# Fonction pour calculer les statistiques actuelles
def get_current_stats():
    """Calcule les statistiques actuelles pour le tableau de bord"""
    # Mettre à jour les statuts d'habilitations avant de calculer
    update_habilitations_status()

    stats = {
        'vehicules': len(st.session_state.vehicules),
        'achats': len(st.session_state.achats),
        'anomalies_ouvertes': len(st.session_state.anomalies[
            st.session_state.anomalies['Statut'] == 'Ouverte'
        ]) if not st.session_state.anomalies.empty else 0,
        'habilitations_expirees': len(st.session_state.habilitations[
            st.session_state.habilitations['Statut'] == 'Expirée'
        ]) if not st.session_state.habilitations.empty else 0
    }

    # Debug: Afficher les statistiques calculées
    print(f"Debug - Stats calculées: vehicules={stats['vehicules']}, achats={stats['achats']}, anomalies_ouvertes={stats['anomalies_ouvertes']}, habilitations_expirees={stats['habilitations_expirees']}")

    return stats

# Fonction pour vérifier si les statistiques ont changé
def stats_have_changed():
    """Vérifie si les statistiques ont changé depuis le dernier calcul"""
    current_stats = get_current_stats()
    last_stats = st.session_state.get('last_dashboard_stats', {})

    if current_stats != last_stats:
        st.session_state.last_dashboard_stats = current_stats
        return True
    return False

# Tableau de bord avec métriques
def display_dashboard():
    monitoring_systeme()

# Module Inspection des Véhicules
def inspection_vehicules():
    st.markdown("### 🚙 Inspection des Véhicules")
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Gestion du mode édition
    if 'edit_mode' in st.session_state and st.session_state.edit_mode in ['add_vehicle', 'edit_vehicle']:
        st.markdown("### ✏️ Mode Édition")
        
        if st.session_state.edit_mode == 'edit_vehicle' and st.session_state.edit_index is not None:
            # Pré-remplir avec les données existantes
            vehicle_data = st.session_state.vehicules.iloc[st.session_state.edit_index]
            st.markdown(f"**Modification du véhicule:** {vehicle_data['Immatriculation']}")
            
            col1, col2 = st.columns(2)
            with col1:
                immatriculation = st.text_input("Immatriculation *", value=vehicle_data['Immatriculation'])
                marque = st.text_input("Marque *", value=vehicle_data['Marque'])
                modele = st.text_input("Modèle *", value=vehicle_data['Modèle'])
                annee = st.number_input("Année", min_value=1990, max_value=2025, value=int(vehicle_data['Année']))
                type_vehicule = st.selectbox("Type de véhicule", 
                    ["Véhicule léger", "Utilitaire", "Poids lourd", "Moto", "Autre"],
                    index=["Véhicule léger", "Utilitaire", "Poids lourd", "Moto", "Autre"].index(vehicle_data['Type']))
            
            with col2:
                st.markdown("**Équipements de sécurité**")
                boite_pharmacie = st.selectbox("Boîte à pharmacie", 
                    ["Conforme", "Non conforme", "Absente"],
                    index=["Conforme", "Non conforme", "Absente"].index(vehicle_data['Boîte_Pharmacie']))
                extincteur = st.selectbox("Extincteur", 
                    ["Conforme", "Non conforme", "Absent", "Périmé"],
                    index=["Conforme", "Non conforme", "Absent", "Périmé"].index(vehicle_data['Extincteur']))
                triangle_panne = st.selectbox("Triangle de panne", 
                    ["Conforme", "Non conforme", "Absent"],
                    index=["Conforme", "Non conforme", "Absent"].index(vehicle_data['Triangle_Panne']))
                cale = st.selectbox("Cale", 
                    ["Conforme", "Non conforme", "Absente"],
                    index=["Conforme", "Non conforme", "Absente"].index(vehicle_data['Cale']))
            
            etat_proprete = st.select_slider(
                "État de propreté",
                options=["Très sale", "Sale", "Moyen", "Propre", "Très propre"],
                value=vehicle_data['Etat_Propreté']
            )
            
            col1, col2 = st.columns(2)
            with col1:
                inspecteur = st.text_input("Inspecteur *", value=vehicle_data['Inspecteur'])
            with col2:
                date_inspection = st.date_input("Date d'inspection", 
                    value=pd.to_datetime(vehicle_data['Date_Inspection']))
            
            observations = st.text_area("Observations complémentaires", 
                value=vehicle_data.get('Observations', ''))
            
        else:
            # Mode ajout - même formulaire que tab1
            col1, col2 = st.columns(2)
            with col1:
                immatriculation = st.text_input("Immatriculation *", placeholder="AA-123-BB")
                marque = st.text_input("Marque *", placeholder="Peugeot, Renault, etc.")
                modele = st.text_input("Modèle *", placeholder="308, Clio, etc.")
                annee = st.number_input("Année", min_value=1990, max_value=2025, value=2020)
                type_vehicule = st.selectbox("Type de véhicule", 
                    ["Véhicule léger", "Utilitaire", "Poids lourd", "Moto", "Autre"])
            
            with col2:
                st.markdown("**Équipements de sécurité**")
                boite_pharmacie = st.selectbox("Boîte à pharmacie", ["Conforme", "Non conforme", "Absente"])
                extincteur = st.selectbox("Extincteur", ["Conforme", "Non conforme", "Absent", "Périmé"])
                triangle_panne = st.selectbox("Triangle de panne", ["Conforme", "Non conforme", "Absent"])
                cale = st.selectbox("Cale", ["Conforme", "Non conforme", "Absente"])
            
            etat_proprete = st.select_slider(
                "État de propreté",
                options=["Très sale", "Sale", "Moyen", "Propre", "Très propre"],
                value="Moyen"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                inspecteur = st.text_input("Inspecteur *", value="Madame AZIZET")
            with col2:
                date_inspection = st.date_input("Date d'inspection", datetime.now())
            
            observations = st.text_area("Observations complémentaires", 
                placeholder="Notez ici toute observation particulière...")
        
        # Calcul automatique du statut
        statut = "Conforme"
        if any([boite_pharmacie == "Absente", extincteur in ["Absent", "Périmé"], 
                triangle_panne == "Absent", cale == "Absente"]):
            statut = "Non conforme"
        elif any([boite_pharmacie == "Non conforme", extincteur == "Non conforme",
                  triangle_panne == "Non conforme", cale == "Non conforme"]):
            statut = "À surveiller"
        
        st.markdown(f"**Statut automatique:** <span class='status-badge status-{'ok' if statut=='Conforme' else 'warning' if statut=='À surveiller' else 'danger'}'>{statut}</span>", 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Sauvegarder", width='stretch'):
                print("Debug - Save button pressed")
                print(f"Debug - Fields: Immatriculation={immatriculation}, Marque={marque}, Modele={modele}, Inspecteur={inspecteur}")
                if immatriculation and marque and modele and inspecteur:
                    vehicle_dict = {
                        'Immatriculation': immatriculation,
                        'Marque': marque,
                        'Modèle': modele,
                        'Année': annee,
                        'Type': type_vehicule,
                        'Boîte_Pharmacie': boite_pharmacie,
                        'Extincteur': extincteur,
                        'Triangle_Panne': triangle_panne,
                        'Cale': cale,
                        'Etat_Propreté': etat_proprete,
                        'Date_Inspection': date_inspection.strftime('%Y-%m-%d'),
                        'Inspecteur': inspecteur,
                        'Statut': statut,
                        'Observations': observations
                    }
                    
                    if st.session_state.edit_mode == 'edit_vehicle':
                        # Mise à jour
                        old_vehicle = st.session_state.vehicules.iloc[st.session_state.edit_index].copy()
                        for key, value in vehicle_dict.items():
                            st.session_state.vehicules.at[st.session_state.edit_index, key] = value
                        # Enregistrer dans les logs d'audit
                        log_action("MODIFICATION", "véhicule", vehicle_dict['Immatriculation'], 
                                  f"Modifié: {old_vehicle['Marque']} {old_vehicle['Modèle']} → {vehicle_dict['Marque']} {vehicle_dict['Modèle']}")
                        st.success("✅ Véhicule modifié avec succès!")
                        result = save_app_data()
                        if result:
                            st.success("✅ Données sauvegardées")
                        else:
                            st.error("❌ Erreur lors de la sauvegarde")
                    else:
                        # Ajout
                        new_vehicle = pd.DataFrame([vehicle_dict])
                        if st.session_state.vehicules.empty:
                            st.session_state.vehicules = new_vehicle
                        else:
                            st.session_state.vehicules = pd.concat([st.session_state.vehicules, new_vehicle], 
                                                                   ignore_index=True)
                        # Enregistrer dans les logs d'audit
                        log_action("AJOUT", "véhicule", vehicle_dict['Immatriculation'], 
                                  f"Inspection ajoutée - {vehicle_dict['Marque']} {vehicle_dict['Modèle']} - Statut: {statut}")
                        st.success("✅ Véhicule ajouté avec succès!")
                        st.balloons()
                        result = save_app_data()
                        if result:
                            st.success("✅ Données sauvegardées")
                        else:
                            st.error("❌ Erreur lors de la sauvegarde")
                    
                    # Réinitialiser le mode édition
                    del st.session_state.edit_mode
                    if 'edit_index' in st.session_state:
                        del st.session_state.edit_index
                    st.rerun()
                else:
                    missing = []
                    if not immatriculation:
                        missing.append("Immatriculation")
                    if not marque:
                        missing.append("Marque")
                    if not modele:
                        missing.append("Modèle")
                    if not inspecteur:
                        missing.append("Inspecteur")
                    if missing:
                        st.error(f"❌ Les champs suivants sont obligatoires : {', '.join(missing)}")
                    else:
                        st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
        
        with col2:
            if st.button("🔄 Annuler", width='stretch'):
                del st.session_state.edit_mode
                if 'edit_index' in st.session_state:
                    del st.session_state.edit_index
                st.rerun()
        
        with col3:
            if st.session_state.edit_mode == 'edit_vehicle' and st.button("🗑️ Supprimer ce véhicule", 
                width='stretch', type="primary"):
                # Récupérer les infos avant suppression pour le log
                vehicle_to_delete = st.session_state.vehicules.iloc[st.session_state.edit_index]
                vehicle_info = f"{vehicle_to_delete['Immatriculation']} - {vehicle_to_delete['Marque']} {vehicle_to_delete['Modèle']}"
                
                # Ajouter à la corbeille au lieu de supprimer
                vehicle_data = vehicle_to_delete.to_dict()
                if add_to_corbeille('véhicule', vehicle_data):
                    st.session_state.vehicules = st.session_state.vehicules.drop(st.session_state.edit_index).reset_index(drop=True)
                    # Enregistrer dans les logs d'audit
                    log_action("SUPPRESSION", "véhicule", vehicle_to_delete['Immatriculation'], 
                              f"Véhicule déplacé vers la corbeille: {vehicle_info}")
                    st.success("✅ Véhicule déplacé vers la corbeille!")
                    result = save_app_data()
                    if result:
                        st.success("✅ Données sauvegardées")
                    else:
                        st.error("❌ Erreur lors de la sauvegarde")
                else:
                    st.error("❌ Erreur lors du déplacement vers la corbeille")
                del st.session_state.edit_mode
                del st.session_state.edit_index
                st.rerun()
        
        st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Ajouter une inspection", "📋 Liste des inspections", "📊 Statistiques"])
    
    with tab1:
        st.markdown("#### Nouvelle inspection de véhicule")
        
        col1, col2 = st.columns(2)
        
        with col1:
            immatriculation = st.text_input("Immatriculation *", placeholder="AA-123-BB")
            marque = st.text_input("Marque *", placeholder="Peugeot, Renault, etc.")
            modele = st.text_input("Modèle *", placeholder="308, Clio, etc.")
            annee = st.number_input("Année", min_value=1990, max_value=2025, value=2020)
            type_vehicule = st.selectbox("Type de véhicule", 
                ["Véhicule léger", "Utilitaire", "Poids lourd", "Moto", "Autre"])
        
        with col2:
            st.markdown("**Équipements de sécurité**")
            boite_pharmacie = st.selectbox("Boîte à pharmacie", ["Conforme", "Non conforme", "Absente"])
            extincteur = st.selectbox("Extincteur", ["Conforme", "Non conforme", "Absent", "Périmé"])
            triangle_panne = st.selectbox("Triangle de panne", ["Conforme", "Non conforme", "Absent"])
            cale = st.selectbox("Cale", ["Conforme", "Non conforme", "Absente"])
        
        etat_proprete = st.select_slider(
            "État de propreté",
            options=["Très sale", "Sale", "Moyen", "Propre", "Très propre"],
            value="Moyen"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            inspecteur = st.text_input("Inspecteur *", value="Madame AZIZET")
        with col2:
            date_inspection = st.date_input("Date d'inspection", datetime.now())
        
        observations = st.text_area("Observations complémentaires", 
            placeholder="Notez ici toute observation particulière...")
        
        # Calcul automatique du statut
        statut = "Conforme"
        if any([boite_pharmacie == "Absente", extincteur in ["Absent", "Périmé"], 
                triangle_panne == "Absent", cale == "Absente"]):
            statut = "Non conforme"
        elif any([boite_pharmacie == "Non conforme", extincteur == "Non conforme",
                  triangle_panne == "Non conforme", cale == "Non conforme"]):
            statut = "À surveiller"
        
        st.markdown(f"**Statut automatique:** <span class='status-badge status-{'ok' if statut=='Conforme' else 'warning' if statut=='À surveiller' else 'danger'}'>{statut}</span>", 
                   unsafe_allow_html=True)
        
        if st.button("✅ Enregistrer l'inspection", width='stretch'):
            if immatriculation and marque and modele and inspecteur:
                new_inspection = pd.DataFrame([{
                    'Immatriculation': immatriculation,
                    'Marque': marque,
                    'Modèle': modele,
                    'Année': annee,
                    'Type': type_vehicule,
                    'Boîte_Pharmacie': boite_pharmacie,
                    'Extincteur': extincteur,
                    'Triangle_Panne': triangle_panne,
                    'Cale': cale,
                    'Etat_Propreté': etat_proprete,
                    'Date_Inspection': date_inspection.strftime('%Y-%m-%d'),
                    'Inspecteur': inspecteur,
                    'Statut': statut,
                    'Observations': observations
                }])
                if st.session_state.vehicules.empty:
                    st.session_state.vehicules = new_inspection
                else:
                    st.session_state.vehicules = pd.concat([st.session_state.vehicules, new_inspection], 
                                                           ignore_index=True)
                # Enregistrer dans les logs d'audit
                log_action("AJOUT", "véhicule", immatriculation, 
                          f"Inspection ajoutée - {marque} {modele} - Statut: {statut}")
                st.success("✅ Inspection enregistrée avec succès!")
                st.balloons()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab2:
        st.markdown("#### Liste des inspections")
        
        if not st.session_state.vehicules.empty:
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                filtre_statut = st.multiselect("Filtrer par statut", 
                    options=st.session_state.vehicules['Statut'].unique().tolist(),
                    default=st.session_state.vehicules['Statut'].unique().tolist())
            with col2:
                filtre_type = st.multiselect("Filtrer par type",
                    options=st.session_state.vehicules['Type'].unique().tolist(),
                    default=st.session_state.vehicules['Type'].unique().tolist())
            with col3:
                recherche = st.text_input("🔍 Rechercher", placeholder="Immatriculation, marque...")
            
            # Application des filtres
            df_filtre = st.session_state.vehicules[
                (st.session_state.vehicules['Statut'].isin(filtre_statut)) &
                (st.session_state.vehicules['Type'].isin(filtre_type))
            ]
            
            if recherche:
                df_filtre = df_filtre[
                    df_filtre.apply(lambda row: recherche.lower() in str(row).lower(), axis=1)
                ]
            
            st.dataframe(df_filtre, width='stretch', height=400)
            
            # Actions sur les éléments
            st.markdown("### 🛠️ Actions sur les véhicules")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Ajouter un véhicule", width='stretch'):
                    st.session_state.edit_mode = "add_vehicle"
                    st.session_state.edit_index = None
                    st.rerun()
            
            with col2:
                # Sélectionner un véhicule à modifier
                if not df_filtre.empty:
                    selected_vehicle = st.selectbox(
                        "Sélectionner un véhicule à modifier",
                        options=[f"{row['Immatriculation']} - {row['Marque']} {row['Modèle']}" 
                                for idx, row in df_filtre.iterrows()],
                        key="vehicle_select"
                    )
                    if st.button("✏️ Modifier", width='stretch'):
                        # Trouver l'index dans le dataframe original
                        selected_immat = selected_vehicle.split(" - ")[0]
                        original_index = st.session_state.vehicules[
                            st.session_state.vehicules['Immatriculation'] == selected_immat
                        ].index[0]
                        st.session_state.edit_mode = "edit_vehicle"
                        st.session_state.edit_index = original_index
                        st.rerun()
            
            with col3:
                # Sélectionner un véhicule à supprimer
                if not df_filtre.empty:
                    vehicle_to_delete = st.selectbox(
                        "Sélectionner un véhicule à supprimer",
                        options=[f"{row['Immatriculation']} - {row['Marque']} {row['Modèle']}" 
                                for idx, row in df_filtre.iterrows()],
                        key="vehicle_delete"
                    )
                    if st.button("🗑️ Supprimer", width='stretch', type="primary"):
                        selected_immat = vehicle_to_delete.split(" - ")[0]
                        st.session_state.vehicules = st.session_state.vehicules[
                            st.session_state.vehicules['Immatriculation'] != selected_immat
                        ].reset_index(drop=True)
                        st.success("✅ Véhicule supprimé avec succès!")
                        # save_data_to_sqlite()  # Retiré
                        st.rerun()
            
            # Export
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df_filtre.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exporter CSV", csv, "inspections_vehicules.csv", 
                                 "text/csv", width='stretch')
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_filtre.to_excel(writer, index=False, sheet_name='Inspections')
                excel_data = excel_buffer.getvalue()
                st.download_button("📥 Exporter Excel", excel_data, "inspections_vehicules.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 width='stretch')
            with col3:
                pdf_data = generate_pdf_bytes(df_filtre, "Inspections des Véhicules")
                st.download_button("📄 Exporter PDF", pdf_data, "inspections_vehicules.pdf", 
                                 "application/pdf", width='stretch')
        else:
            st.success("📝 Aucune inspection enregistrée pour le moment.")
    
    with tab3:
        if not st.session_state.vehicules.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Répartition par statut")
                statut_counts = st.session_state.vehicules['Statut'].value_counts()
                fig = px.bar(x=statut_counts.index, y=statut_counts.values,
                           labels={'x': 'Statut', 'y': 'Nombre de véhicules'},
                           color=statut_counts.values,
                           color_continuous_scale='RdYlGn')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Conformité des équipements")
                equipements = ['Boîte_Pharmacie', 'Extincteur', 'Triangle_Panne', 'Cale']
                conf_data = []
                for eq in equipements:
                    conformes = len(st.session_state.vehicules[st.session_state.vehicules[eq] == 'Conforme'])
                    conf_data.append({'Équipement': eq.replace('_', ' '), 'Conformes': conformes})
                df_conf = pd.DataFrame(conf_data)
                fig = px.bar(df_conf, x='Équipement', y='Conformes',
                           color='Conformes', color_continuous_scale='Viridis')
                st.plotly_chart(fig, width='stretch')
            
            # Ajouter plus de graphiques
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Répartition par marque")
                marque_counts = st.session_state.vehicules['Marque'].value_counts().head(10)
                fig = px.bar(x=marque_counts.index, y=marque_counts.values,
                           labels={'x': 'Marque', 'y': 'Nombre de véhicules'},
                           title="Top 10 marques",
                           color=marque_counts.values,
                           color_continuous_scale='Plasma')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Répartition par année")
                annee_counts = st.session_state.vehicules['Année'].value_counts().sort_index()
                fig = px.line(x=annee_counts.index, y=annee_counts.values,
                            labels={'x': 'Année', 'y': 'Nombre de véhicules'},
                            title="Évolution par année de fabrication",
                            markers=True)
                st.plotly_chart(fig, width='stretch')
            
            # Graphique de corrélation statut/équipements
            st.markdown("#### Analyse de conformité détaillée")
            conformite_data = []
            for idx, row in st.session_state.vehicules.iterrows():
                conformite = 0
                total_equip = 0
                for eq in equipements:
                    total_equip += 1
                    if row[eq] == 'Conforme':
                        conformite += 1
                
                taux_conformite = (conformite / total_equip) * 100 if total_equip > 0 else 0
                conformite_data.append({
                    'Véhicule': f"{row['Marque']} {row['Modèle']} ({row['Immatriculation']})",
                    'Taux_Conformité': taux_conformite,
                    'Statut': row['Statut']
                })
            
            df_conformite = pd.DataFrame(conformite_data)
            fig = px.scatter(df_conformite, x='Véhicule', y='Taux_Conformité', 
                           color='Statut',
                           labels={'x': 'Véhicule', 'y': 'Taux de conformité (%)'},
                           title="Taux de conformité par véhicule",
                           color_discrete_map={'Conforme': 'green', 'Non conforme': 'red', 'À surveiller': 'orange'})
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, width='stretch')
        else:
            st.success("📊 Aucune donnée disponible pour les statistiques.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Module Suivi des Achats
def suivi_achats():
    st.markdown("### 🛒 Suivi des Achats Annuels")
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Gestion du mode édition
    if 'edit_mode' in st.session_state and st.session_state.edit_mode in ['add_achat', 'edit_achat']:
        st.markdown("### ✏️ Mode Édition - Achats")
        
        # Initialisation des variables communes
        devise = "EUR (€)"  # Valeur par défaut
        
        if st.session_state.edit_mode == 'edit_achat' and st.session_state.edit_index is not None:
            # Pré-remplir avec les données existantes
            achat_data = st.session_state.achats.iloc[st.session_state.edit_index]
            st.markdown(f"**Modification de l'achat:** {achat_data['Article']}")
            
            col1, col2 = st.columns(2)
            with col1:
                article = st.text_input("Article / Description *", value=achat_data['Article'])
                categorie = st.selectbox("Catégorie *", 
                    ["Pièces détachées", "Entretien", "Carburant", "Assurance",
                     "Équipements de sécurité", "Fournitures", "Services", "Autre"],
                    index=["Pièces détachées", "Entretien", "Carburant", "Assurance",
                          "Équipements de sécurité", "Fournitures", "Services", "Autre"].index(achat_data['Catégorie']))
                quantite = st.number_input("Quantité *", min_value=1, value=int(achat_data['Quantité']))
                devise = st.selectbox("Devise *", 
                    ["EUR (€)", "USD ($)", "XAF (FCFA)", "XOF (CFA)", "GBP (£)", "CAD (C$)", "CHF (Fr)", "Autre"],
                    index=["EUR (€)", "USD ($)", "XAF (FCFA)", "XOF (CFA)", "GBP (£)", "CAD (C$)", "CHF (Fr)", "Autre"].index(
                        achat_data.get('Devise', 'EUR (€)') if achat_data.get('Devise', 'EUR (€)') in ["EUR (€)", "USD ($)", "XAF (FCFA)", "XOF (CFA)", "GBP (£)", "CAD (C$)", "CHF (Fr)", "Autre"] else "EUR (€)"
                    ))
                prix_unitaire = st.number_input(f"Prix unitaire ({devise.split(' ')[-1]}) *", min_value=0.0, 
                    value=float(achat_data['Prix_Unitaire']), step=0.01)
                prix_total = quantite * prix_unitaire
                st.metric("Prix total", f"{prix_total:.2f} {devise.split(' ')[-1]}")
            
            with col2:
                fournisseur = st.text_input("Fournisseur *", value=achat_data['Fournisseur'])
                responsable = st.text_input("Responsable *", value=achat_data['Responsable'])
                date_achat = st.date_input("Date d'achat", value=pd.to_datetime(achat_data['Date']))
                statut_achat = st.selectbox("Statut", ["Commandé", "Reçu", "Payé", "En attente"],
                    index=["Commandé", "Reçu", "Payé", "En attente"].index(achat_data['Statut']))
                mode_paiement = st.selectbox("Mode de paiement",
                    ["Virement", "Chèque", "Carte bancaire", "Espèces", "Autre"],
                    index=["Virement", "Chèque", "Carte bancaire", "Espèces", "Autre"].index(achat_data['Mode_Paiement']))
            
            reference = st.text_input("Numéro de référence / Facture", value=achat_data.get('Reference', ''))
            notes = st.text_area("Notes complémentaires", value=achat_data.get('Notes', ''))
            
        else:
            # Mode ajout
            col1, col2 = st.columns(2)
            with col1:
                article = st.text_input("Article / Description *", placeholder="Pneus, huile moteur, etc.")
                categorie = st.selectbox("Catégorie *", 
                    ["Pièces détachées", "Entretien", "Carburant", "Assurance",
                     "Équipements de sécurité", "Fournitures", "Services", "Autre"])
                quantite = st.number_input("Quantité *", min_value=1, value=1)
                devise = st.selectbox("Devise *", 
                    ["EUR (€)", "USD ($)", "XAF (FCFA)", "XOF (CFA)", "GBP (£)", "CAD (C$)", "CHF (Fr)", "Autre"])
                prix_unitaire = st.number_input(f"Prix unitaire ({devise.split(' ')[-1]}) *", min_value=0.0, value=0.0, step=0.01)
                prix_total = quantite * prix_unitaire
                st.metric("Prix total", f"{prix_total:.2f} {devise.split(' ')[-1]}")
            
            with col2:
                fournisseur = st.text_input("Fournisseur *", placeholder="Nom du fournisseur")
                responsable = st.text_input("Responsable *", value="Mr PAOLO")
                date_achat = st.date_input("Date d'achat", datetime.now())
                statut_achat = st.selectbox("Statut", ["Commandé", "Reçu", "Payé", "En attente"])
                mode_paiement = st.selectbox("Mode de paiement",
                    ["Virement", "Chèque", "Carte bancaire", "Espèces", "Autre"])
            
            reference = st.text_input("Numéro de référence / Facture", placeholder="F-2024-001")
            notes = st.text_area("Notes complémentaires", placeholder="Informations additionnelles...")
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Sauvegarder", width='stretch'):
                if article and categorie and fournisseur and responsable and prix_unitaire > 0:
                    achat_dict = {
                        'Date': date_achat.strftime('%Y-%m-%d'),
                        'Article': article,
                        'Catégorie': categorie,
                        'Quantité': quantite,
                        'Prix_Unitaire': prix_unitaire,
                        'Prix_Total': prix_total,
                        'Devise': devise,
                        'Fournisseur': fournisseur,
                        'Responsable': responsable,
                        'Statut': statut_achat,
                        'Mode_Paiement': mode_paiement,
                        'Reference': reference,
                        'Notes': notes
                    }
                    
                    if st.session_state.edit_mode == 'edit_achat':
                        old_achat = st.session_state.achats.iloc[st.session_state.edit_index].copy()
                        for key, value in achat_dict.items():
                            st.session_state.achats.at[st.session_state.edit_index, key] = value
                        # Enregistrer dans les logs d'audit
                        log_action("MODIFICATION", "achat", achat_dict['Article'], 
                                  f"Modifié: {old_achat['Article']} ({old_achat['Prix_Total']}€) → {achat_dict['Article']} ({achat_dict['Prix_Total']}€)")
                        st.success("✅ Achat modifié avec succès!")
                        save_app_data()
                    else:
                        new_achat = pd.DataFrame([achat_dict])
                        if st.session_state.achats.empty:
                            st.session_state.achats = new_achat
                        else:
                            st.session_state.achats = pd.concat([st.session_state.achats, new_achat], 
                                                               ignore_index=True)
                        # Enregistrer dans les logs d'audit
                        log_action("AJOUT", "achat", achat_dict['Article'], 
                                  f"Achat ajouté - {achat_dict['Article']} - {achat_dict['Prix_Total']}€ - {achat_dict['Fournisseur']}")
                        st.success("✅ Achat ajouté avec succès!")
                        st.balloons()
                        save_app_data()
                        # save_data_to_sqlite()  # Retiré, utilisation de Cloudinary pour les images uniquement
                        st.success("✅ Données sauvegardées (session)")
                    
                    del st.session_state.edit_mode
                    if 'edit_index' in st.session_state:
                        del st.session_state.edit_index
                    st.rerun()
                else:
                    st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
        
        with col2:
            if st.button("🔄 Annuler", width='stretch'):
                del st.session_state.edit_mode
                if 'edit_index' in st.session_state:
                    del st.session_state.edit_index
                st.rerun()
        
        with col3:
            if st.session_state.edit_mode == 'edit_achat' and st.button("🗑️ Supprimer cet achat", 
                width='stretch', type="primary"):
                # Récupérer les infos avant suppression pour le log
                achat_to_delete = st.session_state.achats.iloc[st.session_state.edit_index]
                achat_info = f"{achat_to_delete['Article']} - {achat_to_delete['Prix_Total']}€ - {achat_to_delete['Fournisseur']}"
                
                # Ajouter à la corbeille au lieu de supprimer
                achat_data = achat_to_delete.to_dict()
                if add_to_corbeille('achat', achat_data):
                    st.session_state.achats = st.session_state.achats.drop(st.session_state.edit_index).reset_index(drop=True)
                    # Enregistrer dans les logs d'audit
                    log_action("SUPPRESSION", "achat", achat_to_delete['Article'], 
                              f"Achat déplacé vers la corbeille: {achat_info}")
                    st.success("✅ Achat déplacé vers la corbeille!")
                    save_app_data()
                else:
                    st.error("❌ Erreur lors du déplacement vers la corbeille")
                del st.session_state.edit_mode
                del st.session_state.edit_index
                st.rerun()
        
        st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Nouvel achat", "📋 Historique des achats", "💰 Analyse budgétaire"])
    
    with tab1:
        st.markdown("#### Enregistrer un nouvel achat")
        
        col1, col2 = st.columns(2)
        
        with col1:
            article = st.text_input("Article / Description *", placeholder="Pneus, huile moteur, etc.")
            categorie = st.selectbox("Catégorie *", 
                ["Pièces détachées", "Entretien", "Carburant", "Assurance",
                 "Équipements de sécurité", "Fournitures", "Services", "Autre"])
            quantite = st.number_input("Quantité *", min_value=1, value=1)
            devise = st.selectbox("Devise *", 
                ["EUR (€)", "USD ($)", "XAF (FCFA)", "XOF (CFA)", "GBP (£)", "CAD (C$)", "CHF (Fr)", "Autre"])
            prix_unitaire = st.number_input(f"Prix unitaire ({devise.split(' ')[-1]}) *", min_value=0.0, value=0.0, step=0.01)
            prix_total = quantite * prix_unitaire
            st.metric("Prix total", f"{prix_total:.2f} {devise.split(' ')[-1]}")
        
        with col2:
            fournisseur = st.text_input("Fournisseur *", placeholder="Nom du fournisseur")
            responsable = st.text_input("Responsable *", value="Mr PAOLO")
            date_achat = st.date_input("Date d'achat", datetime.now())
            statut_achat = st.selectbox("Statut", ["Commandé", "Reçu", "Payé", "En attente"])
            mode_paiement = st.selectbox("Mode de paiement",
                ["Virement", "Chèque", "Carte bancaire", "Espèces", "Autre"])
        
        reference = st.text_input("Numéro de référence / Facture", placeholder="F-2024-001")
        notes = st.text_area("Notes complémentaires", placeholder="Informations additionnelles...")
        
        if st.button("💾 Enregistrer l'achat", width='stretch'):
            if article and categorie and fournisseur and responsable and prix_unitaire > 0:
                new_achat = pd.DataFrame([{
                    'Date': date_achat.strftime('%Y-%m-%d'),
                    'Article': article,
                    'Catégorie': categorie,
                    'Quantité': quantite,
                    'Prix_Unitaire': prix_unitaire,
                    'Prix_Total': prix_total,
                    'Devise': devise,
                    'Fournisseur': fournisseur,
                    'Responsable': responsable,
                    'Statut': statut_achat,
                    'Mode_Paiement': mode_paiement,
                    'Référence': reference,
                    'Notes': notes
                }])
                if st.session_state.achats.empty:
                    st.session_state.achats = new_achat
                else:
                    st.session_state.achats = pd.concat([st.session_state.achats, new_achat], 
                                                        ignore_index=True)
                st.success("✅ Achat enregistré avec succès!")
                st.balloons()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab2:
        st.markdown("#### Historique complet des achats")
        
        if not st.session_state.achats.empty:
            # Filtres avancés
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                filtre_categorie = st.multiselect("Catégorie",
                    options=st.session_state.achats['Catégorie'].unique().tolist(),
                    default=st.session_state.achats['Catégorie'].unique().tolist())
            with col2:
                filtre_statut = st.multiselect("Statut",
                    options=st.session_state.achats['Statut'].unique().tolist(),
                    default=st.session_state.achats['Statut'].unique().tolist())
            with col3:
                date_debut = st.date_input("Du", datetime.now() - timedelta(days=365))
            with col4:
                date_fin = st.date_input("Au", datetime.now())
            
            # Application des filtres
            df_filtre = st.session_state.achats[
                (st.session_state.achats['Catégorie'].isin(filtre_categorie)) &
                (st.session_state.achats['Statut'].isin(filtre_statut))
            ]
            
            if not df_filtre.empty:
                df_filtre['Date'] = pd.to_datetime(df_filtre['Date'])
                df_filtre = df_filtre[
                    (df_filtre['Date'] >= pd.Timestamp(date_debut)) &
                    (df_filtre['Date'] <= pd.Timestamp(date_fin))
                ]
            
            # Affichage avec total
            st.dataframe(df_filtre, width='stretch', height=400)
            
            if not df_filtre.empty:
                # Calcul des totaux par devise
                totaux_par_devise = df_filtre.groupby('Devise')['Prix_Total'].sum()
                st.markdown("### Totaux par devise:")
                for devise, total in totaux_par_devise.items():
                    devise_str = str(devise)
                    symbole = devise_str.split(' ')[-1] if ' ' in devise_str else devise_str
                    st.markdown(f"- **{devise_str}**: {total:.2f} {symbole}")
                
                total_general_eur = 0
                # Conversion approximative en EUR (à améliorer avec taux de change réels)
                for devise, total in totaux_par_devise.items():
                    devise_str = str(devise)
                    if 'EUR' in devise_str:
                        total_general_eur += total
                    elif 'USD' in devise_str:
                        total_general_eur += total * 0.85  # Taux approximatif
                    elif 'XAF' in devise_str or 'XOF' in devise_str:
                        total_general_eur += total * 0.0015  # Taux approximatif
                    elif 'GBP' in devise_str:
                        total_general_eur += total * 1.15  # Taux approximatif
                    else:
                        total_general_eur += total  # Pour autres devises, pas de conversion
                
                st.markdown(f"### Total estimé en EUR: **{total_general_eur:.2f} €**")
            
            # Actions sur les éléments
            st.markdown("### 🛠️ Actions sur les achats")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Ajouter un achat", width='stretch'):
                    st.session_state.edit_mode = "add_achat"
                    st.session_state.edit_index = None
                    st.rerun()
            
            with col2:
                # Sélectionner un achat à modifier
                if not df_filtre.empty:
                    selected_achat = st.selectbox(
                        "Sélectionner un achat à modifier",
                        options=[f"{row['Date']} - {row['Article']} ({row['Prix_Total']:.2f}€)" 
                                for idx, row in df_filtre.iterrows()],
                        key="achat_select"
                    )
                    if st.button("✏️ Modifier", width='stretch'):
                        # Trouver l'index dans le dataframe original
                        selected_info = selected_achat.split(" - ")[1].split(" (")[0]
                        original_index = st.session_state.achats[
                            st.session_state.achats['Article'] == selected_info
                        ].index[0]
                        st.session_state.edit_mode = "edit_achat"
                        st.session_state.edit_index = original_index
                        st.rerun()
            
            with col3:
                # Sélectionner un achat à supprimer
                if not df_filtre.empty:
                    achat_to_delete = st.selectbox(
                        "Sélectionner un achat à supprimer",
                        options=[f"{row['Date']} - {row['Article']} ({row['Prix_Total']:.2f} {str(row['Devise']).split(' ')[-1]})" 
                                for idx, row in df_filtre.iterrows()],
                        key="achat_delete"
                    )
                    if st.button("🗑️ Supprimer", width='stretch', type="primary"):
                        selected_info = achat_to_delete.split(" - ")[1].split(" (")[0]
                        st.session_state.achats = st.session_state.achats[
                            st.session_state.achats['Article'] != selected_info
                        ].reset_index(drop=True)
                        st.success("✅ Achat supprimé avec succès!")
                        save_app_data()
                        st.rerun()
            
            # Export
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df_filtre.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exporter CSV", csv, "achats.csv", 
                                 "text/csv", width='stretch')
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_filtre.to_excel(writer, index=False, sheet_name='Achats')
                excel_data = excel_buffer.getvalue()
                st.download_button("📥 Exporter Excel", excel_data, "achats.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 width='stretch')
            with col3:
                pdf_data = generate_pdf_bytes(df_filtre, "Achats")
                st.download_button("📄 Exporter PDF", pdf_data, "achats.pdf", 
                                 "application/pdf", width='stretch')
        else:
            st.success("📝 Aucun achat enregistré pour le moment.")
    
    with tab3:
        if not st.session_state.achats.empty:
            # Analyse par devise
            st.markdown("### Analyse par devise")
            devise_totals = st.session_state.achats.groupby('Devise')['Prix_Total'].sum().sort_values(ascending=False)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Répartition par devise")
                fig = px.pie(values=devise_totals.values, names=devise_totals.index,
                           hole=0.4, title="Répartition des dépenses par devise")
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Totaux par devise")
                for devise, total in devise_totals.items():
                    devise_str = str(devise)
                    symbole = devise_str.split(' ')[-1] if ' ' in devise_str else devise_str
                    st.metric(f"Total {devise_str}", f"{total:.2f} {symbole}")
            
            st.markdown("---")
            
            # Analyse par catégorie (conversion en EUR approximative pour comparaison)
            st.markdown("### Analyse par catégorie (estimée en EUR)")
            achats_eur = st.session_state.achats.copy()
            
            # Créer la colonne Mois pour l'analyse temporelle
            achats_eur['Date'] = pd.to_datetime(achats_eur['Date'], errors='coerce')
            achats_eur = achats_eur[achats_eur['Date'].notna()]  # Filtrer les dates invalides
            achats_eur['Mois'] = pd.PeriodIndex(achats_eur['Date'], freq='M')
            
            # Conversion approximative
            def convert_to_eur(row):
                devise = str(row['Devise'])
                montant = row['Prix_Total']
                if 'EUR' in devise:
                    return montant
                elif 'USD' in devise:
                    return montant * 0.85
                elif 'XAF' in devise or 'XOF' in devise:
                    return montant * 0.0015
                elif 'GBP' in devise:
                    return montant * 1.15
                else:
                    return montant  # Pas de conversion pour autres devises
            
            achats_eur['Prix_EUR'] = achats_eur.apply(convert_to_eur, axis=1)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Dépenses par catégorie (EUR)")
                cat_totals_eur = achats_eur.groupby('Catégorie')['Prix_EUR'].sum().sort_values(ascending=False)
                fig = px.bar(x=cat_totals_eur.index, y=cat_totals_eur.values,
                           labels={'x': 'Catégorie', 'y': 'Montant total (EUR)'},
                           color=cat_totals_eur.values,
                           color_continuous_scale='Turbo')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Top 5 fournisseurs (EUR)")
                fournisseur_totals_eur = achats_eur.groupby('Fournisseur')['Prix_EUR'].sum().sort_values(ascending=False).head(5)
                fig = px.pie(values=fournisseur_totals_eur.values, names=fournisseur_totals_eur.index,
                           hole=0.4)
                st.plotly_chart(fig, width='stretch')
            
            # Ajouter plus de graphiques
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Évolution des quantités achetées")
                quantites_mensuelles = achats_eur.groupby('Mois')['Quantité'].sum()
                fig = px.area(x=quantites_mensuelles.index.astype(str), y=quantites_mensuelles.values,
                            labels={'x': 'Mois', 'y': 'Quantité totale'},
                            title="Évolution des quantités achetées par mois",
                            color_discrete_sequence=['lightblue'])
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Prix moyen par catégorie")
                prix_moyen_categorie = achats_eur.groupby('Catégorie')['Prix_EUR'].mean().sort_values(ascending=False)
                fig = px.bar(x=prix_moyen_categorie.index, y=prix_moyen_categorie.values,
                           labels={'x': 'Catégorie', 'y': 'Prix moyen (EUR)'},
                           title="Prix moyen par catégorie",
                           color=prix_moyen_categorie.values,
                           color_continuous_scale='Cividis')
                st.plotly_chart(fig, width='stretch')
            
            # Graphique de tendance des achats
            st.markdown("#### Analyse des tendances d'achat")
            achats_tendance = achats_eur.copy()
            achats_tendance['Mois'] = achats_tendance['Mois'].astype(str)
            
            fig = px.scatter(achats_tendance, x='Mois', y='Prix_EUR', 
                           color='Catégorie',
                           size='Quantité',
                           labels={'x': 'Mois', 'y': 'Prix (EUR)', 'color': 'Catégorie'},
                           title="Tendances d'achat: Prix vs Quantité par mois et catégorie",
                           trendline="ols")
            st.plotly_chart(fig, width='stretch')
            
            # Analyse des fournisseurs
            st.markdown("#### Analyse comparative des fournisseurs")
            fournisseur_stats = achats_eur.groupby('Fournisseur').agg({
                'Prix_EUR': ['sum', 'mean', 'count'],
                'Quantité': 'sum'
            }).round(2)
            fournisseur_stats.columns = ['Total_EUR', 'Moyen_EUR', 'Nombre_Achats', 'Quantité_Totale']
            fournisseur_stats = fournisseur_stats.sort_values('Total_EUR', ascending=False).head(10)
            
            fig = px.bar(fournisseur_stats.reset_index(), x='Fournisseur', y=['Total_EUR', 'Moyen_EUR'],
                        title="Analyse comparative des top 10 fournisseurs",
                        barmode='group',
                        color_discrete_sequence=['darkblue', 'lightblue'])
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, width='stretch')
            
            # Tableau récapitulatif
            st.markdown("#### Récapitulatif budgétaire")
            total_depenses_eur = achats_eur['Prix_EUR'].sum()
            nb_achats = len(st.session_state.achats)
            montant_moyen_eur = total_depenses_eur / nb_achats if nb_achats > 0 else 0
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total dépenses (EUR)", f"{total_depenses_eur:.2f} €")
            col2.metric("Nombre d'achats", nb_achats)
            col3.metric("Montant moyen (EUR)", f"{montant_moyen_eur:.2f} €")
        else:
            st.success("💡 Aucune donnée disponible pour l'analyse budgétaire.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Module Anomalies et Réclamations
def gestion_anomalies():
    st.markdown("### ⚠️ Gestion des Anomalies et Réclamations")
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Gestion du mode édition
    if 'edit_mode' in st.session_state and st.session_state.edit_mode in ['add_anomalie', 'edit_anomalie']:
        st.markdown("### ✏️ Mode Édition - Anomalies")
        
        if st.session_state.edit_mode == 'edit_anomalie' and st.session_state.edit_index is not None:
            # Pré-remplir avec les données existantes
            anomalie_data = st.session_state.anomalies.iloc[st.session_state.edit_index]
            st.markdown(f"**Modification de l'anomalie:** {anomalie_data['Type']}")
            
            col1, col2 = st.columns(2)
            with col1:
                type_anomalie = st.selectbox("Type d'anomalie *",
                    ["Technique", "Administrative", "Sécurité", "Qualité", "Autre"],
                    index=["Technique", "Administrative", "Sécurité", "Qualité", "Autre"].index(anomalie_data['Type']))
                priorite = st.selectbox("Priorité",
                    ["Faible", "Moyenne", "Élevée", "Critique"],
                    index=["Faible", "Moyenne", "Élevée", "Critique"].index(anomalie_data['Priorité']))
                vehicule_concerne = st.text_input("Véhicule concerné", value=anomalie_data['Véhicule_Concerné'])
                date_signalement = st.date_input("Date de signalement", 
                    value=pd.to_datetime(anomalie_data['Date_Signalement']))
            
            with col2:
                statut = st.selectbox("Statut",
                    ["Ouvert", "En cours", "Résolu", "Fermé"],
                    index=["Ouvert", "En cours", "Résolu", "Fermé"].index(anomalie_data['Statut']))
                responsable = st.text_input("Responsable", value=anomalie_data['Responsable'])
                date_resolution = st.date_input("Date de résolution", 
                    value=pd.to_datetime(anomalie_data['Date_Résolution']) if pd.notna(anomalie_data['Date_Résolution']) else None)
            
            description = st.text_area("Description détaillée *", value=anomalie_data['Description'])
            actions_prises = st.text_area("Actions prises / Solution", value=anomalie_data.get('Actions_Prises', ''))
            
            # Photos ou documents pour édition
            existing_docs = anomalie_data.get('Documents', '')
            if existing_docs:
                existing_files = str(existing_docs).split(';') if existing_docs else []
                st.markdown(f"**Documents existants:** {len(existing_files)} fichier(s)")
                for doc in existing_files:
                    if os.path.exists(doc):
                        st.text(f"📎 {os.path.basename(doc)}")
            
            uploaded_files = st.file_uploader("Ajouter/modifier des photos ou documents",
                accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'pdf'], key="edit_uploader")
            
        else:
            # Mode ajout
            col1, col2 = st.columns(2)
            with col1:
                type_anomalie = st.selectbox("Type d'anomalie *",
                    ["Technique", "Administrative", "Sécurité", "Qualité", "Autre"])
                priorite = st.selectbox("Priorité",
                    ["Faible", "Moyenne", "Élevée", "Critique"])
                vehicule_concerne = st.text_input("Véhicule concerné", placeholder="Immatriculation ou description")
                date_signalement = st.date_input("Date de signalement", datetime.now())
            
            with col2:
                statut = st.selectbox("Statut",
                    ["Ouvert", "En cours", "Résolu", "Fermé"])
                responsable = st.text_input("Responsable", value="Madame AZIZET")
                date_resolution = st.date_input("Date de résolution")
            
            description = st.text_area("Description détaillée *", 
                placeholder="Décrivez l'anomalie ou la réclamation en détail...")
            actions_prises = st.text_area("Actions prises / Solution", 
                placeholder="Décrivez les actions entreprises pour résoudre le problème...")
            
            # Photos ou documents
            uploaded_files = st.file_uploader("Joindre des photos ou documents",
                accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'pdf'])
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Sauvegarder", width='stretch'):
                if type_anomalie and description:
                    # Créer le répertoire pour les uploads s'il n'existe pas
                    upload_dir = "uploads/anomalies"
                    os.makedirs(upload_dir, exist_ok=True)
                    
                    # Gérer les fichiers uploadés
                    file_paths = []
                    if uploaded_files:
                        for uploaded_file in uploaded_files:
                            # Générer un nom de fichier unique
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            file_extension = os.path.splitext(uploaded_file.name)[1]
                            unique_filename = f"{timestamp}_{uploaded_file.name}"
                            file_path = os.path.join(upload_dir, unique_filename)
                            
                            # Sauvegarder le fichier
                            with open(file_path, "wb") as f:
                                f.write(uploaded_file.getbuffer())
                            file_paths.append(file_path)
                    
                    # Pour l'édition, conserver les fichiers existants si aucun nouveau fichier n'est uploadé
                    if st.session_state.edit_mode == 'edit_anomalie' and not uploaded_files:
                        existing_docs = st.session_state.anomalies.iloc[st.session_state.edit_index].get('Documents', '')
                        if existing_docs:
                            file_paths = str(existing_docs).split(';')
                    
                    anomalie_dict = {
                        'Date_Signalement': date_signalement.strftime('%Y-%m-%d'),
                        'Type': type_anomalie,
                        'Description': description,
                        'Véhicule_Concerné': vehicule_concerne,
                        'Priorité': priorite,
                        'Statut': statut,
                        'Date_Résolution': date_resolution.strftime('%Y-%m-%d') if date_resolution else None,
                        'Responsable': responsable,
                        'Actions_Prises': actions_prises,
                        'Nb_Documents': len(file_paths),
                        'Documents': ';'.join(file_paths)  # Stocker les chemins séparés par ;
                    }
                    
                    if st.session_state.edit_mode == 'edit_anomalie':
                        old_anomalie = st.session_state.anomalies.iloc[st.session_state.edit_index].copy()
                        for key, value in anomalie_dict.items():
                            st.session_state.anomalies.at[st.session_state.edit_index, key] = value
                        # Enregistrer dans les logs d'audit
                        log_action("MODIFICATION", "anomalie", anomalie_dict['Type'], 
                                  f"Modifiée: {old_anomalie['Type']} ({old_anomalie['Priorité']}) → {anomalie_dict['Type']} ({anomalie_dict['Priorité']})")
                        st.success("✅ Anomalie modifiée avec succès!")
                        save_app_data()
                    else:
                        new_anomalie = pd.DataFrame([anomalie_dict])
                        if st.session_state.anomalies.empty:
                            st.session_state.anomalies = new_anomalie
                        else:
                            st.session_state.anomalies = pd.concat([st.session_state.anomalies, new_anomalie], 
                                                                 ignore_index=True)
                        # Enregistrer dans les logs d'audit
                        log_action("AJOUT", "anomalie", anomalie_dict['Type'], 
                                  f"Anomalie ajoutée - {anomalie_dict['Type']} - Priorité: {anomalie_dict['Priorité']} - {anomalie_dict['Véhicule_Concerné']}")
                        st.success("✅ Anomalie ajoutée avec succès!")
                        st.balloons()
                        save_app_data()
                    
                    del st.session_state.edit_mode
                    if 'edit_index' in st.session_state:
                        del st.session_state.edit_index
                    st.rerun()
                else:
                    st.error("❌ Veuillez remplir les champs obligatoires (*)")
        
        with col2:
            if st.button("🔄 Annuler", width='stretch'):
                del st.session_state.edit_mode
                if 'edit_index' in st.session_state:
                    del st.session_state.edit_index
                st.rerun()
        
        with col3:
            if st.session_state.edit_mode == 'edit_anomalie' and st.button("🗑️ Supprimer cette anomalie", 
                width='stretch', type="primary"):
                # Récupérer les infos avant suppression pour le log
                anomalie_to_delete = st.session_state.anomalies.iloc[st.session_state.edit_index]
                anomalie_info = f"{anomalie_to_delete['Type']} - {anomalie_to_delete['Description'][:50]}... - {anomalie_to_delete['Véhicule_Concerné']}"
                
                # Ajouter à la corbeille au lieu de supprimer
                anomalie_data = anomalie_to_delete.to_dict()
                if add_to_corbeille('anomalie', anomalie_data):
                    st.session_state.anomalies = st.session_state.anomalies.drop(st.session_state.edit_index).reset_index(drop=True)
                    # Enregistrer dans les logs d'audit
                    log_action("SUPPRESSION", "anomalie", anomalie_to_delete['Type'], 
                              f"Anomalie déplacée vers la corbeille: {anomalie_info}")
                    st.success("✅ Anomalie déplacée vers la corbeille!")
                    save_app_data()
                else:
                    st.error("❌ Erreur lors du déplacement vers la corbeille")
                del st.session_state.edit_mode
                del st.session_state.edit_index
                st.rerun()
        
        st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Signaler une anomalie", "📋 Suivi des anomalies", "📈 Analyse"])
    
    with tab1:
        st.markdown("#### Signaler une nouvelle anomalie ou réclamation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            type_anomalie = st.selectbox("Type *",
                ["Défaut véhicule", "Incident", "Réclamation client", "Non-conformité",
                 "Problème de sécurité", "Dysfonctionnement équipement", "Autre"])
            priorite = st.select_slider("Priorité *",
                options=["Basse", "Moyenne", "Haute", "Critique"],
                value="Moyenne")
            vehicule_concerne = st.text_input("Véhicule concerné (si applicable)",
                placeholder="Immatriculation")
            date_signalement = st.date_input("Date de signalement", datetime.now())
        
        with col2:
            responsable = st.text_input("Responsable du suivi *", value="Mr PAOLO")
            statut = st.selectbox("Statut", ["Ouverte", "En cours", "Résolue", "Fermée"])
            date_resolution = None
            if statut in ["Résolue", "Fermée"]:
                date_resolution = st.date_input("Date de résolution")
        
        description = st.text_area("Description détaillée *",
            placeholder="Décrivez l'anomalie ou la réclamation en détail...",
            height=100)
        
        actions_prises = st.text_area("Actions prises / À prendre",
            placeholder="Décrivez les actions correctives...",
            height=100)
        
        # Photos ou documents
        uploaded_files = st.file_uploader("Joindre des photos ou documents",
            accept_multiple_files=True, type=['jpg', 'jpeg', 'png', 'pdf'])
        
        if st.button("🚨 Enregistrer l'anomalie", width='stretch'):
            if type_anomalie and description and responsable:
                # Créer le répertoire pour les uploads s'il n'existe pas
                upload_dir = "uploads/anomalies"
                os.makedirs(upload_dir, exist_ok=True)
                
                # Sauvegarder les fichiers uploadés
                file_paths = []
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        # Générer un nom de fichier unique
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        file_extension = os.path.splitext(uploaded_file.name)[1]
                        unique_filename = f"{timestamp}_{uploaded_file.name}"
                        file_path = os.path.join(upload_dir, unique_filename)
                        
                        # Sauvegarder le fichier
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        file_paths.append(file_path)
                
                new_anomalie = pd.DataFrame([{
                    'Date_Signalement': date_signalement.strftime('%Y-%m-%d'),
                    'Type': type_anomalie,
                    'Description': description,
                    'Véhicule_Concerné': vehicule_concerne,
                    'Priorité': priorite,
                    'Statut': statut,
                    'Date_Résolution': date_resolution.strftime('%Y-%m-%d') if date_resolution else None,
                    'Responsable': responsable,
                    'Actions_Prises': actions_prises,
                    'Nb_Documents': len(file_paths),
                    'Documents': ';'.join(file_paths)  # Stocker les chemins séparés par ;
                }])
                if st.session_state.anomalies.empty:
                    st.session_state.anomalies = new_anomalie
                else:
                    st.session_state.anomalies = pd.concat([st.session_state.anomalies, new_anomalie],
                                                           ignore_index=True)
                st.success("✅ Anomalie enregistrée avec succès!")
                st.balloons()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab2:
        st.markdown("#### Liste et suivi des anomalies")
        
        if not st.session_state.anomalies.empty:
            # Filtres
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                filtre_type = st.multiselect("Type",
                    options=st.session_state.anomalies['Type'].unique().tolist(),
                    default=st.session_state.anomalies['Type'].unique().tolist())
            with col2:
                filtre_priorite = st.multiselect("Priorité",
                    options=st.session_state.anomalies['Priorité'].unique().tolist(),
                    default=st.session_state.anomalies['Priorité'].unique().tolist())
            with col3:
                filtre_statut = st.multiselect("Statut",
                    options=st.session_state.anomalies['Statut'].unique().tolist(),
                    default=st.session_state.anomalies['Statut'].unique().tolist())
            with col4:
                tri = st.selectbox("Trier par", ["Date (récent)", "Date (ancien)", "Priorité"])
            
            # Application des filtres
            df_filtre = st.session_state.anomalies[
                (st.session_state.anomalies['Type'].isin(filtre_type)) &
                (st.session_state.anomalies['Priorité'].isin(filtre_priorite)) &
                (st.session_state.anomalies['Statut'].isin(filtre_statut))
            ]
            
            # Tri
            if tri == "Date (récent)":
                df_filtre = df_filtre.sort_values('Date_Signalement', ascending=False)
            elif tri == "Date (ancien)":
                df_filtre = df_filtre.sort_values('Date_Signalement', ascending=True)
            elif tri == "Priorité":
                priority_order = {"Critique": 4, "Haute": 3, "Moyenne": 2, "Basse": 1}
                df_filtre['Priority_Rank'] = df_filtre['Priorité'].map(priority_order)
                df_filtre = df_filtre.sort_values('Priority_Rank', ascending=False)
                df_filtre = df_filtre.drop('Priority_Rank', axis=1)
            
            st.dataframe(df_filtre, width='stretch', height=400)
            
            # Actions sur les éléments
            st.markdown("### 🛠️ Actions sur les anomalies")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Ajouter une anomalie", width='stretch'):
                    st.session_state.edit_mode = "add_anomalie"
                    st.session_state.edit_index = None
                    st.rerun()
            
            with col2:
                # Sélectionner une anomalie à modifier
                if not df_filtre.empty:
                    selected_anomalie = st.selectbox(
                        "Sélectionner une anomalie à modifier",
                        options=[f"{row['Date_Signalement']} - {row['Type']} ({row['Priorité']})" 
                                for idx, row in df_filtre.iterrows()],
                        key="anomalie_select"
                    )
                    if st.button("✏️ Modifier", width='stretch'):
                        # Trouver l'index dans le dataframe original
                        selected_date = selected_anomalie.split(" - ")[0]
                        selected_type = selected_anomalie.split(" - ")[1].split(" (")[0]
                        original_index = st.session_state.anomalies[
                            (st.session_state.anomalies['Date_Signalement'] == selected_date) &
                            (st.session_state.anomalies['Type'] == selected_type)
                        ].index[0]
                        st.session_state.edit_mode = "edit_anomalie"
                        st.session_state.edit_index = original_index
                        st.rerun()
            
            with col3:
                # Sélectionner une anomalie à supprimer
                if not df_filtre.empty:
                    anomalie_to_delete = st.selectbox(
                        "Sélectionner une anomalie à supprimer",
                        options=[f"{row['Date_Signalement']} - {row['Type']} ({row['Priorité']})" 
                                for idx, row in df_filtre.iterrows()],
                        key="anomalie_delete"
                    )
                    if st.button("🗑️ Supprimer", width='stretch', type="primary"):
                        selected_date = anomalie_to_delete.split(" - ")[0]
                        selected_type = anomalie_to_delete.split(" - ")[1].split(" (")[0]
                        st.session_state.anomalies = st.session_state.anomalies[
                            ~((st.session_state.anomalies['Date_Signalement'] == selected_date) &
                              (st.session_state.anomalies['Type'] == selected_type))
                        ].reset_index(drop=True)
                        st.success("✅ Anomalie supprimée avec succès!")
                        # save_data_to_sqlite()  # Retiré
                        st.rerun()
            
            # Export
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df_filtre.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exporter CSV", csv, "anomalies.csv",
                                 "text/csv", width='stretch')
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_filtre.to_excel(writer, index=False, sheet_name='Anomalies')
                excel_data = excel_buffer.getvalue()
                st.download_button("📥 Exporter Excel", excel_data, "anomalies.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 width='stretch')
            with col3:
                pdf_data = generate_pdf_bytes(df_filtre, "Anomalies et Réclamations")
                st.download_button("📄 Exporter PDF", pdf_data, "anomalies.pdf", 
                                 "application/pdf", width='stretch')
        else:
            st.success("📝 Aucune anomalie enregistrée pour le moment.")
    
    with tab3:
        if not st.session_state.anomalies.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Répartition par statut")
                statut_counts = st.session_state.anomalies['Statut'].value_counts()
                fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                           hole=0.3, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Répartition par priorité")
                priorite_counts = st.session_state.anomalies['Priorité'].value_counts()
                colors = {'Basse': '#90EE90', 'Moyenne': '#FFD700', 
                         'Haute': '#FFA500', 'Critique': '#FF6347'}
                fig = go.Figure(data=[go.Bar(
                    x=priorite_counts.index,
                    y=priorite_counts.values,
                    marker_color=[colors.get(x, '#808080') for x in priorite_counts.index]
                )])
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, width='stretch')
            
            # Ajouter plus de graphiques
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Répartition par type d'anomalie")
                type_counts = st.session_state.anomalies['Type'].value_counts()
                fig = px.bar(x=type_counts.index, y=type_counts.values,
                           labels={'x': 'Type d\'anomalie', 'y': 'Nombre'},
                           title="Types d'anomalies",
                           color=type_counts.values,
                           color_continuous_scale='Reds')
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Évolution temporelle")
                anomalies_temp = st.session_state.anomalies.copy()
                anomalies_temp['Date_Signalement'] = pd.to_datetime(anomalies_temp['Date_Signalement'], errors='coerce')
                # Créer la colonne Mois en utilisant une approche compatible avec Pylance
                anomalies_temp['Mois'] = anomalies_temp['Date_Signalement'].dt.to_period('M')  # type: ignore
                anomalies_mensuelles = anomalies_temp.groupby('Mois').size()
                
                fig = px.line(x=anomalies_mensuelles.index.astype(str), y=anomalies_mensuelles.values,
                             labels={'x': 'Mois', 'y': 'Nombre d\'anomalies'},
                             title="Évolution des signalements",
                             markers=True)
                st.plotly_chart(fig, width='stretch')
            
            # Analyse par véhicule concerné
            st.markdown("#### Top véhicules avec anomalies")
            vehicule_counts = st.session_state.anomalies['Véhicule_Concerné'].value_counts().head(10)
            fig = px.bar(x=vehicule_counts.index, y=vehicule_counts.values,
                        labels={'x': 'Véhicule', 'y': 'Nombre d\'anomalies'},
                        title="Véhicules les plus concernés",
                        color=vehicule_counts.values,
                        color_continuous_scale='Oranges')
            st.plotly_chart(fig, width='stretch')
            
            # Matrice de corrélation priorité/statut
            st.markdown("#### Analyse priorité vs statut")
            priority_status = pd.crosstab(st.session_state.anomalies['Priorité'], st.session_state.anomalies['Statut'])
            fig = px.imshow(priority_status, 
                           labels=dict(x="Statut", y="Priorité", color="Nombre"),
                           title="Matrice priorité/statut",
                           color_continuous_scale='Viridis')
            st.plotly_chart(fig, width='stretch')
            
            # Métriques clés
            col1, col2, col3 = st.columns(3)
            with col1:
                taux_resolution = len(st.session_state.anomalies[
                    st.session_state.anomalies['Statut'].isin(['Résolue', 'Fermée'])
                ]) / len(st.session_state.anomalies) * 100
                st.metric("Taux de résolution", f"{taux_resolution:.1f}%")
            with col2:
                critiques = len(st.session_state.anomalies[
                    st.session_state.anomalies['Priorité'] == 'Critique'
                ])
                st.metric("Anomalies critiques", critiques)
            with col3:
                en_cours = len(st.session_state.anomalies[
                    st.session_state.anomalies['Statut'] == 'En cours'
                ])
                st.metric("En cours de traitement", en_cours)
        else:
            st.info("📊 Aucune donnée disponible pour l'analyse.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Fonction pour mettre à jour automatiquement les statuts des habilitations
def update_habilitations_status():
    """Met à jour automatiquement le statut des habilitations en fonction des dates d'expiration"""
    if not st.session_state.habilitations.empty and 'Date_Expiration' in st.session_state.habilitations.columns:
        try:
            today = datetime.now().date()
            
            for idx, row in st.session_state.habilitations.iterrows():
                try:
                    expiration_date = pd.to_datetime(row['Date_Expiration']).date()
                    jours_restants = (expiration_date - today).days
                    
                    if jours_restants < 0:
                        new_statut = "Expirée"
                    elif jours_restants <= 30:
                        new_statut = "À renouveler"
                    else:
                        new_statut = "Valide"
                    
                    # Mettre à jour le statut seulement s'il a changé
                    if st.session_state.habilitations.at[idx, 'Statut'] != new_statut:
                        st.session_state.habilitations.at[idx, 'Statut'] = new_statut
                    
                    # Mettre à jour les jours restants
                    st.session_state.habilitations.at[idx, 'Jours_Restants'] = jours_restants
                        
                except (ValueError, TypeError):
                    # Si la date n'est pas valide, marquer comme expirée
                    st.session_state.habilitations.at[idx, 'Statut'] = "Expirée"
                    st.session_state.habilitations.at[idx, 'Jours_Restants'] = -999  # Indicateur d'erreur
                    continue
                    
        except Exception as e:
            print(f"Erreur lors de la mise à jour des statuts d'habilitations: {str(e)}")

# Module Vérification des Habilitations
def verification_habilitations():
    # Mettre à jour les statuts des habilitations
    update_habilitations_status()
    
    st.markdown("### 🎓 Vérification des Habilitations")
    st.markdown('<div class="form-container">', unsafe_allow_html=True)
    
    # Gestion du mode édition
    if 'edit_mode' in st.session_state and st.session_state.edit_mode in ['add_habilitation', 'edit_habilitation']:
        st.markdown("### ✏️ Mode Édition - Habilitations")
        
        if st.session_state.edit_mode == 'edit_habilitation' and st.session_state.edit_index is not None:
            # Pré-remplir avec les données existantes
            hab_data = st.session_state.habilitations.iloc[st.session_state.edit_index]
            st.markdown(f"**Modification de l'habilitation:** {hab_data['Employé']} - {hab_data['Type_Habilitation']}")
            
            col1, col2 = st.columns(2)
            with col1:
                employe = st.text_input("Nom de l'employé *", value=hab_data['Employé'])
                type_habilitation = st.selectbox("Type d'habilitation *",
                    ["CACES", "SST", "Habilitation électrique", "Travail en hauteur", "Conduite VL", "Conduite PL", "Autre"],
                    index=["CACES", "SST", "Habilitation électrique", "Travail en hauteur", "Conduite VL", "Conduite PL", "Autre"].index(hab_data['Type_Habilitation']))
                numero = st.text_input("Numéro d'habilitation", value=hab_data['Numéro'])
                organisme = st.text_input("Organisme délivrant *", value=hab_data['Organisme'])
            
            with col2:
                date_obtention = st.date_input("Date d'obtention", value=pd.to_datetime(hab_data['Date_Obtention']))
                date_expiration = st.date_input("Date d'expiration *", value=pd.to_datetime(hab_data['Date_Expiration']))
                statut = st.selectbox("Statut",
                    ["Valide", "Expirée", "En cours de renouvellement", "Suspendue"],
                    index=["Valide", "Expirée", "En cours de renouvellement", "Suspendue"].index(hab_data['Statut']))
                verificateur = st.text_input("Vérifié par", value=hab_data['Vérifié_Par'])
            
            date_verification = st.date_input("Date de vérification", 
                value=pd.to_datetime(hab_data['Date_Vérification']) if pd.notna(hab_data['Date_Vérification']) else datetime.now())
            
        else:
            # Mode ajout
            col1, col2 = st.columns(2)
            with col1:
                employe = st.text_input("Nom de l'employé *", placeholder="Prénom NOM")
                type_habilitation = st.selectbox("Type d'habilitation *",
                    ["CACES", "SST", "Habilitation électrique", "Travail en hauteur", "Conduite VL", "Conduite PL", "Autre"])
                numero = st.text_input("Numéro d'habilitation", placeholder="N° d'habilitation")
                organisme = st.text_input("Organisme délivrant *", placeholder="Organisme officiel")
            
            with col2:
                date_obtention = st.date_input("Date d'obtention")
                date_expiration = st.date_input("Date d'expiration *")
                statut = st.selectbox("Statut",
                    ["Valide", "Expirée", "En cours de renouvellement", "Suspendue"])
                verificateur = st.text_input("Vérifié par", value="Madame AZIZET")
            
            date_verification = st.date_input("Date de vérification", datetime.now())
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("💾 Sauvegarder", width='stretch'):
                if employe and type_habilitation and organisme and date_expiration:
                    hab_dict = {
                        'Employé': employe,
                        'Type_Habilitation': type_habilitation,
                        'Numéro': numero,
                        'Date_Obtention': date_obtention.strftime('%Y-%m-%d'),
                        'Date_Expiration': date_expiration.strftime('%Y-%m-%d'),
                        'Organisme': organisme,
                        'Statut': statut,
                        'Vérifié_Par': verificateur,
                        'Date_Vérification': date_verification.strftime('%Y-%m-%d')
                    }
                    
                    if st.session_state.edit_mode == 'edit_habilitation':
                        old_hab = st.session_state.habilitations.iloc[st.session_state.edit_index].copy()
                        for key, value in hab_dict.items():
                            st.session_state.habilitations.at[st.session_state.edit_index, key] = value
                        # Enregistrer dans les logs d'audit
                        log_action("MODIFICATION", "habilitation", hab_dict['Employé'], 
                                  f"Modifiée: {old_hab['Employé']} - {old_hab['Type_Habilitation']} → {hab_dict['Type_Habilitation']}")
                        st.success("✅ Habilitation modifiée avec succès!")
                        # save_data_to_sqlite()  # Retiré
                        img_bytes, img_url = generate_habilitation_image(hab_dict)
                        if img_url:
                            st.image(img_url, caption="Certificat d'habilitation")
                            st.success(f"✅ Image uploadée vers Cloudinary: {img_url}")
                        else:
                            st.image(img_bytes, caption="Certificat d'habilitation")
                            st.warning("⚠️ Upload Cloudinary échoué, image affichée localement")
                    else:
                        new_hab = pd.DataFrame([hab_dict])
                        if st.session_state.habilitations.empty:
                            st.session_state.habilitations = new_hab
                        else:
                            st.session_state.habilitations = pd.concat([st.session_state.habilitations, new_hab], 
                                                                     ignore_index=True)
                        # Enregistrer dans les logs d'audit
                        log_action("AJOUT", "habilitation", hab_dict['Employé'], 
                                  f"Habilitation ajoutée - {hab_dict['Employé']} - {hab_dict['Type_Habilitation']} - Expire: {hab_dict['Date_Expiration']}")
                        st.success("✅ Habilitation ajoutée avec succès!")
                        st.balloons()
                        # save_data_to_sqlite()  # Retiré, utilisation de Cloudinary pour les images uniquement
                        st.success("✅ Données sauvegardées (session)")
                        img_bytes, img_url = generate_habilitation_image(hab_dict)
                        if img_url:
                            st.image(img_url, caption="Certificat d'habilitation")
                            st.success(f"✅ Image uploadée vers Cloudinary: {img_url}")
                        else:
                            st.image(img_bytes, caption="Certificat d'habilitation")
                            st.warning("⚠️ Upload Cloudinary échoué, image affichée localement")
                    
                    del st.session_state.edit_mode
                    if 'edit_index' in st.session_state:
                        del st.session_state.edit_index
                    st.rerun()
                else:
                    st.error("❌ Veuillez remplir les champs obligatoires (*)")
        
        with col2:
            if st.button("🔄 Annuler", width='stretch'):
                del st.session_state.edit_mode
                if 'edit_index' in st.session_state:
                    del st.session_state.edit_index
                st.rerun()
        
        with col3:
            if st.session_state.edit_mode == 'edit_habilitation' and st.button("🗑️ Supprimer cette habilitation", 
                width='stretch', type="primary"):
                # Récupérer les infos avant suppression pour le log
                hab_to_delete = st.session_state.habilitations.iloc[st.session_state.edit_index]
                hab_info = f"{hab_to_delete['Employé']} - {hab_to_delete['Type_Habilitation']} - Expire: {hab_to_delete['Date_Expiration']}"
                
                # Ajouter à la corbeille au lieu de supprimer
                hab_data = hab_to_delete.to_dict()
                if add_to_corbeille('habilitation', hab_data):
                    st.session_state.habilitations = st.session_state.habilitations.drop(st.session_state.edit_index).reset_index(drop=True)
                    # Enregistrer dans les logs d'audit
                    log_action("SUPPRESSION", "habilitation", hab_to_delete['Employé'], 
                              f"Habilitation déplacée vers la corbeille: {hab_info}")
                    st.success("✅ Habilitation déplacée vers la corbeille!")
                    save_app_data()
                else:
                    st.error("❌ Erreur lors du déplacement vers la corbeille")
                del st.session_state.edit_mode
                del st.session_state.edit_index
                st.rerun()
                del st.session_state.edit_mode
                del st.session_state.edit_index
                st.rerun()
        
        st.markdown("---")
    
    tab1, tab2, tab3 = st.tabs(["➕ Ajouter une habilitation", "📋 Registre des habilitations", "⏰ Alertes d'expiration"])
    
    with tab1:
        st.markdown("#### Enregistrer une nouvelle habilitation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            employe = st.text_input("Nom de l'employé *", placeholder="Prénom NOM")
            type_habilitation = st.selectbox("Type d'habilitation *",
                ["Permis de conduire", "CACES", "Habilitation électrique",
                 "Formation sécurité", "Autorisation de conduite",
                 "Certificat professionnel", "Autre"])
            numero = st.text_input("Numéro d'habilitation *", placeholder="Ex: B123456")
            date_obtention = st.date_input("Date d'obtention", datetime.now())
        
        with col2:
            date_expiration = st.date_input("Date d'expiration",
                datetime.now() + timedelta(days=365*3))
            organisme = st.text_input("Organisme délivrant", placeholder="Nom de l'organisme")
            verificateur = st.text_input("Vérifié par *", value="Madame AZIZET")
            date_verification = st.date_input("Date de vérification", datetime.now())
        
        # Calcul automatique du statut
        jours_restants = (date_expiration - datetime.now().date()).days
        if jours_restants < 0:
            statut_hab = "Expirée"
            badge_class = "status-danger"
        elif jours_restants <= 30:
            statut_hab = "À renouveler"
            badge_class = "status-warning"
        else:
            statut_hab = "Valide"
            badge_class = "status-ok"
        
        st.markdown(f"**Statut:** <span class='status-badge {badge_class}'>{statut_hab}</span> ({jours_restants} jours restants)",
                   unsafe_allow_html=True)
        
        document_joint = st.file_uploader("Joindre le document (PDF, image)",
            type=['pdf', 'jpg', 'jpeg', 'png'])
        
        observations = st.text_area("Observations", placeholder="Notes complémentaires...")
        
        if st.button("✅ Enregistrer l'habilitation", width='stretch'):
            if employe and type_habilitation and numero and verificateur:
                new_habilitation = pd.DataFrame([{
                    'Employé': employe,
                    'Type_Habilitation': type_habilitation,
                    'Numéro': numero,
                    'Date_Obtention': date_obtention.strftime('%Y-%m-%d'),
                    'Date_Expiration': date_expiration.strftime('%Y-%m-%d'),
                    'Organisme': organisme,
                    'Statut': statut_hab,
                    'Vérifié_Par': verificateur,
                    'Date_Vérification': date_verification.strftime('%Y-%m-%d'),
                    'Jours_Restants': jours_restants,
                    'Observations': observations
                }])
                if st.session_state.habilitations.empty:
                    st.session_state.habilitations = new_habilitation
                else:
                    st.session_state.habilitations = pd.concat([st.session_state.habilitations, new_habilitation],
                                                               ignore_index=True)
                st.success("✅ Habilitation enregistrée avec succès!")
                st.balloons()
            else:
                st.error("❌ Veuillez remplir tous les champs obligatoires (*)")
    
    with tab2:
        st.markdown("#### Registre complet des habilitations")
        
        if not st.session_state.habilitations.empty:
            # Filtres
            col1, col2, col3 = st.columns(3)
            with col1:
                filtre_type = st.multiselect("Type d'habilitation",
                    options=st.session_state.habilitations['Type_Habilitation'].unique().tolist(),
                    default=st.session_state.habilitations['Type_Habilitation'].unique().tolist())
            with col2:
                filtre_statut = st.multiselect("Statut",
                    options=st.session_state.habilitations['Statut'].unique().tolist(),
                    default=st.session_state.habilitations['Statut'].unique().tolist())
            with col3:
                recherche_employe = st.text_input("🔍 Rechercher un employé")
            
            # Application des filtres
            df_filtre = st.session_state.habilitations[
                (st.session_state.habilitations['Type_Habilitation'].isin(filtre_type)) &
                (st.session_state.habilitations['Statut'].isin(filtre_statut))
            ]
            
            if recherche_employe:
                df_filtre = df_filtre[
                    df_filtre['Employé'].str.contains(recherche_employe, case=False, na=False)
                ]
            
            # Tri par date d'expiration
            if 'Date_Expiration' in df_filtre.columns:
                df_filtre = df_filtre.sort_values('Date_Expiration')
            
            st.dataframe(df_filtre, width='stretch', height=400)
            
            # Actions sur les éléments
            st.markdown("### 🛠️ Actions sur les habilitations")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ Ajouter une habilitation", width='stretch'):
                    st.session_state.edit_mode = "add_habilitation"
                    st.session_state.edit_index = None
                    st.rerun()
            
            with col2:
                # Sélectionner une habilitation à modifier
                if not df_filtre.empty:
                    selected_hab = st.selectbox(
                        "Sélectionner une habilitation à modifier",
                        options=[f"{row['Employé']} - {row['Type_Habilitation']} ({row['Statut']})" 
                                for idx, row in df_filtre.iterrows()],
                        key="hab_select"
                    )
                    if st.button("✏️ Modifier", width='stretch'):
                        # Trouver l'index dans le dataframe original
                        selected_employe = selected_hab.split(" - ")[0]
                        selected_type = selected_hab.split(" - ")[1].split(" (")[0]
                        original_index = st.session_state.habilitations[
                            (st.session_state.habilitations['Employé'] == selected_employe) &
                            (st.session_state.habilitations['Type_Habilitation'] == selected_type)
                        ].index[0]
                        st.session_state.edit_mode = "edit_habilitation"
                        st.session_state.edit_index = original_index
                        st.rerun()
            
            with col3:
                # Sélectionner une habilitation à supprimer
                if not df_filtre.empty:
                    hab_to_delete = st.selectbox(
                        "Sélectionner une habilitation à supprimer",
                        options=[f"{row['Employé']} - {row['Type_Habilitation']} ({row['Statut']})" 
                                for idx, row in df_filtre.iterrows()],
                        key="hab_delete"
                    )
                    if st.button("🗑️ Supprimer", width='stretch', type="primary"):
                        selected_employe = hab_to_delete.split(" - ")[0]
                        selected_type = hab_to_delete.split(" - ")[1].split(" (")[0]
                        st.session_state.habilitations = st.session_state.habilitations[
                            ~((st.session_state.habilitations['Employé'] == selected_employe) &
                              (st.session_state.habilitations['Type_Habilitation'] == selected_type))
                        ].reset_index(drop=True)
                        st.success("✅ Habilitation supprimée avec succès!")
                        # save_data_to_sqlite()  # Retiré
                        st.rerun()
            
            # Export
            col1, col2, col3 = st.columns(3)
            with col1:
                csv = df_filtre.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Exporter CSV", csv, "habilitations.csv",
                                 "text/csv", width='stretch')
            with col2:
                excel_buffer = io.BytesIO()
                with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                    df_filtre.to_excel(writer, index=False, sheet_name='Habilitations')
                excel_data = excel_buffer.getvalue()
                st.download_button("📥 Exporter Excel", excel_data, "habilitations.xlsx",
                                 "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 width='stretch')
            with col3:
                pdf_data = generate_pdf_bytes(df_filtre, "Habilitations et Certifications")
                st.download_button("📄 Exporter PDF", pdf_data, "habilitations.pdf", 
                                 "application/pdf", width='stretch')
        else:
            st.info("📝 Aucune habilitation enregistrée pour le moment.")
    
    with tab3:
        st.markdown("#### ⏰ Chronomètre des délais d'habilitation")
        
        # Bouton de rafraîchissement
        col_refresh, col_empty = st.columns([1, 4])
        with col_refresh:
            if st.button("🔄 Actualiser les chronomètres", help="Met à jour les compteurs de temps"):
                update_habilitations_status()
                st.success("✅ Chronomètres mis à jour!")
                st.rerun()
        
        if not st.session_state.habilitations.empty:
            # Chronomètre en temps réel pour les habilitations actives
            st.markdown("### 🕐 Compteurs de temps actifs")
            
            # Filtrer les habilitations non expirées
            actives = st.session_state.habilitations[
                st.session_state.habilitations['Statut'].isin(['Valide', 'À renouveler'])
            ]
            
            if not actives.empty:
                # Créer des colonnes pour afficher les chronomètres
                cols = st.columns(min(3, len(actives)))
                
                for i, (idx, hab) in enumerate(actives.iterrows()):
                    col_idx = i % 3
                    with cols[col_idx]:
                        jours_restants = hab.get('Jours_Restants', 0)
                        
                        # Calculer le temps restant en détail
                        date_exp = pd.to_datetime(hab['Date_Expiration'])
                        maintenant = datetime.now()
                        delta = date_exp - maintenant
                        
                        jours = delta.days
                        heures = delta.seconds // 3600
                        minutes = (delta.seconds % 3600) // 60
                        
                        # Déterminer la couleur selon l'urgence
                        if jours < 0:
                            couleur = "🔴"  # Expiré
                            bg_color = "#ffebee"
                            text_color = "#c62828"
                        elif jours <= 7:
                            couleur = "🔴"  # Critique
                            bg_color = "#ffebee"
                            text_color = "#c62828"
                        elif jours <= 30:
                            couleur = "🟠"  # Urgent
                            bg_color = "#fff3e0"
                            text_color = "#ef6c00"
                        elif jours <= 90:
                            couleur = "🟡"  # Attention
                            bg_color = "#fffde7"
                            text_color = "#f57f17"
                        else:
                            couleur = "🟢"  # OK
                            bg_color = "#e8f5e8"
                            text_color = "#2e7d32"
                        
                        # Calculer la progression (pour les 90 derniers jours)
                        if jours >= 0:
                            progression = max(0, min(100, ((90 - jours) / 90) * 100))
                        else:
                            progression = 100
                        
                        # Créer une barre de progression colorée
                        if jours < 0:
                            progress_color = "#d32f2f"  # Rouge
                        elif jours <= 7:
                            progress_color = "#d32f2f"  # Rouge
                        elif jours <= 30:
                            progress_color = "#f57c00"  # Orange
                        elif jours <= 90:
                            progress_color = "#fbc02d"  # Jaune
                        else:
                            progress_color = "#388e3c"  # Vert
                        
                        # Afficher la carte du chronomètre avec barre de progression
                        st.markdown(f"""
                        <div style="background-color: {bg_color}; padding: 15px; border-radius: 10px; border-left: 5px solid {text_color}; margin-bottom: 10px;">
                            <h4 style="color: {text_color}; margin: 0;">{couleur} {hab['Employé']}</h4>
                            <p style="margin: 5px 0; color: {text_color};">{hab['Type_Habilitation']}</p>
                            <div style="font-size: 24px; font-weight: bold; color: {text_color};">
                                {abs(jours)}j {heures}h {minutes}m
                            </div>
                            <small style="color: {text_color};">Expire le {hab['Date_Expiration']}</small>
                            <div style="margin-top: 10px;">
                                <div style="background-color: #e0e0e0; border-radius: 5px; height: 8px; width: 100%;">
                                    <div style="background-color: {progress_color}; height: 8px; border-radius: 5px; width: {progression}%;"></div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("⏰ Aucun chronomètre actif - toutes les habilitations sont expirées.")
            
            # Chronomètre d'urgence pour les 7 prochains jours
            st.markdown("### 🚨 Compteurs critiques (7 jours)")
            critiques = st.session_state.habilitations[
                (st.session_state.habilitations['Jours_Restants'] >= 0) & 
                (st.session_state.habilitations['Jours_Restants'] <= 7)
            ]
            
            if not critiques.empty:
                for idx, hab in critiques.iterrows():
                    date_exp = pd.to_datetime(hab['Date_Expiration'])
                    maintenant = datetime.now()
                    delta = date_exp - maintenant
                    
                    jours = delta.days
                    heures = delta.seconds // 3600
                    minutes = (delta.seconds % 3600) // 60
                    secondes = delta.seconds % 60
                    
                    # Affichage spécial pour les cas critiques
                    st.error(f"🚨 **{hab['Employé']} - {hab['Type_Habilitation']}**")
                    st.markdown(f"""
                    <div style="background-color: #ffebee; padding: 20px; border-radius: 10px; border-left: 5px solid #d32f2f; margin: 10px 0;">
                        <div style="font-size: 36px; font-weight: bold; color: #d32f2f; text-align: center;">
                            {jours:02d}:{heures:02d}:{minutes:02d}:{secondes:02d}
                        </div>
                        <p style="text-align: center; color: #d32f2f; margin: 10px 0;">
                            Expire dans {jours} jour(s), {heures} heure(s), {minutes} minute(s)
                        </p>
                        <small style="color: #d32f2f; text-align: center; display: block;">
                            Date exacte: {hab['Date_Expiration']}
                        </small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Alerte sonore simulée (visuelle)
                    st.warning("⚠️ **ACTION REQUISE** : Cette habilitation expire très bientôt!")
            else:
                st.success("✅ Aucune habilitation critique dans les 7 jours.")
        
        st.markdown("---")
        st.markdown("#### Alertes et renouvellements")
        
        if not st.session_state.habilitations.empty:
            # Habilitations expirées
            expirees = st.session_state.habilitations[
                st.session_state.habilitations['Statut'] == 'Expirée'
            ]
            
            if not expirees.empty:
                st.error(f"🚨 **{len(expirees)} habilitation(s) expirée(s)**")
                st.dataframe(expirees[['Employé', 'Type_Habilitation', 'Date_Expiration']],
                           width='stretch')
            
            # Habilitations à renouveler
            a_renouveler = st.session_state.habilitations[
                st.session_state.habilitations['Statut'] == 'À renouveler'
            ]
            
            if not a_renouveler.empty:
                st.warning(f"⚠️ **{len(a_renouveler)} habilitation(s) à renouveler dans les 30 jours**")
                st.dataframe(a_renouveler[['Employé', 'Type_Habilitation', 'Date_Expiration', 'Jours_Restants']],
                           width='stretch')
            
            if expirees.empty and a_renouveler.empty:
                st.success("✅ Toutes les habilitations sont à jour!")
            
            # Calendrier des expirations
            st.markdown("#### Calendrier des prochaines expirations")
            
            # Préparer les données pour le graphique
            if 'Date_Expiration' in st.session_state.habilitations.columns:
                hab_temp = st.session_state.habilitations.copy()
                hab_temp['Date_Expiration'] = pd.to_datetime(hab_temp['Date_Expiration'])
                hab_temp = hab_temp.sort_values('Date_Expiration')
                hab_temp = hab_temp.head(10)  # Top 10 prochaines expirations
                
                fig = px.timeline(hab_temp, x_start='Date_Vérification', x_end='Date_Expiration',
                                y='Employé', color='Type_Habilitation',
                                title="Prochaines 10 expirations")
                st.plotly_chart(fig, width='stretch')
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                valides = len(st.session_state.habilitations[
                    st.session_state.habilitations['Statut'] == 'Valide'
                ])
                st.metric("Habilitations valides", valides)
            with col2:
                st.metric("À renouveler", len(a_renouveler))
            with col3:
                st.metric("Expirées", len(expirees))
            
            # Ajouter plus de graphiques
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Répartition par statut")
                statut_counts = st.session_state.habilitations['Statut'].value_counts()
                fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                           title="Statuts des habilitations",
                           color_discrete_sequence=['green', 'orange', 'red'])
                st.plotly_chart(fig, width='stretch')
            
            with col2:
                st.markdown("#### Répartition par type")
                type_counts = st.session_state.habilitations['Type_Habilitation'].value_counts()
                fig = px.bar(x=type_counts.index, y=type_counts.values,
                           labels={'x': 'Type d\'habilitation', 'y': 'Nombre'},
                           title="Types d'habilitations",
                           color=type_counts.values,
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, width='stretch')
            
            # Graphique de distribution des jours restants
            st.markdown("#### Distribution des délais d'expiration")
            jours_data = st.session_state.habilitations['Jours_Restants'].value_counts().sort_index()
            fig = px.histogram(st.session_state.habilitations, x='Jours_Restants',
                             labels={'x': 'Jours restants', 'y': 'Nombre d\'habilitations'},
                             title="Distribution des délais d'expiration",
                             color_discrete_sequence=['lightcoral'])
            st.plotly_chart(fig, width='stretch')
            
            # Top employés par nombre d'habilitations
            st.markdown("#### Top employés")
            employe_counts = st.session_state.habilitations['Employé'].value_counts().head(10)
            fig = px.bar(x=employe_counts.index, y=employe_counts.values,
                        labels={'x': 'Employé', 'y': 'Nombre d\'habilitations'},
                        title="Top 10 employés par nombre d'habilitations",
                        color=employe_counts.values,
                        color_continuous_scale='Greens')
            st.plotly_chart(fig, width='stretch')
            
            # Évolution temporelle des délivrances
            st.markdown("#### Évolution des délivrances")
            hab_temp = st.session_state.habilitations.copy()
            hab_temp['Date_Obtention'] = pd.to_datetime(hab_temp['Date_Obtention'], errors='coerce')
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            hab_temp['Mois'] = hab_temp['Date_Obtention'].dt.to_period('M')  # type: ignore
            hab_mensuelles = hab_temp.groupby('Mois').size()
            
            fig = px.line(x=hab_mensuelles.index.astype(str), y=hab_mensuelles.values,
                         labels={'x': 'Mois', 'y': 'Nombre d\'habilitations délivrées'},
                         title="Évolution des délivrances d'habilitations",
                         markers=True)
            st.plotly_chart(fig, width='stretch')
        else:
            st.info("⏰ Aucune donnée d'habilitation disponible.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Sidebar
def display_sidebar():
    with st.sidebar:
        # Logo dans la sidebar
        st.image("LOGO VECTORISE PNG.png", width=200)
        st.markdown("---")
        
        # Indicateur de mode online/offline
        app_mode = get_app_mode()
        if app_mode == "offline":
            st.error("🔴 **MODE HORS LIGNE** - Certaines fonctionnalités sont limitées")
            st.warning("Cloudinary et services externes non disponibles")
        elif app_mode == "partial":
            st.warning("🟡 **MODE PARTIEL** - Backend indisponible")
            st.info("Internet disponible mais services limités (emails, OTP)")
        else:
            st.success("🟢 **MODE EN LIGNE** - Toutes les fonctionnalités disponibles")
        
        st.markdown("---")
        
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Choisissez un module:",
            ["📊 Tableau de Bord", "🚙 Inspection Véhicules", 
             "🛒 Suivi Achats", "⚠️ Anomalies & Réclamations",
             "🎓 Habilitations", "🗑️ Corbeille"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        st.markdown("### 💾 Gestion des données")
        
        # Sauvegarde dans SQLite
        if st.button("💾 Sauvegarder dans SQLite", width='stretch'):
            if save_app_data():
                st.success("✅ Données sauvegardées!")
            else:
                st.error("❌ Erreur lors de la sauvegarde")
        
        # Chargement depuis SQLite
        if st.button("📂 Charger depuis bases de données", width='stretch'):
            if load_app_data():
                st.success("✅ Données chargées!")
                st.rerun()
            else:
                st.error("❌ Erreur lors du chargement")
        
        # Synchronisation manuelle des données
        if st.button("🔄 Synchroniser les données", width='stretch'):
            with st.spinner("Synchronisation en cours..."):
                if sync_data_after_save():
                    st.success("✅ Données synchronisées!")
                    st.rerun()
                else:
                    st.error("❌ Échec de la synchronisation")
        
        st.markdown("---")
        
        # Sauvegarde/chargement JSON (optionnel)
        st.markdown("### 📄 Sauvegarde JSON (optionnel)")
        
        # Sauvegarde
        if st.button("💾 Préparer sauvegarde JSON", width='stretch'):
            data = save_data()
            json_data = json.dumps(data, indent=2, default=str)
            st.download_button(
                "📥 Télécharger la sauvegarde JSON",
                json_data,
                "sauvegarde_gestion.json",
                "application/json",
                width='stretch'
            )
            st.success("✅ Données JSON prêtes à être téléchargées!")
        
        # Chargement
        uploaded_file = st.file_uploader("📂 Charger une sauvegarde JSON", 
                                        type=['json'])
        if uploaded_file is not None:
            try:
                data = json.load(uploaded_file)
                load_data(data)
                st.success("✅ Données JSON chargées avec succès!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement JSON: {str(e)}")
        
        st.markdown("---")
        
        # Logs d'audit
        st.markdown("### 📋 Logs d'Audit")
        if st.button("📋 Voir les logs", width='stretch'):
            st.session_state.show_logs = not st.session_state.get('show_logs', False)
        
        if st.session_state.get('show_logs', False):
            display_audit_logs()
        
        st.markdown("---")
        
        # Statistiques rapides
        st.markdown("### 📈 Statistiques rapides")
        st.metric("Véhicules", len(st.session_state.vehicules))
        st.metric("Achats", len(st.session_state.achats))
        st.metric("Anomalies", len(st.session_state.anomalies))
        st.metric("Habilitations", len(st.session_state.habilitations))
        
        st.markdown("---")
        st.markdown("### ℹ️ À propos")
        st.info("""
        **Système de Gestion v2.0**
        
        Application complète pour la gestion de:
        - Inspection des véhicules
        - Suivi des achats
        - Anomalies et réclamations
        - Habilitations et certifications
        
        Développé avec Streamlit 🚀
        """)
        
        # Monitoring de la base de données
        st.markdown("---")
        display_database_monitoring()
        
        return page

# Fonction de gestion de la corbeille
def gestion_corbeille():
    st.markdown("## 🗑️ Corbeille")
    st.markdown("---")
    
    # Récupérer les éléments de la corbeille
    corbeille_items = get_corbeille_items()
    
    if not corbeille_items:
        st.info("🗑️ La corbeille est vide.")
        return
    
    st.markdown(f"### 📦 Éléments dans la corbeille: {len(corbeille_items)}")
    
    # Statistiques par type
    types_count = {}
    for item in corbeille_items:
        entity_type = item['entity_type']
        types_count[entity_type] = types_count.get(entity_type, 0) + 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Véhicules", types_count.get('véhicule', 0))
    with col2:
        st.metric("Achats", types_count.get('achat', 0))
    with col3:
        st.metric("Anomalies", types_count.get('anomalie', 0))
    with col4:
        st.metric("Habilitations", types_count.get('habilitation', 0))
    
    st.markdown("---")
    
    # Bouton pour vider la corbeille (avec validation OTP)
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🗑️ Vider la corbeille", type="secondary", use_container_width=True):
            st.session_state['empty_corbeille_confirm'] = True
            st.rerun()
    
    # Modal de confirmation pour vider la corbeille
    if 'empty_corbeille_confirm' in st.session_state and st.session_state['empty_corbeille_confirm']:
        with st.container():
            st.markdown("### 🔐 Confirmation de vidage")
            st.warning("⚠️ **ATTENTION**: Cette action est irréversible. Tous les éléments de la corbeille seront supprimés définitivement.")
            
            # Demander l'OTP pour confirmation
            otp_input = st.text_input("Entrez le code OTP envoyé à votre email pour confirmer:", 
                                    type="password", key="empty_corbeille_otp")
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button("📧 Envoyer OTP", use_container_width=True):
                    # Envoyer OTP pour confirmation
                    result = send_otp(st.session_state.get('user_email', 'admin@entreprise.com'), 'empty_corbeille')
                    if 'message' in result:
                        st.success("✅ Code OTP envoyé!")
                    else:
                        st.error(f"❌ Erreur envoi OTP: {result.get('error', 'Erreur inconnue')}")
            
            with col2:
                if st.button("✅ Confirmer", use_container_width=True):
                    if not otp_input:
                        st.error("❌ Veuillez entrer le code OTP")
                    else:
                        # Vérifier l'OTP
                        result = verify_otp(st.session_state.get('user_email', 'admin@entreprise.com'), otp_input)
                        if 'message' in result:
                            # Vider la corbeille
                            success, message = empty_corbeille()
                            if success:
                                st.success(f"✅ {message}")
                                del st.session_state['empty_corbeille_confirm']
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                        else:
                            st.error(f"❌ Code OTP invalide: {result.get('error', 'Erreur inconnue')}")
            
            with col3:
                if st.button("❌ Annuler", use_container_width=True):
                    del st.session_state['empty_corbeille_confirm']
                    st.rerun()
    
    st.markdown("---")
    
    # Afficher les éléments par type
    tabs = st.tabs(["🚙 Véhicules", "🛒 Achats", "⚠️ Anomalies", "🎓 Habilitations"])
    
    # Véhicules dans la corbeille
    with tabs[0]:
        vehicules_corbeille = [item for item in corbeille_items if item['entity_type'] == 'véhicule']
        if vehicules_corbeille:
            for item in vehicules_corbeille:
                data = item['entity_data']
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{data.get('Immatriculation', 'N/A')}** - {data.get('Marque', '')} {data.get('Modèle', '')}")
                        st.caption(f"Supprimé le: {item['deleted_at']} par {item['deleted_by']}")
                    with col2:
                        if st.button("🔄 Restaurer", key=f"restore_veh_{item['id']}", use_container_width=True):
                            success, message = restore_from_corbeille(item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    with col3:
                        st.caption("Véhicule")
        else:
            st.info("Aucun véhicule dans la corbeille.")
    
    # Achats dans la corbeille
    with tabs[1]:
        achats_corbeille = [item for item in corbeille_items if item['entity_type'] == 'achat']
        if achats_corbeille:
            for item in achats_corbeille:
                data = item['entity_data']
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{data.get('Article', 'N/A')}** - {data.get('Prix_Total', 0)}€ - {data.get('Fournisseur', '')}")
                        st.caption(f"Supprimé le: {item['deleted_at']} par {item['deleted_by']}")
                    with col2:
                        if st.button("🔄 Restaurer", key=f"restore_achat_{item['id']}", use_container_width=True):
                            success, message = restore_from_corbeille(item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    with col3:
                        st.caption("Achat")
        else:
            st.info("Aucun achat dans la corbeille.")
    
    # Anomalies dans la corbeille
    with tabs[2]:
        anomalies_corbeille = [item for item in corbeille_items if item['entity_type'] == 'anomalie']
        if anomalies_corbeille:
            for item in anomalies_corbeille:
                data = item['entity_data']
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{data.get('Type', 'N/A')}** - {data.get('Description', '')[:50]}...")
                        st.caption(f"Véhicule: {data.get('Véhicule_Concerné', 'N/A')} | Supprimé le: {item['deleted_at']} par {item['deleted_by']}")
                    with col2:
                        if st.button("🔄 Restaurer", key=f"restore_anomalie_{item['id']}", use_container_width=True):
                            success, message = restore_from_corbeille(item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    with col3:
                        st.caption("Anomalie")
        else:
            st.info("Aucune anomalie dans la corbeille.")
    
    # Habilitations dans la corbeille
    with tabs[3]:
        habilitations_corbeille = [item for item in corbeille_items if item['entity_type'] == 'habilitation']
        if habilitations_corbeille:
            for item in habilitations_corbeille:
                data = item['entity_data']
                with st.container():
                    col1, col2, col3 = st.columns([3, 1, 1])
                    with col1:
                        st.markdown(f"**{data.get('Employé', 'N/A')}** - {data.get('Type_Habilitation', '')}")
                        st.caption(f"Expire: {data.get('Date_Expiration', 'N/A')} | Supprimé le: {item['deleted_at']} par {item['deleted_by']}")
                    with col2:
                        if st.button("🔄 Restaurer", key=f"restore_hab_{item['id']}", use_container_width=True):
                            success, message = restore_from_corbeille(item['id'])
                            if success:
                                st.success(f"✅ {message}")
                                st.rerun()
                            else:
                                st.error(f"❌ {message}")
                    with col3:
                        st.caption("Habilitation")
        else:
            st.info("Aucune habilitation dans la corbeille.")

# Fonction de monitoring du système
def monitoring_systeme():
    st.markdown("## 📈 Monitoring du Système")
    st.markdown("---")
    
    # Métriques générales
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Véhicules", len(st.session_state.vehicules))
    with col2:
        st.metric("Achats", len(st.session_state.achats))
    with col3:
        st.metric("Anomalies", len(st.session_state.anomalies))
    with col4:
        st.metric("Habilitations", len(st.session_state.habilitations))
    with col5:
        corbeille_items = get_corbeille_items()
        st.metric("Corbeille", len(corbeille_items))
    
    st.markdown("---")
    
    # Onglets pour différentes vues
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📊 Vue d'ensemble", "🚙 Véhicules", "🛒 Achats", 
        "⚠️ Anomalies", "🎓 Habilitations", "💾 Base de données"
    ])
    
    with tab1:
        st.markdown("### 📊 Vue d'ensemble du système")
        
        # Graphique de répartition globale
        data_counts = {
            'Véhicules': len(st.session_state.vehicules),
            'Achats': len(st.session_state.achats),
            'Anomalies': len(st.session_state.anomalies),
            'Habilitations': len(st.session_state.habilitations),
            'Corbeille': len(corbeille_items)
        }
        
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = px.bar(x=list(data_counts.keys()), y=list(data_counts.values()),
                        labels={'x': 'Module', 'y': 'Nombre d\'enregistrements'},
                        color=list(data_counts.values()),
                        color_continuous_scale='Viridis',
                        title="Répartition des données par module")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(values=list(data_counts.values()), names=list(data_counts.keys()),
                        title="Proportion des données",
                        hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        
        # Métriques temporelles
        st.markdown("### 📅 Évolution temporelle")
        
        # Pour les véhicules (par date d'inspection)
        if not st.session_state.vehicules.empty:
            vehicules_par_mois = st.session_state.vehicules.copy()
            vehicules_par_mois['Date_Inspection'] = pd.to_datetime(vehicules_par_mois['Date_Inspection'])
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            vehicules_par_mois['Mois'] = vehicules_par_mois['Date_Inspection'].apply(lambda x: x.to_period('M') if pd.notna(x) else pd.NaT)
            vehicules_mensuels = vehicules_par_mois.groupby('Mois').size()
            
            fig = px.line(x=vehicules_mensuels.index.astype(str), y=vehicules_mensuels.values,
                         labels={'x': 'Mois', 'y': 'Nombre de véhicules inspectés'},
                         title="Évolution des inspections de véhicules")
            st.plotly_chart(fig, use_container_width=True)
        
        # Pour les achats (par date)
        if not st.session_state.achats.empty:
            achats_par_mois = st.session_state.achats.copy()
            achats_par_mois['Date'] = pd.to_datetime(achats_par_mois['Date'])
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            achats_par_mois['Mois'] = achats_par_mois['Date'].apply(lambda x: x.to_period('M') if pd.notna(x) else pd.NaT)
            achats_mensuels = achats_par_mois.groupby('Mois')['Prix_Total'].sum()
            
            fig = px.bar(x=achats_mensuels.index.astype(str), y=achats_mensuels.values,
                        labels={'x': 'Mois', 'y': 'Montant total (€)'},
                        title="Évolution des dépenses mensuelles",
                        color=achats_mensuels.values,
                        color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.markdown("### 🚙 Analyse détaillée des véhicules")
        
        if not st.session_state.vehicules.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par statut
                statut_counts = st.session_state.vehicules['Statut'].value_counts()
                fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                           title="Répartition par statut de conformité",
                           color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition par type de véhicule
                type_counts = st.session_state.vehicules['Type'].value_counts()
                fig = px.bar(x=type_counts.index, y=type_counts.values,
                           labels={'x': 'Type de véhicule', 'y': 'Nombre'},
                           title="Répartition par type de véhicule",
                           color=type_counts.values,
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            # État des équipements
            st.markdown("### 🔧 État des équipements de sécurité")
            equipements = ['Boîte_Pharmacie', 'Extincteur', 'Triangle_Panne', 'Cale']
            
            equip_data = []
            for eq in equipements:
                conformes = len(st.session_state.vehicules[st.session_state.vehicules[eq] == 'Conforme'])
                non_conformes = len(st.session_state.vehicules[st.session_state.vehicules[eq] == 'Non conforme'])
                absents = len(st.session_state.vehicules[st.session_state.vehicules[eq].isin(['Absent', 'Absente'])])
                
                equip_data.append({
                    'Équipement': eq.replace('_', ' '),
                    'Conformes': conformes,
                    'Non conformes': non_conformes,
                    'Absents': absents
                })
            
            df_equip = pd.DataFrame(equip_data)
            fig = px.bar(df_equip, x='Équipement', y=['Conformes', 'Non conformes', 'Absents'],
                        title="État des équipements de sécurité",
                        barmode='stack',
                        color_discrete_sequence=['green', 'orange', 'red'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Propreté des véhicules
            st.markdown("### 🧹 État de propreté")
            if 'Etat_Propreté' in st.session_state.vehicules.columns:
                proprete_counts = st.session_state.vehicules['Etat_Propreté'].value_counts()
                fig = px.bar(x=proprete_counts.index, y=proprete_counts.values,
                            labels={'x': 'État de propreté', 'y': 'Nombre de véhicules'},
                            title="Répartition par état de propreté",
                            color=proprete_counts.values,
                            color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("⚠️ Colonne 'Etat_Propreté' non trouvée dans les données des véhicules")
        else:
            st.info("Aucune donnée de véhicule disponible.")
    
    with tab3:
        st.markdown("### 🛒 Analyse détaillée des achats")
        
        if not st.session_state.achats.empty:
            # Analyse temporelle des achats
            achats_temp = st.session_state.achats.copy()
            achats_temp['Date'] = pd.to_datetime(achats_temp['Date'])
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            achats_temp['Mois'] = achats_temp['Date'].apply(lambda x: x.to_period('M') if pd.notna(x) else pd.NaT)
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Évolution des achats par mois
                achats_mensuels = achats_temp.groupby('Mois').size()
                fig = px.line(x=achats_mensuels.index.astype(str), y=achats_mensuels.values,
                             labels={'x': 'Mois', 'y': 'Nombre d\'achats'},
                             title="Évolution du nombre d'achats")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Évolution des dépenses par mois
                depenses_mensuelles = achats_temp.groupby('Mois')['Prix_Total'].sum()
                fig = px.bar(x=depenses_mensuelles.index.astype(str), y=depenses_mensuelles.values,
                            labels={'x': 'Mois', 'y': 'Montant total (€)'},
                            title="Évolution des dépenses mensuelles",
                            color=depenses_mensuelles.values,
                            color_continuous_scale='Oranges')
                st.plotly_chart(fig, use_container_width=True)
            
            # Analyse par catégorie
            st.markdown("### 📂 Répartition par catégorie")
            categorie_counts = st.session_state.achats['Catégorie'].value_counts()
            fig = px.pie(values=categorie_counts.values, names=categorie_counts.index,
                        title="Répartition des achats par catégorie",
                        hole=0.3)
            st.plotly_chart(fig, use_container_width=True)
            
            # Top fournisseurs
            st.markdown("### 🏢 Top 10 fournisseurs")
            fournisseur_totals = st.session_state.achats.groupby('Fournisseur')['Prix_Total'].sum().sort_values(ascending=False).head(10)
            fig = px.bar(x=fournisseur_totals.index, y=fournisseur_totals.values,
                        labels={'x': 'Fournisseur', 'y': 'Montant total (€)'},
                        title="Top 10 fournisseurs par montant",
                        color=fournisseur_totals.values,
                        color_continuous_scale='Purples')
            st.plotly_chart(fig, use_container_width=True)
            
            # Analyse par devise
            st.markdown("### 💱 Répartition par devise")
            devise_counts = st.session_state.achats['Devise'].value_counts()
            devise_montants = st.session_state.achats.groupby('Devise')['Prix_Total'].sum()
            
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(values=devise_counts.values, names=devise_counts.index,
                            title="Nombre d'achats par devise")
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(x=devise_montants.index, y=devise_montants.values,
                            labels={'x': 'Devise', 'y': 'Montant total'},
                            title="Montants totaux par devise",
                            color=devise_montants.values,
                            color_continuous_scale='Teal')
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée d'achat disponible.")
    
    with tab4:
        st.markdown("### ⚠️ Analyse détaillée des anomalies")
        
        if not st.session_state.anomalies.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par statut
                statut_counts = st.session_state.anomalies['Statut'].value_counts()
                fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                           title="Répartition des anomalies par statut",
                           color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition par priorité
                priorite_counts = st.session_state.anomalies['Priorité'].value_counts()
                priorite_df = priorite_counts.reset_index()
                priorite_df.columns = ['Priorité', 'Nombre']
                fig = px.bar(priorite_df, x='Priorité', y='Nombre',
                           title="Répartition par priorité",
                           color='Priorité',
                           color_discrete_map={'Critique': 'red', 'Moyenne': 'orange', 'Faible': 'green'})
                st.plotly_chart(fig, use_container_width=True)
            
            # Évolution temporelle des anomalies
            st.markdown("### 📅 Évolution des anomalies")
            anomalies_temp = st.session_state.anomalies.copy()
            anomalies_temp['Date_Signalement'] = pd.to_datetime(anomalies_temp['Date_Signalement'], errors='coerce')
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            anomalies_temp['Mois'] = anomalies_temp['Date_Signalement'].dt.to_period('M')  # type: ignore
            
            anomalies_mensuelles = anomalies_temp.groupby('Mois').size()
            fig = px.line(x=anomalies_mensuelles.index.astype(str), y=anomalies_mensuelles.values,
                         labels={'x': 'Mois', 'y': 'Nombre d\'anomalies'},
                         title="Évolution du nombre d'anomalies signalées")
            st.plotly_chart(fig, use_container_width=True)
            
            # Répartition par type
            st.markdown("### 📋 Répartition par type d'anomalie")
            type_counts = st.session_state.anomalies['Type'].value_counts()
            fig = px.bar(x=type_counts.index, y=type_counts.values,
                        labels={'x': 'Type d\'anomalie', 'y': 'Nombre'},
                        title="Types d'anomalies les plus fréquents",
                        color=type_counts.values,
                        color_continuous_scale='Reds')
            st.plotly_chart(fig, use_container_width=True)
            
            # Délais de résolution
            if 'Date_Résolution' in st.session_state.anomalies.columns:
                st.markdown("### ⏱️ Analyse des délais de résolution")
                anomalies_resolues = st.session_state.anomalies.dropna(subset=['Date_Résolution'])
                if not anomalies_resolues.empty:
                    anomalies_resolues['Date_Signalement'] = pd.to_datetime(anomalies_resolues['Date_Signalement'])
                    anomalies_resolues['Date_Résolution'] = pd.to_datetime(anomalies_resolues['Date_Résolution'])
                    anomalies_resolues['Délai_Résolution'] = (anomalies_resolues['Date_Résolution'] - anomalies_resolues['Date_Signalement']).dt.days
                    
                    fig = px.histogram(anomalies_resolues, x='Délai_Résolution',
                                     labels={'x': 'Délai (jours)', 'y': 'Nombre d\'anomalies'},
                                     title="Distribution des délais de résolution")
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée d'anomalie disponible.")
    
    with tab5:
        st.markdown("### 🎓 Analyse détaillée des habilitations")
        
        if not st.session_state.habilitations.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Répartition par statut
                statut_counts = st.session_state.habilitations['Statut'].value_counts()
                fig = px.pie(values=statut_counts.values, names=statut_counts.index,
                           title="Répartition des habilitations par statut",
                           color_discrete_sequence=['green', 'red', 'orange'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Répartition par type d'habilitation
                type_counts = st.session_state.habilitations['Type_Habilitation'].value_counts()
                fig = px.bar(x=type_counts.index, y=type_counts.values,
                           labels={'x': 'Type d\'habilitation', 'y': 'Nombre'},
                           title="Répartition par type d'habilitation",
                           color=type_counts.values,
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            # Alertes d'expiration
            st.markdown("### ⏰ Alertes d'expiration")
            today = pd.Timestamp.now()
            habilitations_temp = st.session_state.habilitations.copy()
            habilitations_temp['Date_Expiration'] = pd.to_datetime(habilitations_temp['Date_Expiration'])
            habilitations_temp['Jours_Restants'] = (habilitations_temp['Date_Expiration'] - today).dt.days
            
            # Catégorisation des alertes
            conditions = [
                (habilitations_temp['Jours_Restants'] < 0),
                (habilitations_temp['Jours_Restants'] <= 30),
                (habilitations_temp['Jours_Restants'] <= 90)
            ]
            choices = ['Expiré', 'Critique (≤30 jours)', 'Attention (≤90 jours)']
            habilitations_temp['Niveau_alerte'] = pd.cut(habilitations_temp['Jours_Restants'], 
                                                       bins=[-float('inf'), 0, 30, 90, float('inf')],
                                                       labels=['Expiré', 'Critique', 'Attention', 'OK'])
            
            alertes_counts = habilitations_temp['Niveau_alerte'].value_counts()
            fig = px.bar(x=alertes_counts.index, y=alertes_counts.values,
                        labels={'x': 'Niveau d\'alerte', 'y': 'Nombre d\'habilitations'},
                        title="Répartition des alertes d'expiration",
                        color=['red', 'orange', 'yellow', 'green'],
                        color_discrete_map={'Expiré': 'red', 'Critique': 'orange', 'Attention': 'yellow', 'OK': 'green'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Évolution temporelle des habilitations
            st.markdown("### 📅 Évolution des habilitations")
            hab_temp = st.session_state.habilitations.copy()
            hab_temp['Date_Obtention'] = pd.to_datetime(hab_temp['Date_Obtention'])
            # Créer la colonne Mois en utilisant une approche compatible avec Pylance
            hab_temp['Mois'] = hab_temp['Date_Obtention'].apply(lambda x: x.to_period('M') if pd.notna(x) else pd.NaT)
            
            hab_mensuelles = hab_temp.groupby('Mois').size()
            fig = px.line(x=hab_mensuelles.index.astype(str), y=hab_mensuelles.values,
                         labels={'x': 'Mois', 'y': 'Nombre d\'habilitations délivrées'},
                         title="Évolution des habilitations délivrées")
            st.plotly_chart(fig, use_container_width=True)
            
            # Top employés par nombre d'habilitations
            st.markdown("### 👥 Top employés")
            employe_counts = st.session_state.habilitations['Employé'].value_counts().head(10)
            fig = px.bar(x=employe_counts.index, y=employe_counts.values,
                        labels={'x': 'Employé', 'y': 'Nombre d\'habilitations'},
                        title="Top 10 employés par nombre d'habilitations",
                        color=employe_counts.values,
                        color_continuous_scale='Greens')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Aucune donnée d'habilitation disponible.")

# Fonction de monitoring de la base de données
def get_database_info():
    """Récupère les informations sur la base de données"""
    try:
        # Taille du fichier de base de données
        db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
        db_size_mb = db_size / (1024 * 1024)
        
        # Informations sur les tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Compter les enregistrements par table
        tables_info = {}
        tables = ['app_data', 'audit_logs', 'corbeille']
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                result = cursor.fetchone()
                count = result[0] if result else 0
                tables_info[table] = count
            except:
                tables_info[table] = 0
        
        # Informations sur les logs d'audit
        cursor.execute('SELECT COUNT(*), MAX(timestamp) FROM audit_logs')
        audit_info = cursor.fetchone()
        audit_count = audit_info[0] if audit_info[0] else 0
        last_audit = audit_info[1] if audit_info[1] else "Aucun"
        
        conn.close()
        
        return {
            'db_size_mb': db_size_mb,
            'tables_info': tables_info,
            'audit_count': audit_count,
            'last_audit': last_audit,
            'allocated_storage_gb': 5.0  # Stockage alloué par utilisateur
        }
        
    except Exception as e:
        print(f"Erreur récupération info DB: {str(e)}")
        return {
            'db_size_mb': 0,
            'tables_info': {},
            'audit_count': 0,
            'last_audit': "Erreur",
            'allocated_storage_gb': 5.0
        }

    with tab6:
        st.markdown("### 💾 Monitoring de la Base de Données")
        
        # Récupérer les informations de la base de données
        db_info = get_database_info()
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Taille DB", f"{db_info['db_size_mb']:.2f} MB")
        with col2:
            remaining_gb = db_info['allocated_storage_gb'] - (db_info['db_size_mb'] / 1024)
            st.metric("Stockage restant", f"{remaining_gb:.2f} GB")
        with col3:
            st.metric("Stockage alloué", f"{db_info['allocated_storage_gb']} GB")
        with col4:
            usage_percent = (db_info['db_size_mb'] / (db_info['allocated_storage_gb'] * 1024)) * 100
            st.metric("Utilisation", f"{usage_percent:.1f}%")
        
        st.markdown("---")
        
        # Graphique d'utilisation du stockage
        col1, col2 = st.columns([1, 2])
        with col1:
            # Jauge d'utilisation
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=usage_percent,
                title={'text': "Utilisation du stockage"},
                gauge={'axis': {'range': [0, 100]},
                       'bar': {'color': "darkblue"},
                       'steps': [
                           {'range': [0, 50], 'color': "lightgreen"},
                           {'range': [50, 80], 'color': "yellow"},
                           {'range': [80, 100], 'color': "red"}
                       ]}
            ))
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Graphique en barres de l'utilisation
            storage_data = {
                'Utilisé': db_info['db_size_mb'] / 1024,
                'Restant': remaining_gb
            }
            fig = px.bar(x=list(storage_data.keys()), y=list(storage_data.values()),
                        labels={'x': 'Type', 'y': 'Stockage (GB)'},
                        title="Répartition du stockage",
                        color=['red', 'green'],
                        color_discrete_map={'Utilisé': 'red', 'Restant': 'green'})
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Informations détaillées sur les tables
        st.markdown("### 📋 Statistiques des tables")
        
        table_data = []
        for table_name, count in db_info['tables_info'].items():
            table_data.append({
                'Table': table_name,
                'Enregistrements': count
            })
        
        # Ajouter les logs d'audit
        table_data.append({
            'Table': 'audit_logs (total)',
            'Enregistrements': db_info['audit_count']
        })
        
        df_tables = pd.DataFrame(table_data)
        st.dataframe(df_tables, use_container_width=True)
        
        # Graphique des enregistrements par table
        fig = px.bar(df_tables, x='Table', y='Enregistrements',
                    title="Nombre d'enregistrements par table",
                    color='Enregistrements',
                    color_continuous_scale='Viridis')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Informations sur les logs d'audit
        st.markdown("### 📝 Logs d'audit")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Nombre total de logs", db_info['audit_count'])
        with col2:
            st.metric("Dernier log", db_info['last_audit'])
        
        # Évolution des logs d'audit (si disponible)
        if db_info['audit_count'] > 0:
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT DATE(timestamp) as date, COUNT(*) as count 
                    FROM audit_logs 
                    GROUP BY DATE(timestamp) 
                    ORDER BY date DESC 
                    LIMIT 30
                ''')
                audit_trend = cursor.fetchall()
                conn.close()
                
                if audit_trend:
                    dates = [row[0] for row in audit_trend]
                    counts = [row[1] for row in audit_trend]
                    
                    fig = px.line(x=dates, y=counts,
                                 labels={'x': 'Date', 'y': 'Nombre de logs'},
                                 title="Évolution des logs d'audit (30 derniers jours)",
                                 markers=True)
                    st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.warning(f"Impossible de récupérer l'évolution des logs: {str(e)}")
        
        st.markdown("---")
        
        # Affichage des données brutes des tables
        st.markdown("### 📊 Données brutes des tables")
        
        # Sélecteur de table
        table_options = ['app_data', 'audit_logs', 'corbeille']
        selected_table = st.selectbox("Sélectionner une table à afficher :", table_options)
        
        if st.button(f"Afficher les données de {selected_table}", key="show_table_data"):
            try:
                conn = sqlite3.connect(db_path)
                
                # Récupérer le schéma de la table pour les colonnes
                cursor = conn.cursor()
                cursor.execute(f"PRAGMA table_info({selected_table})")
                columns_info = cursor.fetchall()
                columns = [col[1] for col in columns_info]  # Nom des colonnes
                
                # Récupérer les données (limité à 1000 enregistrements pour performance)
                cursor.execute(f"SELECT * FROM {selected_table} ORDER BY ROWID DESC LIMIT 1000")
                rows = cursor.fetchall()
                
                conn.close()
                
                if rows:
                    # Créer un DataFrame avec les données
                    df_table = pd.DataFrame(rows, columns=columns)
                    
                    st.success(f"✅ {len(rows)} enregistrement(s) trouvé(s) dans la table '{selected_table}'")
                    
                    # Afficher le DataFrame
                    st.dataframe(df_table, use_container_width=True)
                    
                    # Statistiques rapides
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Nombre de colonnes", len(columns))
                    with col2:
                        st.metric("Nombre de lignes affichées", len(rows))
                    with col3:
                        if len(rows) == 1000:
                            st.metric("Note", "Limité à 1000 lignes")
                        else:
                            st.metric("Total", f"{len(rows)} lignes")
                    
                    # Bouton d'export CSV
                    csv_data = df_table.to_csv(index=False)
                    st.download_button(
                        label="📥 Télécharger en CSV",
                        data=csv_data,
                        file_name=f"{selected_table}_export.csv",
                        mime="text/csv",
                        key=f"download_{selected_table}"
                    )
                    
                else:
                    st.info(f"📭 La table '{selected_table}' est vide")
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de la lecture de la table '{selected_table}': {str(e)}")
        
        # Informations sur la corbeille
        st.markdown("### 🗑️ État de la corbeille")
        corbeille_items = get_corbeille_items()
        
        if corbeille_items:
            corbeille_stats = {}
            for item in corbeille_items:
                entity_type = item['entity_type']
                corbeille_stats[entity_type] = corbeille_stats.get(entity_type, 0) + 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total éléments corbeille", len(corbeille_items))
            
            with col2:
                oldest_item = min(corbeille_items, key=lambda x: x['deleted_at'])
                st.metric("Plus ancien élément", oldest_item['deleted_at'])
            
            # Graphique de répartition de la corbeille
            fig = px.pie(values=list(corbeille_stats.values()), names=list(corbeille_stats.keys()),
                        title="Répartition des éléments dans la corbeille")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("🗑️ La corbeille est vide")
        
        # Recommandations de maintenance
        st.markdown("---")
        st.markdown("### 🔧 Recommandations de maintenance")
        
        recommendations = []
        
        if usage_percent > 80:
            recommendations.append("⚠️ **Stockage élevé** : Considérez l'archivage des anciennes données")
        
        if db_info['audit_count'] > 10000:
            recommendations.append("📝 **Logs volumineux** : Pensez à archiver les anciens logs d'audit")
        
        if len(corbeille_items) > 100:
            recommendations.append("🗑️ **Corbeille pleine** : Videz régulièrement la corbeille")
        
        if not recommendations:
            recommendations.append("✅ **Système sain** : Aucune action de maintenance requise")
        
        for rec in recommendations:
            st.info(rec)

# Main
def main():
    # Attendre que MariaDB soit complètement démarré (une seule fois)
    if 'mariadb_waited' not in st.session_state:
        import time
        print("Debug - Attente de 3 secondes pour MariaDB...")
        time.sleep(3)
        st.session_state.mariadb_waited = True

    init_session_state()
    init_audit_logs()  # Initialiser les logs d'audit

    # Log du démarrage de l'application (une seule fois par session)
    if 'app_started_logged' not in st.session_state:
        log_action("DÉMARRAGE", "application", "Système de Gestion",
                  "Application démarrée - Chargement des données et interface")
        st.session_state.app_started_logged = True

    display_header()

    page = display_sidebar()

    # Mettre à jour la page courante pour détecter les changements
    st.session_state.current_page = page

    if page == "📊 Tableau de Bord":
        # Debug: Afficher l'état des données avant d'afficher le dashboard
        print(f"Debug - Avant display_dashboard: vehicules={len(st.session_state.vehicules)}, achats={len(st.session_state.achats)}, anomalies={len(st.session_state.anomalies)}, habilitations={len(st.session_state.habilitations)}")
        display_dashboard()
    elif page == "🚙 Inspection Véhicules":
        inspection_vehicules()
    elif page == "🛒 Suivi Achats":
        suivi_achats()
    elif page == "⚠️ Anomalies & Réclamations":
        gestion_anomalies()
    elif page == "🎓 Habilitations":
        verification_habilitations()
    elif page == "🗑️ Corbeille":
        gestion_corbeille()

if __name__ == "__main__":
    main()
