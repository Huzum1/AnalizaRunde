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
    st.header("📋 Rundele Loteriei")
    
    st.write("**Format:** Fiecare linie = o rundă cu numere separate prin virgulă")
    st.caption("Exemplu:\n1,6,7,9,44,77,85\n2,5,3,77,6,56,34")
    
    text_runde = st.text_area(
        "Introdu rundele (câte o rundă pe fiecare linie):",
        height=200,
        placeholder="1,6,7,9,44,77,85\n2,5,3,77,6,56,34\n3,12,23,34,45,56,67",
        key="input_runde_bulk"
    )
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Adaugă Runde", type="primary", use_container_width=True):
            if text_runde.strip():
                linii = text_runde.strip().split('\n')
                runde_noi = []
                erori = []
                
                for i, linie in enumerate(linii, 1):
                    try:
                        numere = [int(n.strip()) for n in linie.split(',') if n.strip()]
                        if numere:
                            runde_noi.append(numere)
                    except:
                        erori.append(f"Linia {i}")
                
                if runde_noi:
                    st.session_state.runde.extend(runde_noi)
                    st.success(f"✅ {len(runde_noi)} runde adăugate!")
                    if erori:
                        st.warning(f"⚠️ Erori la: {', '.join(erori)}")
                    st.rerun()
                else:
                    st.error("❌ Nicio rundă validă găsită!")
    
    with col_btn2:
        if st.button("🗑️ Șterge Runde", use_container_width=True):
            st.session_state.runde = []
            st.rerun()
    
    # Afișare runde existente
    if st.session_state.runde:
        st.subheader(f"Runde înregistrate ({len(st.session_state.runde)}):")
        
        # Creare DataFrame pentru afișare
        df_runde = pd.DataFrame(st.session_state.runde)
        df_runde.index = range(1, len(df_runde) + 1)
        df_runde.index.name = 'Rundă'
        
        st.dataframe(df_runde, use_container_width=True)
    else:
        st.info("Nu sunt runde înregistrate încă.")

# COLOANA 2: VARIANTE
with col2:
    st.header("🎲 Variantele Tale")
    
    st.write("**Format:** ID, număr1 număr2 număr3 ... (separate prin spații)")
    st.caption("Exemplu:\n1, 6 7 5 77\n2, 4 65 45 23\n3, 67 44 22 15")
    
    text_variante = st.text_area(
        "Introdu variantele (câte o variantă pe fiecare linie):",
        height=200,
        placeholder="1, 6 7 5 77\n2, 4 65 45 23\n3, 67 44 22 15",
        key="input_variante_bulk"
    )
    
    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("➕ Adaugă Variante", type="primary", use_container_width=True):
            if text_variante.strip():
                linii = text_variante.strip().split('\n')
                variante_noi = []
                erori = []
                
                for linie in linii:
                    try:
                        # Separăm după virgulă
                        parti = linie.split(',', 1)
                        if len(parti) == 2:
                            id_var = parti[0].strip()
                            numere_str = parti[1].strip()
                            # Separăm numerele după spații
                            numere = [int(n.strip()) for n in numere_str.split() if n.strip()]
                            if numere:
                                variante_noi.append({
                                    'id': id_var,
                                    'numere': numere
                                })
                    except:
                        erori.append(f"ID {parti[0] if 'parti' in locals() else '?'}")
                
                if variante_noi:
                    st.session_state.variante.extend(variante_noi)
                    st.success(f"✅ {len(variante_noi)} variante adăugate!")
                    if erori:
                        st.warning(f"⚠️ Erori la: {', '.join(erori)}")
                    st.rerun()
                else:
                    st.error("❌ Nicio variantă validă găsită!")
    
    with col_btn4:
        if st.button("🗑️ Șterge Variante", use_container_width=True):
            st.session_state.variante = []
            st.rerun()
    
    # Afișare variante existente
    if st.session_state.variante:
        st.subheader(f"Variante înregistrate ({len(st.session_state.variante)}):")
        
        # Creare tabel pentru afișare
        for var in st.session_state.variante:
            st.info(f"**ID {var['id']}:** {' '.join(map(str, var['numere']))}")
    else:
        st.info("Nu sunt variante înregistrate încă.")

# SECȚIUNEA 3: REZULTATE
st.divider()
st.header("🏆 Rezultate Verificare")

if st.session_state.runde and st.session_state.variante:
    # Criteriu pentru variante câștigătoare
    col_slider1, col_slider2 = st.columns([2, 1])
    with col_slider1:
        numar_minim = st.slider(
            "Câte numere trebuie să se potrivească pentru a fi câștigătoare?",
            min_value=2,
            max_value=min(10, max(len(r) for r in st.session_state.runde)),
            value=min(4, max(len(r) for r in st.session_state.runde)),
            help="Alege numărul minim de numere potrivite"
        )
    
    st.subheader(f"Verificare cu minim {numar_minim} numere potrivite:")
    
    # Verificare pentru fiecare rundă
    for i, runda in enumerate(st.session_state.runde, 1):
        with st.expander(f"🎯 Runda {i}: {', '.join(map(str, runda))}", expanded=True):
            variante_castigatoare = []
            
            # Verificăm fiecare variantă
            for var_obj in st.session_state.variante:
                varianta = var_obj['numere']
                id_var = var_obj['id']
                potriviri = verifica_varianta(varianta, runda)
                
                if potriviri >= numar_minim:
                    variante_castigatoare.append((id_var, varianta, potriviri))
            
            # Afișare rezultate
            if variante_castigatoare:
                st.success(f"✅ **{len(variante_castigatoare)} variante câștigătoare:**")
                for id_var, var, potriviri in variante_castigatoare:
                    numere_castigatoare = set(var).intersection(set(runda))
                    st.write(f"- **ID {id_var}:** {' '.join(map(str, var))} → **{potriviri} numere potrivite** ({', '.join(map(str, sorted(numere_castigatoare)))}) 🎉")
            else:
                st.error(f"❌ **0 variante câștigătoare**")
    
    # Statistici generale
    st.divider()
    st.subheader("📊 Statistici Generale")
    
    total_verificari = len(st.session_state.runde) * len(st.session_state.variante)
    total_castiguri = 0
    
    for runda in st.session_state.runde:
        for var_obj in st.session_state.variante:
            if verifica_varianta(var_obj['numere'], runda) >= numar_minim:
                total_castiguri += 1
    
    col_stat1, col_stat2, col_stat3 = st.columns(3)
    with col_stat1:
        st.metric("Total Runde", len(st.session_state.runde))
    with col_stat2:
        st.metric("Total Variante", len(st.session_state.variante))
    with col_stat3:
        st.metric("Total Câștiguri", total_castiguri)
    
    if total_verificari > 0:
        procent_castig = (total_castiguri / total_verificari) * 100
        st.info(f"📈 Rata de câștig: **{procent_castig:.1f}%** ({total_castiguri} din {total_verificari} verificări)")

else:
    st.info("👆 Adaugă runde și variante în coloanele de mai sus pentru a începe verificarea.")

# Buton reset general
st.divider()
if st.button("🔄 Șterge Tot (Runde + Variante)", type="secondary"):
    st.session_state.runde = []
    st.session_state.variante = []
    st.rerun()
