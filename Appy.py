import streamlit as st
import pandas as pd
from collections import Counter

# --- Configurare Pagină ---
st.set_page_config(
    page_title="Filtru Variante Unice",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titlul aplicației
st.title("🔢 Filtru de Variante după Frecvența Numerelor")

# --- Funcția de Procesare a Datelor ---
def process_data(input_text, max_occurrence):
    """Procesează datele de intrare și filtrează variantele."""
    
    # 1. Parsarea datelor
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    if not lines:
        return pd.DataFrame(), Counter(), []

    parsed_data = []
    all_numbers = []

    for line in lines:
        try:
            # Separă ID-ul de combinație (prima virgulă)
            id_str, combination_str = line.split(',', 1)
            
            variant_id = id_str.strip()
            # Extrage numerele (le separă după spațiu)
            numbers = [int(n.strip()) for n in combination_str.split() if n.strip().isdigit()]
            
            if numbers:
                parsed_data.append({'ID': variant_id, 'Numere': numbers, 'Linie_Originala': line})
                all_numbers.extend(numbers)
                
        except ValueError:
            st.warning(f"Avertisment: Linia '{line}' a fost ignorată. Formatul nu este corect (ID, Numar Numar...).")
        except Exception as e:
            st.error(f"Eroare la procesarea liniei '{line}': {e}")
            
    if not parsed_data:
        return pd.DataFrame(), Counter(), []

    # 2. Calculul Frecvenței
    # Calculează de câte ori apare fiecare număr în total (pe toate variantele)
    number_counts = Counter(all_numbers)
    
    # 3. Filtrarea Variantelor
    # O variantă este păstrată DOAR dacă TOATE numerele ei au o frecvență <= max_occurrence
    
    filtered_variants = []
    
    for item in parsed_data:
        is_unique_enough = True
        
        # Verifică frecvența fiecărui număr din varianta curentă
        for num in item['Numere']:
            if number_counts[num] > max_occurrence:
                is_unique_enough = False
                break
        
        if is_unique_enough:
            filtered_variants.append(item)
            
    # Pregătirea rezultatului pentru afișare
    df_filtered = pd.DataFrame([
        {'ID': item['ID'], 'Numere': ' '.join(map(str, item['Numere'])), 'Linie_Originala': item['Linie_Originala']}
        for item in filtered_variants
    ])
    
    return df_filtered, number_counts, parsed_data

# --- Interfață Utilizator (UI) ---

with st.sidebar:
    st.header("⚙️ Setări")
    
    # Câmpul de setare a limitei de repetiție
    max_occurrence = st.slider(
        "Maximul de Repetiții Permise (N):",
        min_value=1, 
        max_value=50, 
        value=15, 
        step=1,
        help="Un număr nu poate apărea în întregul set de date de mai mult de N ori pentru ca varianta sa să fie considerată unică."
    )

st.subheader("1. Introduceți Variantele")
input_text = st.text_area(
    "Lipiți variantele aici (câte o variantă pe rând).",
    value="1, 61 34 2 7\n2, 33 24 57 4\n3, 61 1 5 7\n4, 61 7 8 9\n5, 1 2 3 4",
    height=200,
    help="Format: ID, Numar1 Numar2 Numar3..."
)

st.divider()

if st.button("🚀 Rulează Filtrarea"):
    if not input_text:
        st.error("Vă rugăm introduceți date în câmpul de text.")
    else:
        # Apelarea funcției de procesare
        df_filtered, number_counts, all_variants = process_data(input_text, max_occurrence)

        # Afișarea rezultatelor
        st.subheader(f"2. Rezultate Filtrate (Frecvență Max. = {max_occurrence})")

        if df_filtered.empty:
            st.info("Nu a fost găsită nicio variantă care să îndeplinească condiția de unicitate.")
        else:
            st.success(f"Au fost găsite **{len(df_filtered)}** variante unice din **{len(all_variants)}** total:")
            st.dataframe(df_filtered[['ID', 'Numere']], hide_index=True)
            
            # --- Detalii Utile ---
            st.subheader("3. Detalii despre Frecvența Numerelor")
            
            # Creare DataFrame pentru afișarea frecvenței
            counts_df = pd.DataFrame(number_counts.items(), columns=['Număr', 'Frecvență'])
            counts_df = counts_df.sort_values(by='Frecvență', ascending=False)
            
            st.dataframe(counts_df, height=300, hide_index=True)
            
            # Evidențierea numerelor "saturate"
            saturated_numbers = counts_df[counts_df['Frecvență'] > max_occurrence]
            if not saturated_numbers.empty:
                 st.warning(f"🚨 Numerele de mai jos apar de mai mult de {max_occurrence} ori și au cauzat excluderea variantelor care le conțineau:")
                 st.dataframe(saturated_numbers, hide_index=True)
            else:
                 st.info("Toate numerele din setul de date respectă limita de repetiție.")
