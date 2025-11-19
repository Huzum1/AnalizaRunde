import streamlit as st
import pandas as pd
from collections import defaultdict, Counter
import random

# --- Configurare Pagină ---
st.set_page_config(
    page_title="Echilibrare Frecvențe Variante",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titlul aplicației
st.title("⚖️ Echilibrare Frecvențe Variante (Limita N)")

# --- Funcția de Procesare a Datelor ---
def parse_input(input_text):
    """Parsează datele introduse manual."""
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    parsed_data = []
    
    for line in lines:
        try:
            # Separă ID-ul de combinație (prima virgulă)
            id_str, combination_str = line.split(',', 1)
            variant_id = id_str.strip()
            # Extrage numerele (le separă după spațiu)
            # Folosim set pentru a ne asigura că nu avem numere duplicate în interiorul unei variante
            numbers = [int(n.strip()) for n in combination_str.split() if n.strip().isdigit()]
            
            if numbers:
                # Stocăm varianta ca o tuplă (ID, set de numere, linie_originala)
                parsed_data.append((variant_id, set(numbers), line))
                
        except:
            # Ignorăm liniile cu format greșit
            continue
            
    return parsed_data

def balance_variants(all_variants, max_occurrence):
    """Echilibrează selecția variantelor pentru a respecta limita de repetiție."""
    
    if not all_variants:
        return [], Counter()

    # 1. Inițializare
    selected_ids = set()
    current_counts = Counter()
    
    # Randomizăm ordinea variantelor pentru a evita biasul
    random.shuffle(all_variants)

    # 2. Procesul de selecție iterativă (Greedy)
    for variant in all_variants:
        variant_id = variant[0]
        numbers = variant[1]
        
        # Verificăm dacă varianta poate fi adăugată fără a depăși limita N
        can_be_added = True
        for num in numbers:
            if current_counts[num] >= max_occurrence:
                can_be_added = False
                break
        
        # Dacă este OK, o adăugăm și actualizăm contorul
        if can_be_added:
            selected_ids.add(variant_id)
            for num in numbers:
                current_counts[num] += 1

    # 3. Construirea rezultatului final (doar variantele selectate)
    # Păstrăm ordinea inițială a liniilor originale
    final_result_tuples = [v for v in all_variants if v[0] in selected_ids]
    
    return final_result_tuples, current_counts

# --- Interfață Utilizator (UI) ---

with st.sidebar:
    st.header("⚙️ Setări")
    
    max_occurrence = st.number_input(
        "Limită Maximă de Apariții (N) per Număr:",
        min_value=1, 
        max_value=10000, 
        value=15, 
        step=1,
        help="Niciun număr nu va apărea în setul de variante rezultat de mai mult de N ori."
    )
    st.info("Logica: Se încearcă selectarea maximului de variante, respectând limita N pentru fiecare număr.")

st.subheader("1. Introduceți Variantele")
input_text = st.text_area(
    "Lipiți variantele aici (câte o variantă pe rând).",
    value="1, 61 34 2 7\n2, 33 24 57 4\n3, 61 1 5 7\n4, 61 7 8 9\n5, 1 2 3 4",
    height=200,
    help="Format: ID, Numar1 Numar2 Numar3... (folosește un ID unic pentru fiecare rând)."
)

st.divider()

if st.button("🚀 Rulează Echilibrarea"):
    if not input_text:
        st.error("Vă rugăm introduceți date în câmpul de text.")
    else:
        # 1. Parsare
        all_variants = parse_input(input_text)
        
        if not all_variants:
            st.error("Nu s-au putut parsa variante valide. Verificați formatul (ID, Numar Numar...).")
        else:
            total_variants = len(all_variants)
            
            # 2. Echilibrare
            final_result_tuples, final_counts = balance_variants(all_variants, max_occurrence)

            # 3. Afișare Rezultate
            st.subheader(f"2. Rezultate Echilibrate (Limită N = {max_occurrence})")

            if not final_result_tuples:
                st.info("Nu a putut fi selectată nicio variantă care să respecte condițiile.")
            else:
                num_selected = len(final_result_tuples)
                st.success(f"Au fost selectate **{num_selected}** variante din **{total_variants}** totale.")
                
                # Construiește șirul de text pentru copiere
                # V3[2] este linia originală ('1, 61 34 2 7')
                text_to_copy = "\n".join([v[2] for v in final_result_tuples])

                # --- Chenar pentru Copiere ---
                st.subheader("📋 Variante pentru Copiere")
                st.code(text_to_copy, language='text')

                # Afișare în tabel (pentru vizualizare rapidă)
                st.subheader("Vizualizare (Tabel)")
                df_final = pd.DataFrame([
                    {'ID': v[0], 'Numere': ' '.join(map(str, sorted(list(v[1]))))}
                    for v in final_result_tuples
                ])
                st.dataframe(df_final[['ID', 'Numere']], hide_index=True)

                # --- Detalii Utile ---
                st.subheader("3. Verificarea Frecvenței în Setul Rezultat")
                
                counts_df = pd.DataFrame(final_counts.items(), columns=['Număr', 'Frecvență'])
                counts_df = counts_df.sort_values(by='Frecvență', ascending=False)
                
                st.info(f"Frecvența maximă obținută este: **{counts_df['Frecvență'].max() if not counts_df.empty else 0}** (ar trebui să fie $\le {max_occurrence}$)")
                
                st.dataframe(counts_df, height=300, hide_index=True)
