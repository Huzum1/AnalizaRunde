import streamlit as st
import pandas as pd
from collections import Counter
import json
import base64
import random

# ================= CONFIG =================
st.set_page_config(
    page_title="Loterie AI – Top 1150",
    page_icon="crystal_ball",
    layout="wide"
)

st.title("crystal_ball **Loterie AI – Top 1150 Variante Inteligente**")
st.divider()

# ================= SESSION STATE =================
for key in ['runde', 'variante_1', 'variante_2', 'variante_3', 'variante_4', 'variante_5']:
    if key not in st.session_state:
        st.session_state[key] = []
for key in ['page_runde'] + [f'page_var{i}' for i in range(1,6)]:
    if key not in st.session_state:
        st.session_state[key] = 1

# ================= PARSARE FLEXIBILĂ (ORICE FORMAT!) =================
@st.cache_data(show_spinner=False)
def parse_runde(text):
    if not text.strip(): return []
    runde = []
    for linie in text.strip().split('\n'):
        linie = linie.strip()
        if not linie: continue
        # Acceptă: 1,6,7,9,44,77  sau 1 6 7 9 44 77
        nums = [int(x) for x in linie.replace(',', ' ').split() if x.isdigit()]
        if len(nums) >= 6:
            runde.append(tuple(sorted(nums[:6])))
    return runde

@st.cache_data(show_spinner=False)
def parse_variante(text, chenar):
    if not text.strip(): return []
    variante = []
    for linie in text.strip().split('\n'):
        linie = linie.strip()
        if not linie: continue
        # Acceptă: 1, 6 7 5 77  sau  1,6 7 5 77  sau  1 6 7 5 77
        parts = linie.replace(',', ' ').split()
        if not parts: continue
        try:
            id_var = parts[0]
            nums = [int(x) for x in parts[1:] if x.isdigit()]
            if len(nums) >= 6:
                variante.append({
                    'id': id_var,
                    'numere': tuple(sorted(nums[:6])),
                    'chenar': chenar
                })
        except:
            continue
    return variante

def potriviri(v, r): return len(set(v) & set(r))

# ================= SCOR AI =================
@st.cache_data(show_spinner=False)
def calculeaza_scoruri_ai(_variante, _runde, min_match):
    if not _runde or not _variante: return []
    rezultate = []
    total = len(_variante)
    progress = st.progress(0)
    for idx, var in enumerate(_variante):
        v = var['numere']
        castiguri = sum(1 for r in _runde if potriviri(v, r) >= min_match)
        window = 10
        wins = [any(potriviri(v, r) >= min_match for r in _runde[i:i+window]) 
                for i in range(0, len(_runde), window)]
        mean = sum(wins) / len(wins) if wins else 0
        variance = sum((x - mean)**2 for x in wins) / len(wins) if wins else 0
        consistenta = max(0, 1 - (variance ** 0.5))
        recent = sum(wins[-3:]) / min(3, len(wins)) if wins else 0
        scor = castiguri * 8 + mean * 100 + consistenta * 50 + recent * 120 + len(set(v)) * 2
        rezultate.append({**var, 'scor_ai': round(scor, 2), 'castiguri': castiguri})
        progress.progress((idx + 1) / total)
    progress.empty()
    return rezultate

# ================= ACOPERIRE MINIMĂ =================
@st.cache_data(show_spinner=False)
def acoperire_minima(_variante, _runde, min_match):
    runde_castig = [i for i, r in enumerate(_runde) if any(potriviri(v['numere'], r) >= min_match for v in _variante)]
    if not runde_castig: return []
    acoperite = set()
    selectate = []
    ramase = _variante[:]
    while len(acoperite) < len(runde_castig) and ramase:
        best = max(ramase, key=lambda v: sum(1 for i in runde_castig if i not in acoperite and potriviri(v['numere'], _runde[i]) >= min_match), default=None)
        if not best: break
        selectate.append(best)
        acoperite.update(i for i in runde_castig if potriviri(best['numere'], _runde[i]) >= min_match)
        ramase = [v for v in ramase if v['id'] != best['id']]
    return selectate

# ================= PAGINARE =================
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
        if st.button("Previous", key=f"prev_{key}", disabled=page <= 1):
            st.session_state[f'page_{key}'] = page - 1
            st.rerun()
    with col2:
        st.write(f"**Pagina {page} / {total_pages}** | Total: {total}")
    with col3:
        if st.button("Next", key=f"next_{key}", disabled=page >= total_pages):
            st.session_state[f'page_{key}'] = page + 1
            st.rerun()

# ================= UI: RUNDE =================
st.header("clipboard **Runde**")
with st.form("form_runde"):
    text_runde = st.text_area(
        "Ex: 1,6,7,9,44,77  sau  1 6 7 9 44 77",
        height=120,
        placeholder="1,6,7,9,44,77\n2 5 3 77 6 56",
        key="input_runde"
    )
    c1, c2 = st.columns(2)
    with c1:
        if st.form_submit_button("Adaugă runde", type="primary"):
            noi = parse_runde(text_runde)
            st.session_state.runde.extend(noi)
            st.success(f"Adăugate {len(noi)} runde")
            st.rerun()
    with c2:
        if st.form_submit_button("Șterge toate"):
            st.session_state.runde = []
            st.rerun()

with st.expander("Afișează rundele"):
    if st.session_state.runde:
        df = pd.DataFrame(st.session_state.runde)
        df.index = range(1, len(df)+1)
        paginare(df, "runde")
    else:
        st.info("Nicio rundă.")

st.divider()

# ================= UI: CHENARE =================
st.header("game_dice **Chenare**")

for i in range(1, 6):
    key = f'variante_{i}'
    with st.container():
        with st.form(f"form_{key}"):
            st.subheader(f"Chenar {i}")
            text_var = st.text_area(
                "Ex: 1, 6 7 5 77  sau  1 6 7 5 77",
                height=100,
                placeholder="1, 6 7 5 77\n2 4 65 45 23",
                key=f"input_var_{i}"
            )
            c1, c2 = st.columns(2)
            with c1:
                if st.form_submit_button("Adaugă", type="primary"):
                    noi = parse_variante(text_var, f'C{i}')
                    st.session_state[key].extend(noi)
                    st.success(f"Adăugate {len(noi)} variante")
                    st.rerun()
            with c2:
                if st.form_submit_button("Șterge"):
                    st.session_state[key] = []
                    st.rerun()

    with st.expander(f"Afișează variantele din Chenar {i}"):
        if st.session_state[key]:
            df = pd.DataFrame([{"ID": v['id'], "Numere": " ".join(map(str, v['numere']))} for v in st.session_state[key]])
            paginare(df, f"var{i}")
        else:
            st.info("Nicio variantă.")

# ================= TOATE VARIANTELE =================
toate_variantele = sum((st.session_state[f'variante_{i}'] for i in range(1,6)), [])

# ================= ANALIZĂ =================
if st.session_state.runde and toate_variantele:
    min_match = st.slider("Câștig minim:", 2, 6, 4)

    tab1, tab2, tab3, tab4 = st.tabs(["Top 1150", "Acoperire", "Consistente", "Sugestii"])

    with tab1:
        if st.button("Calculează TOP 1150"):
            with st.spinner("Se calculează..."):
                scoruri = calculeaza_scoruri_ai(toate_variantele, st.session_state.runde, min_match)
                top = sorted(scoruri, key=lambda x: x['scor_ai'], reverse=True)[:1150]
                st.session_state.top1150 = top
        if 'top1150' in st.session_state:
            df = pd.DataFrame([{
                "Poz": i+1, "Chenar": v['chenar'], "ID": v['id'],
                "Numere": " ".join(map(str, v['numere'])), "Scor AI": v['scor_ai']
            } for i, v in enumerate(st.session_state.top1150)])
            st.dataframe(df.head(20))
            with st.expander("Toate 1150"):
                st.dataframe(df)
            txt = "\n".join([f"{v['id']}, {' '.join(map(str, v['numere']))}" for v in st.session_state.top1150])
            st.download_button("Descarcă", txt, "top.txt", "text/plain")

    with tab2:
        if st.button("Acoperire minimă"):
            ac = acoperire_minima(toate_variantele, st.session_state.runde, min_match)
            st.session_state.acoperire = ac
        if 'acoperire' in st.session_state:
            st.write(f"**{len(st.session_state.acoperire)} variante acoperă toate câștigurile!**")
            df = pd.DataFrame([{"ID": v['id'], "Numere": " ".join(map(str, v['numere']))} for v in st.session_state.acoperire])
            st.dataframe(df)

    with tab3:
        cons = sorted(toate_variantele, key=lambda v: sum(1 for r in st.session_state.runde if potriviri(v['numere'], r) >= min_match) / len(st.session_state.runde), reverse=True)[:10]
        df = pd.DataFrame([{
            "ID": v['id'], "Numere": " ".join(map(str, v['numere'])),
            "Frecvență": f"{sum(1 for r in st.session_state.runde if potriviri(v['numere'], r) >= min_match) / len(st.session_state.runde):.1%}"
        } for v in cons])
        st.dataframe(df)

    with tab4:
        recente = st.session_state.runde[-50:] if len(st.session_state.runde) > 50 else st.session_state.runde
        hot = [x[0] for x in Counter([n for r in recente for n in r]).most_common(18)]
        st.write("**Numere fierbinți:**", ", ".join(map(str, hot)))
        for i in range(5):
            sug = sorted(random.sample(hot, 6))
            st.write(f"**Sugestie {i+1}:** `{' , '.join(map(str, sug))}`")

else:
    st.info("Adaugă runde și variante.")

# ================= SIDEBAR =================
with st.sidebar:
    if st.button("Salvează backup"):
        data = {k: v for k, v in st.session_state.items() if k.startswith('variante_') or k == 'runde'}
        b64 = base64.b64encode(json.dumps(data).encode()).decode()
        st.download_button("backup.json", b64, "lottery.json", "application/json")
    uploaded = st.file_uploader("Restore", type="json")
    if uploaded:
        st.session_state.update(json.load(uploaded))
        st.rerun()