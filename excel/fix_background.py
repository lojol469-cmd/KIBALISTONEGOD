import base64

# Lire l'image et l'encoder en base64
with open('pexels-felix-antoine-coutu-174902-32211979.jpg', 'rb') as f:
    image_data = f.read()

encoded = base64.b64encode(image_data).decode('utf-8')
data_url = f'data:image/jpeg;base64,{encoded}'

# Lire le fichier app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver et remplacer la ligne background-image
start = content.find('background-image: url(')
if start != -1:
    end = content.find(');', start) + 2
    old_line = content[start:end]

    # Créer la nouvelle ligne
    indent = '        '  # 8 espaces d'indentation
    new_line = f'{indent}background-image: url("{data_url}");'

    print(f'Ancien encodage (longueur: {len(old_line)})')
    print(f'Nouveau encodage (longueur: {len(new_line)})')

    # Remplacer
    new_content = content.replace(old_line, new_line)

    # Écrire le fichier
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)

    print('Remplacement terminé avec succès!')
else:
    print('Ligne background-image non trouvée')