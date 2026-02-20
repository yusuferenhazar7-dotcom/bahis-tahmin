import streamlit as st
import re

# 1. SAYFA AYARLARI (GİRİNTİSİZ - EN ÜSTTE)
st.set_page_config(page_title="Gelişmiş Maç Tahmin", layout="wide")

# 2. GELİŞMİŞ VERİ AYRIŞTIRICI (DİKEY FORMAT DESTEKLİ)
def parse_flashscore_data(raw_data, team_name):
    matches = []
    # Kupa/Hazırlık kelimeleri
    exclude = ['CUP', 'KUP', 'CDR', 'CL', 'EL', 'COL', 'FA', 'DFB', 'FRI', 'HAZ']
    
    # Veriyi satırlara böl ve temizle
    lines = [l.strip() for l in raw_data.split('\n') if l.strip()]
    
    # Dikey veriyi tarayarak maçları bul
    for i in range(len(lines)):
        # Satırda G, M veya B sonucu varsa, bir önceki satırlarda skor ve takım aramaya başla
        if lines[i] in ['G', 'M', 'B']:
            try:
                # G/M/B'den hemen önceki iki satır skorlardır (Genelde i-1 ve i-2)
                s1 = int(lines[i-2])
                s2 = int(lines[i-1])
                
                # Takım ismi G/M/B'den önceki 3. veya 4. satırda olabilir
                # Bu kontrolü kupa maçlarını elemek için yapıyoruz
                is_kupa = False
                for j in range(1, 6):
                    if i-j >= 0 and any(exc in lines[i-j].upper() for exc in exclude):
                        is_kupa = True
                
                if not is_kupa:
                    # Basit Mantık: Eğer takım ismi skordan hemen önceyse EV, değilse DEP
                    # Flashscore dikey kopyada takım ismi genellikle skorun üstündedir
                    # Senin girdiğin takım ismi i-3 veya i-4'te mi?
                    context = " ".join(lines[max(0, i-6):i]).lower()
                    
                    if team_name.lower() in context:
                        # Takım isminin pozisyonuna göre ev/dep tespiti
                        # Eğer takım ismi 1. skordan önceyse ev sahibi
                        team_idx = context.find(team_name.lower())
                        score_idx = context.find(str(s1))
                        
                        is_home = team_idx < score_idx
                        
                        matches.append({
                            'is_home': is_home,
                            'scored': s1 if is_home else s2,
                            'conceded': s2 if is_home else s1
                        })
            except (ValueError, IndexError):
                continue
                
    return matches

# 3. HESAPLAMA MANTIĞI
def calculate_metrics(h_home, h_away, a_home, a_away):
    def get_weighted(match_list):
        total_f, total_a, total_y, total_d = 0, 0, 0, 0
        n = len(match_list)
        for i, m in enumerate(match_list, 1):
            w = n + 1 - i
            fark = m['scored'] - m['conceded']
            if m['scored'] > m['conceded']: fark += 1
            elif m['scored'] < m['conceded']: fark -= 1
            total_f += fark * w
            total_a += m['scored'] * w
            total_y += m['conceded'] * w
            total_d += i
        return total_f, total_a, total_y, total_d

    ee_f, ee_a, ee_y, ee_d = get_weighted(h_home)
    ed_f, ed_a, ed_y, ed_d = get_weighted(h_away)
    de_f, de_a, de_y, de_d = get_weighted(a_home)
    dd_f, dd_a, dd_y, dd_d = get_weighted(a_away)

    total = (2 * ee_f) + ed_f - (2 * dd_f) - de_f
    ev_payda = (4*ee_d + 2*ed_d + de_d + dd_d*2)
    dep_payda = (4*dd_d + 2*de_d + ed_d + ee_d*2)
    
    ev_skor = (4*ee_a + 2*ed_a + de_y + dd_y*2) / ev_payda if ev_payda > 0 else 0
    dep_skor = (4*dd_a + 2*de_a + ed_y + ee_y*2) / dep_payda if dep_payda > 0 else 0

    return {"total": total, "evSkor": ev_skor, "depSkor": dep_skor}

# 4. ARAYÜZ
st.title("⚽ Gelişmiş Maç Tahmin Sistemi")

with st.sidebar:
    st.header("📊 Maç Adetleri")
    n_ee = st.number_input("Ev - İç Saha", 1, 10, 3)
    n_ed = st.number_input("Ev - Dış Saha", 1, 10, 3)
    n_de = st.number_input("Dep - İç Saha", 1, 10, 3)
    n_dd = st.number_input("Dep - Dış Saha", 1, 10, 3)

c1, c2 = st.columns(2)
with c1:
    h_name = st.text_input("Ev Takımı", "Ath. Bilbao")
    h_data = st.text_area("Ev Verisi (Flashscore)", height=200)
with c2:
    a_name = st.text_input("Deplasman Takımı", "Real Sociedad")
    a_data = st.text_area("Deplasman Verisi (Flashscore)", height=200)

if st.button("HESAPLA"):
    if h_data and a_data:
        h_res = parse_flashscore_data(h_data, h_name)
        a_res = parse_flashscore_data(a_data, a_name)
        
        h_h = [m for m in h_res if m['is_home']][:n_ee]
        h_a = [m for m in h_res if not m['is_home']][:n_ed]
        a_h = [m for m in a_res if m['is_home']][:n_de]
        a_a = [m for m in a_res if not m['is_home']][:n_dd]

        if len(h_h) < n_ee or len(h_a) < n_ed or len(a_h) < n_de or len(a_a) < n_dd:
            st.error(f"Yetersiz Veri! Bulunan -> Ev İç:{len(h_h)}, Ev Dış:{len(h_a)}, Dep İç:{len(a_h)}, Dep Dış:{len(a_a)}")
        else:
            res = calculate_metrics(h_h, h_a, a_h, a_a)
            if res['total'] > 2: st.success(f"🔥 {h_name} BAS KARSIIM")
            elif res['total'] < -2: st.warning(f"✈️ SERİ {a_name} BASS")
            else: st.info("⚖️ BERABERE OLABİLİR")
            
            st.metric("Genel Total", f"{res['total']}")
            st.write(f"{h_name} Gol Gücü: {res['evSkor']:.2f} | {a_name} Gol Gücü: {res['depSkor']:.2f}")
