import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sounddevice as sd
import os
import math

# Altyapı Motorları
from NistDataLoader import NistDataLoader
from SpectrumConverter import SpectrumConverter
from AudioSynthesizer import AudioSynthesizer
from WavExporter import WavExporter

class QuantumSonifierGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Kuantum Rezonans v2.0")
        self.root.geometry("850x550")
        self.root.configure(bg="#0d0e12") # Derin Uzay Siyahı
        
        # Altyapı Nesneleri
        self.loader = NistDataLoader(data_folder="data")
        self.converter = SpectrumConverter(audio_min_hz=60.0, audio_max_hz=4000.0)
        self.synthesizer = AudioSynthesizer(sample_rate=22050)
        self.exporter = WavExporter(sample_rate=22050)
        
        # Elementlerin Bilimsel Kart Verileri (Görsel ve Elektron sayıları için)
        self.element_db = {
            "H":  {"name": "Hidrojen", "electrons": 1, "color": "#00ffcc"},
            "He": {"name": "Helyum", "electrons": 2, "color": "#ff007f"},
            "Li": {"name": "Lityum", "electrons": 3, "color": "#ffaa00"},
            "Be": {"name": "Berilyum", "electrons": 4, "color": "#aaff00"},
            "B":  {"name": "Bor", "electrons": 5, "color": "#00aaff"},
            "C":  {"name": "Karbon", "electrons": 6, "color": "#ffffff"},
            "N":  {"name": "Azot", "electrons": 7, "color": "#9933ff"},
            "O":  {"name": "Oksijen", "electrons": 8, "color": "#ff3333"},
            "F":  {"name": "Flor", "electrons": 9, "color": "#ffff33"},
            "Ne": {"name": "Neon", "electrons": 10, "color": "#ff6600"},
            "Fe": {"name": "Demir", "electrons": 26, "color": "#cccccc"},
            "Au": {"name": "Altın", "electrons": 79, "color": "#ffd700"},
            "Hg": {"name": "Cıva", "electrons": 80, "color": "#e5e5e5"},
            "U":  {"name": "Uranyum", "electrons": 92, "color": "#00ff00"}
        }
        
        self.current_frequencies = None
        self.current_amplitudes = None
        self.selected_element = None
        
        self._build_ui()
        self.update_element_view() # İlk açılış çizimi

    def _build_ui(self):
        # Premium Neon Dark Mode Stil Ayarları
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#0d0e12', foreground='#ffffff', font=('Segoe UI', 11))
        style.configure('TButton', background='#1f2330', foreground='#ffffff', font=('Segoe UI', 10, 'bold'), borderwidth=0)
        style.map('TButton', background=[('active', '#2d3247')])
        
        # ANA PANEL: Sol (Kontroller) ve Sağ (Atom Çizimi) olarak ikiye bölüyoruz
        main_frame = tk.Frame(self.root, bg="#0d0e12")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ================= LEFT FRAME (KONTROLLER) =================
        left_frame = tk.Frame(main_frame, bg="#0d0e12")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        title_lbl = tk.Label(left_frame, text="KUANTUM REZONANS", bg="#0d0e12", fg="#00ffcc", font=('Segoe UI', 18, 'bold'))
        title_lbl.pack(anchor=tk.W, pady=(10, 20))
        lbl_select = ttk.Label(left_frame, text="Periyodik Tablodan Element:")
        lbl_select.pack(anchor=tk.W, pady=5)
        
        # Dosyaları Otomatik Tara
        available_elements = []
        if os.path.exists("data"):
            available_elements = [f.split('.')[0] for f in os.listdir("data") if f.endswith(".json")]
        if not available_elements:
            available_elements = list(self.element_db.keys())
            
        self.combo_element = ttk.Combobox(left_frame, values=sorted(available_elements), state="readonly", font=('Segoe UI', 12))
        self.combo_element.pack(fill=tk.X, pady=5)
        self.combo_element.set("H")
        self.combo_element.bind("<<ComboboxSelected>>", lambda e: self.update_element_view())
        
        # Dinamik Kart Alanı (Yazı Bilgileri)
        self.card_frame = tk.Frame(left_frame, bg="#141722", bd=1, relief=tk.SOLID)
        self.card_frame.pack(fill=tk.X, pady=20, ipady=15, padx=2)
        
        self.lbl_card_title = tk.Label(self.card_frame, text="Element: Hidrojen (H)", bg="#141722", fg="#ffffff", font=('Segoe UI', 13, 'bold'))
        self.lbl_card_title.pack(pady=(10, 5), anchor=tk.W, padx=15)
        
        self.lbl_card_electrons = tk.Label(self.card_frame, text="Elektron Sayısı: 1", bg="#141722", fg="#8892b0", font=('Segoe UI', 11))
        self.lbl_card_electrons.pack(anchor=tk.W, padx=15)
        
        # Durum Göstergesi
        self.lbl_info = tk.Label(left_frame, text="● Sistem Hazır", bg="#0d0e12", fg="#00ffcc", font=('Segoe UI', 10, 'italic'))
        self.lbl_info.pack(anchor=tk.W, pady=5)
        
        # Butonlar
        self.btn_play = ttk.Button(left_frame, text="▶  KUANTUM SESİ BAŞLAT", command=self.start_audio_thread)
        self.btn_play.pack(fill=tk.X, pady=5, ipady=8)
        
        self.btn_stop = ttk.Button(left_frame, text="⏹  SESİ KES", command=self.stop_audio)
        self.btn_stop.pack(fill=tk.X, pady=5, ipady=6)
        
        self.btn_export = ttk.Button(left_frame, text="📥  30sn BİLİMSEL WAV İNDİR", command=self.start_export_thread)
        self.btn_export.pack(fill=tk.X, pady=(20, 0), ipady=8)
        
        # ================= RIGHT FRAME (ATOM GÖRSELİ) =================
        right_frame = tk.Frame(main_frame, bg="#0d0e12")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Atom Çizim Tuvali (Canvas)
        self.canvas = tk.Canvas(right_frame, width=380, height=380, bg="#141722", highlightthickness=1, highlightbackground="#23283d")
        self.canvas.pack(pady=10)

    def update_element_view(self):
        """Element değiştiğinde kart bilgilerini ve Bohr atom çizimini dinamik günceller."""
        symbol = self.combo_element.get()
        info = self.element_db.get(symbol, {"name": "Bilinmeyen", "electrons": 0, "color": "#ffffff"})
        
        # Kartı güncelle
        self.lbl_card_title.config(text=f"Atom: {info['name']} ({symbol})", fg=info['color'])
        self.lbl_card_electrons.config(text=f"Toplam Elektron Sayısı: {info['electrons']}")
        
        # Canvas Çizimini Sıfırla ve Yeniden Çiz
        self.canvas.delete("all")
        cx, cy = 190, 190 # Merkez koordinatlar
        
        # Çekirdek (Nucleus) Çizimi
        self.canvas.create_oval(cx-20, cy-20, cx+20, cy+20, fill="#ff3333", outline=info['color'], width=2)
        self.canvas.create_text(cx, cy, text="+", fill="#ffffff", font=('Segoe UI', 14, 'bold'))
        
        # Bohr Yörüngeleri ve Elektron Dağıtım Simülasyonu
        electrons_left = info['electrons']
        # Bohr katman kapasiteleri sırasıyla: 2, 8, 18, 32...
        shell_capacities = [2, 8, 18, 32, 32, 18, 8] 
        radius = 45
        
        for shell_cap in shell_capacities:
            if electrons_left <= 0:
                break
                
            # Yörünge çizgisini çiz (Hafif saydam/kesikli efekt)
            self.canvas.create_oval(cx-radius, cy-radius, cx+radius, cy+radius, outline="#23283d", width=1)
            
            # Bu katmana kaç elektron yerleşecek bak
            current_shell_electrons = min(electrons_left, shell_cap)
            electrons_left -= current_shell_electrons
            
            # Elektronları yörünge dairesine eşit açılarla diz
            for e in range(current_shell_electrons):
                angle = (2 * math.pi / current_shell_electrons) * e
                ex = cx + radius * math.cos(angle)
                ey = cy + radius * math.sin(angle)
                # Küçük parlayan kuantum elektron küreleri
                self.canvas.create_oval(ex-4, ey-4, ex+4, ey+4, fill=info['color'], outline="#141722", width=1)
                
            radius += 28 # Bir sonraki katman yarıçapı

    def _process_quantum_data(self):
        self.selected_element = self.combo_element.get()
        element_json = self.loader.load_element_levels(self.selected_element)
        self.current_frequencies, self.current_amplitudes = self.converter.process_element_levels(element_json["levels"])

    def start_audio_thread(self):
        self.lbl_info.config(text="● Sıçramalar Hesaplanıyor...", fg="#ffcc00")
        
        def run():
            try:
                self._process_quantum_data()
                self.lbl_info.config(text=f"● Akor Çalınıyor: {self.selected_element}", fg="#00ffcc")
                self.synthesizer.play_element_sound(self.current_frequencies, self.current_amplitudes, duration=5.0)
                self.lbl_info.config(text="● Sistem Hazır", fg="#00ffcc")
            except Exception as e:
                messagebox.showerror("Sistem Hatası", f"Kuantum motoru hatası: {e}")
                self.lbl_info.config(text="● Hata Oluştu", fg="#ff3333")
                
        threading.Thread(target=run, daemon=True).start()

    def stop_audio(self):
        sd.stop()
        self.lbl_info.config(text="● Ses Durduruldu", fg="#ff3333")

    def start_export_thread(self):
        self.lbl_info.config(text="● 30sn Matris Taranıyor...", fg="#ffcc00")
        
        def run():
            try:
                self._process_quantum_data()
                file_output = self.exporter.export_30s_quantum_wav(self.current_frequencies, self.current_amplitudes, self.selected_element)
                
                # KLASÖRÜ BULABİLMEN İÇİN: Tam dosya yolunu (Absolute Path) alıyoruz
                kesin_yol = os.path.abspath(file_output)
                
                self.lbl_info.config(text="● Sistem Hazır", fg="#00ffcc")
                messagebox.showinfo("İndirme Başarılı", f"Kuantum ses belgesi üretildi ve direkt bu klasöre mühürlendi:\n\n{kesin_yol}\n\nBu yolu kopyalayarak dosya gezgininden anında erişebilirsiniz.")
            except Exception as e:
                messagebox.showerror("İndirme Hatası", f"WAV üretilemedi: {e}")
                self.lbl_info.config(text="● Hata Oluştu", fg="#ff3333")
                threading.Thread(target=run, daemon=True).start()