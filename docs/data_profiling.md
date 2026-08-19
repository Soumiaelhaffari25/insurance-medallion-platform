# Profiling des données freMTPL2 (avant transformation)

## POLICIES (freMTPL2freq) — 678 013 lignes, 12 colonnes
Clé : `IDpol` (float64 → à caster en entier)
Colonnes : ClaimNb, Exposure, Area, VehPower, VehAge, DrivAge,
BonusMalus, VehBrand, VehGas, Density, Region

## CLAIMS (freMTPL2sev) — 26 639 lignes, 2 colonnes
Clé : `IDpol` (int64)
Colonne : ClaimAmount

## Anomalies détectées → à corriger en couche Silver
1. IDpol de types différents (float vs int) → caster des deux côtés.
2. VehGas contient des quotes parasites : 'Regular' / 'Diesel' → nettoyer.
3. Exposure > 1 (max 2.01) → hors plage actuarielle ]0,1] → plafonner/filtrer.
4. ClaimAmount extrêmes (max 4 075 401 €) → plafonner (winsorisation).
5. ClaimAmount min = 1 → vérifier montants négatifs/nuls (aucun ici, ≥ 1).
6. Écart connu entre somme(ClaimNb) et nb lignes sev → documenté (limite dataset).

## Relation
1 police (freq) ⟷ 0..N sinistres (sev), jointure sur IDpol.
~5 % de taux de sinistralité (26 639 / 678 013).