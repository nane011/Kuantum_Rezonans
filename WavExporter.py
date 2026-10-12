import numpy as np
import scipy.io.wavfile as wav
import os

class WavExporter:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate

    def export_30s_quantum_wav(self, frequencies, amplitudes, element_name):
        """
        1500 aktif kuantum sıçrama akorunu alır ve 30 saniyelik 
        saf bilimsel WAV ses dosyası olarak diske ihraç eder.
        """
        duration = 30.0
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        master_signal = np.zeros_like(t)
        
        # Dosya güvenliği için klasör kontrolü
        os.makedirs("generated", exist_ok=True)
        file_name = f"generated/{element_name}_quantum_30s.wav"
        
        # Hafif atomlarda ve ağır atomlarda 30 saniyelik süperpozisyon dalgası oluşturma
        for freq, amp in zip(frequencies, amplitudes):
            master_signal += amp * np.sin(2 * np.pi * freq * t)
            
        # Normalizasyon
        max_val = np.max(np.abs(master_signal))
        if max_val > 0:
            master_signal = master_signal / max_val
            
        # 16-bit PCM WAV formatına dönüştürme (Ses kalitesi için)
        audio_data = (master_signal * 32767).astype(np.int16)
        
        # Diske yazma işlemi
        wav.write(file_name, self.sample_rate, audio_data)

        return file_name
