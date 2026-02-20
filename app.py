import streamlit as st
import re

def parse_flashscore_universal(raw_data, team_name):
    matches = []
    # Kupa ve hazırlık maçlarını dışlamak için anahtar kelimeler
    exclude_list = ['CUP', 'KUP', 'CDR', 'CL', 'EL', 'COL', 'FA', 'DFB', 'FRI', 'HAZ']
    
    lines = raw_data.strip().split('\n')
    for line in lines:
        tarih_match = re.search(r'(\d{2}\.\d{2}\.\d{2})', line)
        if tarih_match:
            # Satırda dışlanacak kelime var mı kontrol et
            if any(exc in line.upper() for exc in exclude_list):
                continue
            
            # Skoru ve sonucu bul (Örn: 21G, 03M, 11B)
            score_match = re.search(r'(\d)(\d)[GMB]', line)
            if score_match:
                score_home = int(score_match.group(1))
                score_away = int(score_match.group(2))
                
                # Takım isminin konumuna göre ev/dep tespiti
                score_pos = line.find(score_match.group(0))
                team_pos = line.find(team_name)
                is_home = team_pos < score_pos - (len(team_name) // 2)
                
                matches.append({
                    'is_home': is_home,
                    'scored': score_home if is_home else score_away,
                    'conceded': score_away if is_home else score_home
                })
    return matches
    def calculate_metrics(h_home, h_away, a_home, a_away):
    def get_weighted_stats(match_list):
        total_fark, total_atilan, total_yenilen, total_deg = 0, 0, 0, 0
        n = len(match_list)
        for i, m in enumerate(match_list, 1):
            weight = n + 1 - i
            fark = m['scored'] - m['conceded']
            if m['scored'] > m['conceded']: fark += 1
            elif m['scored'] < m['conceded']: fark -= 1
            
            total_fark += fark * weight
            total_atilan += m['scored'] * weight
            total_yenilen += m['conceded'] * weight
            total_deg += i
        return total_fark, total_atilan, total_yenilen, total_deg

    # Her kategori için hesapla
    ee_f, ee_a, ee_y, ee_d = get_weighted_stats(h_home)
    ed_f, ed_a, ed_y, ed_d = get_weighted_stats(h_away)
    de_f, de_a, de_y, de_d = get_weighted_stats(a_home)
    dd_f, dd_a, dd_y, dd_d = get_weighted_stats(a_away)

    # Senin formüllerin
    total = (2 * ee_f) + ed_f - (2 * dd_f) - de_f
    ev_puan = (2 * ee_f + ed_f)
    dep_puan = (2 * dd_f + de_f)
    
    # Gol Atma Puanları
    ev_skor_p = (4*ee_a + 2*ed_a + de_y + dd_y*2) / (4*ee_d + 2*ed_d + de_d + dd_d*2)
    dep_skor_p = (4*dd_a + 2*de_a + ed_y + ee_y*2) / (4*dd_d + 2*de_d + ed_d + ee_d*2)

    return {
        "total": total, "evPuan": ev_puan, "depPuan": dep_puan,
        "evSkor": ev_skor_p, "depSkor": dep_skor_p,
        "ee_f": ee_f, "ed_f": ed_f, "de_f": de_f, "dd_f": dd_f
    }
    # BU SATIR DOSYANIN EN ÜSTÜNDE OLMALI (Importlardan hemen sonra)
st.set_page_config(page_title="Universal Maç Tahmin", layout="wide")

st.title("⚽ Gelişmiş Maç Tahmin Sistemi")

with st.sidebar:
    st.header("📊 Maç Adetleri")
    ee_n = st.number_input("Ev - İç Saha", 1, 10, 3)
    ed_n = st.number_input("Ev - Dış Saha", 1, 10, 3)
    de_n = st.number_input("Dep - İç Saha", 1, 10, 3)
    dd_n = st.number_input("Dep - Dış Saha", 1, 10, 3)

c1, c2 = st.columns(2)
with c1:
    h_name = st.text_input("Ev Takımı Adı", "Ath. Bilbao")
    h_data = st.text_area("Ev Takımı Son Maçlar (Flashscore)", height=200)
with c2:
    a_name = st.text_input("Deplasman Takımı Adı", "Real Sociedad")
    a_data = st.text_area("Deplasman Takımı Son Maçlar (Flashscore)", height=200)

if st.button("HESAPLA"):
    if h_data and a_data:
        h_res = parse_flashscore_universal(h_data, h_name)
        a_res = parse_flashscore_universal(a_data, a_name)
        
        h_home = [m for m in h_res if m['is_home']][:ee_n]
        h_away = [m for m in h_res if not m['is_home']][:ed_n]
        a_home = [m for m in a_res if m['is_home']][:de_n]
        a_away = [m for m in a_res if not m['is_home']][:dd_n]

        if len(h_home) < ee_n or len(h_away) < ed_n or len(a_home) < de_n or len(a_away) < dd_n:
            st.error("⚠️ Yetersiz lig maçı verisi! Lütfen daha fazla maç geçmişi yapıştırın.")
        else:
            res = calculate_metrics(h_home, h_away, a_home, a_away)
            
            # Karar
            if res['total'] > 2: st.success(f"✅ {h_name} BAS KARSIIM")
            elif res['total'] < -2: st.warning(f"🚀 SERİ {a_name} BASS")
            else: st.info("⚖️ BERABERE OLUR GİBİ MORUK")

            # Metrikler
            m1, m2, m3 = st.columns(3)
            m1.metric("Genel Total", f"{res['total']}")
            m2.metric(f"{h_name} Gol Puanı", f"{res['evSkor']:.2f}")
            m3.metric(f"{a_name} Gol Puanı", f"{res['depSkor']:.2f}")
            
            st.write(f"**Detaylar:** Ev İç(x2): {res['ee_f']*2} | Ev Dış: {res['ed_f']} | Dep İç: {res['de_f']} | Dep Dış(x2): {res['dd_f']*2}")
