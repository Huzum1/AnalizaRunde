import streamlit as st
import pandas as pd

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
if 'variante' not in st.session_state:
    st.session_state.variante = []

# Funcție pentru comparare numere
def verifica_varianta(varianta, runda):
    """Verifică câte numere se potrivesc între variantă și rundă"""
    set_varianta = set(varianta)
    set_runda = set(runda)
    return len(set_varianta.intersection(set_runda))

# Layout în 2 coloane
col1, col2 = st.columns(2)

# COLOANA 1: RUNDE
with col1:
    st.header("📋 Runde")
    
    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_bulk"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Adaugă", type="primary", use_container_width=True):
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
        if st.button("Șterge", use_container_width=True):
            st.session_state.runde = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde:
        st.caption(f"Total: {len(st.session_state.runde)} runde")
        
        container_runde = st.container(height=250)
        with container_runde:
            for i, runda in enumerate(st.session_state.runde, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

# COLOANA 2: VARIANTE
with col2:
    st.header("🎲 Variante")
    
    text_variante = st.text_area(
        "Format: 1, 6 7 5 77",
        height=150,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23",
        key="input_variante_bulk"
    )
    
    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_var"):
            if text_variante.strip():
                linii = text_variante.strip().split('\n')
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
                                    'numere': numere
                                })
                    except:
                        pass
                
                if variante_noi:
                    st.session_state.variante.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante")
                    st.rerun()
    
    with col_btn4:
        if st.button("Șterge", use_container_width=True, key="del_var"):
            st.session_state.variante = []
            st.rerun()
    
    # Afișare variante - MAX 10 cu scroll
    if st.session_state.variante:
        st.caption(f"Total: {len(st.session_state.variante)} variante")
        
        container_variante = st.container(height=250)
        with container_variante:
            for var in st.session_state.variante:
                st.text(f"ID {var['id']}: {' '.join(map(str, var['numere']))}")

# SECȚIUNEA REZULTATE - MINIMALIST
st.divider()
st.header("🏆 Rezultate")

if st.session_state.runde and st.session_state.variante:
    
    numar_minim = st.slider(
        "Numere minime potrivite:",
        min_value=2,
        max_value=10,
        value=4
    )
    
    st.divider()
    
    # Container cu scroll pentru rezultate
    rezultate_container = st.container(height=300)
    with rezultate_container:
        for i, runda in enumerate(st.session_state.runde, 1):
            castiguri = 0
            
            for var_obj in st.session_state.variante:
                varianta = var_obj['numere']
                potriviri = verifica_varianta(varianta, runda)
                
                if potriviri >= numar_minim:
                    castiguri += 1
            
            st.text(f"Runda {i} - {castiguri} variante câștigătoare")
    
    # Statistici compacte
    st.divider()
    col_s1, col_s2, col_s3 = st.columns(3)
    
    total_castiguri = 0
    for runda in st.session_state.runde:
        for var_obj in st.session_state.variante:
            if verifica_varianta(var_obj['numere'], runda) >= numar_minim:
                total_castiguri += 1
    
    with col_s1:
        st.metric("Runde", len(st.session_state.runde))
    with col_s2:
        st.metric("Variante", len(st.session_state.variante))
    with col_s3:
        st.metric("Câștiguri", total_castiguri)

else:
    st.info("Adaugă runde și variante pentru verificare")
