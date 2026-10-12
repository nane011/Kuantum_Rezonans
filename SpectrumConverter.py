import numpy as np

class SpectrumConverter:
    def __init__(self, audio_min_hz=60.0, audio_max_hz=4000.0):
        self.C_CM_S = 29979245800.0
        self.AUDIO_MIN_HZ = audio_min_hz
        self.AUDIO_MAX_HZ = audio_max_hz

    def process_element_levels(self, levels_list):
        """
        %100 REALİSTİK VEKTÖREL KUANTUM SIÇRAMA MOTORU
        """
        # 1. Verileri NumPy dizilerine alıyoruz
        levels_cm1 = np.array([level["level_cm1"] for level in levels_list])
        aki_values = np.array([level.get("transition_probability_Aki", 0.0) for level in levels_list])
        
        # 2. ADIM: SIFIRLARI 1.0 YAPMAYI BIRAK, TAMAMEN SİL (Kuantum Filtrelemesi)
        # Sadece geçiş olasılığı (Aki) 0.0'dan büyük olan seviyeleri maske kullanarak hayatta tutuyoruz.
        # İlk taban seviye (0.0 cm⁻¹) uyarılma başlangıcı olduğu için onu koruyoruz, diğer Aki'si 0 olanları eliyoruz.
        active_mask = (aki_values > 0.0) | (levels_cm1 == 0.0)
        
        levels_cm1 = levels_cm1[active_mask]
        aki_values = aki_values[active_mask]
        
        if len(levels_cm1) < 2:
            # Eğer filtrelendikten sonra sıçrama yapacak yeterli seviye kalmadıysa varsayılan döndür
            return np.array([self.AUDIO_MIN_HZ]), np.array([1.0])

        # 3. ADIM: np.subtract.outer() İLE VEKTÖREL ENERJİ FARKI MATRİSİ (ΔE)
        # Hiçbir döngü yazmadan, tek bir milisaniyede tüm seviyelerin birbiriyle farkını alır.
        # delta_E_matrix[i, j] = levels_cm1[i] - levels_cm1[j] değerini üretir.
        delta_E_matrix = np.subtract.outer(levels_cm1, levels_cm1)
        
        # Fizik Kuralı: Elektron sadece yüksek enerjiden düşük enerjiye düşerken foton fırlatır (Sıçrama).
        # Bu yüzden matrisin sadece pozitif (0'dan büyük) olan farklarını filtreleyip düz bir listeye alıyoruz.
        sıçrama_mask = delta_E_matrix > 0.0
        active_transitions_cm1 = delta_E_matrix[sıçrama_mask]
        
        # 4. Gerçek Işık Frekanslarını Hesaplama (f = ΔE * c)
        light_frequencies = active_transitions_cm1 * self.C_CM_S
        
        min_light = np.min(light_frequencies)
        max_light = np.max(light_frequencies)
        
        # 5. Logaritmik Haritalama (İşitilebilir Hz Sınırlarına Ölçekleme)
        light_freq_safe = np.maximum(light_frequencies, 1e-5)
        min_light_safe = max(min_light, 1e-5)
        max_light_safe = max(max_light, 1e-5)
        
        log_current = np.log10(light_freq_safe)
        log_min = np.log10(min_light_safe)
        log_max = np.log10(max_light_safe)
        
        if log_max == log_min:
            normalized = np.zeros_like(log_current)
        else:
            normalized = (log_current - log_min) / (log_max - log_min)
            
        log_audio = np.log10(self.AUDIO_MIN_HZ) + (normalized * (np.log10(self.AUDIO_MAX_HZ) - np.log10(self.AUDIO_MIN_HZ)))
        audio_frequencies = 10 ** log_audio
        
        # 6. Realistik Genlik (Şiddet) Hesaplama
        # Her bir sıçramanın şiddetini, o sıçramayı yapan üst seviyenin Aki olasılığı belirler.
        # Sıçrama matrisinin koordinatlarına denk gelen Aki değerlerini vektörel olarak eşliyoruz.
        upper_level_indices = np.where(sıçrama_mask)[0]
        transition_akis = aki_values[upper_level_indices]
        
        max_aki = np.max(transition_akis) if np.max(transition_akis) > 0 else 1.0
        amplitudes = transition_akis / max_aki
        
        # Harmonik sönümlenme payı ekleme
        sönümlenme = 1.0 / (np.arange(len(audio_frequencies)) + 1)
        amplitudes = amplitudes * sönümlenme

        if len(audio_frequencies) > 500:
            idx_baskin = np.argsort(amplitudes)[-1500:] # En güçlü 1500 geçişin indeksini bulur
            audio_frequencies = audio_frequencies[idx_baskin]
            amplitudes = amplitudes[idx_baskin]

        return audio_frequencies, amplitudes
