import streamlit as st
import pandas as pd
from collections import Counter

# Configurare pagină
st.set_page_config(
    page_title="Verificare Loterie",
    page_icon="🎰",
    layout="wide"
)

# Titlu principal
st.title("🎰 Verificare Variante Loterie")
st.divider()

# Inițializare session state
if 'runde' not in st.session_state:
    st.session_state.runde = []
if 'variante_1' not in st.session_state:
    st.session_state.variante_1 = []
if 'variante_2' not in st.session_state:
    st.session_state.variante_2 = []
if 'variante_3' not in st.session_state:
    st.session_state.variante_3 = []
if 'variante_4' not in st.session_state:
    st.session_state.variante_4 = []
if 'variante_5' not in st.session_state:
    st.session_state.variante_5 = []

# Funcție pentru comparare numere
def verifica_varianta(varianta, runda):
    """Verifică câte numere se potrivesc între variantă și rundă"""
    set_varianta = set(varianta)
    set_runda = set(runda)
    return len(set_varianta.intersection(set_runda))

def calculeaza_statistici_chenar(variante_list, runde_list, numar_minim):
    """Calculează statistici pentru un chenar de variante"""
    if not variante_list or not runde_list:
        return {
            'total_castiguri': 0,
            'acoperire_runde': 0,
            'castiguri_per_runda': 0,
            'acoperire_2': 0,
            'acoperire_3': 0,
            'acoperire_4': 0,
            'acoperire_5': 0,
            'acoperire_6': 0,
            'numere_unice': 0,
            'diversitate': 0
        }
    
    total_castiguri = 0
    runde_castigatoare = set()
    distributie_potriviri = Counter()
    toate_numerele = set()
    
    for idx_runda, runda in enumerate(runde_list):
        castig_runda = False
        for var_obj in variante_list:
            varianta = var_obj['numere']
            potriviri = verifica_varianta(varianta, runda)
            distributie_potriviri[potriviri] += 1
            
            if potriviri >= numar_minim:
                total_castiguri += 1
                castig_runda = True
            
            toate_numerele.update(varianta)
        
        if castig_runda:
            runde_castigatoare.add(idx_runda)
    
    acoperire_runde = (len(runde_castigatoare) / len(runde_list) * 100) if runde_list else 0
    castiguri_per_runda = total_castiguri / len(runde_list) if runde_list else 0
    numere_unice = len(toate_numerele)
    diversitate = numere_unice / len(variante_list) if variante_list else 0
    
    return {
        'total_castiguri': total_castiguri,
        'acoperire_runde': acoperire_runde,
        'castiguri_per_runda': castiguri_per_runda,
        'acoperire_2': distributie_potriviri[2],
        'acoperire_3': distributie_potriviri[3],
        'acoperire_4': distributie_potriviri[4],
        'acoperire_5': distributie_potriviri[5],
        'acoperire_6': distributie_potriviri[6],
        'numere_unice': numere_unice,
        'diversitate': diversitate
    }

def genereaza_top_variante(toate_variantele, runde_list, numar_minim, limit=1150):
    """Generează top variante pe baza performanței"""
    if not toate_variantele or not runde_list:
        return []
    
    scoruri = []
    
    for var_obj in toate_variantele:
        varianta = var_obj['numere']
        chenar = var_obj.get('chenar', '')
        
        total_potriviri = 0
        castiguri = 0
        potriviri_mari = 0
        
        for runda in runde_list:
            potriviri = verifica_varianta(varianta, runda)
            total_potriviri += potriviri
            if potriviri >= numar_minim:
                castiguri += 1
            if potriviri >= 4:
                potriviri_mari += 1
        
        scor = castiguri * 10 + potriviri_mari * 5 + total_potriviri
        
        scoruri.append({
            'id': var_obj['id'],
            'chenar': chenar,
            'numere': varianta,
            'castiguri': castiguri,
            'total_potriviri': total_potriviri,
            'potriviri_mari': potriviri_mari,
            'scor': scor
        })
    
    scoruri.sort(key=lambda x: x['scor'], reverse=True)
    return scoruri[:limit]

# Layout pentru RUNDE - O singură secțiune
st.header("📋 Runde")

text_runde = st.text_area(
    "Format: 1,6,7,9,44,77",
    height=150,
    placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
    key="input_runde_bulk"
)

col_btn1, col_btn2 = st.columns(2)
with col_btn1:
    if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde"):
        if text_runde.strip():
            linii = text_runde.strip().split('\n')
            runde_noi = []
            
            for linie in linii:
                try:
                    numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                    if numere:
                        runde_noi.append(numere)
                except:
                    pass
            
            if runde_noi:
                st.session_state.runde.extend(runde_noi)
                st.success(f"✅ {len(runde_noi)} runde")
                st.rerun()

with col_btn2:
    if st.button("Șterge", use_container_width=True, key="del_runde"):
        st.session_state.runde = []
        st.rerun()

# Afișare runde
if st.session_state.runde:
    st.caption(f"Total: {len(st.session_state.runde)} runde")
    
    container_runde = st.container(height=250)
    with container_runde:
        for i, runda in enumerate(st.session_state.runde, 1):
            st.text(f"{i}. {','.join(map(str, runda))}")

st.divider()

# Layout pentru VARIANTE - 5 chenare în grid 2x3
st.header("🎲 Chenare Variante")

# Rând 1: Chenar 1 și 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Chenar 1 Variante")
    text_variante_1 = st.text_area(
        "Format: 1, 6 7 5 77",
        height=120,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_1_bulk"
    )
    
    col_btn1_1, col_btn1_2 = st.columns(2)
    with col_btn1_1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var_1"):
            if text_variante_1.strip():
                linii = text_variante_1.strip().split('\n')
                variante_noi = []
                
                for linie in linii:
                    try:
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere,
                                    'chenar': 'C1'
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante_1.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn1_2:
        if st.button("Șterge", use_container_width=True, key="del_var_1"):
            st.session_state.variante_1 = []
            st.rerun()
    
    if st.session_state.variante_1:
        st.caption(f"Total: {len(st.session_state.variante_1)} variante")
        container_variante_1 = st.container(height=150)
        with container_variante_1:
            for var in st.session_state.variante_1:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

with col2:
    st.subheader("Chenar 2 Variante")
    text_variante_2 = st.text_area(
        "Format: 1, 6 7 5 77",
        height=120,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_2_bulk"
    )
    
    col_btn2_1, col_btn2_2 = st.columns(2)
    with col_btn2_1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var_2"):
            if text_variante_2.strip():
                linii = text_variante_2.strip().split('\n')
                variante_noi = []
                
                for linie in linii:
                    try:
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere,
                                    'chenar': 'C2'
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante_2.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn2_2:
        if st.button("Șterge", use_container_width=True, key="del_var_2"):
            st.session_state.variante_2 = []
            st.rerun()
    
    if st.session_state.variante_2:
        st.caption(f"Total: {len(st.session_state.variante_2)} variante")
        container_variante_2 = st.container(height=150)
        with container_variante_2:
            for var in st.session_state.variante_2:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

st.write("")

# Rând 2: Chenar 3 și 4
col3, col4 = st.columns(2)

with col3:
    st.subheader("Chenar 3 Variante")
    text_variante_3 = st.text_area(
        "Format: 1, 6 7 5 77",
        height=120,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_3_bulk"
    )
    
    col_btn3_1, col_btn3_2 = st.columns(2)
    with col_btn3_1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var_3"):
            if text_variante_3.strip():
                linii = text_variante_3.strip().split('\n')
                variante_noi = []
                
                for linie in linii:
                    try:
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere,
                                    'chenar': 'C3'
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante_3.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn3_2:
        if st.button("Șterge", use_container_width=True, key="del_var_3"):
            st.session_state.variante_3 = []
            st.rerun()
    
    if st.session_state.variante_3:
        st.caption(f"Total: {len(st.session_state.variante_3)} variante")
        container_variante_3 = st.container(height=150)
        with container_variante_3:
            for var in st.session_state.variante_3:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

with col4:
    st.subheader("Chenar 4 Variante")
    text_variante_4 = st.text_area(
        "Format: 1, 6 7 5 77",
        height=120,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_4_bulk"
    )
    
    col_btn4_1, col_btn4_2 = st.columns(2)
    with col_btn4_1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var_4"):
            if text_variante_4.strip():
                linii = text_variante_4.strip().split('\n')
                variante_noi = []
                
                for linie in linii:
                    try:
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere,
                                    'chenar': 'C4'
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante_4.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn4_2:
        if st.button("Șterge", use_container_width=True, key="del_var_4"):
            st.session_state.variante_4 = []
            st.rerun()
    
    if st.session_state.variante_4:
        st.caption(f"Total: {len(st.session_state.variante_4)} variante")
        container_variante_4 = st.container(height=150)
        with container_variante_4:
            for var in st.session_state.variante_4:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

st.write("")

# Rând 3: Chenar 5 (centrat)
col5, col6, col7 = st.columns([1, 2, 1])

with col6:
    st.subheader("Chenar 5 Variante")
    text_variante_5 = st.text_area(
        "Format: 1, 6 7 5 77",
        height=120,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_5_bulk"
    )
    
    col_btn5_1, col_btn5_2 = st.columns(2)
    with col_btn5_1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var_5"):
            if text_variante_5.strip():
                linii = text_variante_5.strip().split('\n')
                variante_noi = []
                
                for linie in linii:
                    try:
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere,
                                    'chenar': 'C5'
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante_5.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn5_2:
        if st.button("Șterge", use_container_width=True, key="del_var_5"):
            st.session_state.variante_5 = []
            st.rerun()
    
    if st.session_state.variante_5:
        st.caption(f"Total: {len(st.session_state.variante_5)} variante")
        container_variante_5 = st.container(height=150)
        with container_variante_5:
            for var in st.session_state.variante_5:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

st.divider()

# SECȚIUNEA ANALIZĂ ȘI REZULTATE
toate_variantele = (st.session_state.variante_1 + st.session_state.variante_2 + 
                    st.session_state.variante_3 + st.session_state.variante_4 + 
                    st.session_state.variante_5)

if st.session_state.runde and toate_variantele:
    
    numar_minim = st.slider(
        "Numere minime potrivite:",
        min_value=2,
        max_value=10,
        value=4
    )
    
    st.divider()
    
    # ANALIZĂ COMPARATIVĂ CHENARE
    st.header("📊 Analiză Comparativă Chenare")
    
    statistici_chenare = {
        'Chenar 1': calculeaza_statistici_chenar(st.session_state.variante_1, st.session_state.runde, numar_minim),
        'Chenar 2': calculeaza_statistici_chenar(st.session_state.variante_2, st.session_state.runde, numar_minim),
        'Chenar 3': calculeaza_statistici_chenar(st.session_state.variante_3, st.session_state.runde, numar_minim),
        'Chenar 4': calculeaza_statistici_chenar(st.session_state.variante_4, st.session_state.runde, numar_minim),
        'Chenar 5': calculeaza_statistici_chenar(st.session_state.variante_5, st.session_state.runde, numar_minim)
    }
    
    # Tabel comparativ
    df_comparativ = pd.DataFrame(statistici_chenare).T
    df_comparativ = df_comparativ.round(2)
    
    st.dataframe(df_comparativ, use_container_width=True)
    
    # Identificare cel mai bun chenar pe categorii
    st.subheader("🏆 Cele Mai Bune Chenare")
    
    col_best1, col_best2, col_best3 = st.columns(3)
    
    with col_best1:
        best_castiguri = max(statistici_chenare.items(), key=lambda x: x[1]['total_castiguri'])
        st.metric("Cel mai profitabil", best_castiguri[0], f"{best_castiguri[1]['total_castiguri']} câștiguri")
        
        best_acoperire = max(statistici_chenare.items(), key=lambda x: x[1]['acoperire_runde'])
        st.metric("Acoperire runde", best_acoperire[0], f"{best_acoperire[1]['acoperire_runde']:.1f}%")
    
    with col_best2:
        best_per_runda = max(statistici_chenare.items(), key=lambda x: x[1]['castiguri_per_runda'])
        st.metric("Câștiguri/Rundă", best_per_runda[0], f"{best_per_runda[1]['castiguri_per_runda']:.2f}")
        
        best_diversitate = max(statistici_chenare.items(), key=lambda x: x[1]['diversitate'])
        st.metric("Diversitate", best_diversitate[0], f"{best_diversitate[1]['diversitate']:.2f}")
    
    with col_best3:
        best_2 = max(statistici_chenare.items(), key=lambda x: x[1]['acoperire_2'])
        st.metric("Potriviri 2/2", best_2[0], f"{best_2[1]['acoperire_2']}")
        
        best_3 = max(statistici_chenare.items(), key=lambda x: x[1]['acoperire_3'])
        st.metric("Potriviri 3/3", best_3[0], f"{best_3[1]['acoperire_3']}")
    
    st.divider()
    
    # TOP VARIANTE
    st.header("🌟 Top 1150 Variante Cele Mai Bune")
    
    top_variante = genereaza_top_variante(toate_variantele, st.session_state.runde, numar_minim)
    
    if top_variante:
        st.caption(f"Afișare: Primele 10 din {len(top_variante)} variante")
        
        # Preview primele 10
        preview_container = st.container(height=300)
        with preview_container:
            for idx, var in enumerate(top_variante[:10], 1):
                st.text(f"{idx}. [{var['chenar']}] ID {var['id']}: {' '.join(map(str, var['numere']))} | Scor: {var['scor']} | Câștiguri: {var['castiguri']}")
        
        # Container scrollabil cu toate variantele
        with st.expander("📋 Vezi toate variantele (scrollabil)"):
            toate_container = st.container(height=400)
            with toate_container:
                for idx, var in enumerate(top_variante, 1):
                    st.text(f"{idx}. [{var['chenar']}] ID {var['id']}: {' '.join(map(str, var['numere']))} | Scor: {var['scor']} | Câștiguri: {var['castiguri']}")
        
        # Opțiune Copy to Clipboard
        text_pentru_clipboard = "\n".join([
            f"{idx}. [{var['chenar']}] ID {var['id']}: {' '.join(map(str, var['numere']))} | Scor: {var['scor']} | Câștiguri: {var['castiguri']}"
            for idx, var in enumerate(top_variante, 1)
        ])
        
        st.download_button(
            label="📋 Descarcă Top Variante (TXT)",
            data=text_pentru_clipboard,
            file_name="top_variante.txt",
            mime="text/plain"
        )
        
        # Statistici top variante
        st.subheader("📈 Statistici Top Variante")
        col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
        
        with col_stat1:
            st.metric("Total variante", len(top_variante))
        with col_stat2:
            avg_castiguri = sum(v['castiguri'] for v in top_variante) / len(top_variante)
            st.metric("Medie câștiguri", f"{avg_castiguri:.2f}")
        with col_stat3:
            max_castiguri = max(v['castiguri'] for v in top_variante)
            st.metric("Max câștiguri", max_castiguri)
        with col_stat4:
            distributie_chenare = Counter(v['chenar'] for v in top_variante)
            cel_mai_comun = distributie_chenare.most_common(1)[0]
            st.metric("Chenar dominant", cel_mai_comun[0], f"{cel_mai_comun[1]} var.")
    
else:
    st.info("Adaugă runde și variante pentru analiză")
