import cloudinary
import cloudinary.uploader
from PIL import Image
import io
import matplotlib.pyplot as plt

# Configuration Cloudinary
cloudinary.config(
    cloud_name='dddkmikpf',
    api_key='848997274359864',
    api_secret='5TZZdDTf7gmAFk_eVpJWeKgilb8'
)

# Créer une image de test
fig, ax = plt.subplots()
ax.text(0.5, 0.5, 'Test Cloudinary', ha='center', va='center')
ax.axis('off')
buf = io.BytesIO()
fig.savefig(buf, format='png')
buf.seek(0)
plt.close(fig)

# Tester l'upload
try:
    result = cloudinary.uploader.upload(buf, folder="test")
    print(f"Upload réussi: {result['secure_url']}")
except Exception as e:
    print(f"Erreur upload: {e}")