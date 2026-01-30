from huggingface_hub import HfApi
import os

repo_id = "THUDM/glm-4v-9b"
local_dir = "models/glm-4v-9b"

api = HfApi()
files = api.list_repo_files(repo_id)

# Create input file for aria2
with open("aria2_input.txt", "w") as f:
    for file in files:
        url = f"https://huggingface.co/{repo_id}/resolve/main/{file}"
        out = os.path.basename(file)
        f.write(f"{url}\n out={out}\n dir={local_dir}\n\n")

# Run aria2
os.system("aria2c -i aria2_input.txt -j 16 -x 16")

print("Download completed with aria2")