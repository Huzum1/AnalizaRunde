import streamlit as st
import pandas as pd
from collections import Counter
import json
import base64
import random

# ================= CONFIG =================
st.set_page_config(
    page_title="Loterie AI – Top 1150",
    page_icon="🔮",
    layout="wide"
)

st.title("🔮 **Loterie AI – Top 1150 Variante Inteligente**")
st.divider()

# ================= SESSION STATE =================
list_keys = ['runde'] + [f'variante_{i}' for i in range(1, 6)]
page_keys = ['page_runde'] + [f'page_var{i}' for i in range(1, 6)]

for key in list_keys:
    if key not in st.session_state:
        st.session_state[key] = []
for key in page_keys:
    if key not in st.session_state:
        st.session_state[key] = 1

# ================= PARSARE FLEXIBILĂ (ORICE FORMAT!) =================
@st.cache_data(show_spinner="Se parsează rundele...")
def parse_runde(text):
    if not text.strip(): return []
    runde = []
    for linie in text.strip().split('\n'):
        linie = linie.strip()
        if not linie: continue
        
        nums = [int(x) for x in linie.replace(',', ' ').split() if x.isdigit()]
        
        # =============== MODIFICARE: FĂRĂ RESTRICȚII ===============
        # Orice linie cu cel puțin un număr este validă
        if len(nums) > 0:
            # Salvăm TOATE numerele găsite
            runde.append(tuple(sorted(nums)))
        # =========================================================
            
    return runde

@st.cache_data(show_spinner="Se parsează variantele...")
def parse_variante(text, chenar):
    if not text.strip(): return []
    variante = []
    for linie in text.strip().split('\n'):
        linie = linie.strip()
        if not linie: continue
        parts = linie.replace(',', ' ').split()
        if not parts: continue
        try:
            id_var = parts[0]
            nums = [int(x) for x in parts[1:] if x.isdigit()]
            
            # =============== MODIFICARE: FĂRĂ RESTRICȚII ===============
            # Dacă nu găsim numere după ID, încercăm să vedem dacă
            # întreaga linie e formată din numere (și ID-ul e primul număr)
            if not nums and all(p.isdigit() for p in parts):
                 id_var = parts[0] # Primul număr devine ID
                 nums = [int(x) for x in parts[1:] if x.isdigit()]

            # Dacă tot nu avem numere, poate e formatul "V1 1 2 3"
            if not nums and not parts[0].isdigit():
                 id_var = parts[0]
                 nums = [int(x) for x in parts[1:] if x.isdigit()]
            
            # Dacă formatul este "1 2 3 4 5" (fără ID)
            if not nums and all(p.isdigit() for p in parts):
                 id_var = f"AutoID_{len(variante)+1}" # Generăm un ID
                 nums = [int(x) for x in parts if x.isdigit()]

            # Singura regulă: să existe cel puțin un număr
            if len(nums) > 0: 
                variante.append({
                    'id': id_var,
                    'numere': tuple(sorted(nums)), # Salvăm TOATE numerele
                    'chenar': chenar
                })
            # =========================================================
            
        except (ValueError, IndexError):
            # Ignoră silențios orice linie cu format ciudat
            continue
    return variante

def potriviri(v, r): return len(set(v) & set(r))

# ================= SCOR AI =================
@st.cache_data(show_spinner="Se calculează Scor AI (Top 1150)...")
def calculeaza_scoruri_ai(_variante, _runde, min_match):
    if not _runde or not _variante: return []
    rezultate = []
    total = len(_variante)
    progress = st.progress(0, text="Se analizează variantele...")
    
    potriviri_runde = [
        [potriviri(var['numere'], r) >= min_match for r in _runde]
        for var in _variante
    ]

    for idx, var in enumerate(_variante):
        v = var['numere']
        rez_runde = potriviri_runde[idx]
        castiguri = sum(rez_runde)
        window = 10
        wins = [any(rez_runde[i:i+window]) 
                for i in range(0, len(_runde), window)]
        
        if not wins:
            mean = 0
            variance = 0
            consistenta = 0
            recent = 0
        else:
            mean = sum(wins) / len(wins)
            variance = sum((x - mean)**2 for x in wins) / len(wins)
            consistenta = max(0, 1 - (variance ** 0.5))
            recent = sum(wins[-3:]) / min(3, len(wins))

        unicitate = len(set(v)) 
        scor = (castiguri * 8) + (mean * 100) + (consistenta * 50) + (recent * 120) + (unicitate * 2)
        
        rezultate.append({**var, 'scor_ai': round(scor, 2), 'castiguri': castiguri})
        progress.progress((idx + 1) / total, text=f"Se analizează variantele... {idx+1}/{total}")
        
    progress.empty()
    return sorted(rezultate, key=lambda x: x['scor_ai'], reverse=True)

# ================= ACOPERIRE MINIMĂ =================
@st.cache_data(show_spinner="Se calculează acoperirea minimă...")
def acoperire_minima(_variante, _runde, min_match):
    runde_castig = {i for i, r in enumerate(_runde) 
                    if any(potriviri(v['numere'], r) >= min_match for v in _variante)}
    
    if not runde_castig: return []
    acoperite = set()
    selectate = []
    
    var_acopera = {
        v['id']: {i for i in runde_castig if potriviri(v['numere'], _runde[i]) >= min_match}
        for v in _variante
    }
    
    ramase = {v['id']: var_acopera[v['id']] for v in _variante if var_acopera[v['id']]}
    variante_dict = {v['id']: v for v in _variante}

    while acoperite != runde_castig and ramase:
        best_id = max(ramase, key=lambda id_var: len(ramase[id_var] - acoperite))
        runde_noi_acoperite = ramase[best_id] - acoperite
        
        if not runde_noi_acoperite:
            break
            
        selectate.append(variante_dict[best_id])
        acoperite.update(runde_noi_acoperite)
        del ramase[best_id]

    return selectate

# ================= CONSISTENȚĂ =================
@st.cache_data(show_spinner="Se calculează consistența...")
def calculeaza_consistenta(_variante, _runde, min_match):
    if not _runde or not _variante: return []
    rez = []
    total_runde = len(_runde)
    
    for v in _variante:
        castiguri = sum(1 for r in _runde if potriviri(v['numere'], r) >= min_match)
        frecventa = (castiguri / total_runde) if total_runde > 0 else 0
        rez.append({**v, 'frecventa': frecventa})
        
    return sorted(rez, key=lambda x: x['frecventa'], reverse=True)

# ================= PAGINARE =================
def paginare(df, key, page_size=50, height=300):
    total = len(df)
    if total == 0: 
        st.info("Nicio intrare.")
        return
        
    page = st.session_state.get(f'page_{key}', 1)
    total_pages = max(1, (total - 1) // page_size + 1)
    
    page = max(1, min(page, total_pages))
    st.session_state[f'page_{key}'] = page
    
    start = (page - 1) * page_size
    end = start + page_size
    
    df_page = df.iloc[start:end].copy()
    df_page.index = range(start + 1, len(df_page) + start + 1)
    
    st.dataframe(df_page, use_container_width=True, height=height)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Anterior", key=f"prev_{key}", disabled=page <= 1):
            st.session_state[f'page_{key}'] -= 1
            st.rerun()
    with col2:
        st.write(f"**Pagina {page} / {total_pages}** | Total: {total}")
    with col3:
        if st.button("Următor ➡️", key=f"next_{key}", disabled=page >= total_pages):
            st.session_state[f'page_{key}'] += 1
            st.rerun()

# ================= UI: RUNDE =================
st.header("📋 **Runde (Extrageri)**")
# st.info("Formatul așteptat pentru runde este de 6 numere (ex: `1 2 3 4 5 6`).") # Eliminat
with st.form("form_runde"):
    text_runde = st.text_area(
        "Lipește rundele aici. Un rând per rundă. Numere separate prin spațiu sau virgulă.",
        height=120,
        placeholder="1,6,7,9,44,77\n2 5 3 77 6 56",
        key="input_runde"
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.form_submit_button("✅ Adaugă runde", type="primary"):
            noi = parse_runde(text_runde)
            runde_existente = set(st.session_state.runde)
            runde_noi_filtrate = [r for r in noi if r not in runde_existente]
            st.session_state.runde.extend(runde_noi_filtrate)
            st.success(f"Adăugate {len(runde_noi_filtrate)} runde unice.")
            st.rerun()
    with c2:
        if st.form_submit_button("❌ Șterge toate"):
            st.session_state.runde = []
            st.success("Toate rundele au fost șterse.")
            st.rerun()

with st.expander(f"Afișează rundele ({len(st.session_state.runde)} în total)"):
    if st.session_state.runde:
        # Afișăm ca listă, deoarece DataFrame-ul e urât dacă rundele au lungimi diferite
        st.json([list(r) for r in st.session_state.runde])
    else:
        st.info("Nicio rundă adăugată.")

st.divider()

# ================= UI: CHENARE =================
st.header("🎲 **Chenare (Variante)**")

def afiseaza_chenar(i):
    key = f'variante_{i}'
    
    with st.container(border=True):
        with st.form(f"form_{key}"):
            st.subheader(f"Chenar {i}")
            text_var = st.text_area(
                "Lipește variantele aici. Ex: `ID, 1 2 3 4` sau `ID 1 2 3 4 5 6`",
                height=100,
                placeholder="V1, 6 7 5 77\nV2 4 65 45 23 11 12\n1, 44 54 56 61",
                key=f"input_var_{i}"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("✅ Adaugă", type="primary"):
                    noi = parse_variante(text_var, f'C{i}')
                    ids_existenti = {v['id'] for v in st.session_state[key]}
                    variante_noi_filtrate = [v for v in noi if v['id'] not in ids_existenti]
                    
                    st.session_state[key].extend(variante_noi_filtrate)
                    st.success(f"Adăugate {len(variante_noi_filtrate)} variante unice în Chenarul {i}.")
                    st.rerun()
            with c2:
                if st.form_submit_button("❌ Șterge"):
                    st.session_state[key] = []
                    st.success(f"Variantele din Chenarul {i} au fost șterse.")
                    st.rerun()

        with st.expander(f"Afișează variantele din Chenar {i} ({len(st.session_state[key])} în total)"):
            if st.session_state[key]:
                df = pd.DataFrame([
                    {"ID": v['id'], "Numere": " ".join(map(str, v['numere']))} 
                    for v in st.session_state[key]
                ])
                paginare(df, f"var{i}")
            else:
                st.info("Nicio variantă.")

for i in range(1, 6):
    afiseaza_chenar(i)

# ================= TOATE VARIANTELE =================
toate_variantele = sum((st.session_state[f'variante_{i}'] for i in range(1,6)), [])

st.divider()

# ================= ANALIZĂ =================
st.header("🧠 **Analiză AI**")

if st.session_state.runde and toate_variantele:
    
    # =============== MODIFICARE: SLIDER FLEXIBIL ===============
    min_match = st.slider("Număr minim de potriviri pentru un „câștig”:", 1, 10, 3,
                          help="Stabilește câte numere trebuie să se potrivească pentru ca o variantă să fie considerată câștigătoare într-o rundă.")
    # =========================================================

    tab1, tab2, tab3, tab4 = st.tabs(["🏆 Top 1150 Scor AI", "🎯 Acoperire Minimă", "📊 Consistență", "💡 Sugestii"])

    with tab1:
        st.subheader("Top 1150 Variante (bazat pe Scor AI)")
        if st.button("Calculează TOP 1150", type="primary"):
            scoruri_sortate = calculeaza_scoruri_ai(toate_variantele, st.session_state.runde, min_match)
            st.session_state.top1150 = scoruri_sortate[:1150]

        if 'top1150' in st.session_state:
            top_df = pd.DataFrame([{
                "Poz": i+1, "Chenar": v['chenar'], "ID": v['id'],
                "Numere": " ".join(map(str, v['numere'])), 
                "Scor AI": v['scor_ai'],
                "Câștiguri": v['castiguri']
            } for i, v in enumerate(st.session_state.top1150)])
            
            st.info("Top 20 de variante cu cel mai bun scor AI:")
            st.dataframe(top_df.head(20), use_container_width=True)
            
            with st.expander("Afișează toate cele 1150 de variante"):
                st.dataframe(top_df, use_container_width=True, height=500)
                
            txt_export = "\n".join([
                f"{v['ID']}, {' '.join(v['Numere'].split())}" 
                for _, v in top_df.iterrows()
            ])
            st.download_button("📥 Descarcă Top 1150 (txt)", txt_export, "top1150.txt", "text/plain")
        else:
            st.info("Apasă pe buton pentru a calcula Top 1150.")

    with tab2:
        st.subheader("Acoperire Minimă")
        st.write("Găsește cel mai mic set de variante care ar fi „câștigat” (cu `min_match` potriviri) în toate rundele câștigătoare din istoric.")
        
        if st.button("Calculează Acoperirea", type="primary"):
            ac = acoperire_minima(toate_variantele, st.session_state.runde, min_match)
            st.session_state.acoperire = ac
            
        if 'acoperire' in st.session_state:
            acoperire_data = st.session_state.acoperire
            st.success(f"**{len(acoperire_data)} variante** sunt necesare pentru a acoperi toate rundele câștigătoare din istoric.")
            if acoperire_data:
                df_acoperire = pd.DataFrame([
                    {"Chenar": v['chenar'], "ID": v['id'], "Numere": " ".join(map(str, v['numere']))} 
                    for v in acoperire_data
                ])
                st.dataframe(df_acoperire, use_container_width=True)
            else:
                st.warning("Nicio variantă nu a îndeplinit criteriul de câștig minim în rundele furnizate.")
        else:
            st.info("Apasă pe buton pentru a calcula acoperirea minimă.")

    with tab3:
        st.subheader("Top 10 Cele Mai Consistente Variante")
        st.write("Variantele care au avut cea mai mare frecvență de câștiguri (cu `min_match` potriviri) de-a lungul timpului.")
        
        consistente = calculeaza_consistenta(toate_variantele, st.session_state.runde, min_match)
        
        if consistente:
            df_cons = pd.DataFrame([{
                "Chenar": v['chenar'], "ID": v['id'], "Numere": " ".join(map(str, v['numere'])),
                "Frecvență": v['frecventa']
            } for v in consistente[:10]])
            
            st.dataframe(
                df_cons, 
                use_container_width=True,
                column_config={"Frecvență": st.column_config.ProgressColumn("Frecvență", format="%.1f%%", min_value=0, max_value=max(0.01, df_cons['Frecvență'].max()))}
            )
        else:
            st.info("Nu s-au putut calcula date de consistență.")

    with tab4:
        st.subheader("Sugestii Bazate pe Numere Fierbinți")
        
        runde_recente = st.session_state.runde[-50:]
        if runde_recente:
            numere = [n for r in runde_recente for n in r]
            contor_numere = Counter(numere)
            
            hot = [x[0] for x in contor_numere.most_common(18)]
            
            st.write(f"**Cele mai 'fierbinți' 18 numere din ultimele {len(runde_recente)} runde:**")
            st.info(", ".join(map(str, sorted(hot))))
            
            # =============== MODIFICARE: SLIDER SUGESTII ===============
            num_sugestie = st.slider("Numere per sugestie:", 3, 10, 6)
            st.write(f"**Sugestii (combinații aleatorii de {num_sugestie} numere 'fierbinți'):**")
            # ===========================================================

            if len(hot) >= num_sugestie:
                for i in range(5):
                    sugestie = sorted(random.sample(hot, num_sugestie))
                    st.code(f"Sugestia {i+1}:  {'  '.join(map(str, sugestie))}")
            else:
                st.warning(f"Nu există suficiente numere 'fierbinți' (minim {num_sugestie}) pentru a genera sugestii.")
        else:
            st.warning("Nu există runde pentru a calcula numere fierbinți.")

else:
    st.warning("Te rog adaugă cel puțin o rundă și o variantă pentru a începe analiza.")
