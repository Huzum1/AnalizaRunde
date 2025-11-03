import streamlit as st
import pandas as pd
from collections import Counter
import json
import base64
import random
from itertools import combinations

# ================= CONFIG =================
st.set_page_config(page_title="Loterie AI", page_icon="crystal_ball", layout="wide")
st.title("crystal_ball Loterie AI – Top 1150 Variante cu Potențial Viitor")
st.divider()

# ================= SESSION STATE =================
for key in ['runde', 'variante_1', 'variante_2', 'variante_3', 'variante_4', 'variante_5']:
    if key not in st.session_state:
        st.session_state[key] = []
for key in ['page_runde', 'page_var1', 'page_var2', 'page_var3', 'page_var4', 'page_var5']:
    if key not in st.session_state:
        st.session_state[key] = 1

# ================= FUNCTII DE BAZĂ =================
@st.cache_data(show_spinner=False)
def parse_runde(text):
    if not text.strip(): return []
    runde = []
    for linie in text.strip().split('\n'):
        try:
            nums = [int(n.strip()) for n in linie.split(',') if n.strip().isdigit()]
            if nums: runde.append(tuple(sorted(nums)))
        except: continue
    return runde

@st.cache_data(show_spinner=False)
def parse_variante(text, chenar):
    if not text.strip(): return []
    variante = []
    for linie in text.strip().split('\n'):
        try:
            parti = linie.split(',', 1)
            if len(parti) < 2: continue
            id_var = parti[0].strip()
            nums = [int(n.strip()) for n in parti[1].split() if n.strip().isdigit()]
            if nums: variante.append({'id': id_var, 'numere': tuple(sorted(nums)), 'chenar': chenar})
        except: continue
    return variante

def potriviri(v, r): return len(set(v) & set(r))

# ================= STRATEGII NOI =================

# 1. Consistență pe ferestre
def consistenta_varianta(varianta, runde, min_match, window=10):
    if len(runde) < window: 
        win_rate = sum(1 for r in runde if potriviri(varianta, r) >= min_match) / len(runde) if runde else 0
        return win_rate, win_rate, len(runde)
    
    wins = []
    for i in range(0, len(runde), window):
        chunk = runde[i:i+window]
        win = any(potriviri(varianta, r) >= min_match for r in chunk)
        wins.append(1 if win else 0)
    
    mean = sum(wins) / len(wins)
    variance = sum((x - mean)**2 for x in wins) / len(wins) if wins else 0
    consistenta = 1 - (variance ** 0.5)
    recent = sum(wins[-3:]) / min(3, len(wins)) if wins else 0
    return consistenta, mean, recent

# 2. Set Cover pentru acoperire minimă
@st.cache_data(show_spinner=False)
def acoperire_minima(variante, runde, min_match):
    runde_castig = [i for i, r in enumerate(runde) if any(potriviri(v['numere'], r) >= min_match for v in variante)]
    if not runde_castig: return []
    
    acoperite = set()
    selectate = []
    while len(acoperite) < len(runde_castig):
        best = max(variante, key=lambda v: len(
            {i for i in runde_castig if i not in acoperite and potriviri(v['numere'], runde[i]) >= min_match}
        ), default=None)
        if not best or not any(i not in acoperite and potriviri(best['numere'], runde[i]) >= min_match for i in runde_castig):
            break
        selectate.append(best)
        acoperite.update({i for i in runde_castig if potriviri(best['numere'], runde[i]) >= min_match})
    return selectate

# 3. Numere fierbinți
def numere_fierbinti(runde, top_n=20, recent_weight=3):
    toate = []
    for i, r in enumerate(runde):
        weight = recent_weight if i >= len(runde) - 20 else 1
        toate.extend([n] * weight for n in r)
    return [x[0] for x in Counter(toate).most_common(top_n)]

# 4. Scor predictiv avansat
def scor_predictiv(var, runde, min_match):
    v = var['numere']
    castiguri = sum(1 for r in runde if potriviri(v, r) >= min_match)
    consistenta, frecventa, recent = consistenta_varianta(v, runde, min_match)
    
    scor = 0
    scor += castiguri * 8
    scor += frecventa * 100
    scor += consistenta * 50
    scor += recent * 120
    scor += len(set(v)) * 2
    return round(scor, 2)

# ================= UI: INPUT =================
st.header("clipboard Runde")
with st.form("form_runde"):
    text_runde = st.text_area("1,2,3,4,5,6", height=100)
    c1, c2 = st.columns(2)
    if c1.form_submit_button("Adaugă", type="primary"):
        st.session_state.runde.extend(parse_runde(text_runde))
        st.rerun()
    if c2.form_submit_button("Șterge"):
        st.session_state.runde = []
        st.rerun()

with st.expander("Afișează runde"):
    if st.session_state.runde:
        df = pd.DataFrame(st.session_state.runde)
        df.index = range(1, len(df)+1)
        st.dataframe(df, height=200)

st.divider()
st.header("game_dice Chenare")

for i in range(1, 6):
    key = f'variante_{i}'
    with st.expander(f"Chenar {i} – {len(st.session_state[key])} variante"):
        with st.form(f"form_c{i}"):
            text = st.text_area("1, 1 2 3 4 5 6", height=80, key=f"in_c{i}")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("Adaugă", type="primary"):
                st.session_state[key].extend(parse_variante(text, f'C{i}'))
                st.rerun()
            if c2.form_submit_button("Șterge"):
                st.session_state[key] = []
                st.rerun()

toate_variantele = sum((st.session_state[f'variante_{i}'] for i in range(1,6)), [])

# ================= ANALIZĂ STRATEGICĂ =================
if st.session_state.runde and toate_variantele:
    min_match = st.slider("Câștig minim", 2, 6, 4)
    
    tab1, tab2, tab3, tab4 = st.tabs(["Top 1150 (AI)", "Acoperire Minimă", "Consistente", "Sugestii Viitor"])

    with tab1:
        st.subheader("star Top 1150 Variante – Scor Predictiv")
        with st.spinner("Calculare..."):
            for v in toate_variantele:
                v['scor_ai'] = scor_predictiv(v, st.session_state.runde, min_match)
            top1150 = sorted(toate_variantele, key=lambda x: x['scor_ai'], reverse=True)[:1150]
        
        df_top = pd.DataFrame([{
            "Poz": i+1,
            "Chenar": v['chenar'],
            "ID": v['id'],
            "Numere": " ".join(map(str, v['numere'])),
            "Scor AI": v['scor_ai'],
            "Câștiguri": sum(1 for r in st.session_state.runde if potriviri(v['numere'], r) >= min_match)
        } for i, v in enumerate(top1150)])
        
        st.dataframe(df_top.head(20), use_container_width=True, height=400)
        with st.expander("Toate 1150"):
            st.dataframe(df_top, height=500)
        
        txt = "\n".join([f"{v['id']}, {' '.join(map(str, v['numere']))}" for v in top1150])
        st.download_button("Descarcă TOP 1150", txt, "top_1150_ai.txt", "text/plain")

    with tab2:
        st.subheader("shield Acoperire Minimă (Set Cover)")
        acoperire = acoperire_minima(toate_variantele, st.session_state.runde, min_match)
        st.write(f"**{len(acoperire)} variante acoperă toate câștigurile posibile**")
        if acoperire:
            df = pd.DataFrame([{
                "Chenar": v['chenar'], "ID": v['id'], "Numere": " ".join(map(str, v['numere']))
            } for v in acoperire])
            st.dataframe(df, use_container_width=True)

    with tab3:
        st.subheader("chart_with_upwards_trend Cele Mai Consistente")
        consistente = sorted(toate_variantele, key=lambda v: consistenta_varianta(v['numere'], st.session_state.runde, min_match)[0], reverse=True)[:10]
        df = pd.DataFrame([{
            "ID": v['id'], "Numere": " ".join(map(str, v['numere'])),
            "Consistenta": f"{consistenta_varianta(v['numere'], st.session_state.runde, min_match)[0]:.3f}"
        } for v in consistente])
        st.dataframe(df)

    with tab4:
        st.subheader("fire Numere Fierbinți & Sugestii")
        hot = numere_fierbinti(st.session_state.runde[-50:] if len(st.session_state.runde) > 50 else st.session_state.runde)
        st.write("**Numere fierbinți:**", ", ".join(map(str, hot)))
        
        st.write("**5 sugestii pentru următoarea rundă:**")
        for i in range(5):
            sug = sorted(random.sample(hot, 6))
            st.write(f"{i+1}. **{', '.join(map(str, sug))}**")

else:
    st.info("Adaugă runde și variante pentru analiză strategică.")

# ================= SIDEBAR: BACKUP =================
with st.sidebar:
    st.header("backup Backup")
    if st.button("Salvează"):
        data = {k: st.session_state[k] for k in st.session_state if k.startswith('variante_') or k == 'runde'}
        b64 = base64.b64encode(json.dumps(data).encode()).decode()
        st.download_button("backup.json", b64, "lottery_ai.json", "application/json")
    uploaded = st.file_uploader("Restore", type="json")
    if uploaded:
        st.session_state.update(json.load(uploaded))
        st.rerun()