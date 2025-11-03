import streamlit as st
import pandas as pd
from collections import Counter
import json
import base64
import random

# ================= CONFIG PAGINĂ =================
st.set_page_config(
    page_title="Loterie AI – Top 1150 Variante Inteligente",
    page_icon="crystal_ball",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
# crystal_ball **Loterie AI**  
### Top 1150 variante cu potențial maxim pentru viitor
""")
st.divider()

# ================= SESSION STATE =================
default_keys = [
    'runde', 'variante_1', 'variante_2', 'variante_3', 'variante_4', 'variante_5',
    'page_runde', 'page_var1', 'page_var2', 'page_var3', 'page_var4', 'page_var5'
]
for key in default_keys:
    if key not in st.session_state:
        st.session_state[key] = [] if 'variante_' in key or key == 'runde' else 1

# ================= FUNCTII DE BAZĂ =================
@st.cache_data(show_spinner=False)
def parse_runde(text):
    if not text.strip():
        return []
    runde = []
    for linie in text.strip().split('\n'):
        try:
            nums = [int(n.strip()) for n in linie.split(',') if n.strip().isdigit()]
            if len(nums) >= 6:
                runde.append(tuple(sorted(nums[:6])))  # doar primele 6
        except:
            continue
    return runde

@st.cache_data(show_spinner=False)
def parse_variante(text, chenar):
    if not text.strip():
        return []
    variante = []
    for linie in text.strip().split('\n'):
        try:
            parti = linie.split(',', 1)
            if len(parti) < 2:
                continue
            id_var = parti[0].strip()
            nums = [int(n.strip()) for n in parti[1].split() if n.strip().isdigit()]
            if len(nums) >= 6:
                variante.append({
                    'id': id_var,
                    'numere': tuple(sorted(nums[:6])),
                    'chenar': chenar
                })
        except:
            continue
    return variante

def potriviri(v, r):
    return len(set(v) & set(r))

# ================= SCOR AI – CU CACHE + PROGRESS =================
@st.cache_data(show_spinner=False)
def calculeaza_scoruri_ai(_variante, _runde, min_match):
    if not _runde or not _variante:
        return []
    
    rezultate = []
    total = len(_variante)
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, var in enumerate(_variante):
        v = var['numere']
        castiguri = sum(1 for r in _runde if potriviri(v, r) >= min_match)
        
        # Consistență pe ferestre de 10 runde
        window = 10
        wins = []
        for i in range(0, len(_runde), window):
            chunk = _runde[i:i+window]
            win = any(potriviri(v, r) >= min_match for r in chunk)
            wins.append(1 if win else 0)
        
        if wins:
            mean = sum(wins) / len(wins)
            variance = sum((x - mean)**2 for x in wins) / len(wins)
            consistenta = max(0, 1 - (variance ** 0.5))
            recent = sum(wins[-3:]) / min(3, len(wins))
        else:
            consistenta = recent = mean = 0
        
        scor = (
            castiguri * 8 +
            mean * 100 +
            consistenta * 50 +
            recent * 120 +
            len(set(v)) * 2
        )
        
        rezultate.append({
            **var,
            'scor_ai': round(scor, 2),
            'castiguri': castiguri,
            'consistenta': round(consistenta, 3),
            'recent': round(recent, 3)
        })
        
        progress_bar.progress((idx + 1) / total)
        status_text.text(f"Procesare: {idx + 1}/{total} variante...")
    
    progress_bar.empty()
    status_text.empty()
    return rezultate

# ================= ACOPERIRE MINIMĂ =================
@st.cache_data(show_spinner=False)
def acoperire_minima(_variante, _runde, min_match):
    runde_castig = [i for i, r in enumerate(_runde) if any(potriviri(v['numere'], r) >= min_match for v in _variante)]
    if not runde_castig:
        return []
    
    acoperite = set()
    selectate = []
    variante_ramase = _variante[:]
    
    with st.spinner(f"Calcul acoperire pentru {len(runde_castig)} runde..."):
        while len(acoperite) < len(runde_castig) and variante_ramase:
            best = max(variante_ramase, key=lambda v: sum(
                1 for i in runde_castig if i not in acoperite and potriviri(v['numere'], _runde[i]) >= min_match
            ), default=None)
            if not best:
                break
            selectate.append(best)
            acoperite.update(i for i in runde_castig if potriviri(best['numere'], _runde[i]) >= min_match)
            variante_ramase = [v for v in variante_ramase if v['id'] != best['id']]
    
    return selectate

# ================= PAGINARE HELPER =================
def paginare(df, key, page_size=50, height=300):
    total = len(df)
    if total == 0:
        st.info("Nicio intrare.")
        return
    page = st.session_state.get(f'page_{key}', 1)
    total_pages = max(1, (total - 1) // page_size + 1)
    start = (page - 1) * page_size
    end = start + page_size
    df_page = df.iloc[start:end].copy()
    df_page.index = range(start + 1, end + 1)
    
    st.dataframe(df_page, use_container_width=True, height=height)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("◀", key=f"prev_{key}", disabled=page <= 1):
            st.session_state[f'page_{key}'] = page - 1
            st.rerun()
    with col2:
        st.write(f"**Pagina {page} / {total_pages}** | Total: {total}")
    with col3:
        if st.button("▶", key=f"next_{key}", disabled=page >= total_pages):
            st.session_state[f'page_{key}'] = page + 1
            st.rerun()

# ================= UI: RUNDE =================
st.header("clipboard **Runde jucate**")

with st.form("form_runde"):
    text_runde = st.text_area(
        "Format: 1,6,7,9,44,77",
        height=120,
        placeholder="1,6,7,9,44,77\n2,5,3,77,6,56",
        key="input_runde"
    )
    col1, col2 = st.columns(2)
    with col1:
        add_runde = st.form_submit_button("Adaugă runde", type="primary")
    with col2:
        clear_runde = st.form_submit_button("Șterge toate rundele")

    if add_runde and text_runde.strip():
        noi = parse_runde(text_runde)
        st.session_state.runde.extend(noi)
        st.success(f"Adăugate {len(noi)} runde")
        st.rerun()
    if clear_runde:
        st.session_state.runde = []
        st.rerun()

with st.expander("Afișează toate rundele"):
    if st.session_state.runde:
        df_runde = pd.DataFrame(st.session_state.runde)
        df_runde.index = range(1, len(df_runde) + 1)
        paginare(df_runde, "runde", page_size=50, height=300)
    else:
        st.info("Nicio rundă adăugată.")

st.divider()

# ================= UI: CHENARE =================
st.header("game_dice **Chenare cu variante**")

for i in range(1, 6):
    key = f'variante_{i}'
    label = f"Chenar {i}"
    with st.expander(f"**{label}** – {len(st.session_state[key])} variante", expanded=False):
        with st.form(f"form_{key}"):
            text_var = st.text_area(
                f"Format: 1, 6 7 5 77",
                height=100,
                placeholder="1, 6 7 5 77\n2, 4 65 45 23",
                key=f"input_{key}"
            )
            c1, c2 = st.columns(2)
            with c1:
                add_btn = st.form_submit_button("Adaugă", type="primary")
            with c2:
                clear_btn = st.form_submit_button("Șterge")

            if add_btn and text_var.strip():
                noi = parse_variante(text_var, f'C{i}')
                st.session_state[key].extend(noi)
                st.success(f"Adăugate {len(noi)} variante")
                st.rerun()
            if clear_btn:
                st.session_state[key] = []
                st.rerun()

        if st.session_state[key]:
            df = pd.DataFrame([{
                "ID": v['id'],
                "Numere": " ".join(map(str, v['numere']))
            } for v in st.session_state[key]])
            paginare(df, f"var{i}", page_size=30, height=250)

# ================= TOATE VARIANTELE =================
toate_variantele = []
for i in range(1, 6):
    toate_variantele.extend(st.session_state[f'variante_{i}'])

# ================= ANALIZĂ STRATEGICĂ =================
if st.session_state.runde and toate_variantele:
    min_match = st.slider(
        "**Numere minime pentru câștig:**",
        min_value=2, max_value=6, value=4, step=1
    )
    
    st.divider()
    tab1, tab2, tab3, tab4 = st.tabs([
        "Top 1150 AI", "Acoperire Minimă", "Consistente", "Sugestii Viitor"
    ])

    # ================= TAB 1: TOP 1150 AI =================
    with tab1:
        st.subheader("star **Top 1150 variante – Scor AI Predictiv**")
        if st.button("Calculează TOP 1150", type="primary", use_container_width=True):
            with st.spinner("Se calculează scorurile inteligente..."):
                variante_cu_scor = calculeaza_scoruri_ai(toate_variantele, st.session_state.runde, min_match)
                top1150 = sorted(variante_cu_scor, key=lambda x: x['scor_ai'], reverse=True)[:1150]
                st.session_state.top1150 = top1150
                st.success("TOP 1150 calculat!")

        if 'top1150' in st.session_state and st.session_state.top1150:
            df_top = pd.DataFrame([{
                "Poz": i+1,
                "Chenar": v['chenar'],
                "ID": v['id'],
                "Numere": " ".join(map(str, v['numere'])),
                "Scor AI": v['scor_ai'],
                "Câștiguri": v['castiguri']
            } for i, v in enumerate(st.session_state.top1150)])
            
            st.dataframe(df_top.head(20), use_container_width=True, height=400)
            with st.expander("Vezi toate 1150 variantele"):
                st.dataframe(df_top, height=500, use_container_width=True)
            
            txt = "\n".join([
                f"{v['id']}, {' '.join(map(str, v['numere']))}"
                for v in st.session_state.top1150
            ])
            st.download_button(
                "Descarcă TOP 1150 (TXT)",
                txt,
                "top_1150_ai.txt",
                "text/plain",
                use_container_width=True
            )

    # ================= TAB 2: ACOPERIRE MINIMĂ =================
    with tab2:
        st.subheader("shield **Acoperire Minimă – Garantat 1 câștig per rundă**")
        if st.button("Găsește set minim de variante", type="primary"):
            acoperire = acoperire_minima(toate_variantele, st.session_state.runde, min_match)
            st.session_state.acoperire = acoperire
        
        if 'acoperire' in st.session_state and st.session_state.acoperire:
            st.write(f"**Doar {len(st.session_state.acoperire)} variante acoperă toate câștigurile posibile!**")
            df = pd.DataFrame([{
                "Chenar": v['chenar'],
                "ID": v['id'],
                "Numere": " ".join(map(str, v['numere']))
            } for v in st.session_state.acoperire])
            st.dataframe(df, use_container_width=True)

    # ================= TAB 3: CONSISTENTE =================
    with tab3:
        st.subheader("chart_with_upwards_trend **Cele mai consistente variante**")
        consistente = sorted(toate_variantele, key=lambda v: (
            lambda: (
                sum(1 for r in st.session_state.runde if potriviri(v['numere'], r) >= min_match) /
                len(st.session_state.runde) if st.session_state.runde else 0
            )
        )(), reverse=True)[:10]
        
        df = pd.DataFrame([{
            "ID": v['id'],
            "Chenar": v['chenar'],
            "Numere": " ".join(map(str, v['numere'])),
            "Frecvență câștig": f"{sum(1 for r in st.session_state.runde if potriviri(v['numere'], r) >= min_match) / len(st.session_state.runde):.1%}"
        } for v in consistente])
        st.dataframe(df, use_container_width=True)

    # ================= TAB 4: SUGESTII VIITOR =================
    with tab4:
        st.subheader("fire **Sugestii pentru următoarea rundă**")
        recente = st.session_state.runde[-50:] if len(st.session_state.runde) > 50 else st.session_state.runde
        toate = [n for r in recente for n in r]
        hot = [x[0] for x in Counter(toate).most_common(18)]
        st.write("**Numere fierbinți (ultimele 50 runde):**")
        st.write(", ".join(map(str, hot)))
        
        st.write("**5 variante sugerate pentru următoarea rundă:**")
        for i in range(5):
            sug = sorted(random.sample(hot, 6))
            st.write(f"**{i+1}.** `{' , '.join(map(str, sug))}`")

else:
    st.info("Adăugă runde și cel puțin un chenar cu variante pentru a începe analiza.")

# ================= SIDEBAR: BACKUP & INFO =================
with st.sidebar:
    st.header("backup **Backup & Restore**")
    
    if st.button("Salvează sesiune (JSON)"):
        data = {k: v for k, v in st.session_state.items() if k.startswith('variante_') or k == 'runde'}
        b64 = base64.b64encode(json.dumps(data, ensure_ascii=False).encode()).decode()
        st.download_button(
            "Descarcă backup.json",
            b64,
            "lottery_backup.json",
            "application/json"
        )
    
    uploaded = st.file_uploader("Încarcă backup", type="json")
    if uploaded:
        try:
            data = json.load(uploaded)
            for k, v in data.items():
                if k in st.session_state:
                    st.session_state[k] = v
            st.success("Backup încărcat cu succes!")
            st.rerun()
        except:
            st.error("Fișier invalid.")
    
    st.divider()
    st.metric("Total runde", len(st.session_state.runde))
    st.metric("Total variante", len(toate_variantele))