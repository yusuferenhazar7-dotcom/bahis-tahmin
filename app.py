import streamlit as st
import re
import numpy as np
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="ProMatch Predictor", layout="wide")
st.title("⚽ Gelişmiş Maç Tahmin ve Simülasyon Portalı")
st.markdown("Flashscore verilerini yapıştırın ve ağırlıklı algoritma ile sonucu görün.")

# --- FONKSİYONLAR ---
def veri_ayikla_gelismis(metin, takim_adi):
    if not metin: return []
    satirlar = metin.strip().split('\n')
    lig_maclari = []
    # Yaygın lig kısaltmaları
    lig_kodlari = ["LL", "TSL", "EPL", "SA", "BL", "L1", "TFF"]
    
    for i in range(len(satirlar)):
        satir = satirlar[i]
        if any(lig in satir for lig in lig_kodlari):
            try:
                # Skor ayıklama (Örn: 12G)
                skor_match = re.search(r'(\d)(\d)', satirlar[i+2])
                if skor_match:
                    g1, g2 = int(skor_match.group(1)), int(skor_match.group(2))
                    ev_takim = satirlar[i+1].strip()
                    is_home = takim_adi.lower() in ev_takim.lower()
                    lig_maclari.append({
                        'is_home': is_home,
                        'attigi': g1 if is_home else g2,
                        'yedigi': g2 if is_home else g1
                    })
            except:
                continue
    return lig_maclari

def monte_carlo_sim(ev_lambda, dep_lambda):
    sim_sayisi = 10000
    ev_goller = np.random.poisson(ev_lambda, sim_sayisi)
    dep_goller = np.random.poisson(dep_lambda, sim_sayisi)
    
    ev_gal = np.sum(ev_goller > dep_goller)
    berabere = np.sum(ev_goller == dep_goller)
    dep_gal = np.sum(ev_goller < dep_goller)
    
    return (ev_gal/sim_sayisi, berabere/sim_sayisi, dep_gal/sim_sayisi)

# --- ARAYÜZ / SIDEBAR ---
with st.sidebar:
    st.header("Takım Bilgileri")
    ev_ad = st.text_input("Ev Sahibi Takım", "Ath. Bilbao")
    dep_ad = st.text_input("Deplasman Takımı", "Real Sociedad")
    st.divider()
    st.info("Flashscore'dan 'Son Karşılaşmalar' kısmını kopyalayıp sağdaki kutulara yapıştırın.")

# --- ANA PANEL ---
col1, col2 = st.columns(2)

with col1:
    ev_raw = st.text_area(f"{ev_ad} Son 10 Maç Verisi", height=200)
with col2:
    dep_raw = st.text_area(f"{dep_ad} Son 10 Maç Verisi", height=200)

if st.button("ANALİZİ BAŞLAT"):
    if ev_raw and dep_raw:
        # Verileri İşle
        ev_verileri = veri_ayikla_gelismis(ev_raw, ev_ad)
        dep_verileri = veri_ayikla_gelismis(dep_raw, dep_ad)
        
        # Filtreleme (Ev/Dep ayrımı)
        ee_maclar = [m for m in ev_verileri if m['is_home']][:3]
        ed_maclar = [m for m in ev_verileri if not m['is_home']][:3]
        de_maclar = [m for m in dep_verileri if m['is_home']][:3]
        dd_maclar = [m for m in dep_verileri if not m['is_home']][:3]

        if len(ee_maclar) < 3 or len(dd_maclar) < 3:
            st.error("⚠️ Yetersiz veri! En az 3 ev/deplasman lig maçı gerekiyor.")
        else:
            # Senin Ağırlıklı Hesaplama Mantığın
            def hesapla_metrikler(maclar):
                total, atilan, yenilen, degisken = 0, 0, 0, 0
                N = len(maclar)
                for i, m in enumerate(maclar, 1):
                    fark = (m['attigi'] - m['yedigi']) + (1 if m['attigi'] > m['yedigi'] else (-1 if m['attigi'] < m['yedigi'] else 0))
                    carpan = (N + 1 - i)
                    total += fark * carpan
                    atilan += m['attigi'] * carpan
                    yenilen += m['yedigi'] * carpan
                    degisken += i
                return total, atilan, yenilen, degisken

            eeT, eeA, eeY, eeD = hesapla_metrikler(ee_maclar)
            edT, edA, edY, edD = hesapla_metrikler(ed_maclar)
            deT, deA, deY, deD = hesapla_metrikler(de_maclar)
            ddT, ddA, ddY, ddD = hesapla_metrikler(dd_maclar)

            total_skor = (2*eeT) + (edT) - (2*ddT) - (deT)
            ev_puan = (4*eeA + 2*edA + deY + ddY*2) / (4*eeD + 2*edD + deD + ddD*2)
            dep_puan = (4*ddA + 2*deA + edY + eeY*2) / (4*ddD + 2*deD + edD + eeD*2)

            # --- SONUÇ GÖSTERİMİ ---
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Analiz Skoru", round(total_skor, 2))
            c2.metric(f"{ev_ad} Gücü", round(ev_puan, 2))
            c3.metric(f"{dep_ad} Gücü", round(dep_puan, 2))

            # Karar
            if total_skor > 2:
                st.success(f"🔥 ÖNERİ: {ev_ad} BAS KARŞİİM")
            elif total_skor < -2:
                st.success(f"🚀 ÖNERİ: SERİ {dep_ad} BASS")
            else:
                st.warning("😐 DURUM: Berabere biter gibi moruk, riskli.")

            # Simülasyon
            ev_o, ber_o, dep_o = monte_carlo_sim(ev_puan, dep_puan)
            
            st.subheader("🎲 Monte Carlo Simülasyon Tahminleri")
            sim_data = pd.DataFrame({
                "Sonuç": [ev_ad, "Beraberlik", dep_ad],
                "Olasılık": [ev_o, ber_o, dep_o]
            })
            st.bar_chart(sim_data.set_index("Sonuç"))
    else:
        st.info("Lütfen her iki takımın da verilerini yapıştırın.")
