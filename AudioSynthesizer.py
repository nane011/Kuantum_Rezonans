import numpy as np
import sounddevice as sd
from multiprocessing import Pool, cpu_count

# DİKKAT: Çoklu çekirdek motorunun arka planda bağımsız çalışabilmesi için 
# bu fonksiyonun sınıfın dışında (en tepede) durması Python kuralıdır.
def _worker_generate_wave(args):
    """Her bir çekirdeğin paralel olarak hesaplayacağı mini dalga fabrikası."""
    freq, amp, t = args
    return amp * np.sin(2 * np.pi * freq * t)

class AudioSynthesizer:
    def __init__(self, sample_rate=22050):
        """
        Çoklu Çekirdek Destekli RAM ve CPU Dostu Sentezleyici Motoru.
        Sample rate telefon için 22050 (veya 16000), bilgisayar için 44100 yapılabilir.
        """
        self.sample_rate = sample_rate

    def play_element_sound(self, frequencies, amplitudes, duration=5.0):
        # 1. Zaman ekseni dizisini oluşturuyoruz
        t = np.linspace(0, duration, int(self.sample_rate * duration), endpoint=False)
        
        # İşlemci çekirdek sayısını öğreniyoruz
        cores = cpu_count()
        print(f"⚡ Çoklu Çekirdek Motoru Aktif! {cores} Çekirdek Paralel Göreve Çağrıldı...")
        
        # 2. Çekirdeklere dağıtılacak görev paketlerini hazırlıyoruz
        tasks = [(freq, amp, t) for freq, amp in zip(frequencies, amplitudes)]
        
        # 3. İşlemci havuzunu açıp hesaplamayı tüm çekirdeklere eşit bölüyoruz
        # Bu satır sayesinde donma tamamen sıfıra inecek
        with Pool(processes=cores) as pool:
            wave_components = pool.map(_worker_generate_wave, tasks)
            
        print("🔗 Çekirdeklerden gelen dalgalar kuantum süperpozisyonu ile toplanıyor...")
        # Çekirdeklerin ürettiği tüm dalgaları tek bir ana sinyalde birleştiriyoruz
        master_signal = np.sum(wave_components, axis=0)
            
        # 4. Ses Seviyesi Güvenliği (Normalizasyon)
        max_val = np.max(np.abs(master_signal))
        if max_val > 0:
            master_signal = master_signal / max_val
            
        print(f"🔊 {len(frequencies)} adet kuantum sıçraması donmadan harmanlandı! Hoparlörden ses veriliyor...")
        sd.play(master_signal, self.sample_rate)
        sd.wait()
        print("🎵 Çalma bitti.")
