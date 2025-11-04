#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from collections import defaultdict, Counter
from itertools import combinations
import random
import io # Esențial pentru a citi conținutul fișierului ca text

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_rounds_from_content(file_content):
    """Citește rundele din conținutul fișierului încărcat"""
    rounds = []
    
    # Verifică dacă s-a primit conținut
    if not file_content or not isinstance(file_content, str):
        return []
        
    # Folosim io.StringIO pentru a trata conținutul ca pe un fișier
    file_like_object = io.StringIO(file_content)
    
    for line in file_like_object:
        line = line.strip()
        if line:
            try:
                # Citim numere întregi separate prin virgulă
                nums = [int(x.strip()) for x in line.split(',')]
                # Presupunem că o rundă validă are 4 numere
                if len(nums) == 4:
                    rounds.append(set(nums))
                # else: Ignorăm liniile cu alt număr de elemente
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
    if not matches:
        return None
        
    stability = 1 / (1 + np.std(matches))
    consistency = sum(1 for m in matches if m >= 2) / len(matches)
    avg_coverage = np.mean(matches)
    
    score = (
        c4 * 150 +
        c3 * 60 +
        c2 * 8 +
        stability * 120 +
        consistency * 60
    )
    
    return {
        'score': score,
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

def generate_hybrid_variants_optimized(blocks, rounds, sample_size=250000):
    """Generare optimizată cu garantare non-overlap"""
    
    block_nums = [list(range(min_n, max_n + 1)) for min_n, max_n, name in blocks]
    
    variants = []
    generated = set()
    
    # Strategie 1: Random sampling (70%)
    phase1_size = int(sample_size * 0.7)
    
    for i in range(phase1_size):
        nums = tuple(sorted([random.choice(b) for b in block_nums]))
        
        if nums in generated:
            continue
        
        generated.add(nums)
        m = calc_metrics(nums, rounds)
        
        if m:
            variants.append((f"H{i}", nums, m))
    
    # Strategie 2: Targeted generation (30%)
    num_performance = defaultdict(lambda: {'4': 0, '3': 0})
    
    for r in rounds:
        for n in r:
            for bi, (min_n, max_n, _) in enumerate(blocks):
                if min_n <= n <= max_n:
                    # Folosim set(r) & rr pentru potriviri între runde, nu între varianta și rundă
                    num_performance[n]['4'] += sum(1 for rr in rounds if len(set(r) & rr) == 4)
                    num_performance[n]['3'] += sum(1 for rr in rounds if len(set(r) & rr) == 3)
                    break
    
    top_per_block = []
    for bi, nums in enumerate(block_nums):
        scored = [(n, num_performance[n]['4'] * 2 + num_performance[n]['3']) for n in nums]
        scored.sort(key=lambda x: x[1], reverse=True)
        top_per_block.append([n for n, _ in scored[:len(nums)//2]])
    
    phase2_size = sample_size - phase1_size
    phase2_generated = 0
    
    while phase2_generated < phase2_size and len(variants) < sample_size:
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
    
    variants.sort(key=lambda x: x[2]['score'], reverse=True)
    
    selected = []
    used = set()
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
            
            for ri in m['rounds_3_3']: round_3_3_count[ri] += 1
            for ri in m['rounds_4_4']: round_4_4_count[ri] += 1
            for n in nums: num_usage[n] += 1
    
    # FAZA 2: Optimizare acoperire
    remaining = [v for v in variants if tuple(sorted(v[1])) not in used]
    
    while len(selected) < target_count and remaining:
        
        best_score = -1
        best_idx = -1
        
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
            break
        
        idx, nums, m = candidates[best_idx]
        key = tuple(sorted(nums))
        
        selected.append((idx, nums, m))
        used.add(key)
        
        for ri in m['rounds_3_3']: round_3_3_count[ri] += 1
        for ri in m['rounds_4_4']: round_4_4_count[ri] += 1
        for n in nums: num_usage[n] += 1
        
        remaining.pop(best_idx)
    
    return selected

def format_statistics(selected, rounds, blocks):
    """Calculează și formatează statisticile finale"""
    
    total_4 = sum(m['count_4_4'] for _, _, m in selected)
    total_3 = sum(m['count_3_3'] for _, _, m in selected)
    
    report = [
        f"\n{'='*70}",
        "📈 STATISTICI FINALE",
        f"{'='*70}",
        f"🎯 Potriviri totale generate de cele {len(selected)} variante:",
        f"  4/4: {total_4:,} ({total_4/len(selected):.2f} pe variantă)",
        f"  3/3: {total_3:,} ⭐ ({total_3/len(selected):.1f} pe variantă)",
        "\n🌈 Verificare Hibrid (Procent de utilizare al numerelor din blocuri):",
    ]

    # Acoperire
    all_nums = []
    for _, nums, _ in selected:
        all_nums.extend(nums)

    num_counts = Counter(all_nums)

    for min_n, max_n, name in blocks:
        count = sum(1 for n in all_nums if min_n <= n <= max_n)
        expected = len(selected)
        report.append(f"  Bloc {name:8s}: {count/expected*100:.1f}%")

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

    return "\n".join(report)

# ============================================================================
# MAIN
# ============================================================================

def main(file_content):
    """Funcția principală, acceptă conținutul fișierului ca argument"""
    
    # 1. Definirea blocurilor
    blocks = create_non_overlapping_blocks()
    
    # 2. Citirea rundelor
    rounds = read_rounds_from_content(file_content)
    
    if not rounds:
        return "❌ Nu s-au putut citi runde valide din conținutul furnizat. Vă rugăm să verificați formatul (4 numere întregi pe linie, separate prin virgulă, ex: 1,16,30,43)."
    
    # Afișare log
    print("="*70)
    print("🚀 GENERATOR VARIANTE HIBRIDE OPTIMIZAT")
    print("="*70)
    print(f"📊 Runde istorice citite: {len(rounds):,}")
    
    # 3. Generare
    SAMPLE_SIZE = 250000
    print(f"🔄 Generare a {SAMPLE_SIZE:,} de variante hibride (1 număr/bloc)...")
    variants = generate_hybrid_variants_optimized(blocks, rounds, SAMPLE_SIZE)
    
    if not variants:
        return "\n❌ Nicio variantă validă! Nicio combinație hibridă din eșantion nu a atins măcar un 4/4 în istoric."
    
    print(f"  ✓ Variante valide generate (cu cel puțin un 4/4): {len(variants):,}")
    
    # 4. Selecție
    TARGET_COUNT = 1150
    print(f"\n🎯 Selecție Greedy de {TARGET_COUNT} variante pentru maximizarea acoperirii...")
    selected = select_best_variants_greedy(variants, rounds, TARGET_COUNT)
    
    print(f"  ✓ Total variante selectate: {len(selected)}/{TARGET_COUNT}")
    
    # 5. Output și Statistică
    
    # Formează lista de variante pentru salvare/copiere
    output_lines = []
    for i, (idx, nums, m) in enumerate(selected, 1):
        # Format: Index, N1 N2 N3 N4
        output_lines.append(f"{i},{' '.join(str(n) for n in nums)}")
    output_content = "\n".join(output_lines)
    
    # Generează raportul statistic
    stats_report = format_statistics(selected, rounds, blocks)
    
    final_output = stats_report + "\n\n" + "="*70 + "\n✅ COMPLET!" + "\n" + "="*70

    return final_output, output_content
