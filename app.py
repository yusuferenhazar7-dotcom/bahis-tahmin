import streamlit as st
import re

# 1. SAYFA AYARLARI (GİRİNTİSİZ - EN ÜSTTE OLMALI)
st.set_page_config(page_title="Gelişmiş Maç Tahmin", layout="wide")

# 2. DİKEY VERİ OKUYUCU (FLASH SCORE İÇİN ÖZEL)
def parse_flashscore_data(raw_data, team_name):
    matches = []
    exclude = ['CUP', 'KUP', 'CDR', 'CL', 'EL', 'COL', 'FA', 'DFB', 'FRI', 'HAZ']
    lines = [l.strip() for l in raw_data.split('\n') if l.strip()]
    
    # G/M/B harflerini referans noktası alarak yukarı doğru tarama yapar
    for i in range(len(lines)):
        if lines[i] in ['G', 'M', 'B']:
            try:
                # Sonucun (G/M/B) hemen üzerindeki iki sayı skordur
                s1 = int(lines[i-2])
                s2 = int(lines[i-1])
                
                # Kupa maçlarını ele
                context_lines = lines[max(0, i-10):i]
                if any(exc in " ".join(context_lines).upper() for exc in exclude):
                    continue
                
                # Takım isminin konumunu bul
                # Veride takım ismi skorun üstünde ise: [Ev Takımı, Deplasman Takımı, Skor1, Skor2, Sonuç]
                # Bu dikey formatta takım isminin listedeki sırası ev/dep olduğunu belirler
                found_team = False
                is_home = False
                
                for j in range(1, 6): # Geriye dönük 5 satırı tara
                    prev_line = lines[i-j-2].lower() # Skorların üstündeki satırlar
                    if team_name.lower() in prev_line:
                        # Eğer takım ismi 2. skora daha yakınsa deplasmandır
                        # Basit ve etkili mantık: Girdiğin isim metinde geçiyorsa yakala
                        found_team = True
                        # Flashscore dikey kopyada: Ev \n Dep \n Skor1 \n Skor2
                        # Eğer girdiğin isim 'Ev' ise i-4 veya i-5 civarıdır
                        if team_name.lower() in lines[i-4].lower():
                            is_home = True
                        else:
                            is_home = False
                        break
                
                if found_team:
                    matches.append({
                        'is_home': is_home,
                        'scored': s1 if is_home else s2,
                        'conceded': s2 if is_home else s1
                    })
            except:
                continue
    return matches

# 3. HESAPLAMA MANTIĞI
def calculate_metrics(h_h, h_a, a_h, a_a):
    def get_weighted(match_list):
        total_f, total_a, total_y, total_d = 0, 0, 0, 0
        n = len(match_list)
        for i, m in enumerate(match_list, 1):
            w = n + 1 - i
            f = m['scored'] - m['conceded']
            if m['scored'] > m['conceded']: f += 1
            elif m['scored'] < m['conceded']: f -= 1
            total_f += f * w
            total_a += m['scored'] * w
            total_y += m['conceded'] * w
            total_d += i
        return total_f, total_a, total_y, total_d

    ee_f, ee_a, ee_y, ee_d = get_weighted(h_h)
    ed_f, ed_a, ed_y, ed_d = get_weighted(h_a)
    de_f, de_a, de_y, de_d = get_weighted(a_h)
    dd_f, dd_a, dd_y, dd_d = get_weighted(a_a)

    total = (2 * ee_f) + ed_f - (2 * dd_f) - de_f
    
    payda_e = (4*ee_d + 2*ed_d + de_d + dd_d*2)
    payda_d = (4*dd_d + 2*de_d + ed_d + ee_d*2)
    
    skor_e = (4*ee_a + 2*ed_a + de_y + dd_y*2) / payda_e if payda_e > 0 else 0
    skor_d = (4*dd_a + 2*de_a + ed_y + ee_y*2) / payda_d if payda_d > 0 else 0

    return {"total": total, "skor_e": skor_e, "skor_d": skor_d}

# 4. ARAYÜZ
st.title("⚽ Gelişmiş Maç Tahmin Sistemi")

with st.sidebar:
    st.header("📊 Ayarlar")
    n_ee = st.number_input("Ev İç Saha", 1, 10, 3)
    n_ed = st.number_input("Ev Dış Saha", 1, 10, 3)
    n_de = st.number_input("Dep İç Saha", 1, 10, 3)
    n_dd = st.number_input("Dep Dış Saha", 1, 10, 3)

c1, c2 = st.columns(2)
with c1:
    h_name = st.text_input("Ev Takımı", "Ath. Bilbao")
    h_data = st.text_area("Ev Verisi (Flashscore)", height=250)
with c2:
    a_name = st.text_input("Deplasman Takımı", "Real Sociedad")
    a_data = st.text_area("Deplasman Verisi (Flashscore)", height=250)

if st.button("HESAPLA"):
    if h_data and a_data:
        h_res = parse_flashscore_data(h_data, h_name)
        a_res = parse_flashscore_data(a_data, a_name)
        
        h_h = [m for m in h_res if m['is_home']][:n_ee]
        h_a = [m for m in h_res if not m['is_home']][:n_ed]
        a_h = [m for m in a_res if m['is_home']][:n_de]
        a_a = [m for m in a_res if not m['is_home']][:n_dd]

        if len(h_h) < n_ee or len(h_a) < n_ed or len(a_h) < n_de or len(a_a) < n_dd:
            st.error(f"Yetersiz Veri! \n Bulunan -> Ev İç:{len(h_h)}, Ev Dış:{len(h_a)}, Dep İç:{len(a_h)}, Dep Dış:{len(a_a)}")
            st.info("İpucu: Takım isimlerinin kutucuklara yazdığınızla aynı olduğundan (Örn: Real Sociedad) ve kopyaladığınız metinde bu ismin geçtiğinden emin olun.")
        else:
            res = calculate_metrics(h_h, h_a, a_h, a_a)
            if res['total'] > 2: st.success(f"🔥 {h_name} BAS KARSIIM")
            elif res['total'] < -2: st.warning(f"✈️ SERİ {a_name} BASS")
            else: st.info("⚖️ BERABERE OLABİLİR")
            
            col1, col2 = st.columns(2)
            col1.metric("Genel Total", f"{res['total']}")
            col2.write(f"**Gol Gücü:** \n {h_name}: {res['skor_e']:.2f} \n {a_name}: {res['skor_d']:.2f}")
