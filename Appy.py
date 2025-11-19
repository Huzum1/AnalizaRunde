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
            numbers = [int(n.strip()) for n in combination_str.split() if n.strip().isdigit()]
            
            if numbers:
                # Stocăm varianta ca o tuplă (ID, set de numere)
                parsed_data.append((variant_id, set(numbers), line))
                
        except:
            # Ignorăm liniile cu format greșit
            continue
            
    return parsed_data

def balance_variants(all_variants, max_occurrence):
    """Echilibrează selecția variantelor pentru a respecta limita de repetiție."""
    
    if not all_variants:
        return []

    # 1. Indexarea variantelor după număr
    # variants_by_number[numar] = [variant_originala1, variant_originala2, ...]
    variants_by_number = defaultdict(list)
    for variant in all_variants:
        for num in variant[1]: # variant[1] este setul de numere
            variants_by_number[num].append(variant)

    # 2. Inițializare
    # Selected: Set de ID-uri (chei unice) ale variantelor selectate
    selected_ids = set()
    # Current_Counts: Contorul de frecvență al numerelor în setul rezultat
    current_counts = Counter()
    
    # Randomizăm ordinea numerelor pentru a evita biasul
    all_numbers = list(variants_by_number.keys())
    random.shuffle(all_numbers)

    # 3. Procesul de selecție iterativă
    # Prioritizăm variantele care conțin numere mai puțin frecvente în selecția curentă.
    
    # Sortăm variantele inițiale o singură dată (ID, set, linie_originala)
    random.shuffle(all_variants)

    for variant in all_variants:
        variant_id = variant[0]
        numbers = variant[1]
        
        # Verificăm dacă varianta poate fi adăugată fără a depăși limita
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

    # 4. Construirea rezultatului final (doar variantele selectate)
    final_result = [v for v in all_variants if v[0] in selected_ids]
    
    return final_result, current_counts

# --- Interfață Utilizator (UI) ---

with st.sidebar:
    st.header("⚙️ Setări")
    
    # Câmpul de setare a limitei de repetiție
    max_occurrence = st.number_input(
        "Limită Maximă de Apariții (N) per Număr:",
        min_value=1, 
        max_value=10000, 
        value=15, 
        step=1,
        help="Niciun număr (e.g., 7) nu va apărea în setul de variante rezultat de mai mult de N ori."
    )
    st.info("Logica: Aplicația încearcă să selecteze cât mai multe variante din total, respectând limita N pentru fiecare număr individual.")

st.subheader("1. Introduceți Variantele")
input_text = st.text_area(
    "Lipiți variantele aici (câte o variantă pe rând).",
    value="1, 61 34 2 7\n2, 33 24 57 4\n3, 61 1 5 7\n4, 61 7 8 9\n5, 1 2 3 4\n6, 7 10 11 12\n7, 7 13 14 15\n8, 7 16 17 18\n9, 7 19 20 21\n10, 7 22 23 24\n11, 7 25 26 27\n12, 7 28 29 30\n13, 7 31 32 33\n14, 7 34 35 36\n15, 7 37 38 39\n16, 7 40 41 42\n17, 7 43 44 45\n18, 7 46 47 48\n19, 7 49 50 51\n20, 7 52 53 54\n21, 7 55 56 57",
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
            final_result, final_counts = balance_variants(all_variants, max_occurrence)

            # 3. Afișare Rezultate
            st.subheader(f"2. Rezultate Echilibrate (Limită N = {max_occurrence})")

            if not final_result:
                st.info("Nu a putut fi selectată nicio variantă.")
            else:
                num_selected = len(final_result)
                st.success(f"Au fost selectate **{num_selected}** variante din **{total_variants}** totale.")
                
                # Pregătirea rezultatului pentru afișare
                df_final = pd.DataFrame([
                    {'ID': v[0], 'Numere': ' '.join(map(str, sorted(list(v[1])))), 'Linie_Originala': v[2]}
                    for v in final_result
                ])

                # Afișează numerele în ordine crescătoare în coloana Numere
                st.dataframe(df_final[['ID', 'Numere']], hide_index=True)
                
                # --- Detalii Utile ---
                st.subheader("3. Verificarea Frecvenței în Setul Rezultat")
                
                # Creare DataFrame pentru afișarea frecvenței finale
                counts_df = pd.DataFrame(final_counts.items(), columns=['Număr', 'Frecvență'])
                counts_df = counts_df.sort_values(by='Frecvență', ascending=False)
                
                st.info(f"Frecvența maximă obținută este: **{counts_df['Frecvență'].max() if not counts_df.empty else 0}** (ar trebui să fie $\le {max_occurrence}$)")
                
                st.dataframe(counts_df, height=300, hide_index=True)
