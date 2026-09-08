import math
Z_A, Z_B = 1.959964, 0.8416212   # alpha=0.05 two-sided, power=0.80
M = Z_A + Z_B

def mde_cross(sigma, N, rho, m, R2=0.0, P=0.5):
    """Cross-sectional MDE. Treatment assigned at cluster (ward/walkshed) level."""
    deff = 1.0 + (m - 1) * rho
    return M * sigma * math.sqrt(deff * (1 - R2) / (P * (1 - P) * N))

def mde_did(sigma, N, rho, m, r, R2=0.0, P=0.5):
    """2-period panel DiD, N = individuals followed in both waves.
    Var(diff) = 2 sigma^2 (1-r); relative to cross-section factor sqrt(2(1-r))."""
    return mde_cross(sigma, N, rho, m, R2, P) * math.sqrt(2 * (1 - r))

# ---- Outcome parameters
p0 = 0.25                      # baseline female employment rate, urban India, indicative
sig_emp = math.sqrt(p0*(1-p0))
mean_exp, sd_exp = 1500.0, 1200.0   # monthly household transport spend, Rs

print("="*104)
print("BBUS POWER ANALYSIS  |  total sample 6,000 across 6 cities  |  alpha 0.05 two-sided, power 0.80")
print("="*104)

print("\n--- PART 1: how much the clustering of a geographic treatment costs you ---")
print("Treatment is 'within 500 m of a stop'. That is assigned to WARDS, not households.")
print("m = households sampled per ward.  Design effect = 1 + (m-1) x ICC\n")
print(f"{'wards/city':>11} {'hh/ward':>8} | " + " | ".join(f"ICC={r:<5}" for r in (0.02,0.05,0.10)))
for J in (10, 20, 25, 40, 50):
    m = 1000 // J
    row = f"{J:>11} {m:>8} | "
    row += " | ".join(f"DEFF {1+(m-1)*r:>5.2f} eff.N {1000/(1+(m-1)*r):>5.0f}" for r in (0.02,0.05,0.10))
    print(row)

print("\n--- PART 2: Group A (Bengaluru, Jaipur, Bhubaneswar). Cross-section, 3,000 households ---")
print("MDE for FEMALE EMPLOYMENT, baseline 25%, in percentage points\n")
print(f"{'design':<34}" + "".join(f"{'ICC '+str(r):>13}" for r in (0.02,0.05,0.10)))
for label,N,m,R2 in [("pooled 3 cities, 25 wards each",3000,40,0.0),
                     ("pooled 3 cities, 25 wards, +controls",3000,40,0.30),
                     ("pooled, 50 wards each (20 hh/ward)",3000,20,0.30),
                     ("single city, 25 wards, +controls",1000,40,0.30)]:
    print(f"{label:<34}" + "".join(f"{100*mde_cross(sig_emp,N,r,m,R2):>12.1f}pp" for r in (0.02,0.05,0.10)))

print("\nMDE for MONTHLY TRANSPORT SPEND, mean Rs 1,500, SD Rs 1,200, in rupees/month\n")
print(f"{'design':<34}" + "".join(f"{'ICC '+str(r):>13}" for r in (0.02,0.05,0.10)))
for label,N,m,R2 in [("pooled 3 cities, 25 wards each",3000,40,0.0),
                     ("pooled 3 cities, 25 wards, +controls",3000,40,0.30),
                     ("pooled, 50 wards each (20 hh/ward)",3000,20,0.30),
                     ("single city, 25 wards, +controls",1000,40,0.30)]:
    print(f"{label:<34}" + "".join(f"{mde_cross(sd_exp,N,r,m,R2):>11.0f}Rs" for r in (0.02,0.05,0.10)))

print("\n--- PART 3: Group B panel DiD. 450 treated + 450 control per city, 3 cities = 2,700 ---")
print("r = correlation between a person's wave-1 and wave-2 outcome.")
print("Panel DiD beats a same-size cross-section only when r > 0.5.\n")
print("FEMALE EMPLOYMENT, percentage points, 25 wards/city (36 hh/ward), controls R2=0.30\n")
print(f"{'':<24}" + "".join(f"{'ICC '+str(rr):>13}" for rr in (0.02,0.05,0.10)))
for r in (0.3, 0.5, 0.7, 0.8):
    print(f"{'r = '+str(r)+', pooled':<24}" + "".join(f"{100*mde_did(sig_emp,2700,rr,36,r,0.30):>12.1f}pp" for rr in (0.02,0.05,0.10)))
print()
for r in (0.5, 0.7):
    print(f"{'r = '+str(r)+', single city':<24}" + "".join(f"{100*mde_did(sig_emp,900,rr,36,r,0.30):>12.1f}pp" for rr in (0.02,0.05,0.10)))

print("\nMONTHLY TRANSPORT SPEND, rupees/month, pooled 2,700, 25 wards/city, R2=0.30\n")
print(f"{'':<24}" + "".join(f"{'ICC '+str(rr):>13}" for rr in (0.02,0.05,0.10)))
for r in (0.3, 0.5, 0.7, 0.8):
    print(f"{'r = '+str(r):<24}" + "".join(f"{mde_did(sd_exp,2700,rr,36,r,0.30):>11.0f}Rs" for rr in (0.02,0.05,0.10)))

print("\n--- PART 4: the vulnerability interaction (the triple-difference coefficient) ---")
print("A subgroup-difference test needs roughly 4x the sample of a main effect for the same MDE,")
print("so the detectable interaction is about 2x the main-effect MDE.\n")
base = 100*mde_cross(sig_emp,3000,0.05,40,0.30)
print(f"  Group A pooled main effect (ICC 0.05):        {base:.1f} pp")
print(f"  Group A pooled VI interaction, approx:        {2*base:.1f} pp")
based = 100*mde_did(sig_emp,2700,0.05,36,0.7,0.30)
print(f"  Group B DiD main effect (ICC 0.05, r=0.7):    {based:.1f} pp")
print(f"  Group B DiD VI interaction, approx:           {2*based:.1f} pp")

print("\n--- PART 5: how many wards to buy, holding 1,000 households per city ---")
print("Same money, different spread. MDE for female employment, ICC 0.05, R2=0.30, single city.\n")
print(f"{'wards':>7} {'hh/ward':>9} {'DEFF':>7} {'effective N':>13} {'MDE (pp)':>10}")
for J in (10,15,20,25,30,40,50,60):
    m = 1000//J
    d = 1+(m-1)*0.05
    print(f"{J:>7} {m:>9} {d:>7.2f} {1000/d:>13.0f} {100*mde_cross(sig_emp,1000,0.05,m,0.30):>9.1f}")
print("\nDoubling wards from 25 to 50 cuts the MDE by roughly a third, at no extra sample cost.")
