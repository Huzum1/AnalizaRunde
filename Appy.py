#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
import random
import io # Adăugat pentru a citi conținutul fișierului

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_rounds_from_content(file_content):
    """Citește rundele din conținutul fișierului încărcat"""
    rounds = []
    # Folosim io.StringIO pentru a trata conținutul ca pe un fișier
    file_like_object = io.StringIO(file_content)
    
    for line in file_like_object:
        line = line.strip()
        if line:
            # Asigură-te că citirea se face corect, chiar dacă există spații
            try:
                nums = [int(x.strip()) for x in line.split(',')]
                # Verificăm dacă sunt 4 numere (sau numărul așteptat)
                if len(nums) == 4:
                    rounds.append(set(nums))
                else:
                    # Poți adăuga un avertisment dacă o linie nu are 4 numere
                    pass
            except ValueError:
                # Ignoră liniile care nu sunt numere întregi
                pass
                
    return rounds

def calc_metrics(nums, rounds):
    """Calculează metrici pentru o variantă"""
    v_set = set(nums)
    c4, c3, c2, c1 = 0, 0, 0, 0
    matches = []
    rounds_3_3 = []
    rounds_4_4 = []
    
    for ri, r in enumerate(rounds):
        m = len(v_set & r)
        matches.append(m)
        
        if m == 4:
            c4 += 1
            rounds_4_4.append(ri)
        elif m == 3:
            c3 += 1
            rounds_3_3.append(ri)
        elif m == 2:
            c2 += 1
        elif m == 1:
            c1 += 1
    
    # Condiția de validare: cel puțin o potrivire 4/4
    if c4 == 0:
        return None
    
    # Calculul scorului și al metricilor
    stability = 1 / (1 + np.std(matches)) if matches else 0
    consistency = sum(1 for m in matches if m >= 2) / len(matches) if matches else 0
    avg_coverage = np.mean(matches) if matches else 0
    
    score = (
        c4 * 150 +
        c3 * 60 +
        c2 * 8 +
        stability * 120 +
        consistency * 60
    )
    
    return {
        'score': score, # Score-ul este calculat direct aici
        'count_4_4': c4,
        'count_3_3': c3,
        'count_2_2': c2,
        'count_1_1': c1,
        'rounds_3_3': rounds_3_3,
        'rounds_4_4': rounds_4_4,
        'stability': stability,
        'avg_coverage': avg_coverage,
        'consistency': consistency
    }

def create_non_overlapping_blocks():
    """Creează blocuri NON-suprapuse pentru hibrid adevărat"""
    blocks = [
        (1, 16, "1-16"),      # 16 numere
        (17, 29, "17-29"),    # 13 numere
        (30, 42, "30-42"),    # 13 numere  
        (43, 65, "43-65")     # 23 numere
    ]
    return blocks

def generate_hybrid_variants_optimized(blocks, rounds, sample_size=200000):
    """Generare optimizată cu garantare non-overlap"""
    
    # Extragem numerele pe blocuri
    block_nums = []
    for min_n, max_n, name in blocks:
        nums = list(range(min_n, max_n + 1))
        block_nums.append(nums)
    
    variants = []
    generated = set()
    
    # Strategie 1: Random sampling (70%)
    phase1_size = int(sample_size * 0.7)
    
    for i in range(phase1_size):
        # Alegem 1 număr din fiecare bloc
        nums = tuple(sorted([random.choice(b) for b in block_nums]))
        
        if nums in generated:
            continue
        
        generated.add(nums)
        m = calc_metrics(nums, rounds)
        
        if m:
            variants.append((f"H{i}", nums, m))
    
    # Strategie 2: Targeted generation (30%)
    
    # Identificăm cele mai performante numere per bloc
    # NOTE: Această secțiune calculează performanța numerelor bazat pe potrivirile Rundelor (r) 
    # NU pe potrivirile variantelor generate (v). Este o metodă OK de estimare.
    num_performance = defaultdict(lambda: {'4': 0, '3': 0})
    
    for r in rounds:
        for n in r:
            for bi, (min_n, max_n, _) in enumerate(blocks):
                if min_n <= n <= max_n:
                    # Numărul de potriviri 4/4 și 3/3 în care a fost implicată RUNDA respectivă
                    num_performance[n]['4'] += sum(1 for rr in rounds if len(set(r) & rr) == 4)
                    num_performance[n]['3'] += sum(1 for rr in rounds if len(set(r) & rr) == 3)
                    break
    
    # Top numere per bloc
    top_per_block = []
    for bi, nums in enumerate(block_nums):
        scored = [(n, num_performance[n]['4'] * 2 + num_performance[n]['3']) for n in nums]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_per_block.append([n for n, _ in scored[:len(nums)//2]])  # Top 50%
    
    phase2_size = sample_size - phase1_size
    phase2_generated = 0
    
    while phase2_generated < phase2_size and len(variants) < sample_size:
        # Combinație din top numere
        nums = tuple(sorted([random.choice(top_per_block[bi]) for bi in range(4)]))
        
        if nums in generated:
            continue
        
        generated.add(nums)
        m = calc_metrics(nums, rounds)
        
        if m:
            variants.append((f"H{len(variants)}", nums, m))
        
        phase2_generated += 1
    
    return variants

def select_best_variants_greedy(variants, rounds, target_count=1150):
    """Selecție greedy optimizată cu maximizare acoperire"""
    
    if len(variants) <= target_count:
        return variants
    
    # Sortare inițială
    variants.sort(key=lambda x: x[2]['score'], reverse=True)
    
    selected = []
    used = set()
    
    # Tracking
    round_3_3_count = defaultdict(int)
    round_4_4_count = defaultdict(int)
    num_usage = defaultdict(int)
    
    # FAZA 1: Elite top 20%
    elite_count = int(target_count * 0.2)
    
    for idx, nums, m in variants[:elite_count * 3]:
        if len(selected) >= elite_count:
            break
        
        key = tuple(sorted(nums))
        if key not in used:
            selected.append((idx, nums, m))
            used.add(key)
            
            for ri in m['rounds_3_3']:
                round_3_3_count[ri] += 1
            for ri in m['rounds_4_4']:
                round_4_4_count[ri] += 1
            for n in nums:
                num_usage[n] += 1
    
    # FAZA 2: Optimizare acoperire
    remaining = [v for v in variants if tuple(sorted(v[1])) not in used]
    
    while len(selected) < target_count and remaining:
        
        best_score = -1
        best_idx = -1
        
        # Evaluăm mai mulți candidați pentru diversitate
        eval_size = min(5000, len(remaining))
        candidates = remaining[:eval_size]
        
        for i, (idx, nums, m) in enumerate(candidates):
            score = 0
            
            # Penalizăm runde supraacoperite / Bonus pentru sub-acoperite
            for ri in m['rounds_3_3']:
                cnt = round_3_3_count[ri]
                score += (25 - cnt) * 150 if cnt < 25 else 50 if cnt < 35 else -(cnt - 35) * 20
            
            for ri in m['rounds_4_4']:
                cnt = round_4_4_count[ri]
                score += (3 - cnt) * 800 if cnt < 3 else 100 if cnt < 6 else -(cnt - 6) * 50
            
            # Diversitate numere
            diversity = sum(100 / (1 + num_usage[n]) for n in nums)
            score += diversity
            
            # Metrici proprii
            score += m['count_3_3'] * 10
            score += m['count_4_4'] * 50
            score += m['stability'] * 100
            
            if score > best_score:
                best_score = score
                best_idx = i
        
        if best_idx == -1:
            # Nu mai există candidați viabili
            break
        
        # Adăugăm best
        idx, nums, m = candidates[best_idx]
        key = tuple(sorted(nums))
        
        selected.append((idx, nums, m))
        used.add(key)
        
        for ri in m['rounds_3_3']:
            round_3_3_count[ri] += 1
        for ri in m['rounds_4_4']:
            round_4_4_count[ri] += 1
        for n in nums:
            num_usage[n] += 1
        
        # Eliminăm varianta selectată din lista de candidați
        remaining.pop(best_idx)
    
    return selected

# ============================================================================
# MAIN
# ============================================================================

def main(file_content):
    
    # 1. Definirea blocurilor
    blocks = create_non_overlapping_blocks()
    
    # 2. Citirea rundelor
    rounds = read_rounds_from_content(file_content)
    
    if not rounds:
        return "❌ Nu s-au putut citi runde valide din fișierul furnizat. Vă rugăm să verificați formatul (4 numere întregi pe linie, separate prin virgulă, ex: 1,16,30,43)."
    
    print("="*70)
    print("🚀 GENERATOR VARIANTE HIBRIDE OPTIMIZAT")
    print("="*70)
    print(f"📊 Runde istorice încărcate: {len(rounds):,}")
    
    # 3. Generare
    SAMPLE_SIZE = 250000
    print(f"🔄 Generare a {SAMPLE_SIZE:,} de variante hibride (1 număr/bloc)...")
    variants = generate_hybrid_variants_optimized(blocks, rounds, SAMPLE_SIZE)
    
    if not variants:
        return "\n❌ Nicio variantă validă! (Nicio combinație hibridă nu a atins măcar un 4/4 în istoric)"
    
    print(f"  ✓ Variante valide generate (cu cel puțin un 4/4): {len(variants):,}")
    
    # 4. Selecție
    TARGET_COUNT = 1150
    print(f"\n🎯 Selecție Greedy de {TARGET_COUNT} variante pentru maximizarea acoperirii...")
    selected = select_best_variants_greedy(variants, rounds, TARGET_COUNT)
    
    print(f"  ✓ Total variante selectate: {len(selected)}/{TARGET_COUNT}")
    
    # 5. Output (Formare String pentru afișare/descărcare)
    output_lines = []
    for i, (idx, nums, m) in enumerate(selected, 1):
        output_lines.append(f"{i},{' '.join(str(n) for n in nums)}")
    
    output_content = "\n".join(output_lines)
    
    # 6. STATISTICI
    # ... (Codul de statistici a rămas neschimbat, dar va rula în background)
    
    total_4 = sum(m['count_4_4'] for _, _, m in selected)
    total_3 = sum(m['count_3_3'] for _, _, m in selected)
    
    # Formarea unui raport statistic concis
    report = [
        f"\n{'='*70}",
        "📈 STATISTICI FINALE",
        f"{'='*70}",
        f"🎯 Potriviri totale generate de cele {len(selected)} variante:",
        f"  4/4: {total_4:,} ({total_4/len(selected):.2f} pe variantă)",
        f"  3/3: {total_3:,} ⭐ ({total_3/len(selected):.1f} pe variantă)",
        "\n🌈 Verificare Hibrid:",
    ]

    # Acoperire
    all_nums = []
    for _, nums, _ in selected:
        all_nums.extend(nums)

    num_counts = Counter(all_nums)

    for min_n, max_n, name in blocks:
        count = sum(1 for n in all_nums if min_n <= n <= max_n)
        expected = len(selected)
        report.append(f"  Bloc {name:8s}: {count/expected*100:.1f}% utilizare")

    report.append(f"\n🎨 Diversitate:")
    top_nums = num_counts.most_common(5)
    report.append(f"  Numere unice: {len(num_counts)}/65")
    report.append(f"  Top 5 numere: " + ", ".join([f"{n} ({cnt}x)" for n, cnt in top_nums]))

    report.append(f"\n📝 Exemplu (prima variantă):")
    idx, nums, m = selected[0]
    blocks_str = []
    for n in nums:
        for bi, (min_n, max_n, _) in enumerate(blocks, 1):
            if min_n <= n <= max_n:
                blocks_str.append(f"{n}(B{bi})")
                break
    report.append(f"  {' '.join(blocks_str)}")
    report.append(f"  4/4={m['count_4_4']} | 3/3={m['count_3_3']} | 2/2={m['count_2_2']}")
    
    final_output = "\n".join(report)
    
    return final_output, output_content

if __name__ == '__main__':
    # Această secțiune este doar un placeholder. 
    # În mediul de execuție real, conținutul fișierului trebuie transmis funcției main.
    print("Vă rugăm să folosiți funcționalitatea de atașare a fișierelor pentru a rula acest cod.")

def calc_metrics(nums, rounds):
    """Calculează metrici pentru o variantă"""
    v_set = set(nums)
    c4, c3, c2, c1 = 0, 0, 0, 0
    matches = []
    rounds_3_3 = []
    rounds_4_4 = []
    
    for ri, r in enumerate(rounds):
        m = len(v_set & r)
        matches.append(m)
        
        if m == 4:
            c4 += 1
            rounds_4_4.append(ri)
        elif m == 3:
            c3 += 1
            rounds_3_3.append(ri)
        elif m == 2:
            c2 += 1
        elif m == 1:
            c1 += 1
    
    if c4 == 0:
        return None
    
    return {
        'score': 0,
        'count_4_4': c4,
        'count_3_3': c3,
        'count_2_2': c2,
        'count_1_1': c1,
        'rounds_3_3': rounds_3_3,
        'rounds_4_4': rounds_4_4,
        'stability': 1 / (1 + np.std(matches)),
        'avg_coverage': np.mean(matches),
        'consistency': sum(1 for m in matches if m >= 2) / len(matches)
    }

def create_non_overlapping_blocks():
    """Creează blocuri NON-suprapuse pentru hibrid adevărat"""
    blocks = [
        (1, 16, "1-16"),      # 16 numere
        (17, 29, "17-29"),    # 13 numere
        (30, 42, "30-42"),    # 13 numere  
        (43, 65, "43-65")     # 23 numere
    ]
    return blocks

def generate_hybrid_variants_optimized(blocks, rounds, sample_size=200000):
    """Generare optimizată cu garantare non-overlap"""
    
    print(f"\n🔄 GENERARE VARIANTE HIBRIDE OPTIMIZATE")
    print(f"   Garantare: 1 număr UNIC din fiecare bloc (fără overlap)")
    print(f"   Sample size: {sample_size:,}")
    
    # Extragem numerele pe blocuri
    block_nums = []
    for min_n, max_n, name in blocks:
        nums = list(range(min_n, max_n + 1))
        block_nums.append(nums)
        print(f"   Bloc {name}: {len(nums)} numere")
    
    total_possible = np.prod([len(b) for b in block_nums])
    print(f"\n  🎯 Total combinații: {total_possible:,}")
    
    # Generare inteligentă
    variants = []
    generated = set()
    
    # Strategie 1: Random sampling (70%)
    print(f"\n  📊 FAZA 1: Random sampling ({int(sample_size * 0.7):,} variante)")
    phase1_size = int(sample_size * 0.7)
    
    for i in range(phase1_size):
        if (i + 1) % 50000 == 0:
            print(f"     Progress: {i+1:,}/{phase1_size:,} | Valide: {len(variants):,}")
        
        # Alegem 1 număr din fiecare bloc
        nums = tuple(sorted([random.choice(b) for b in block_nums]))
        
        if nums in generated:
            continue
        
        generated.add(nums)
        m = calc_metrics(nums, rounds)
        
        if m:
            score = (
                m['count_4_4'] * 150 +
                m['count_3_3'] * 60 +
                m['count_2_2'] * 8 +
                m['stability'] * 120 +
                m['consistency'] * 60
            )
            m['score'] = score
            variants.append((f"H{i}", nums, m))
    
    print(f"     ✓ Variante valide: {len(variants):,}")
    
    # Strategie 2: Targeted generation (30%)
    print(f"\n  📊 FAZA 2: Generare țintită")
    
    # Identificăm cele mai performante numere per bloc
    num_performance = defaultdict(lambda: {'4': 0, '3': 0, '2': 0})
    
    for r in rounds:
        for n in r:
            for bi, (min_n, max_n, _) in enumerate(blocks):
                if min_n <= n <= max_n:
                    num_performance[n]['4'] += sum(1 for rr in rounds if len(set(r) & rr) == 4)
                    num_performance[n]['3'] += sum(1 for rr in rounds if len(set(r) & rr) == 3)
                    break
    
    # Top numere per bloc
    top_per_block = []
    for bi, nums in enumerate(block_nums):
        scored = [(n, num_performance[n]['4'] * 2 + num_performance[n]['3']) for n in nums]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_per_block.append([n for n, _ in scored[:len(nums)//2]])  # Top 50%
    
    phase2_size = sample_size - phase1_size
    phase2_generated = 0
    
    while phase2_generated < phase2_size and len(variants) < sample_size:
        # Combinație din top numere
        nums = tuple(sorted([random.choice(top_per_block[bi]) for bi in range(4)]))
        
        if nums in generated:
            continue
        
        generated.add(nums)
        m = calc_metrics(nums, rounds)
        
        if m:
            score = (
                m['count_4_4'] * 150 +
                m['count_3_3'] * 60 +
                m['count_2_2'] * 8 +
                m['stability'] * 120 +
                m['consistency'] * 60
            )
            m['score'] = score
            variants.append((f"H{len(variants)}", nums, m))
        
        phase2_generated += 1
        
        if phase2_generated % 20000 == 0:
            print(f"     Progress: {phase2_generated:,}/{phase2_size:,} | Total valide: {len(variants):,}")
    
    print(f"     ✓ Total variante: {len(variants):,}")
    
    return variants

def select_best_variants_greedy(variants, rounds, target_count=1150):
    """Selecție greedy optimizată cu maximizare acoperire"""
    
    print(f"\n🎯 SELECȚIE GREEDY OPTIMIZATĂ")
    print(f"   Target: {target_count} variante")
    
    if len(variants) <= target_count:
        print(f"  ⚠️  Doar {len(variants)} variante disponibile - selectez toate")
        return variants
    
    # Sortare inițială
    variants.sort(key=lambda x: x[2]['score'], reverse=True)
    
    selected = []
    used = set()
    
    # Tracking
    round_3_3_count = defaultdict(int)
    round_4_4_count = defaultdict(int)
    num_usage = defaultdict(int)
    
    # FAZA 1: Elite top 20% (cei mai buni direct)
    elite_count = int(target_count * 0.2)
    print(f"\n  ⭐ FAZA 1: Elite top {elite_count}")
    
    for idx, nums, m in variants[:elite_count * 3]:  # Luăm din top 60% pentru diversitate
        if len(selected) >= elite_count:
            break
        
        key = tuple(sorted(nums))
        if key not in used:
            selected.append((idx, nums, m))
            used.add(key)
            
            for ri in m['rounds_3_3']:
                round_3_3_count[ri] += 1
            for ri in m['rounds_4_4']:
                round_4_4_count[ri] += 1
            for n in nums:
                num_usage[n] += 1
    
    print(f"     ✓ {len(selected)} elite selectate")
    
    # FAZA 2: Optimizare acoperire
    print(f"\n  📊 FAZA 2: Optimizare acoperire")
    
    remaining = [v for v in variants if tuple(sorted(v[1])) not in used]
    
    iteration = 0
    last_progress = 0
    
    while len(selected) < target_count and remaining:
        iteration += 1
        
        current_progress = len(selected)
        if current_progress - last_progress >= 100:
            avg_3 = sum(round_3_3_count.values()) / len(rounds) if round_3_3_count else 0
            avg_4 = sum(round_4_4_count.values()) / len(rounds) if round_4_4_count else 0
            print(f"     {len(selected)}/{target_count} | 3/3: {avg_3:.1f} | 4/4: {avg_4:.1f}")
            last_progress = current_progress
        
        # Evaluare candidați
        best_score = -1
        best_idx = -1
        
        # Evaluăm mai mulți candidați pentru diversitate
        eval_size = min(5000, len(remaining))
        candidates = remaining[:eval_size]
        
        for i, (idx, nums, m) in enumerate(candidates):
            score = 0
            
            # Penalizăm runde supraacoperite
            for ri in m['rounds_3_3']:
                cnt = round_3_3_count[ri]
                if cnt < 25:
                    score += (25 - cnt) * 150  # Bonus mare pentru sub-acoperire
                elif cnt < 35:
                    score += 50
                else:
                    score -= (cnt - 35) * 20  # Penalizare pentru supra-acoperire
            
            for ri in m['rounds_4_4']:
                cnt = round_4_4_count[ri]
                if cnt < 3:
                    score += (3 - cnt) * 800
                elif cnt < 6:
                    score += 100
                else:
                    score -= (cnt - 6) * 50
            
            # Diversitate numere
            diversity = sum(100 / (1 + num_usage[n]) for n in nums)
            score += diversity
            
            # Metrici proprii
            score += m['count_3_3'] * 10
            score += m['count_4_4'] * 50
            score += m['stability'] * 100
            
            if score > best_score:
                best_score = score
                best_idx = i
        
        if best_idx == -1:
            break
        
        # Adăugăm best
        idx, nums, m = candidates[best_idx]
        key = tuple(sorted(nums))
        
        selected.append((idx, nums, m))
        used.add(key)
        
        for ri in m['rounds_3_3']:
            round_3_3_count[ri] += 1
        for ri in m['rounds_4_4']:
            round_4_4_count[ri] += 1
        for n in nums:
            num_usage[n] += 1
        
        remaining = [v for v in remaining if tuple(sorted(v[1])) != key]
    
    print(f"     ✓ Total: {len(selected)} variante")
    
    return selected

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("="*70)
    print("🚀 GENERATOR VARIANTE HIBRIDE OPTIMIZAT")
    print("="*70)
    
    # Blocuri non-suprapuse
    blocks = create_non_overlapping_blocks()
    
    print("\n📋 BLOCURI NON-SUPRAPUSE:")
    for i, (min_n, max_n, name) in enumerate(blocks, 1):
        count = max_n - min_n + 1
        print(f"  {i}. Bloc {name}: {count} numere")
    
    # Load rounds
    rounds = read_rounds('/mnt/user-data/uploads/runde_loterie_doar_runde_unice.txt')
    print(f"\n📊 Runde: {len(rounds):,}")
    
    # Generare
    SAMPLE_SIZE = 250000  # Sample mai mare
    variants = generate_hybrid_variants_optimized(blocks, rounds, SAMPLE_SIZE)
    
    if not variants:
        print("\n❌ Nicio variantă validă!")
        return
    
    # Selecție
    selected = select_best_variants_greedy(variants, rounds, 1150)
    
    # Output
    print(f"\n💾 Generare fișier...")
    with open('/mnt/user-data/outputs/variante_1150_optimized.txt', 'w') as f:
        for i, (idx, nums, m) in enumerate(selected, 1):
            f.write(f"{i},{' '.join(str(n) for n in nums)}\n")
    
    print(f"  ✅ variante_1150_optimized.txt")
    
    # STATISTICI
    print(f"\n{'='*70}")
    print("📈 STATISTICI FINALE")
    print(f"{'='*70}")
    
    total_4 = sum(m['count_4_4'] for _, _, m in selected)
    total_3 = sum(m['count_3_3'] for _, _, m in selected)
    total_2 = sum(m['count_2_2'] for _, _, m in selected)
    
    print(f"\n🎯 POTRIVIRI:")
    print(f"  4/4: {total_4:,} ({total_4/len(selected):.2f}/variantă)")
    print(f"  3/3: {total_3:,} ⭐ ({total_3/len(selected):.1f}/variantă)")
    print(f"  2/2: {total_2:,} ({total_2/len(selected):.1f}/variantă)")
    
    # Acoperire
    round_3_count = defaultdict(int)
    round_4_count = defaultdict(int)
    
    for _, nums, m in selected:
        for ri in m['rounds_3_3']:
            round_3_count[ri] += 1
        for ri in m['rounds_4_4']:
            round_4_count[ri] += 1
    
    cov_3 = [round_3_count[i] for i in range(len(rounds))]
    cov_4 = [round_4_count[i] for i in range(len(rounds))]
    
    print(f"\n📊 ACOPERIRE 3/3:")
    print(f"  Medie: {np.mean(cov_3):.1f} | Mediană: {np.median(cov_3):.1f}")
    print(f"  Range: {min(cov_3)}-{max(cov_3)}")
    print(f"  Std: {np.std(cov_3):.2f}")
    
    print(f"\n🎯 ACOPERIRE 4/4:")
    print(f"  Medie: {np.mean(cov_4):.2f} | Mediană: {np.median(cov_4):.1f}")
    print(f"  Range: {min(cov_4)}-{max(cov_4)}")
    
    # Verificare hibrid
    print(f"\n🌈 VERIFICARE HIBRID:")
    all_nums = []
    for _, nums, _ in selected:
        all_nums.extend(nums)
    
    for min_n, max_n, name in blocks:
        count = sum(1 for n in all_nums if min_n <= n <= max_n)
        expected = len(selected)
        print(f"  Bloc {name:8s}: {count}/{expected} ({count/expected*100:.1f}%)")
    
    # Diversitate
    num_counts = Counter(all_nums)
    print(f"\n🎨 DIVERSITATE:")
    print(f"  Numere unice: {len(num_counts)}/65")
    print(f"  Interval: {min(all_nums)}-{max(all_nums)}")
    
    # Top numere
    top_nums = num_counts.most_common(10)
    print(f"\n  Top 10 numere:")
    for n, cnt in top_nums:
        print(f"    {n}: {cnt}x")
    
    # Sample
    print(f"\n📝 EXEMPLE:")
    for i in [0, len(selected)//2, -1]:
        idx, nums, m = selected[i]
        blocks_str = []
        for n in nums:
            for bi, (min_n, max_n, _) in enumerate(blocks, 1):
                if min_n <= n <= max_n:
                    blocks_str.append(f"{n}(B{bi})")
                    break
        print(f"  Linia {i+1}: {' '.join(blocks_str)}")
        print(f"           4/4={m['count_4_4']} | 3/3={m['count_3_3']} | 2/2={m['count_2_2']}")
    
    print(f"\n{'='*70}")
    print("✅ COMPLET!")
    print(f"{'='*70}")

if __name__ == '__main__':
    main()