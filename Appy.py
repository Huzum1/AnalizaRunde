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
if 'runde_1' not in st.session_state:
    st.session_state.runde_1 = []
if 'runde_2' not in st.session_state:
    st.session_state.runde_2 = []
if 'runde_3' not in st.session_state:
    st.session_state.runde_3 = []
if 'runde_4' not in st.session_state:
    st.session_state.runde_4 = []
if 'runde_5' not in st.session_state:
    st.session_state.runde_5 = []
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

# COLOANA 1: CHENAR 1 RUNDE
with col1:
    st.header("📋 Chenar 1 Runde")
    
    text_runde_1 = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_1_bulk"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde_1"):
            if text_runde_1.strip():
                linii = text_runde_1.strip().split('\n')
                runde_noi = []
                
                for linie in linii:
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        pass
                
                if runde_noi:
                    st.session_state.runde_1.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()
    
    with col_btn2:
        if st.button("Șterge", use_container_width=True, key="del_runde_1"):
            st.session_state.runde_1 = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde_1:
        st.caption(f"Total: {len(st.session_state.runde_1)} runde")
        
        container_runde_1 = st.container(height=250)
        with container_runde_1:
            for i, runda in enumerate(st.session_state.runde_1, 1):
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

st.divider()

# CHENAR 2 RUNDE
col3, col4 = st.columns(2)

with col3:
    st.header("📋 Chenar 2 Runde")
    
    text_runde_2 = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_2_bulk"
    )
    
    col_btn5, col_btn6 = st.columns(2)
    with col_btn5:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde_2"):
            if text_runde_2.strip():
                linii = text_runde_2.strip().split('\n')
                runde_noi = []
                
                for linie in linii:
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        pass
                
                if runde_noi:
                    st.session_state.runde_2.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()
    
    with col_btn6:
        if st.button("Șterge", use_container_width=True, key="del_runde_2"):
            st.session_state.runde_2 = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde_2:
        st.caption(f"Total: {len(st.session_state.runde_2)} runde")
        
        container_runde_2 = st.container(height=250)
        with container_runde_2:
            for i, runda in enumerate(st.session_state.runde_2, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

with col4:
    st.write("")

st.divider()

# CHENAR 3 RUNDE
col5, col6 = st.columns(2)

with col5:
    st.header("📋 Chenar 3 Runde")
    
    text_runde_3 = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_3_bulk"
    )
    
    col_btn7, col_btn8 = st.columns(2)
    with col_btn7:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde_3"):
            if text_runde_3.strip():
                linii = text_runde_3.strip().split('\n')
                runde_noi = []
                
                for linie in linii:
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        pass
                
                if runde_noi:
                    st.session_state.runde_3.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()
    
    with col_btn8:
        if st.button("Șterge", use_container_width=True, key="del_runde_3"):
            st.session_state.runde_3 = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde_3:
        st.caption(f"Total: {len(st.session_state.runde_3)} runde")
        
        container_runde_3 = st.container(height=250)
        with container_runde_3:
            for i, runda in enumerate(st.session_state.runde_3, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

with col6:
    st.write("")

st.divider()

# CHENAR 4 RUNDE
col7, col8 = st.columns(2)

with col7:
    st.header("📋 Chenar 4 Runde")
    
    text_runde_4 = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_4_bulk"
    )
    
    col_btn9, col_btn10 = st.columns(2)
    with col_btn9:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde_4"):
            if text_runde_4.strip():
                linii = text_runde_4.strip().split('\n')
                runde_noi = []
                
                for linie in linii:
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        pass
                
                if runde_noi:
                    st.session_state.runde_4.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()
    
    with col_btn10:
        if st.button("Șterge", use_container_width=True, key="del_runde_4"):
            st.session_state.runde_4 = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde_4:
        st.caption(f"Total: {len(st.session_state.runde_4)} runde")
        
        container_runde_4 = st.container(height=250)
        with container_runde_4:
            for i, runda in enumerate(st.session_state.runde_4, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

with col8:
    st.write("")

st.divider()

# CHENAR 5 RUNDE
col9, col10 = st.columns(2)

with col9:
    st.header("📋 Chenar 5 Runde")
    
    text_runde_5 = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=150,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde_5_bulk"
    )
    
    col_btn11, col_btn12 = st.columns(2)
    with col_btn11:
        if st.button("Adaugă", type="primary", use_container_width=True, key="add_runde_5"):
            if text_runde_5.strip():
                linii = text_runde_5.strip().split('\n')
                runde_noi = []
                
                for linie in linii:
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        pass
                
                if runde_noi:
                    st.session_state.runde_5.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde")
                    st.rerun()
    
    with col_btn12:
        if st.button("Șterge", use_container_width=True, key="del_runde_5"):
            st.session_state.runde_5 = []
            st.rerun()
    
    # Afișare runde - MAX 10 cu scroll
    if st.session_state.runde_5:
        st.caption(f"Total: {len(st.session_state.runde_5)} runde")
        
        container_runde_5 = st.container(height=250)
        with container_runde_5:
            for i, runda in enumerate(st.session_state.runde_5, 1):
                st.text(f"{i}. {','.join(map(str, runda))}")

with col10:
    st.write("")

# SECȚIUNEA REZULTATE - MINIMALIST
st.divider()
st.header("🏆 Rezultate")

# Combinăm toate rundele
toate_rundele = (st.session_state.runde_1 + st.session_state.runde_2 + 
                 st.session_state.runde_3 + st.session_state.runde_4 + 
                 st.session_state.runde_5)

if toate_rundele and st.session_state.variante:
    
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
        for i, runda in enumerate(toate_rundele, 1):
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
    for runda in toate_rundele:
        for var_obj in st.session_state.variante:
            if verifica_varianta(var_obj['numere'], runda) >= numar_minim:
                total_castiguri += 1
    
    with col_s1:
        st.metric("Runde", len(toate_rundele))
    with col_s2:
        st.metric("Variante", len(st.session_state.variante))
    with col_s3:
        st.metric("Câștiguri", total_castiguri)

else:
    st.info("Adaugă runde și variante pentru verificare")
