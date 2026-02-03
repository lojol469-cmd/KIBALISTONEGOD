"""
🌐 Test de Configuration Réseau - SETRAGESTION
Vérifie que l'application est accessible depuis le réseau local
"""

import socket
import subprocess
import sys

def print_header():
    print("\n" + "="*70)
    print("🌐 TEST DE CONFIGURATION RÉSEAU - SETRAGESTION")
    print("="*70 + "\n")

def get_local_ip():
    """Détecte l'adresse IP locale"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception:
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return local_ip
        except:
            return "127.0.0.1"

def get_hostname():
    """Obtient le nom de l'ordinateur"""
    try:
        return socket.gethostname()
    except:
        return "Inconnu"

def check_port(port):
    """Vérifie si un port est disponible"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0  # True si le port est occupé (serveur en cours)
    except:
        return False

def test_network_config():
    """Test principal"""
    print_header()
    
    # 1. Informations machine
    print("📍 INFORMATIONS DE LA MACHINE:")
    hostname = get_hostname()
    local_ip = get_local_ip()
    print(f"   Nom de l'ordinateur: {hostname}")
    print(f"   Adresse IP locale: {local_ip}")
    
    # 2. Test des ports
    print("\n🔌 ÉTAT DES PORTS:")
    ports = {
        8501: "Application Streamlit",
        3000: "API Backend Node.js",
        4000: "Serveur de Licence"
    }
    
    for port, service in ports.items():
        is_running = check_port(port)
        status = "✅ ACTIF" if is_running else "❌ ARRÊTÉ"
        print(f"   Port {port} ({service}): {status}")
    
    # 3. URLs d'accès
    print("\n🌐 ADRESSES D'ACCÈS:")
    print("\n   📱 Depuis CET ordinateur:")
    print(f"      • http://localhost:8501")
    print(f"      • http://127.0.0.1:8501")
    
    print("\n   🌍 Depuis d'autres ordinateurs:")
    print(f"      • http://{local_ip}:8501")
    print(f"      • http://{hostname}:8501 (si le réseau supporte les noms)")
    
    # 4. Recommandations
    print("\n💡 RECOMMANDATIONS:")
    
    any_running = any(check_port(p) for p in ports.keys())
    
    if not any_running:
        print("   ⚠️  Aucun serveur n'est en cours d'exécution")
        print("   ➜ Lancez l'application avec 'Lanceur_SETRAF_Portable.bat'")
    else:
        print("   ✅ Au moins un serveur est actif")
        
    if local_ip == "127.0.0.1":
        print("   ⚠️  IP locale non détectée - problème de réseau possible")
    else:
        print(f"   ✅ IP locale détectée: {local_ip}")
        print(f"   ➜ Partagez cette adresse avec les autres utilisateurs")
    
    # 5. Test de connectivité
    print("\n🔍 TEST DE CONNECTIVITÉ:")
    try:
        # Test connexion Internet
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        print("   ✅ Connexion Internet: OK")
    except:
        print("   ⚠️  Pas de connexion Internet (normal pour réseau local uniquement)")
    
    # 6. Configuration pare-feu
    print("\n🛡️  PARE-FEU:")
    print("   Assurez-vous que les ports 8501, 3000, 4000 sont autorisés")
    print("   Pour tester, désactivez temporairement le pare-feu")
    
    # 7. Instructions pour les clients
    print("\n📋 POUR LES AUTRES UTILISATEURS:")
    print(f"   1. Connectez-vous au même réseau (WiFi/Ethernet)")
    print(f"   2. Ouvrez un navigateur web")
    print(f"   3. Tapez: http://{local_ip}:8501")
    print(f"   4. L'application devrait s'afficher")
    
    print("\n" + "="*70)
    print("✅ Test terminé!")
    print("="*70 + "\n")
    
    # Garder la fenêtre ouverte
    input("Appuyez sur Entrée pour fermer...")

if __name__ == "__main__":
    try:
        test_network_config()
    except Exception as e:
        print(f"\n❌ Erreur lors du test: {e}")
        input("\nAppuyez sur Entrée pour fermer...")
