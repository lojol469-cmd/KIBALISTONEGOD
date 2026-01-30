import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import open3d as o3d
import time
import json
from pathlib import Path
import tempfile
import os
import sys

# Ajouter le chemin vers les modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'A3E'))
sys.path.append(os.path.dirname(__file__))  # Pour models

# Import des modules spécialisés
from risk_simulator import PetroleumRiskSimulator  # type: ignore
from text_to_simulation import TextToSimulationAI  # type: ignore
from models.rag_system import CPT_RAG_System

# Configuration de la page
st.set_page_config(
    page_title="🛢️ Simulateur Ultra-Réaliste de Risques Pétroliers",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour thème sombre professionnel
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .risk-high { background: #ffe6e6; border-left: 4px solid #dc3545; }
    .risk-medium { background: #fff3cd; border-left: 4px solid #ffc107; }
    .risk-low { background: #d1ecf1; border-left: 4px solid #17a2b8; }
    .simulation-result {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid #dee2e6;
    }
</style>
""", unsafe_allow_html=True)

class PetroleumRiskApp:
    """Application Streamlit principale pour simulations de risques pétroliers"""

    def __init__(self):
        self.simulator = PetroleumRiskSimulator()
        self.ai_system = None
        self.rag_system = CPT_RAG_System()
        self.current_simulation = None
        self.point_cloud = None

        # Initialisation des systèmes IA
        self._initialize_ai_systems()

    def _initialize_ai_systems(self):
        """Initialise les systèmes d'IA"""
        try:
            with st.spinner("🔧 Initialisation des systèmes d'IA..."):
                # Initialisation RAG pour analyses de risques
                if not self.rag_system.initialize_model():
                    st.warning("⚠️ Système RAG non disponible - fonctionnalités d'analyse PDF limitées")
                else:
                    st.success("✅ Système RAG initialisé")

                # Initialisation IA text-to-simulation
                if self.rag_system.is_initialized:
                    self.ai_system = TextToSimulationAI(self.rag_system)
                    st.success("✅ IA Text-to-Simulation initialisée")
                else:
                    st.warning("⚠️ IA Text-to-Simulation non disponible - RAG non initialisé")

        except Exception as e:
            st.error(f"❌ Erreur d'initialisation IA: {e}")

    def run(self):
        """Lance l'application principale"""
        self._render_header()
        self._render_sidebar()
        self._render_main_content()

    def _render_header(self):
        """Affiche l'en-tête principal"""
        st.markdown("""
        <div class="main-header">
            <h1>🛢️ Simulateur Ultra-Réaliste de Risques Pétroliers</h1>
            <p><strong>IA • CFD • Visualisation 3D • Analyses RAG</strong></p>
            <p style="font-size: 0.9em; opacity: 0.9;">
            Dépassement des logiciels PHAST/SAFETI via interactivité temps réel, IA conversationnelle, et accessibilité web gratuite
            </p>
        </div>
        """, unsafe_allow_html=True)

    def _render_sidebar(self):
        """Affiche la barre latérale avec contrôles"""
        with st.sidebar:
            st.header("🎛️ Panneau de Contrôle")

            # Sélection du mode
            self.mode = st.selectbox(
                "Mode de Simulation",
                ["IA Conversationnelle", "Paramètres Manuels", "Analyse PDF Risques"],
                help="Choisissez votre méthode d'interaction"
            )

            # Paramètres communs
            st.subheader("🌪️ Conditions Météo")
            self.wind_speed = st.slider("Vitesse du vent (m/s)", 0.0, 20.0, 5.0, 0.5)
            self.stability_class = st.selectbox("Classe de stabilité", ["A", "B", "C", "D", "E", "F"], index=3)

            # Chargement du nuage de points
            st.subheader("📊 Nuage de Points 3D")
            uploaded_pcd = st.file_uploader("Charger nuage de points (.pcd, .ply, .xyz)", type=['pcd', 'ply', 'xyz'])
            if uploaded_pcd:
                self._load_point_cloud(uploaded_pcd)

            # Options avancées
            with st.expander("⚙️ Options Avancées"):
                self.enable_cantera = st.checkbox("Cantera (Combustion)", value=True)
                self.enable_openfoam = st.checkbox("OpenFOAM (CFD)", value=False)
                self.enable_cloud = st.checkbox("Calcul Cloud (AWS/GCP)", value=False)
                self.real_time_updates = st.checkbox("Mises à jour temps réel", value=True)

    def _render_main_content(self):
        """Affiche le contenu principal selon le mode sélectionné"""
        if self.mode == "IA Conversationnelle":
            self._render_ai_mode()
        elif self.mode == "Paramètres Manuels":
            self._render_manual_mode()
        elif self.mode == "Analyse PDF Risques":
            self._render_pdf_analysis_mode()

    def _render_ai_mode(self):
        """Mode IA conversationnel avec text-to-simulation"""
        st.header("🤖 IA Text-to-Simulation")

        # Zone de chat
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []

        # Affichage de l'historique
        for message in st.session_state.chat_history:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                if "simulation" in message:
                    self._display_simulation_result(message["simulation"])

        # Input utilisateur
        user_input = st.chat_input("Décrivez votre scénario de risque pétrolier...")

        if user_input:
            # Ajout du message utilisateur
            st.session_state.chat_history.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.write(user_input)

            # Traitement par IA
            with st.chat_message("assistant"):
                if self.ai_system is None:
                    st.error("❌ Système IA non disponible. Veuillez vérifier l'initialisation.")
                else:
                    with st.spinner("🧠 Analyse de votre requête..."):
                        try:
                            simulation_result, scenario_desc = self.ai_system.generate_simulation_from_text(user_input)

                            # Validation des paramètres
                            warnings = self.ai_system.validate_simulation_parameters(
                                self.ai_system.parse_simulation_request(user_input)
                            )

                            response = f"**Scénario identifié:** {scenario_desc}\n\n"

                            if warnings:
                                response += "**⚠️ Avertissements:**\n" + "\n".join(f"• {w}" for w in warnings) + "\n\n"

                            response += "**Résultats de simulation:**"

                            st.write(response)
                            self._display_simulation_result(simulation_result)

                            # Stockage dans l'historique
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response,
                                "simulation": simulation_result
                            })

                        except Exception as e:
                            error_msg = f"❌ Erreur lors de l'analyse: {e}"
                            st.error(error_msg)
                            st.session_state.chat_history.append({"role": "assistant", "content": error_msg})

    def _render_manual_mode(self):
        """Mode paramètres manuels"""
        st.header("🔧 Simulation Manuelle")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("💨 Dispersion de Gaz")
            gas_type = st.selectbox("Type de gaz", ["methane", "propane", "hydrogen_sulfide"], key="gas_type")
            release_rate = st.number_input("Débit de fuite (kg/s)", 0.1, 1000.0, 10.0, key="release_rate")
            duration = st.number_input("Durée (secondes)", 60, 36000, 3600, key="duration")
            model = st.selectbox("Modèle", ["gaussian", "pasquill_gifford", "cfd_simplified"], key="disp_model")

            if st.button("🚀 Lancer Simulation Dispersion", key="run_dispersion"):
                with st.spinner("🔬 Calcul de la dispersion..."):
                    try:
                        result = self.simulator.simulate_gas_dispersion(
                            gas_type=gas_type,
                            release_rate=release_rate,
                            wind_speed=self.wind_speed,
                            stability_class=self.stability_class,
                            model=model,
                            duration=duration
                        )
                        self.current_simulation = result
                        self._display_simulation_result(result)
                    except Exception as e:
                        st.error(f"Erreur simulation: {e}")

        with col2:
            st.subheader("💥 Explosion")
            fuel_type = st.selectbox("Type de combustible", ["methane", "propane", "gasoline"], key="fuel_type")
            fuel_mass = st.number_input("Masse de combustible (kg)", 1.0, 10000.0, 1000.0, key="fuel_mass")
            confinement = st.selectbox("Confinement", ["unconfined", "partially_confined", "fully_confined"], key="confinement")
            explosion_model = st.selectbox("Modèle explosion", ["tnt_equivalent", "multi_energy", "vce"], key="exp_model")

            if st.button("💥 Lancer Simulation Explosion", key="run_explosion"):
                with st.spinner("💥 Calcul de l'explosion..."):
                    try:
                        result = self.simulator.simulate_explosion(
                            fuel_type=fuel_type,
                            fuel_mass=fuel_mass,
                            confinement=confinement,
                            model=explosion_model
                        )
                        self.current_simulation = result
                        self._display_simulation_result(result)
                    except Exception as e:
                        st.error(f"Erreur simulation: {e}")

    def _render_pdf_analysis_mode(self):
        """Mode analyse de PDF de risques"""
        st.header("📄 Analyse de Documents Risques")

        uploaded_pdf = st.file_uploader("Charger document PDF de risques", type=['pdf'])

        if uploaded_pdf:
            # Extraction du texte (simulation - en production utiliser PyPDF2 ou pdfplumber)
            pdf_text = f"Contenu simulé du PDF: {uploaded_pdf.name}"

            scenario_type = st.selectbox("Type de scénario", ["general", "dispersion", "explosion", "fire"])

            if st.button("🔍 Analyser le PDF"):
                if not hasattr(self.rag_system, 'analyze_petroleum_risks_from_pdf'):
                    st.error("❌ Fonction d'analyse PDF non disponible.")
                else:
                    with st.spinner("📖 Analyse du document..."):
                        try:
                            analysis = self.rag_system.analyze_petroleum_risks_from_pdf(pdf_text, scenario_type)  # type: ignore

                            # Affichage des résultats
                            if 'error' not in analysis:
                                st.success("✅ Analyse terminée")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.subheader("📊 Scénarios Identifiés")
                                    for scenario in analysis.get('risk_scenarios', []):
                                        st.markdown(f"**{scenario['type']}**: {scenario['occurrences']} occurrence(s)")

                                    st.subheader("🔧 Recommandations")
                                    for rec in analysis.get('safety_recommendations', []):
                                        st.markdown(f"• {rec}")

                                with col2:
                                    st.subheader("📋 Conformité")
                                    compliance = analysis.get('compliance_check', {})
                                    for standard, status in compliance.items():
                                        color = "🟢" if status['mentioned'] else "🟡"
                                        st.markdown(f"{color} **{standard}**: {status['status']}")

                                    st.subheader("⚠️ Valeurs Critiques")
                                    critical = analysis.get('critical_values', {})
                                    for key, value in critical.items():
                                        st.metric(key.replace('_', ' ').title(), f"{value}")

                            else:
                                st.error(analysis['error'])

                        except Exception as e:
                            st.error(f"Erreur analyse PDF: {e}")
        """Affiche les résultats de simulation de manière structurée"""
        if not result:
            return

        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if 'max_concentration' in result:
                st.metric("Concentration Max", f"{result['max_concentration']:.2f} mg/m³")
            elif 'tnt_equivalent' in result:
                st.metric("Équivalent TNT", f"{result['tnt_equivalent']:.1f} kg")

        with col2:
            if 'affected_area' in result:
                st.metric("Zone Affectée", f"{result['affected_area']:.0f} m²")
            elif 'damage_radii' in result:
                radii = result['damage_radii']
                st.metric("Rayon Destruction", f"{radii.get('total_destruction', 0):.1f} m")

        with col3:
            st.metric("Modèle", result.get('model', 'N/A'))

        with col4:
            risk_level = self._assess_risk_level(result)
            st.metric("Niveau de Risque", risk_level)

        # Visualisation 3D
        if st.button("🎨 Générer Visualisation 3D", key=f"viz_{hash(str(result))}"):
            with st.spinner("🎨 Création de la visualisation 3D..."):
                try:
                    fig = self.simulator.create_3d_visualization(result, self.point_cloud)
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Erreur visualisation: {e}")

        # Rapport détaillé
        with st.expander("📋 Rapport Détaillé"):
            report = self.simulator.generate_risk_report(result, "Simulation interactive")
            st.markdown(report)

        # Export des résultats
        if st.button("💾 Exporter Résultats", key=f"export_{hash(str(result))}"):
            self._export_results(result)

    def _assess_risk_level(self, result: dict) -> str:
        """Évalue le niveau de risque basé sur les résultats"""
        if 'max_concentration' in result:
            conc = result['max_concentration']
            if conc > 100:
                return "🔴 CRITIQUE"
            elif conc > 50:
                return "🟠 ÉLEVÉ"
            elif conc > 10:
                return "🟡 MOYEN"
            else:
                return "🟢 FAIBLE"
        elif 'damage_radii' in result:
            max_radius = max(result['damage_radii'].values())
            if max_radius > 100:
                return "🔴 CRITIQUE"
            elif max_radius > 50:
                return "🟠 ÉLEVÉ"
            elif max_radius > 20:
                return "🟡 MOYEN"
            else:
                return "🟢 FAIBLE"
        return "⚪ INCONNU"

    def _load_point_cloud(self, uploaded_file):
        """Charge un nuage de points 3D"""
        try:
            # Sauvegarde temporaire
            with tempfile.NamedTemporaryFile(delete=False, suffix=uploaded_file.name) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            # Chargement avec Open3D
            if uploaded_file.name.endswith('.pcd'):
                self.point_cloud = o3d.io.read_point_cloud(tmp_path)
            elif uploaded_file.name.endswith('.ply'):
                self.point_cloud = o3d.io.read_triangle_mesh(tmp_path)
            else:
                # Format XYZ simple
                points = np.loadtxt(tmp_path)
                self.point_cloud = o3d.geometry.PointCloud()
                self.point_cloud.points = o3d.utility.Vector3dVector(points)

            st.success(f"✅ Nuage de points chargé: {len(self.point_cloud.points)} points")

            # Nettoyage
            os.unlink(tmp_path)

        except Exception as e:
            st.error(f"❌ Erreur chargement nuage de points: {e}")

    def _export_results(self, result: dict):
        """Exporte les résultats de simulation"""
        try:
            # Création du fichier JSON
            export_data = {
                'timestamp': time.time(),
                'simulation_result': result,
                'parameters': {
                    'wind_speed': self.wind_speed,
                    'stability_class': self.stability_class
                }
            }

            # Téléchargement
            json_str = json.dumps(export_data, indent=2, default=str)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_str,
                file_name=f"simulation_risques_{int(time.time())}.json",
                mime="application/json",
                key=f"download_{hash(str(result))}"
            )

        except Exception as e:
            st.error(f"Erreur export: {e}")

def main():
    """Fonction principale"""
    app = PetroleumRiskApp()
    app.run()

    # Pied de page
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.8em;">
        <p>🛢️ Simulateur Ultra-Réaliste de Risques Pétroliers v2.0</p>
        <p>Technologies: Cantera • OpenFOAM • Open3D • Plotly • IA RAG • Streamlit</p>
        <p>© 2026 - Dépassement des standards PHAST/SAFETI via IA et interactivité temps réel</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()