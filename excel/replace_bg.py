with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Trouver la ligne background-image
start = content.find('background-image: url(')
end = content.find(');', start) + 2

old_line = content[start:end]

# Nouveau contenu avec l'image fichier dans static
new_line = '        background-image: url("static/pexels-simberto-brauserich-3680746-5882869.jpg");'

print('Replacing...')
print('Old length:', len(old_line))
print('New length:', len(new_line))

# Remplacer
new_content = content.replace(old_line, new_line)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Replacement done!')