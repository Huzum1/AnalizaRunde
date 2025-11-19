import streamlit as st
import pandas as pd
from collections import Counter
import random

# --- Configurare Pagină ---
st.set_page_config(
    page_title="Echilibrare Frecvențe Variante",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Titlul aplicației
st.title("⚖️ Echilibrare Frecvențe Variante (Limita N & K)")

# --- Funcția de Procesare a Datelor ---
def parse_input(input_text, min_numbers_per_variant):
    """Parsează datele introduse manual."""
    lines = [line.strip() for line in input_text.split('\n') if line.strip()]
    
    parsed_data = []
    
    for line in lines:
        try:
            # Separă ID-ul de combinație (prima virgulă)
            id_str, combination_str = line.split(',', 1)
            variant_id = id_str.strip()
            # Extrage numerele (le separă după spațiu)
            numbers_list = [int(n.strip()) for n in combination_str.split() if n.strip().isdigit()]
            
            # Filtrare K (dimensiunea variantei)
            if len(numbers_list) == min_numbers_per_variant:
                # Stocăm (ID, set de numere, lista sortată de numere)
                parsed_data.append((variant_id, set(numbers_list), sorted(numbers_list)))
                
        except:
            # Ignorăm liniile cu format greșit
            continue
            
    return parsed_data

def balance_variants(all_variants, max_occurrence):
    """Echilibrează selecția variantelor pentru a respecta limita de repetiție N."""
    
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
        # variant[1] este setul de numere
        numbers_set = variant[1] 
        
        # Verificăm dacă varianta poate fi adăugată fără a depăși limita N
        can_be_added = True
        for num in numbers_set:
            if current_counts[num] >= max_occurrence:
                can_be_added = False
                break
        
        # Dacă este OK, o adăugăm și actualizăm contorul
        if can_be_added:
            selected_ids.add(variant_id)
            for num in numbers_set:
                current_counts[num] += 1

    # 3. Construirea rezultatului final (doar variantele selectate)
    final_result_tuples = [v for v in all_variants if v[0] in selected_ids]
    
    return final_result_tuples, current_counts

# --- Interfață Utilizator (UI) ---

with st.sidebar:
    st.header("⚙️ Setări Filtrare")
    
    # 1. Setarea Limitei de Apariții (N)
    max_occurrence = st.number_input(
        "1. Limită Maximă de Apariții (N) per Număr:",
        min_value=1, 
        max_value=10000, 
        value=15, 
        step=1,
        help="Niciun număr nu va fi folosit în setul rezultat de mai mult de N ori."
    )

    # 2. Setarea Numărului de Numere din Variantă (K)
    st.markdown("---")
    numbers_per_variant = st.number_input(
        "2. Număr de Numere per Variantă (K):",
        min_value=1, 
        max_value=66, 
        value=4, 
        step=1,
        help="Vor fi procesate doar variantele care conțin exact K numere."
    )

st.subheader("1. Introduceți Variantele")
# Câmpul de text este gol (value="")
input_text = st.text_area(
    "Lipiți variantele aici (câte o variantă pe rând).",
    value="",  # Acum este gol
    height=200,
    placeholder="Exemplu:\n1, 61 34 2 7\n2, 33 24 57 4\n...",
    help=f"Format: ID, Numar1 Numar2 Numar3... Asigură-te că fiecare variantă conține {numbers_per_variant} numere, conform setării K."
)

st.divider()

if st.button("🚀 Rulează Echilibrarea"):
    if not input_text:
        st.error("Vă rugăm introduceți date în câmpul de text.")
    else:
        # 1. Parsare
        all_variants = parse_input(input_text, numbers_per_variant)
        
        if not all_variants:
            st.error(f"Nu s-au putut parsa variante valide care să conțină exact {numbers_per_variant} numere. Verificați formatul și setarea K.")
        else:
            total_variants = len(all_variants)
            
            # 2. Echilibrare
            final_result_tuples, final_counts = balance_variants(all_variants, max_occurrence)

            # 3. Afișare Rezultate
            st.subheader(f"2. Rezultate Echilibrate (K={numbers_per_variant}, N={max_occurrence})")

            if not final_result_tuples:
                st.info("Nu a putut fi selectată nicio variantă care să respecte ambele condiții (K și N).")
            else:
                num_selected = len(final_result_tuples)
                st.success(f"Au fost selectate **{num_selected}** variante din **{total_variants}** care au avut {numbers_per_variant} numere.")
                
                # Construiește șirul de text pentru copiere
                text_to_copy_lines = []
                for v in final_result_tuples:
                    variant_id = v[0]
                    numbers_str = ' '.join(map(str, v[2])) 
                    text_to_copy_lines.append(f"{variant_id}, {numbers_str}")
                
                text_to_copy = "\n".join(text_to_copy_lines)

                # --- Chenar pentru Copiere ---
                st.subheader("📋 Variante pentru Copiere (Format: ID, Numar Numar...)")
                st.code(text_to_copy, language='text')

                # Afișare în tabel
                st.subheader("Vizualizare (Tabel)")
                df_final = pd.DataFrame([
                    {'ID': v[0], 'Numere': ' '.join(map(str, v[2]))} 
                    for v in final_result_tuples
                ])
                st.dataframe(df_final[['ID', 'Numere']], hide_index=True)

                # --- Detalii Utile ---
                st.subheader("3. Verificarea Frecvenței în Setul Rezultat")
                
                counts_df = pd.DataFrame(final_counts.items(), columns=['Număr', 'Frecvență'])
                counts_df = counts_df.sort_values(by='Frecvență', ascending=False)
                
                max_frecventa = counts_df['Frecvență'].max() if not counts_df.empty else 0
                st.info(f"Frecvența maximă obținută în setul selectat este: **{max_frecventa}** (care este $\le N={max_occurrence}$)")
                
                st.dataframe(counts_df, height=300, hide_index=True)
