import streamlit as st
import pandas as pd
import numpy as np
from collections import Counter, defaultdict
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import hashlib
import json

# Configurare pagină
st.set_page_config(
    page_title="Analiză Avansată Loterie",
    page_icon="🎰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Custom pentru design îmbunătățit
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] button {
        padding: 10px 20px;
        font-size: 16px;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .highlight-box {
        background-color: #e7f3ff;
        padding: 10px;
        border-radius: 5px;
        border-left: 3px solid #1f77b4;
    }
    .stButton button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# Titlu principal cu emoji animat
st.title("🎰 Analiză Avansată Loterie - Sistem Optimizat")
st.caption(f"Ultima actualizare: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Inițializare session state cu structură optimizată
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.runde = []
    st.session_state.variante = {f'chenar_{i}': [] for i in range(1, 6)}
    st.session_state.cache = {}
    st.session_state.rezultate_cache = {}
    st.session_state.last_calculation = None

# ======================
# FUNCȚII OPTIMIZATE
# ======================

@st.cache_data(ttl=3600)
def calculeaza_hash_date(runde, variante):
    """Creează un hash unic pentru setul de date pentru cache"""
    data_str = json.dumps({'runde': runde, 'variante': variante}, sort_keys=True)
    return hashlib.md5(data_str.encode()).hexdigest()

@st.cache_data(ttl=3600)
def verifica_varianta_batch(variante_list, runde_list):
    """Verifică toate variantele contra tuturor rundelor - vectorizat pentru performanță"""
    rezultate = []
    
    for varianta in variante_list:
        var_set = set(varianta['numere'])
        potriviri_runde = []
        
        for runda in runde_list:
            runda_set = set(runda)
            potriviri = len(var_set & runda_set)
            potriviri_runde.append(potriviri)
        
        rezultate.append({
            'id': varianta['id'],
            'chenar': varianta.get('chenar', ''),
            'numere': varianta['numere'],
            'potriviri': potriviri_runde
        })
    
    return rezultate

@st.cache_data(ttl=3600)
def calculeaza_metrici_avansate(variante_rezultate, runde_list, numar_minim=4):
    """Calculează metrici statistice avansate pentru variante"""
    metrici = []
    
    for var_rez in variante_rezultate:
        potriviri = var_rez['potriviri']
        
        # Metrici de bază
        castiguri = sum(1 for p in potriviri if p >= numar_minim)
        total_potriviri = sum(potriviri)
        
        # Metrici avansate
        if potriviri:
            # Stabilitate (deviația standard inversă)
            stabilitate = 1 / (np.std(potriviri) + 0.1)
            
            # Consistență (câte runde consecutive cu minim 2 potriviri)
            consecutiv = 0
            max_consecutiv = 0
            for p in potriviri:
                if p >= 2:
                    consecutiv += 1
                    max_consecutiv = max(max_consecutiv, consecutiv)
                else:
                    consecutiv = 0
            consistenta = max_consecutiv / len(potriviri) if potriviri else 0
            
            # Trend (panta regresiei liniare)
            x = np.arange(len(potriviri))
            trend = np.polyfit(x, potriviri, 1)[0] if len(potriviri) > 1 else 0
            
            # Eficiență (raport câștiguri/runde)
            eficienta = castiguri / len(runde_list) if runde_list else 0
            
            # Distribuție potriviri
            distributie = Counter(potriviri)
            
            # Scor compozit
            scor = (
                castiguri * 10 +
                stabilitate * 5 +
                consistenta * 20 +
                eficienta * 100 +
                (trend + 1) * 10 +
                distributie.get(5, 0) * 15 +
                distributie.get(6, 0) * 30
            )
        else:
            stabilitate = consistenta = trend = eficienta = scor = 0
            distributie = Counter()
        
        metrici.append({
            'id': var_rez['id'],
            'chenar': var_rez['chenar'],
            'numere': var_rez['numere'],
            'castiguri': castiguri,
            'total_potriviri': total_potriviri,
            'stabilitate': round(stabilitate, 2),
            'consistenta': round(consistenta, 2),
            'trend': round(trend, 3),
            'eficienta': round(eficienta, 3),
            'distributie': dict(distributie),
            'scor': round(scor, 2),
            'potriviri_detalii': potriviri
        })
    
    return sorted(metrici, key=lambda x: x['scor'], reverse=True)

def analizeaza_chenare_comparativ(toate_variantele, runde_list, numar_minim=4):
    """Analiză comparativă detaliată între chenare"""
    rezultate_chenare = defaultdict(lambda: {
        'variante': [],
        'total_castiguri': 0,
        'acoperire_runde': set(),
        'distributie_globala': Counter(),
        'numere_frecvente': Counter(),
        'stabilitate_medie': 0,
        'eficienta_medie': 0
    })
    
    for chenar_id in range(1, 6):
        chenar_key = f'chenar_{chenar_id}'
        variante_chenar = st.session_state.variante.get(chenar_key, [])
        
        if not variante_chenar:
            continue
            
        # Procesare batch pentru performanță
        rezultate = verifica_varianta_batch(variante_chenar, runde_list)
        metrici = calculeaza_metrici_avansate(rezultate, runde_list, numar_minim)
        
        for metrica in metrici:
            rezultate_chenare[chenar_key]['variante'].append(metrica)
            rezultate_chenare[chenar_key]['total_castiguri'] += metrica['castiguri']
            
            # Actualizare numere frecvente
            for num in metrica['numere']:
                rezultate_chenare[chenar_key]['numere_frecvente'][num] += 1
            
            # Actualizare distribuție
            for k, v in metrica['distributie'].items():
                rezultate_chenare[chenar_key]['distributie_globala'][k] += v
            
            # Identificare runde câștigătoare
            for idx, p in enumerate(metrica['potriviri_detalii']):
                if p >= numar_minim:
                    rezultate_chenare[chenar_key]['acoperire_runde'].add(idx)
        
        # Calculare medii
        if metrici:
            rezultate_chenare[chenar_key]['stabilitate_medie'] = np.mean([m['stabilitate'] for m in metrici])
            rezultate_chenare[chenar_key]['eficienta_medie'] = np.mean([m['eficienta'] for m in metrici])
            rezultate_chenare[chenar_key]['acoperire_procent'] = len(rezultate_chenare[chenar_key]['acoperire_runde']) / len(runde_list) * 100 if runde_list else 0
    
    return dict(rezultate_chenare)

def genereaza_varianta_combinata(top_variante, nr_numere=6):
    """Generează o variantă optimă combinând cele mai bune elemente"""
    # Analiză frecvență numere din top variante
    frecventa_numere = Counter()
    scoruri_numere = defaultdict(float)
    
    for var in top_variante[:50]:  # Analizăm top 50
        for num in var['numere']:
            frecventa_numere[num] += 1
            scoruri_numere[num] += var['scor'] / len(var['numere'])
    
    # Selectare numere cu scor ponderat
    numere_ponderate = []
    for num, freq in frecventa_numere.items():
        scor_ponderat = scoruri_numere[num] * (1 + freq / 100)
        numere_ponderate.append((num, scor_ponderat))
    
    # Sortare și selectare top numere
    numere_ponderate.sort(key=lambda x: x[1], reverse=True)
    
    # Creare mai multe variante combinate
    variante_combinate = []
    
    # Varianta 1: Top absolute
    var1 = [num for num, _ in numere_ponderate[:nr_numere]]
    variante_combinate.append(('Top Absolut', var1))
    
    # Varianta 2: Diversificată (evită clustere)
    var2 = []
    numere_folosite = set()
    for num, scor in numere_ponderate:
        if len(var2) >= nr_numere:
            break
        # Evită numere consecutive
        if not any(abs(num - n) <= 1 for n in numere_folosite):
            var2.append(num)
            numere_folosite.add(num)
    # Completare dacă e nevoie
    for num, _ in numere_ponderate:
        if len(var2) >= nr_numere:
            break
        if num not in var2:
            var2.append(num)
    variante_combinate.append(('Diversificată', var2[:nr_numere]))
    
    # Varianta 3: Echilibrată (mix între frecvență și stabilitate)
    top_stabile = sorted(top_variante[:100], key=lambda x: x['stabilitate'], reverse=True)[:20]
    numere_stabile = Counter()
    for var in top_stabile:
        for num in var['numere']:
            numere_stabile[num] += 1
    
    var3 = []
    for num, _ in numere_stabile.most_common():
        if len(var3) >= nr_numere:
            break
        var3.append(num)
    variante_combinate.append(('Echilibrată', var3))
    
    return variante_combinate

def parse_input_optimizat(text, tip='runde', chenar_id=None):
    """Parser optimizat pentru input-uri"""
    if not text.strip():
        return []
    
    rezultate = []
    linii = text.strip().split('\n')
    
    for linie in linii:
        linie = linie.strip()
        if not linie:
            continue
            
        try:
            if tip == 'runde':
                # Format: 1,2,3,4,5,6
                numere = [int(n.strip()) for n in linie.replace(' ', ',').split(',') if n.strip().isdigit()]
                if numere:
                    rezultate.append(numere)
            else:  # variante
                # Format: ID, numere
                parti = linie.split(',', 1)
                if len(parti) >= 2:
                    id_var = parti[0].strip()
                    numere_str = parti[1].strip()
                else:
                    # Dacă nu are ID, generează unul
                    id_var = f"V{len(rezultate)+1}"
                    numere_str = linie
                
                # Extrage numerele
                numere = []
                for token in numere_str.replace(',', ' ').split():
                    if token.isdigit():
                        numere.append(int(token))
                
                if numere:
                    rezultate.append({
                        'id': id_var,
                        'numere': numere,
                        'chenar': chenar_id
                    })
        except Exception as e:
            st.error(f"Eroare la parsarea liniei: {linie}")
            continue
    
    return rezultate

# ======================
# INTERFAȚĂ PRINCIPALĂ
# ======================

# Sidebar pentru setări globale
with st.sidebar:
    st.header("⚙️ Setări Globale")
    
    numar_minim = st.slider(
        "Numere minime pentru câștig:",
        min_value=2,
        max_value=6,
        value=4,
        help="Numărul minim de potriviri pentru a considera o rundă câștigătoare"
    )
    
    st.divider()
    
    st.subheader("📊 Opțiuni Vizualizare")
    show_charts = st.checkbox("Afișează grafice", value=True)
    show_heatmap = st.checkbox("Afișează heatmap", value=True)
    show_predictions = st.checkbox("Afișează predicții", value=False)
    
    st.divider()
    
    # Statistici rapide
    st.subheader("📈 Statistici Rapide")
    total_runde = len(st.session_state.runde)
    total_variante = sum(len(v) for v in st.session_state.variante.values())
    
    col1, col2 = st.columns(2)
    col1.metric("Runde", total_runde)
    col2.metric("Variante", total_variante)

# Tab-uri principale
tab_input, tab_analiza, tab_combinare, tab_predictii = st.tabs([
    "📥 Date Input",
    "📊 Analiză Detaliată", 
    "🔄 Combinare Inteligentă",
    "🔮 Predicții & Tendințe"
])

# ======================
# TAB 1: INPUT DATE
# ======================
with tab_input:
    st.header("📋 Gestionare Date")
    
    # Secțiune Runde
    with st.expander("🎲 **RUNDE**", expanded=True):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            text_runde = st.text_area(
                "Introdu rundele (una pe linie)",
                height=150,
                placeholder="1,6,7,9,44,77\n2,5,3,77,6,56\nsau\n1 6 7 9 44 77",
                key="input_runde"
            )
        
        with col2:
            st.write("")  # Spacing
            if st.button("➕ Adaugă Runde", type="primary", use_container_width=True):
                if text_runde:
                    with st.spinner("Procesare..."):
                        runde_noi = parse_input_optimizat(text_runde, tip='runde')
                        if runde_noi:
                            st.session_state.runde.extend(runde_noi)
                            st.success(f"✅ {len(runde_noi)} runde adăugate")
                            st.balloons()
            
            if st.button("🗑️ Șterge Toate", use_container_width=True):
                st.session_state.runde = []
                st.rerun()
            
            if st.button("📊 Statistici", use_container_width=True):
                if st.session_state.runde:
                    toate_numerele = []
                    for runda in st.session_state.runde:
                        toate_numerele.extend(runda)
                    freq = Counter(toate_numerele)
                    st.write(f"**Top 5 numere:**")
                    for num, count in freq.most_common(5):
                        st.caption(f"{num}: {count}x")
        
        # Afișare runde existente
        if st.session_state.runde:
            st.info(f"📌 Total: {len(st.session_state.runde)} runde încărcate")
            
            # Container cu scroll pentru runde
            with st.container():
                # Afișare primele 5 și ultimele 5 runde
                if len(st.session_state.runde) > 10:
                    st.caption("Primele 5 runde:")
                    for i, runda in enumerate(st.session_state.runde[:5], 1):
                        st.text(f"R{i}: {', '.join(map(str, runda))}")
                    st.caption("...")
                    st.caption("Ultimele 5 runde:")
                    start = len(st.session_state.runde) - 5
                    for i, runda in enumerate(st.session_state.runde[-5:], start+1):
                        st.text(f"R{i}: {', '.join(map(str, runda))}")
                else:
                    for i, runda in enumerate(st.session_state.runde, 1):
                        st.text(f"R{i}: {', '.join(map(str, runda))}")
    
    st.divider()
    
    # Secțiune Variante - Organizată în tabs
    st.header("🎯 Variante pe Chenare")
    
    chenar_tabs = st.tabs([f"Chenar {i}" for i in range(1, 6)])
    
    for idx, chenar_tab in enumerate(chenar_tabs, 1):
        with chenar_tab:
            chenar_key = f'chenar_{idx}'
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                text_variante = st.text_area(
                    f"Introdu variante pentru Chenar {idx}",
                    height=120,
                    placeholder="ID1, 6 7 5 77 12 45\nID2, 4 65 45 23 11 88\nsau doar numerele:\n6 7 5 77 12 45",
                    key=f"input_var_{idx}"
                )
            
            with col2:
                st.write("")  # Spacing
                if st.button(f"➕ Adaugă", type="primary", key=f"add_{idx}", use_container_width=True):
                    if text_variante:
                        with st.spinner("Procesare..."):
                            variante_noi = parse_input_optimizat(
                                text_variante, 
                                tip='variante', 
                                chenar_id=f'C{idx}'
                            )
                            if variante_noi:
                                st.session_state.variante[chenar_key].extend(variante_noi)
                                st.success(f"✅ {len(variante_noi)} variante adăugate")
                
                if st.button(f"🗑️ Șterge", key=f"del_{idx}", use_container_width=True):
                    st.session_state.variante[chenar_key] = []
                    st.rerun()
                
                # Statistici chenar
                variante_chenar = st.session_state.variante[chenar_key]
                if variante_chenar:
                    st.metric("Total", len(variante_chenar))
                    
                    # Numere unice în chenar
                    numere_unice = set()
                    for var in variante_chenar:
                        numere_unice.update(var['numere'])
                    st.caption(f"Numere unice: {len(numere_unice)}")
            
            # Afișare variante existente
            if st.session_state.variante[chenar_key]:
                with st.expander(f"Vezi variante ({len(st.session_state.variante[chenar_key])} total)"):
                    for var in st.session_state.variante[chenar_key][:10]:
                        st.text(f"{var['id']}: {' '.join(map(str, var['numere']))}")
                    if len(st.session_state.variante[chenar_key]) > 10:
                        st.caption(f"... și alte {len(st.session_state.variante[chenar_key])-10} variante")

# ======================
# TAB 2: ANALIZĂ DETALIATĂ
# ======================
with tab_analiza:
    st.header("📊 Analiză Statistică Avansată")
    
    # Verificare date disponibile
    toate_variantele = []
    for chenar_variante in st.session_state.variante.values():
        toate_variantele.extend(chenar_variante)
    
    if not st.session_state.runde or not toate_variantele:
        st.warning("⚠️ Te rog adaugă runde și variante în tab-ul 'Date Input' pentru a începe analiza.")
    else:
        # Buton pentru recalculare
        if st.button("🔄 Recalculează Analiza", type="primary"):
            st.session_state.rezultate_cache = {}
            st.rerun()
        
        # Hash pentru cache
        data_hash = calculeaza_hash_date(
            st.session_state.runde,
            toate_variantele
        )
        
        # Verificare cache sau calcul nou
        if data_hash in st.session_state.rezultate_cache:
            rezultate_analiza = st.session_state.rezultate_cache[data_hash]
            st.info("📌 Date încărcate din cache pentru performanță")
        else:
            with st.spinner("🔄 Analizez datele... Acest proces poate dura câteva secunde."):
                # Analiză chenare
                rezultate_analiza = analizeaza_chenare_comparativ(
                    toate_variantele,
                    st.session_state.runde,
                    numar_minim
                )
                
                # Salvare în cache
                st.session_state.rezultate_cache[data_hash] = rezultate_analiza
        
        # Dashboard cu metrici principale
        st.subheader("📈 Dashboard Principal")
        
        col1, col2, col3, col4 = st.columns(4)
        
        # Identificare cel mai bun chenar pentru fiecare metrică
        chenare_active = [k for k, v in rezultate_analiza.items() if v['variante']]
        
        if chenare_active:
            # Metrici principale
            best_castiguri = max(chenare_active, key=lambda x: rezultate_analiza[x]['total_castiguri'])
            best_acoperire = max(chenare_active, key=lambda x: rezultate_analiza[x].get('acoperire_procent', 0))
            best_stabilitate = max(chenare_active, key=lambda x: rezultate_analiza[x]['stabilitate_medie'])
            best_eficienta = max(chenare_active, key=lambda x: rezultate_analiza[x]['eficienta_medie'])
            
            with col1:
                st.metric(
                    "🏆 Cel mai profitabil",
                    best_castiguri.replace('_', ' ').title(),
                    f"{rezultate_analiza[best_castiguri]['total_castiguri']} câștiguri"
                )
            
            with col2:
                st.metric(
                    "📊 Acoperire maximă",
                    best_acoperire.replace('_', ' ').title(),
                    f"{rezultate_analiza[best_acoperire].get('acoperire_procent', 0):.1f}%"
                )
            
            with col3:
                st.metric(
                    "⚖️ Cea mai stabilă",
                    best_stabilitate.replace('_', ' ').title(),
                    f"Stabilitate: {rezultate_analiza[best_stabilitate]['stabilitate_medie']:.2f}"
                )
            
            with col4:
                st.metric(
                    "⚡ Cea mai eficientă",
                    best_eficienta.replace('_', ' ').title(),
                    f"Eficiență: {rezultate_analiza[best_eficienta]['eficienta_medie']:.3f}"
                )
        
        st.divider()
        
        # Tabel comparativ chenare
        st.subheader("📋 Comparație Detaliată Chenare")
        
        if chenare_active:
            # Creare DataFrame pentru comparație
            date_comparatie = []
            for chenar in chenare_active:
                rez = rezultate_analiza[chenar]
                date_comparatie.append({
                    'Chenar': chenar.replace('_', ' ').title(),
                    'Variante': len(rez['variante']),
                    'Câștiguri Totale': rez['total_castiguri'],
                    'Acoperire (%)': round(rez.get('acoperire_procent', 0), 2),
                    'Stabilitate': round(rez['stabilitate_medie'], 2),
                    'Eficiență': round(rez['eficienta_medie'], 3),
                    'Runde Acoperite': len(rez['acoperire_runde'])
                })
            
            df_comparatie = pd.DataFrame(date_comparatie)
            
            # Stil pentru tabel
            st.dataframe(
                df_comparatie.style.highlight_max(axis=0, subset=['Câștiguri Totale', 'Acoperire (%)', 'Stabilitate', 'Eficiență']),
                use_container_width=True
            )
        
        # Grafice
        if show_charts and chenare_active:
            st.divider()
            st.subheader("📊 Vizualizări Interactive")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Grafic distribuție câștiguri
                fig_castiguri = go.Figure()
                for chenar in chenare_active:
                    rez = rezultate_analiza[chenar]
                    fig_castiguri.add_trace(go.Bar(
                        name=chenar.replace('_', ' ').title(),
                        x=['Total', '2/2', '3/3', '4/4', '5/5', '6/6'],
                        y=[
                            rez['total_castiguri'],
                            rez['distributie_globala'].get(2, 0),
                            rez['distributie_globala'].get(3, 0),
                            rez['distributie_globala'].get(4, 0),
                            rez['distributie_globala'].get(5, 0),
                            rez['distributie_globala'].get(6, 0)
                        ]
                    ))
                
                fig_castiguri.update_layout(
                    title="Distribuție Câștiguri pe Chenare",
                    xaxis_title="Tip Potrivire",
                    yaxis_title="Număr",
                    barmode='group',
                    height=400
                )
                st.plotly_chart(fig_castiguri, use_container_width=True)
            
            with col2:
                # Grafic radar pentru comparație metrici
                categorii = ['Câștiguri', 'Acoperire', 'Stabilitate', 'Eficiență', 'Diversitate']
                
                fig_radar = go.Figure()
                
                for chenar in chenare_active[:3]:  # Maxim 3 pentru claritate
                    rez = rezultate_analiza[chenar]
                    
                    # Normalizare valori pentru radar (0-100)
                    valori = [
                        min(rez['total_castiguri'] / 10, 100),  # Normalizat
                        rez.get('acoperire_procent', 0),
                        rez['stabilitate_medie'] * 20,  # Scalat
                        rez['eficienta_medie'] * 100,  # Scalat
                        len(rez['numere_frecvente']) / 2  # Diversitate normalizată
                    ]
                    
                    fig_radar.add_trace(go.Scatterpolar(
                        r=valori,
                        theta=categorii,
                        fill='toself',
                        name=chenar.replace('_', ' ').title()
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="Comparație Multidimensională",
                    height=400
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        
        # Heatmap pentru performanță
        if show_heatmap and chenare_active:
            st.divider()
            st.subheader("🗺️ Heatmap Performanță Variante")
            
            # Selectare chenar pentru heatmap
            chenar_selectat = st.selectbox(
                "Selectează chenar pentru heatmap:",
                chenare_active,
                format_func=lambda x: x.replace('_', ' ').title()
            )
            
            if chenar_selectat and rezultate_analiza[chenar_selectat]['variante']:
                # Pregătire date pentru heatmap
                variante_chenar = rezultate_analiza[chenar_selectat]['variante'][:20]  # Top 20
                
                # Creare matrice pentru heatmap
                matrice_performanta = []
                etichete_y = []
                
                for var in variante_chenar:
                    etichete_y.append(f"{var['id']}")
                    # Limitare la primele 50 de runde pentru vizualizare
                    matrice_performanta.append(var['potriviri_detalii'][:50])
                
                # Creare heatmap
                fig_heatmap = go.Figure(data=go.Heatmap(
                    z=matrice_performanta,
                    y=etichete_y,
                    x=[f"R{i+1}" for i in range(len(matrice_performanta[0]))],
                    colorscale='RdYlGn',
                    colorbar=dict(title="Potriviri"),
                    hovertemplate="Varianta: %{y}<br>Runda: %{x}<br>Potriviri: %{z}<extra></extra>"
                ))
                
                fig_heatmap.update_layout(
                    title=f"Heatmap Performanță - {chenar_selectat.replace('_', ' ').title()} (Top 20 variante)",
                    xaxis_title="Runde",
                    yaxis_title="Variante",
                    height=600
                )
                
                st.plotly_chart(fig_heatmap, use_container_width=True)
        
        # Top Variante Globale
        st.divider()
        st.subheader("🌟 Top Variante Performante")
        
        # Agregare toate variantele cu metrici
        toate_variantele_metrici = []
        for chenar in chenare_active:
            toate_variantele_metrici.extend(rezultate_analiza[chenar]['variante'])
        
        # Sortare după scor
        toate_variantele_metrici.sort(key=lambda x: x['scor'], reverse=True)
        
        # Selectare număr de variante de afișat
        nr_top = st.slider("Număr variante top:", 10, 1000, 100, 10)
        
        top_variante = toate_variantele_metrici[:nr_top]
        
        if top_variante:
            # Afișare metrici pentru top variante
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Top Variante", len(top_variante))
            with col2:
                avg_scor = np.mean([v['scor'] for v in top_variante])
                st.metric("Scor Mediu", f"{avg_scor:.2f}")
            with col3:
                max_castiguri = max(v['castiguri'] for v in top_variante)
                st.metric("Max Câștiguri", max_castiguri)
            with col4:
                avg_stabilitate = np.mean([v['stabilitate'] for v in top_variante])
                st.metric("Stabilitate Medie", f"{avg_stabilitate:.2f}")
            
            # Tabel cu top variante
            with st.expander(f"📋 Vezi Top {len(top_variante)} Variante", expanded=False):
                date_top = []
                for i, var in enumerate(top_variante, 1):
                    date_top.append({
                        'Rang': i,
                        'ID': var['id'],
                        'Chenar': var['chenar'],
                        'Numere': ', '.join(map(str, var['numere'])),
                        'Scor': round(var['scor'], 2),
                        'Câștiguri': var['castiguri'],
                        'Stabilitate': var['stabilitate'],
                        'Eficiență': var['eficienta'],
                        'Trend': var['trend']
                    })
                
                df_top = pd.DataFrame(date_top)
                st.dataframe(df_top, use_container_width=True)
            
            # Export rezultate
            st.divider()
            col1, col2, col3 = st.columns(3)
            
            with col1:
                # Export CSV
                csv = df_top.to_csv(index=False)
                st.download_button(
                    label="📥 Descarcă CSV",
                    data=csv,
                    file_name=f"top_{nr_top}_variante.csv",
                    mime="text/csv"
                )
            
            with col2:
                # Export JSON pentru analiză ulterioară
                json_data = json.dumps(top_variante, indent=2)
                st.download_button(
                    label="📥 Descarcă JSON",
                    data=json_data,
                    file_name=f"analiza_completa_{nr_top}.json",
                    mime="application/json"
                )
            
            with col3:
                # Export doar numerele pentru utilizare rapidă
                text_numere = "\n".join([
                    f"{var['id']}, {' '.join(map(str, var['numere']))}"
                    for var in top_variante
                ])
                st.download_button(
                    label="📥 Descarcă TXT",
                    data=text_numere,
                    file_name=f"variante_numere_{nr_top}.txt",
                    mime="text/plain"
                )

# ======================
# TAB 3: COMBINARE INTELIGENTĂ
# ======================
with tab_combinare:
    st.header("🔄 Generator Variante Combinate Inteligent")
    
    if not toate_variantele or not st.session_state.runde:
        st.warning("⚠️ Adaugă date pentru a genera variante combinate.")
    else:
        st.info("""
        🎯 **Sistem de Combinare Inteligentă**
        
        Acest modul analizează cele mai performante variante și generează combinații optime folosind:
        - Analiza frecvenței numerelor câștigătoare
        - Ponderea scorurilor de performanță
        - Diversificare pentru acoperire maximă
        - Echilibrare între stabilitate și potențial de câștig
        """)
        
        # Parametri pentru generare
        col1, col2 = st.columns(2)
        
        with col1:
            nr_numere_combinat = st.number_input(
                "Număr de numere per variantă:",
                min_value=3,
                max_value=10,
                value=6
            )
            
            nr_variante_analiza = st.slider(
                "Analizează top X variante:",
                min_value=10,
                max_value=200,
                value=50,
                step=10
            )
        
        with col2:
            strategie = st.selectbox(
                "Strategie de combinare:",
                ["Echilibrată", "Agresivă (Scor Maxim)", "Conservatoare (Stabilitate)", "Diversificată"]
            )
            
            include_trend = st.checkbox("Include analiza de trend", value=True)
        
        if st.button("🚀 Generează Variante Combinate", type="primary"):
            with st.spinner("Generez variante optime..."):
                # Obține toate variantele cu metrici
                toate_metrici = []
                for chenar in st.session_state.variante:
                    if st.session_state.variante[chenar]:
                        rezultate = verifica_varianta_batch(
                            st.session_state.variante[chenar],
                            st.session_state.runde
                        )
                        metrici = calculeaza_metrici_avansate(
                            rezultate,
                            st.session_state.runde,
                            numar_minim
                        )
                        toate_metrici.extend(metrici)
                
                # Sortare după strategie
                if strategie == "Agresivă (Scor Maxim)":
                    toate_metrici.sort(key=lambda x: x['scor'], reverse=True)
                elif strategie == "Conservatoare (Stabilitate)":
                    toate_metrici.sort(key=lambda x: x['stabilitate'], reverse=True)
                elif strategie == "Diversificată":
                    toate_metrici.sort(key=lambda x: x['total_potriviri'], reverse=True)
                else:  # Echilibrată
                    toate_metrici.sort(key=lambda x: x['scor'] * x['stabilitate'], reverse=True)
                
                # Generare variante combinate
                variante_combinate = genereaza_varianta_combinata(
                    toate_metrici[:nr_variante_analiza],
                    nr_numere_combinat
                )
                
                # Afișare rezultate
                st.success("✅ Variante combinate generate cu succes!")
                
                for nume, varianta in variante_combinate:
                    with st.expander(f"🎲 Variantă {nume}"):
                        st.subheader(f"Numere: {', '.join(map(str, sorted(varianta)))}")
                        
                        # Verificare performanță pe rundele existente
                        potriviri = []
                        for runda in st.session_state.runde:
                            potriviri.append(len(set(varianta) & set(runda)))
                        
                        castiguri = sum(1 for p in potriviri if p >= numar_minim)
                        
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Câștiguri simulate", castiguri)
                        col2.metric("Potriviri medii", f"{np.mean(potriviri):.2f}")
                        col3.metric("Max potriviri", max(potriviri) if potriviri else 0)
                        
                        # Mini grafic performanță
                        if potriviri:
                            fig_mini = go.Figure()
                            fig_mini.add_trace(go.Scatter(
                                y=potriviri[:50],  # Primele 50 de runde
                                mode='lines+markers',
                                name='Potriviri',
                                line=dict(color='green', width=2)
                            ))
                            fig_mini.add_hline(y=numar_minim, line_dash="dash", 
                                             annotation_text=f"Prag câștig ({numar_minim})")
                            fig_mini.update_layout(
                                title=f"Performanță pe ultimele {min(50, len(potriviri))} runde",
                                xaxis_title="Runda",
                                yaxis_title="Potriviri",
                                height=300
                            )
                            st.plotly_chart(fig_mini, use_container_width=True)
                
                # Analiza numerelor frecvente
                st.divider()
                st.subheader("📊 Analiza Numerelor din Top Variante")
                
                frecventa = Counter()
                for var in toate_metrici[:nr_variante_analiza]:
                    for num in var['numere']:
                        frecventa[num] += 1
                
                # Top 20 cele mai frecvente numere
                top_numere = frecventa.most_common(20)
                
                fig_freq = go.Figure()
                fig_freq.add_trace(go.Bar(
                    x=[str(num) for num, _ in top_numere],
                    y=[freq for _, freq in top_numere],
                    marker_color='lightblue'
                ))
                fig_freq.update_layout(
                    title=f"Top 20 Numere Frecvente în Primele {nr_variante_analiza} Variante",
                    xaxis_title="Număr",
                    yaxis_title="Frecvență",
                    height=400
                )
                st.plotly_chart(fig_freq, use_container_width=True)
                
                # Matrice de corelație numere
                st.subheader("🔗 Numere care apar frecvent împreună")
                
                perechi = Counter()
                for var in toate_metrici[:nr_variante_analiza]:
                    numere = sorted(var['numere'])
                    for i in range(len(numere)):
                        for j in range(i+1, len(numere)):
                            perechi[(numere[i], numere[j])] += 1
                
                top_perechi = perechi.most_common(10)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Top 10 Perechi Frecvente:**")
                    for (n1, n2), freq in top_perechi:
                        st.caption(f"{n1}-{n2}: apare de {freq} ori")
                
                with col2:
                    st.write("**Recomandări bazate pe perechi:**")
                    # Sugestii bazate pe perechi frecvente
                    numere_recomandate = set()
                    for (n1, n2), _ in top_perechi[:5]:
                        numere_recomandate.add(n1)
                        numere_recomandate.add(n2)
                    st.info(f"Numere recomandate: {', '.join(map(str, sorted(numere_recomandate)))}")

# ======================
# TAB 4: PREDICȚII
# ======================
with tab_predictii:
    st.header("🔮 Predicții și Analiză Tendințe")
    
    if not st.session_state.runde:
        st.warning("⚠️ Adaugă runde pentru analiza tendințelor.")
    else:
        st.info("""
        📈 **Modul Predictiv**
        
        Analizează pattern-uri istorice și tendințe pentru a identifica:
        - Numere cu potențial crescut de apariție
        - Cicluri și pattern-uri recurente
        - Perioade de "căldură" și "răceală" pentru numere
        - Predicții bazate pe analiza statistică
        """)
        
        # Analiza tendințelor numerelor
        st.subheader("📊 Analiza Frecvenței și Tendințelor")
        
        # Calculare statistici pentru fiecare număr
        numere_stats = defaultdict(lambda: {
            'aparitii': 0,
            'ultima_aparitie': -1,
            'distanta_medie': 0,
            'distante': [],
            'trend': 0
        })
        
        for idx, runda in enumerate(st.session_state.runde):
            for num in runda:
                if numere_stats[num]['ultima_aparitie'] >= 0:
                    distanta = idx - numere_stats[num]['ultima_aparitie']
                    numere_stats[num]['distante'].append(distanta)
                
                numere_stats[num]['aparitii'] += 1
                numere_stats[num]['ultima_aparitie'] = idx
        
        # Calculare metrici avansate
        for num in numere_stats:
            if numere_stats[num]['distante']:
                numere_stats[num]['distanta_medie'] = np.mean(numere_stats[num]['distante'])
                
                # Calculare trend (ultimele 5 vs primele 5 apariții)
                if len(numere_stats[num]['distante']) >= 5:
                    recent = np.mean(numere_stats[num]['distante'][-5:])
                    vechi = np.mean(numere_stats[num]['distante'][:5])
                    numere_stats[num]['trend'] = vechi - recent  # Pozitiv = devine mai frecvent
        
        # Clasificare numere
        numere_fierbinti = []  # Apar frecvent recent
        numere_reci = []       # Nu au apărut de mult
        numere_echilibrate = [] # Apar constant
        numere_emergente = []   # Trend crescător
        
        total_runde = len(st.session_state.runde)
        
        for num, stats in numere_stats.items():
            distanta_ultima = total_runde - stats['ultima_aparitie'] - 1
            frecventa = stats['aparitii'] / total_runde
            
            if distanta_ultima <= 5 and frecventa > 0.1:
                numere_fierbinti.append((num, stats))
            elif distanta_ultima > 15:
                numere_reci.append((num, stats))
            elif stats['trend'] > 1:
                numere_emergente.append((num, stats))
            elif 0.08 <= frecventa <= 0.12 and stats['distanta_medie'] > 0:
                if 8 <= stats['distanta_medie'] <= 12:
                    numere_echilibrate.append((num, stats))
        
        # Afișare clasificare
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("### 🔥 Numere Fierbinți")
            st.caption("Apar frecvent recent")
            for num, stats in sorted(numere_fierbinti, key=lambda x: x[1]['aparitii'], reverse=True)[:5]:
                st.write(f"**{num}** - {stats['aparitii']}x")
        
        with col2:
            st.markdown("### ❄️ Numere Reci")
            st.caption("Nu au apărut recent")
            for num, stats in sorted(numere_reci, key=lambda x: total_runde - x[1]['ultima_aparitie'] - 1, reverse=True)[:5]:
                rounds_ago = total_runde - stats['ultima_aparitie'] - 1
                st.write(f"**{num}** - acum {rounds_ago} runde")
        
        with col3:
            st.markdown("### 📈 Emergente")
            st.caption("Trend crescător")
            for num, stats in sorted(numere_emergente, key=lambda x: x[1]['trend'], reverse=True)[:5]:
                st.write(f"**{num}** - trend: +{stats['trend']:.1f}")
        
        with col4:
            st.markdown("### ⚖️ Echilibrate")
            st.caption("Apar constant")
            for num, stats in sorted(numere_echilibrate, key=lambda x: x[1]['aparitii'], reverse=True)[:5]:
                st.write(f"**{num}** - la ~{stats['distanta_medie']:.0f} runde")
        
        st.divider()
        
        # Grafic istoric pentru număr selectat
        st.subheader("🔍 Analiză Detaliată Număr")
        
        numere_disponibile = sorted(list(numere_stats.keys()))
        numar_selectat = st.selectbox("Selectează număr pentru analiză:", numere_disponibile)
        
        if numar_selectat:
            stats_numar = numere_stats[numar_selectat]
            
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Total apariții", stats_numar['aparitii'])
            col2.metric("Ultima apariție", f"Runda {stats_numar['ultima_aparitie']+1}")
            col3.metric("Distanță medie", f"{stats_numar['distanta_medie']:.1f}" if stats_numar['distanta_medie'] else "N/A")
            col4.metric("Trend", f"{stats_numar['trend']:+.2f}" if stats_numar['trend'] else "0")
            
            # Grafic apariții în timp
            aparitii_timp = []
            for idx, runda in enumerate(st.session_state.runde):
                if numar_selectat in runda:
                    aparitii_timp.append(1)
                else:
                    aparitii_timp.append(0)
            
            # Calcul medie mobilă
            window = min(10, len(aparitii_timp) // 4)
            if window > 0:
                medie_mobila = pd.Series(aparitii_timp).rolling(window=window, center=True).mean()
            else:
                medie_mobila = aparitii_timp
            
            fig_istoric = go.Figure()
            
            # Bare pentru apariții
            fig_istoric.add_trace(go.Bar(
                y=aparitii_timp,
                name='Apariții',
                marker_color=['green' if x else 'lightgray' for x in aparitii_timp],
                opacity=0.6
            ))
            
            # Linie pentru medie mobilă
            fig_istoric.add_trace(go.Scatter(
                y=medie_mobila,
                mode='lines',
                name=f'Medie mobilă ({window} runde)',
                line=dict(color='red', width=2)
            ))
            
            fig_istoric.update_layout(
                title=f"Istoric apariții pentru numărul {numar_selectat}",
                xaxis_title="Runda",
                yaxis_title="Apariție",
                height=400,
                showlegend=True
            )
            
            st.plotly_chart(fig_istoric, use_container_width=True)
        
        # Predicții sugerate
        st.divider()
        st.subheader("🎯 Sugestii Predictive")
        
        # Generare sugestii bazate pe analiză
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("### 💡 Set Echilibrat")
            st.caption("Mix între fierbinte și rece")
            
            set_echilibrat = []
            # 2 fierbinți
            for num, _ in numere_fierbinti[:2]:
                set_echilibrat.append(num)
            # 2 reci
            for num, _ in numere_reci[:2]:
                set_echilibrat.append(num)
            # 2 echilibrate
            for num, _ in numere_echilibrate[:2]:
                set_echilibrat.append(num)
            
            if len(set_echilibrat) >= 6:
                st.success(f"Numere sugerate: {', '.join(map(str, sorted(set_echilibrat[:6])))}")
            else:
                st.info("Date insuficiente pentru predicție")
        
        with col2:
            st.markdown("### 🚀 Set Agresiv")
            st.caption("Focus pe numere emergente")
            
            set_agresiv = []
            # Emergente și fierbinți
            for num, _ in numere_emergente[:3]:
                set_agresiv.append(num)
            for num, _ in numere_fierbinti[:3]:
                if num not in set_agresiv:
                    set_agresiv.append(num)
            
            if len(set_agresiv) >= 6:
                st.success(f"Numere sugerate: {', '.join(map(str, sorted(set_agresiv[:6])))}")
            else:
                st.info("Date insuficiente pentru predicție")
        
        with col3:
            st.markdown("### 🛡️ Set Conservator")
            st.caption("Numere cu istoric solid")
            
            # Top numere după frecvență totală
            numere_frecvente = sorted(
                [(num, stats['aparitii']) for num, stats in numere_stats.items()],
                key=lambda x: x[1],
                reverse=True
            )
            
            set_conservator = [num for num, _ in numere_frecvente[:6]]
            
            if set_conservator:
                st.success(f"Numere sugerate: {', '.join(map(str, sorted(set_conservator)))}")
            else:
                st.info("Date insuficiente pentru predicție")
        
        # Avertisment
        st.warning("""
        ⚠️ **Disclaimer Important**
        
        Aceste predicții sunt bazate pe analiză statistică istorică și NU garantează rezultate.
        Loteria este un joc de noroc și fiecare extragere este independentă.
        Jucați responsabil!
        """)

# Footer
st.divider()
st.caption("🎰 Analiză Loterie Avansată | Dezvoltat pentru performanță maximă | Jucați responsabil!")
