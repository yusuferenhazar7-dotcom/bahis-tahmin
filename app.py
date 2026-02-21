import re

def veri_ayikla(metin, takim_adi):
    # Satırları parçala
    satirlar = metin.strip().split('\n')
    lig_maclari = []
    
    # Flashscore formatındaki tarih ve lig kodlarını yakalamak için basit bir döngü
    # Genelde format: Tarih + Lig Kısaltması + Ev Sahibi + Skor + Deplasman + Sonuç
    
    for i in range(len(satirlar)):
        satir = satirlar[i]
        # Sadece lig maçlarını (LL, TSL, EPL vb.) al, kupa kısaltmalarını (CDR, CL, FA) dışla
        # Flashscore kopyalamasında lig kodu genelde tarihin hemen yanındadır (örn: 15.02.26LL)
        if "LL" in satir or "TSL" in satir or "EPL" in satir or "SA" in satir or "BL" in satir: 
            try:
                # Takım isimlerini ve skorları bir sonraki satırlardan veya aynı satırdan çekme simülasyonu
                # Kopyalanan metin yapısına göre regex ile skorları (Örn: 12G veya 1-2) ayıklıyoruz
                skor_match = re.search(r'(\d)(\d)', satirlar[i+2])
                if skor_match:
                    ev_gol = int(skor_match.group(1))
                    dep_gol = int(skor_match.group(2))
                    
                    ev_takim = satirlar[i+1].strip()
                    dep_takim = satirlar[i+3].strip() if i+3 < len(satirlar) else ""

                    is_home = takim_adi.lower() in ev_takim.lower()
                    
                    lig_maclari.append({
                        'is_home': is_home,
                        'attigi': ev_gol if is_home else dep_gol,
                        'yedigi': dep_gol if is_home else ev_gol
                    })
            except:
                continue
                
    return lig_maclari
    def hesapla_ve_kontrol_et(ev_sahibi_adi, ev_metin, deplasman_adi, dep_metin):
    ev_verileri = veri_ayikla(ev_metin, ev_sahibi_adi)
    dep_verileri = veri_ayikla(dep_metin, deplasman_adi)
    
    # Ev sahibinin son 3 İÇ SAHA maçı
    ev_ic_saha = [m for m in ev_verileri if m['is_home']][:3]
    
    # Deplasman takımının son 3 DIŞ SAHA maçı
    dep_dis_saha = [m for m in dep_verileri if not m['is_home']][:3]
    
    hata = False
    if len(ev_ic_saha) < 3:
        print(f"⚠️ UYARI: {ev_sahibi_adi} için yeterli ev sahibi lig maçı bulunamadı! (Bulunan: {len(ev_ic_saha)})")
        hata = True
    if len(dep_dis_saha) < 3:
        print(f"⚠️ UYARI: {deplasman_adi} için yeterli deplasman lig maçı bulunamadı! (Bulunan: {len(dep_dis_saha)})")
        hata = True
        
    if hata:
        print("❌ Lütfen Flashscore'dan daha fazla maç verisi (Daha fazla göster'e basarak) kopyalayıp tekrar yapıştırın.")
        return None
    
    # Ortalama Hesaplama (Buraya kendi özel formülünü de ekleyebilirsin)
    ev_at_ort = sum(m['attigi'] for m in ev_ic_saha) / 3
    ev_ye_ort = sum(m['yedigi'] for m in ev_ic_saha) / 3
    dep_at_ort = sum(m['attigi'] for m in dep_dis_saha) / 3
    dep_ye_ort = sum(m['yedigi'] for m in dep_dis_saha) / 3
    
    return {
        'ev_hucum': ev_at_ort, 'ev_defans': ev_ye_ort,
        'dep_hucum': dep_at_ort, 'dep_defans': dep_ye_ort
    }
    # --- VERİ GİRİŞ ALANI ---
ev_sahibi_isimi = "Ath. Bilbao"
deplasman_isimi = "Real Sociedad"

# Buraya Flashscore'dan kopyaladığın metni yapıştır
ev_sahibi_raw_veri = """
15.02.26LLOviedo Ath. Bilbao 12G
08.02.26LLAth. Bilbao Levante 42G
01.02.26LLAth. Bilbao Real Sociedad 11B
24.01.26LLSevilla Ath. Bilbao 21M
"""

dep_takim_raw_veri = """
11.02.26CDRAth. Bilbao Real Sociedad 01M
01.02.26LLAth. Bilbao Real Sociedad 11B
25.01.26LLReal Sociedad Getafe 20G
18.01.26LLValencia Real Sociedad 12G
"""
# ------------------------

sonuc = hesapla_ve_kontrol_et(ev_sahibi_isimi, ev_sahibi_raw_veri, deplasman_isimi, dep_takim_raw_veri)

if sonuc:
    print(f"--- {ev_sahibi_isimi} vs {deplasman_isimi} Analizi ---")
    print(f"Ev Sahibi Gol Atma Ort (Son 3 Ev): {sonuc['ev_hucum']:.2f}")
    print(f"Ev Sahibi Gol Yeme Ort (Son 3 Ev): {sonuc['ev_defans']:.2f}")
    print(f"Deplasman Gol Atma Ort (Son 3 Dep): {sonuc['dep_hucum']:.2f}")
    print(f"Deplasman Gol Yeme Ort (Son 3 Dep): {sonuc['dep_defans']:.2f}")
    # Buradan sonra kendi tahmin kodunu/mantığını sonuc['...'] verilerini kullanarak ekleyebiliriz.
    import re

def veri_ayikla_gelismis(metin, takim_adi):
    satirlar = metin.strip().split('\n')
    lig_maclari = []
    
    # Maç verilerini ayıklama
    for i in range(len(satirlar)):
        satir = satirlar[i]
        # Lig maçlarını filtrele (Ligue 1, Süper Lig, Premier League vb.)
        if any(lig in satir for lig in ["LL", "TSL", "EPL", "SA", "BL", "L1"]): 
            try:
                # Skor bulma (Örn: 12G veya 42G gibi bitişik sayıları yakalar)
                skor_match = re.search(r'(\d)(\d)', satirlar[i+2])
                if skor_match:
                    g1 = int(skor_match.group(1))
                    g2 = int(skor_match.group(2))
                    
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
    def algoritma_hesapla(ev_ad, ev_raw, dep_ad, dep_raw):
    # Verileri ayıkla
    ev_verileri = veri_ayikla_gelismis(ev_raw, ev_ad)
    dep_verileri = veri_ayikla_gelismis(dep_raw, dep_ad)
    
    # Senin değişkenlerin (Ev Sahibi için)
    ev_ev_maclar = [m for m in ev_verileri if m['is_home']]
    ev_dep_maclar = [m for m in ev_verileri if not m['is_home']]
    
    # Senin değişkenlerin (Deplasman Takımı için)
    dep_ev_maclar = [m for m in dep_verileri if m['is_home']]
    dep_dep_maclar = [m for m in dep_verileri if not m['is_home']]

    # Yeterlilik kontrolü (Senin istediğin uyarı mekanizması)
    if len(ev_ev_maclar) < 3 or len(ev_dep_maclar) < 3 or len(dep_ev_maclar) < 3 or len(dep_dep_maclar) < 3:
        print("⚠️ EKSİK VERİ UYARISI!")
        print(f"{ev_ad} -> Ev: {len(ev_ev_maclar)}, Dep: {len(ev_dep_maclar)}")
        print(f"{dep_ad} -> Ev: {len(dep_ev_maclar)}, Dep: {len(dep_dep_maclar)}")
        print("Lütfen daha fazla maç verisi yükleyin.")
        return

    # Değişkenleri sıfırla
    evEvTotal, evDepTotal, depEvTotal, depDepTotal = 0, 0, 0, 0
    evEvAtilanTotal, evEvYenilenTotal, evDepAtilanTotal, evDepYenilenTotal = 0, 0, 0, 0
    depEvAtilanTotal, depEvYenilenTotal, depDepAtilanTotal, depDepYenilenTotal = 0, 0, 0, 0
    evEvDegiskeniToplami, evDepDegiskeniToplami, depEvDegiskeniToplami, depDepDegiskeniToplami = 0, 0, 0, 0

    # 1. Ev Takımının Ev Maçları
    N = len(ev_ev_maclar)
    for i, m in enumerate(ev_ev_maclar[:N], 1):
        fark = m['attigi'] - m['yedigi']
        fark += 1 if m['attigi'] > m['yedigi'] else (-1 if m['attigi'] < m['yedigi'] else 0)
        carpan = (N + 1 - i)
        evEvTotal += fark * carpan
        evEvAtilanTotal += m['attigi'] * carpan
        evEvYenilenTotal += m['yedigi'] * carpan
        evEvDegiskeniToplami += i

    # 2. Ev Takımının Dep Maçları
    N = len(ev_dep_maclar)
    for i, m in enumerate(ev_dep_maclar[:N], 1):
        fark = m['attigi'] - m['yedigi']
        fark += 1 if m['attigi'] > m['yedigi'] else (-1 if m['attigi'] < m['yedigi'] else 0)
        carpan = (N + 1 - i)
        evDepTotal += fark * carpan
        evDepAtilanTotal += m['attigi'] * carpan
        evDepYenilenTotal += m['yedigi'] * carpan
        evDepDegiskeniToplami += i

    # ... (Aynı mantık Deplasman Takımı için de uygulanır)
    # 3. Dep Takımının Ev Maçları
    N = len(dep_ev_maclar)
    for i, m in enumerate(dep_ev_maclar[:N], 1):
        fark = m['attigi'] - m['yedigi']
        fark += 1 if m['attigi'] > m['yedigi'] else (-1 if m['attigi'] < m['yedigi'] else 0)
        carpan = (N + 1 - i)
        depEvTotal += fark * carpan
        depEvAtilanTotal += m['attigi'] * carpan
        depEvYenilenTotal += m['yedigi'] * carpan
        depEvDegiskeniToplami += i

    # 4. Dep Takımının Dep Maçları
    N = len(dep_dep_maclar)
    for i, m in enumerate(dep_dep_maclar[:N], 1):
        fark = m['attigi'] - m['yedigi']
        fark += 1 if m['attigi'] > m['yedigi'] else (-1 if m['attigi'] < m['yedigi'] else 0)
        carpan = (N + 1 - i)
        depDepTotal += fark * carpan
        depDepAtilanTotal += m['attigi'] * carpan
        depDepYenilenTotal += m['yedigi'] * carpan
        depDepDegiskeniToplami += i

    # FINAL HESAPLAMALARIN (Senin Formülün)
    total = (2*evEvTotal) + (evDepTotal) - (2*depDepTotal) - (depEvTotal)
    evTakimiSkorPuani = (4*evEvAtilanTotal + 2*evDepAtilanTotal + depEvYenilenTotal + depDepYenilenTotal*2) / \
                        (4*evEvDegiskeniToplami + 2*evDepDegiskeniToplami + depEvDegiskeniToplami + depDepDegiskeniToplami*2)
    depTakimiSkorPuani = (4*depDepAtilanTotal + 2*depEvAtilanTotal + evDepYenilenTotal + evEvYenilenTotal*2) / \
                         (4*depDepDegiskeniToplami + 2*depEvDegiskeniToplami + evDepDegiskeniToplami + evEvDegiskeniToplami*2)

    return total, evTakimiSkorPuani, depTakimiSkorPuani, evEvTotal, evDepTotal, depEvTotal, depDepTotal
    # --- VERİ GİRİŞİ ---
ev_sahibi = "Ath. Bilbao"
dep_takimi = "Real Sociedad"

# Flashscore metinlerini buraya yapıştır
ev_metin = """BURAYA EV SAHİBİ SON 10 MAÇI YAPIŞTIR"""
dep_metin = """BURAYA DEPLASMAN SON 10 MAÇI YAPIŞTIR"""

# Hesapla
res = algoritma_hesapla(ev_sahibi, ev_metin, dep_takimi, dep_metin)

if res:
    total, evSkor, depSkor, eeT, edT, deT, ddT = res
    
    if total > 2:
        print(f"🔥 {ev_sahibi} BAS KARŞİİM")
    elif total < -2:
        print(f"🚀 SERİ {dep_takimi} BASS")
    else:
        print("😐 Berabere olur gibi moruk ama çok da inanma skrtt")
        
    print("-" * 30)
    print(f"TOTAL SKOR: {total}")
    print(f"{ev_sahibi} Gol Puanı: {evSkor:.2f} | {dep_takimi} Gol Puanı: {depSkor:.2f}")
    print(f"Detaylar: Ev_Ev: {eeT*2}, Ev_Dep: {edT}, Dep_Ev: {deT}, Dep_Dep: {ddT*2}")
    import numpy as np

def monte_carlo_simulasyonu(ev_lambda, dep_lambda, simulasyon_sayisi=10000):
    # Poisson dağılımına göre rastgele gol sayıları üret
    ev_goller = np.random.poisson(ev_lambda, simulasyon_sayisi)
    dep_goller = np.random.poisson(dep_lambda, simulasyon_sayisi)
    
    ev_galibiyet = 0
    beraberlik = 0
    dep_galibiyet = 0
    
    ust_25 = 0
    kg_var = 0
    
    skorlar = {}

    for i in range(simulasyon_sayisi):
        e = ev_goller[i]
        d = dep_goller[i]
        
        # Galibiyet/Beraberlik/Mağlubiyet
        if e > d: ev_galibiyet += 1
        elif e == d: beraberlik += 1
        else: dep_galibiyet += 1
        
        # Alt/Üst ve KG
        if (e + d) > 2.5: ust_25 += 1
        if e > 0 and d > 0: kg_var += 1
        
        # Skor Frekansı
        skor = f"{e}-{d}"
        skorlar[skor] = skorlar.get(skor, 0) + 1

    # Yüzdeleri hesapla
    print(f"--- 🎲 {simulasyon_sayisi} Maçlık Simülasyon Sonuçları ---")
    print(f"🏠 Ev Sahibi Kazanır: %{(ev_galibiyet/simulasyon_sayisi)*100:.2f}")
    print(f"🤝 Beraberlik: %{(beraberlik/simulasyon_sayisi)*100:.2f}")
    print(f"🚀 Deplasman Kazanır: %{(dep_galibiyet/simulasyon_sayisi)*100:.2f}")
    print(f"⚽ 2.5 ÜST: %{(ust_25/simulasyon_sayisi)*100:.2f}")
    print(f"🥅 Karşılıklı Gol: %{(kg_var/simulasyon_sayisi)*100:.2f}")
    
    # En yüksek olasılıklı 3 skor
    sirali_skorlar = sorted(skorlar.items(), key=lambda x: x[1], reverse=True)
    print("\n📍 En Yüksek Olasılıklı Skorlar:")
    for i in range(3):
        skor, adet = sirali_skorlar[i]
        print(f"   {skor}: %{(adet/simulasyon_sayisi)*100:.1f}")

# Kullanım (Önceki kutucuktaki sonuçları kullanır):
# monte_carlo_simulasyonu(evTakimiSkorPuani, depTakimiSkorPuani)
