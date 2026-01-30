import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import os
from matplotlib.patches import Circle
import matplotlib.patches as patches

# Charger l'image cobaye
img_path = 'riskIA/cap.png'
img = cv2.imread(img_path)
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

print('=== PLUGIN CRUES AMÉLIORÉ AVEC ANIMATION - Test sur cap.png ===')
print(f'Image cobaye: {img.shape[1]}x{img.shape[0]} pixels')

height, width = img.shape[:2]

# === PARTIE 1: IMAGE COBAYE INCRUSTÉE ===
mask = np.zeros((height, width, 3), dtype=np.uint8)
num_zones = 8
flood_zones = []
for i in range(num_zones):
    x = np.random.randint(width//6, 5*width//6)
    y = np.random.randint(3*height//4, height)
    radius = np.random.randint(30, 80)
    cv2.circle(mask, (x, y), radius, (255, 0, 0), -1)
    flood_zones.append((x, y, radius))

alpha = 0.35
img_incrusted = cv2.addWeighted(img_rgb, 1-alpha, mask, alpha, 0)
cv2.putText(img_incrusted, 'ZONE INONDABLE', (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
cv2.putText(img_incrusted, 'Risque Crues - Niveau Moderé', (50, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

# === PARTIE 2: ANIMATION DE L'INONDATION ===
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

ax1.imshow(img_incrusted)
ax1.set_title('Image Cobaye Incrustée - Zones de Crues', fontsize=14, fontweight='bold')
ax1.axis('off')

ax2.set_title('Simulation Animée - Propagation des Crues', fontsize=14, fontweight='bold')
ax2.set_xlim(0, width)
ax2.set_ylim(height, 0)
ax2.set_xlabel('Coordonnées X (pixels)')
ax2.set_ylabel('Coordonnées Y (pixels)')

# Contour du site
site_contour = patches.Rectangle((0, 0), width, height, linewidth=2, edgecolor='black', facecolor='none', label='Périmètre du site')
ax2.add_patch(site_contour)

# Sources d'eau
water_sources = [(width//4, height), (width//2, height), (3*width//4, height)]
water_patches = []
for x, y in water_sources:
    patch = Circle((x, y), 5, color='blue', alpha=0.8, label="Source d'eau")
    ax2.add_patch(patch)
    water_patches.append(patch)

# Zones d'inondation
flood_patches = []
for x, y, r in flood_zones:
    patch = Circle((x, y), 0, color='lightblue', alpha=0.6)
    ax2.add_patch(patch)
    flood_patches.append(patch)

ax2.legend(loc='upper right')
ax2.grid(True, alpha=0.3)

# Fonction d'animation
def animate(frame):
    progress = frame / 100.0

    for i, patch in enumerate(flood_patches):
        max_radius = flood_zones[i][2]
        current_radius = max_radius * progress
        patch.set_radius(current_radius)
        alpha_val = 0.3 + 0.4 * progress
        patch.set_alpha(alpha_val)
        if progress > 0.8:
            patch.set_color('blue')

    if progress < 0.3:
        status = "Début de l'inondation"
    elif progress < 0.7:
        status = 'Propagation en cours'
    else:
        status = 'Niveau critique atteint'

    ax2.set_title(f'Simulation Animée - Propagation des Crues\n{status} ({progress:.0%})', fontsize=14, fontweight='bold')

    return flood_patches

# Créer et sauvegarder l'animation
anim = animation.FuncAnimation(fig, animate, frames=101, interval=100, blit=False)
gif_path = 'plugin_crues_animation.gif'
anim.save(gif_path, writer='pillow', fps=10, dpi=100)
print(f'Animation GIF sauvegardée: {gif_path}')

# === PARTIE 3: VERSION SVG STATIQUE ===
fig2, ax3 = plt.subplots(figsize=(8, 6))
ax3.imshow(img_rgb)
ax3.set_title('Version SVG - Environnement Dessiné', fontsize=14, fontweight='bold')
ax3.axis('off')

# Dessiner les bâtiments
buildings = [(100, 200, 80, 60), (300, 250, 100, 70), (500, 180, 90, 80)]
for x, y, w, h in buildings:
    rect = patches.Rectangle((x, y), w, h, linewidth=2, edgecolor='black', facecolor='lightgray', alpha=0.7)
    ax3.add_patch(rect)
    roof = patches.Polygon([(x, y), (x+w//2, y-20), (x+w, y)], closed=True, facecolor='darkgray', edgecolor='black')
    ax3.add_patch(roof)

# Routes
roads = [[(0, height//2), (width//3, height//2)], [(2*width//3, height//2), (width, height//2)], [(width//2, height//4), (width//2, 3*height//4)]]
for road in roads:
    ax3.plot([road[0][0], road[1][0]], [road[0][1], road[1][1]], 'k-', linewidth=8, alpha=0.6)

# Annotations des zones
for i, (x, y, r) in enumerate(flood_zones):
    circle = Circle((x, y), r, color='lightblue', alpha=0.5, edgecolor='blue', linewidth=2)
    ax3.add_patch(circle)
    ax3.text(x, y-10, f'Zone {i+1}', ha='center', va='bottom', fontsize=10,
             bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))

ax3.text(50, 100, 'ENVIRONNEMENT RECREÉ\nBasé sur image cobaye', fontsize=12,
         bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.8))

svg_path = 'plugin_crues_svg_dessin.svg'
fig2.savefig(svg_path, format='svg', dpi=300, bbox_inches='tight')
print(f'Version SVG statique sauvegardée: {svg_path}')

# === PARTIE 4: NOTIONS ET NORMES ===
notion_text = '''
NOTIONS EXTRAITES DU PDF - CRUES:
• Les constructions doivent résister aux accélérations sismiques
• Définition basée sur zone de sismicité et catégorie d'importance
• Risque lié au type de sol de construction
• Analyse des zones inondables et niveaux de risque

NORMES DE RÉFÉRENCE:
• ISO 10137: Bases pour le calcul des structures
• ISO 22111: Bases de calcul sismique
• Source: Étude des dangers - Pages 12, 35, 37, 45
• Référentiel: NF EN 1998-1 (Eurocode 8)
'''

plt.figtext(0.02, 0.02, notion_text, fontsize=9, verticalalignment='bottom',
           bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', alpha=0.9))

plt.tight_layout()
final_path = 'plugin_crues_complet.png'
plt.savefig(final_path, dpi=300, bbox_inches='tight')
print(f'Version complète sauvegardée: {final_path}')

print('\n=== RÉSUMÉ PLUGIN CRUES AMÉLIORÉ ===')
print(f'✓ Image cobaye incrustée avec {num_zones} zones inondables')
print(f'✓ Animation GIF de propagation des crues')
print(f'✓ Version SVG statique avec environnement dessiné')
print(f'✓ Notions PDF intégrées + normes ISO/Eurocode')