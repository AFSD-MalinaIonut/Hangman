import re
import csv
import random
from collections import Counter
from pathlib import Path

# =============================
# 1. Încarcă lista de cuvinte dintr-un fișier local
# =============================
def incarca_cuvinte(fisier_local="cuvinte.txt"):
    p = Path(fisier_local)
    if not p.exists():
        raise FileNotFoundError(f"{fisier_local} nu a fost găsit.")
    with p.open("r", encoding="utf-8") as f:
        lines = [l.strip().lower() for l in f.readlines()]
    # Păstrăm doar linii alfabetice (inclusiv diacritice)
    cuvinte = [c for c in lines if c and all(ch.isalpha() or ch == '-' for ch in c)]
    print(f"{len(cuvinte)} cuvinte încărcate din {fisier_local}")
    return cuvinte

# =============================
# 1.1. Încarcă lista de teste (pattern + cuvânt)
# =============================
def incarca_teste_din_fisier(fisier_teste="cuvinte_de_verificat.txt"):
    p = Path(fisier_teste)
    if not p.exists():
        raise FileNotFoundError(f"{fisier_teste} nu a fost găsit.")
    teste = []
    with p.open("r", encoding="utf-8") as f:
        for linie in f:
            parts = linie.strip().split(";")
            if len(parts) >= 3:
                _, pattern, cuvant = parts[:3]
                pattern = pattern.strip().lower()
                cuvant = cuvant.strip().lower()
                if len(pattern) != len(cuvant):
                    print(f"Atenție: pattern și cuvânt difera ca lungime, ignor: {linie.strip()}")
                    continue
                teste.append((pattern, cuvant))
    print(f"{len(teste)} teste încărcate din {fisier_teste}")
    return teste

# =============================
# 2. Filtrare după pattern
# =============================
def filtreaza_cuvinte(pattern, cuvinte, litere_incercate):
    regex = '^' + re.escape(pattern).replace('\\*', '.').replace('\\_', '.') + '$'
    filtrate = []
    for c in cuvinte:
        if re.match(regex, c):
            invalid = False
            for l in litere_incercate:
                if l not in pattern and l in c:
                    invalid = True
                    break
            if not invalid:
                filtrate.append(c)
    return filtrate

# =============================
# 3. Alege cea mai frecventă literă
# =============================
def cea_mai_frecventa_litera(cuvinte, litere_incercate):
    counter = Counter()
    for c in cuvinte:
        for l in set(c):
            if l not in litere_incercate:
                counter[l] += 1
    if not counter:
        return None
    return counter.most_common(1)[0][0]

# =============================
# 4. Joacă Hangman până ghicește complet cuvântul
# =============================
def joaca_hangman(cuvant_real, toate_cuvintele, pattern_initial=None):
    pattern = pattern_initial if pattern_initial else '*' * len(cuvant_real)
    litere_incercate = set(ch for ch in pattern if ch != '*' and ch != '_')
    incercari = 0

    while '*' in pattern or '_' in pattern:
        posibile = filtreaza_cuvinte(pattern, toate_cuvintele, litere_incercate)
        litera = cea_mai_frecventa_litera(posibile, litere_incercate)

        # Dacă nu mai sunt litere candidate, alegem litere necunoscute din cuvântul real
        if not litera:
            litera = next((l for l in cuvant_real if l not in litere_incercate), None)

        litere_incercate.add(litera)
        incercari += 1

        # Actualizează pattern cu litera descoperită
        pattern = ''.join([cuvant_real[i] if cuvant_real[i] == litera else pattern[i] for i in range(len(cuvant_real))])

    return True, incercari, pattern  # mereu va fi True, deoarece ghicește complet

# =============================
# 5. Simulare pe 100 de cuvinte random
# =============================
def simulare_100_cuvinte(toate_cuvintele, num_cuvinte=100, exclude_cuvinte_teste=None):
    candidates = list(toate_cuvintele)
    if exclude_cuvinte_teste:
        candidates = [w for w in candidates if w not in exclude_cuvinte_teste]
    if len(candidates) < num_cuvinte:
        raise ValueError("Listă prea mică pentru a selecta numărul cerut de cuvinte.")
    selectate = random.sample(candidates, num_cuvinte)
    rezultate = []
    for cuv in selectate:
        gasit, incercari, pattern = joaca_hangman(cuv, toate_cuvintele)
        rezultate.append((cuv, gasit, incercari))
    medie_incercari = sum(r[2] for r in rezultate) / len(rezultate)
    procent_succes = sum(1 for r in rezultate if r[1]) / len(rezultate) * 100
    print(f"\nSimulare pentru {num_cuvinte} cuvinte random:")
    print(f"  Medie încercări per cuvânt: {medie_incercari:.2f}")
    print(f"  Procent succes: {procent_succes:.2f}%")
    return rezultate

# =============================
# 6. Testare pe fișierul de teste
# =============================
def testeaza_din_fisier(teste, toate_cuvintele, salvare_csv=None):
    rezultate = []
    for pattern, cuvant_real in teste:
        # Pool fără cuvântul real
        pool = [w for w in toate_cuvintele if w != cuvant_real]
        gasit, incercari, pattern_final = joaca_hangman(cuvant_real, pool, pattern)
        rezultate.append((pattern, cuvant_real, gasit, incercari, pattern_final))
        print(f"{cuvant_real.upper():<20} | pattern inițial: {pattern} | găsit: {gasit} | încercări: {incercari}")
    if salvare_csv:
        with open(salvare_csv, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["pattern_initial", "cuvant_real", "gasit", "incercari", "pattern_final"])
            for r in rezultate:
                writer.writerow(r)
        print(f"Rezultate salvate în {salvare_csv}")
    return rezultate

# =============================
# 7. Executare principală
# =============================
if __name__ == "__main__":
    toate_cuvintele = incarca_cuvinte("cuvinte.txt")
    teste = incarca_teste_din_fisier("cuvinte_de_verificat.txt")

    # Rulează testele din fișier
    print("\n--- Teste din fișier (cuvântul real eliminat din pool) ---")
    rezultate_teste = testeaza_din_fisier(teste, toate_cuvintele, salvare_csv="rezultate_teste.csv")

    # Simulare pe 100 de cuvinte random
    exclude_test_words_from_random = True
    test_words_set = set(c for _, c in teste)
    print("\n--- Simulare pe 100 de cuvinte random ---")
    rezultate_random = simulare_100_cuvinte(toate_cuvintele, num_cuvinte=100,
                                           exclude_cuvinte_teste=(test_words_set if exclude_test_words_from_random else None))

    # Salvăm rezultatele random
    with open("rezultate_random.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["cuvant", "gasit", "incercari"])
        for r in rezultate_random:
            writer.writerow(r)
    print("Rezultate random salvate în rezultate_random.csv")
