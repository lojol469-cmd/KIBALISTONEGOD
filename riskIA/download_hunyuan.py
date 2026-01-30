import os
from huggingface_hub import snapshot_download
from huggingface_hub.utils import HfHubHTTPError

def download_hunyuan3d_model():
    """Télécharge le modèle Hunyuan3D-2.1 depuis Hugging Face"""
    model_id = "tencent/Hunyuan3D-2.1"
    local_dir = "Hunyuan3D-2.1"

    print(f"Téléchargement du modèle {model_id} vers {local_dir}...")

    try:
        # Télécharger tout le snapshot
        snapshot_path = snapshot_download(
            repo_id=model_id,
            local_dir=local_dir,
            local_dir_use_symlinks=False,
            resume_download=True,
            max_workers=4
        )
        print(f"Modèle téléchargé avec succès dans: {snapshot_path}")

        # Lister les fichiers téléchargés
        print("\nFichiers téléchargés:")
        for root, dirs, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                size = os.path.getsize(file_path)
                print(f"  {os.path.relpath(file_path, local_dir)} ({size} bytes)")

    except HfHubHTTPError as e:
        print(f"Erreur lors du téléchargement: {e}")
        print("Vérifiez que le repo existe et que vous avez accès à internet.")
    except Exception as e:
        print(f"Erreur inattendue: {e}")

if __name__ == "__main__":
    download_hunyuan3d_model()