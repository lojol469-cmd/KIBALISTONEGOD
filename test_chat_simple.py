import sys
import os
import torch
from transformers import AutoProcessor, AutoModelForCausalLM
from PIL import Image

class ImageChatBot:
    def __init__(self):
        print("Initialisation du chatbot...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Utilisation du device: {self.device}")
        self.image = None

    def load_image(self, image_path):
        try:
            self.image = Image.open(image_path).convert("RGB")
            print(f"Image chargée: {image_path}")
            return True
        except Exception as e:
            print(f"Erreur: {e}")
            return False

    def chat(self, message):
        if self.image is None:
            return "Aucune image chargée"

        return f"Message reçu: {message}. Image chargée de taille {self.image.size}"

def main():
    bot = ImageChatBot()
    print("Chatbot prêt")
    print("Tapez /quit pour quitter")

    while True:
        user_input = input("Vous: ").strip()
        if user_input == "/quit":
            break
        elif user_input.startswith("/load "):
            path = user_input[6:]
            bot.load_image(path)
        else:
            response = bot.chat(user_input)
            print(f"Bot: {response}")

if __name__ == "__main__":
    main()