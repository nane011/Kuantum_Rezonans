# src/data_loader.py
import json
import os

class NistDataLoader:
    def __init__(self, data_folder="data"):
        # Veri dosyalarının durduğu klasör yolunu sabitliyoruz
        self.data_folder = data_folder

    def load_element_levels(self, element_symbol):
        """
        Girdi olarak 'H' veya 'He' alır ve data/H.json dosyasını okur.
        """
        # Dosya adını dinamik olarak oluşturuyoruz (Örn: data/H.json)
        file_path = os.path.join(self.data_folder, f"{element_symbol}.json")
        
        # Dosya sistemde var mı kontrol ediyoruz, yoksa hata fırlatıyoruz
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Hata: {file_path} dosyası bulunamadı! Lütfen JSON dosyasını kontrol edin.")
            
        # Dosyayı okuma modunda ('r') açıp içindeki JSON verisini Python sözlüğüne çeviriyoruz
        with open(file_path, 'r', encoding='utf-8') as file:
            element_data = json.load(file)
            
        return element_data
