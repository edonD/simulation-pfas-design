# Phase 1: Can We Detect PFOS on an Electrode?

## The One Question This Experiment Answers

> Put a PFOS-binding aptamer on a cheap electrode, dip it in PFOS solution, and measure if the electrical signal changes. That's it.

If yes — we have a path to a product. If no — we stop and rethink.

---

## Budget: ~$700-1,100

This is the cheapest possible version that gives a real answer.

### Shopping List

| # | Item | What it is | Source | Est. Cost |
|---|------|-----------|--------|-----------|
| 1 | **Potentiostat** | Measures electrical signal from electrode | Rodeostat (IO Rodeo) or AD5940 eval board (DigiKey) | $80-350 |
| 2 | **Screen-printed electrodes** (50-pack, gold or carbon) | Disposable sensor chips | Metrohm DropSens DRP-110 (carbon) or Zensor | $200-300 |
| 3 | **PFOS aptamer** (thiol-modified, custom oligo) | The molecule that grabs PFOS | IDT (Integrated DNA Technologies) | $150-250 |
| 4 | **PFOS standard** (pure chemical) | The thing we're trying to detect | Sigma-Aldrich #77282 (25 mg neat salt) | $50-80 |
| 5 | **MCH** (6-mercaptohexanol) | Blocks empty spots on electrode | Sigma-Aldrich #725226 | $30-50 |
| 6 | **Ferricyanide** (K3[Fe(CN)6]) | Redox probe — generates the electrical signal | Sigma-Aldrich #244023 | $25 |
| 7 | **PBS buffer tablets** | Keeps pH stable | Sigma-Aldrich #P4417 | $20 |
| 8 | **KCl** (potassium chloride) | Supporting electrolyte | Sigma-Aldrich | $15 |
| 9 | **Ethanol** (absolute, for cleaning) | Electrode prep | Any lab supplier | $15 |
| 10 | **Microcentrifuge tubes** (1.5 mL, 100-pack) | Sample prep | Fisher / Amazon | $10 |
| 11 | **Micropipettes + tips** (if you don't have them) | Measuring tiny volumes | Amazon (adjustable set) | $50-150 |
| **TOTAL** | | | | **$645-1,265** |

### Where to Order

- **IDT** (idtdna.com) — custom aptamer synthesis, create free account, use "custom oligo" order form
- **Sigma-Aldrich** (sigmaaldrich.com) — chemicals, need institutional or company account
- **IO Rodeo** (iorodeo.com) — Rodeostat open-source potentiostat
- **DigiKey** (digikey.com) — AD5940 eval board (EVAL-AD5940BIOZ) if going ultra-cheap
- **Metrohm DropSens** (metrohm-dropsens.com) — screen-printed electrodes
- **Amazon** — pipettes, tubes, gloves, general lab supplies

---

## The Aptamer

Order this from IDT as a custom oligo:

```
Sequence:  5'-HS-C6-TGTTTGTGGATTGTGCGTTCGTGG-3'

Modifications:
  - 5' end: Thiol-C6 (this anchors to gold electrode surface)

Scale: 25 nmol (enough for 100+ electrodes)
Purification: HPLC (important for modified oligos)
```

This is a 24-mer ssDNA aptamer reported to bind PFOS with Kd in the low-nanomolar range (Park et al.). The thiol group self-assembles onto gold electrode surfaces.

**Alternative (if using carbon electrodes instead of gold):** Order with a 5'-Biotin modification instead, and use streptavidin-coated carbon SPEs. Or use EDC/NHS coupling with a 5'-Amino-C6 modification.

**Cost at IDT:** ~$150-250 for 25 nmol, thiol-modified, HPLC purified.

---

## Equipment You Need Access To

| Equipment | Required? | Alternatives |
|-----------|-----------|-------------|
| Micropipettes (0.5-10 uL, 10-100 uL, 100-1000 uL) | Yes | Minimum: one adjustable 2-200 uL pipette (~$50 on Amazon) |
| Computer with USB | Yes | To run potentiostat software |
| Fume hood | Recommended | For PFOS handling. If unavailable, work in well-ventilated area with gloves |
| Analytical balance | Nice to have | For weighing PFOS salt. Alternative: buy pre-made PFOS solution instead of neat salt |
| Vortex mixer | Nice to have | Shake tubes by hand instead |
| DI water source | Yes | Buy distilled water from grocery store if no lab access |
| Nitrile gloves | Yes | Amazon, box of 100 for ~$10 |

**You do NOT need:** a cleanroom, a chemistry lab, HPLC, mass spec, a centrifuge, or any expensive instrument beyond the potentiostat.

---

## Step-by-Step Protocol

### Day 1: Prepare Solutions (1-2 hours)

**1.1 Make PBS buffer (pH 7.4)**
- Dissolve 1 PBS tablet in 200 mL DI water
- This is your base buffer for everything

**1.2 Make ferricyanide redox probe solution**
- Dissolve 0.165 g K3[Fe(CN)6] + 0.211 g K4[Fe(CN)6] in 100 mL PBS
- Final: 5 mM ferro/ferricyanide in PBS
- This is your "signal solution" — you measure how the electrode responds to this

**1.3 Make PFOS stock solution (1000 ug/mL = 1000 ppm)**
- Dissolve 10 mg PFOS salt in 10 mL methanol
- Vortex until dissolved
- Store at 4C (fridge)
- HANDLE WITH GLOVES — PFOS is a persistent pollutant

**1.4 Make PFOS dilution series (in PBS)**
- From the 1000 ug/mL stock, serial dilute in PBS:
  - 1000, 100, 10, 1, 0.1, 0.01 ng/mL
  - Each dilution: take 10 uL, add to 990 uL PBS (100x dilution per step)
  - Make 3 tubes of each concentration (triplicates)

**1.5 Prepare aptamer solution**
- Reconstitute lyophilized aptamer in PBS to 1 uM (follow IDT instructions)
- Heat to 95C for 5 min, cool slowly to room temperature (this folds the aptamer correctly)

**1.6 Prepare MCH blocking solution**
- Dissolve MCH in ethanol to 1 mM stock
- Dilute to 100 uM in PBS for use

---

### Day 2: Functionalize Electrodes (2-3 hours + overnight)

**2.1 Clean gold SPEs**
- Rinse electrode with ethanol, then DI water
- Air dry 5 min

**2.2 Apply aptamer to electrode**
- Pipette 5 uL of 1 uM aptamer solution onto the gold working electrode
- Incubate 2 hours at room temperature in a humid chamber (closed petri dish with wet paper towel)
- The thiol-aptamer self-assembles onto gold via Au-S bond

**2.3 Block with MCH**
- Rinse electrode gently with PBS
- Apply 5 uL of 100 uM MCH
- Incubate 1 hour at room temperature
- MCH fills the gaps between aptamers, preventing non-specific adsorption

**2.4 Rinse and store**
- Rinse with PBS
- Store electrodes in PBS at 4C overnight
- Prepare 10-15 electrodes total (3 for each PFOS concentration + controls)

---

### Day 3: Run the Experiment (3-4 hours)

This is the critical day. You measure whether the electrode signal changes when exposed to PFOS.

**3.1 Baseline measurement**
- Connect functionalized electrode to potentiostat
- Apply 50 uL ferricyanide solution on top of electrode
- Run Square Wave Voltammetry (SWV):
  - Potential range: -0.3 V to +0.6 V
  - Frequency: 25 Hz
  - Amplitude: 25 mV
  - Step: 5 mV
- Record the peak current (this is your BASELINE signal)
- Rinse electrode with PBS

**3.2 PFOS exposure**
- Apply 50 uL of PFOS solution (start with lowest concentration: 0.01 ng/mL)
- Incubate 30 minutes at room temperature
- Rinse gently with PBS

**3.3 Post-exposure measurement**
- Apply fresh ferricyanide solution
- Run identical SWV scan
- Record peak current (this is your SIGNAL AFTER PFOS)

**3.4 Calculate signal change**
```
Signal change (%) = (Baseline current - Post-PFOS current) / Baseline current × 100
```

When PFOS binds to the aptamer, the aptamer changes shape (folds), which blocks the ferricyanide from reaching the electrode surface. This DECREASES the peak current. More PFOS = more blocking = bigger signal change.

**3.5 Repeat for each concentration**
- Use a fresh electrode for each PFOS concentration
- 3 replicates per concentration
- Work from lowest to highest concentration

**3.6 Run negative controls**
- 3 electrodes with NO aptamer (just MCH) — exposed to highest PFOS concentration
  - If signal changes: something other than the aptamer is responding (bad)
  - If no signal change: the aptamer is doing the work (good)

---

### Day 4: Analyze Data (2-3 hours)

**4.1 Plot calibration curve**
```
X-axis: PFOS concentration (ng/mL), log scale
Y-axis: Signal change (%), with error bars (standard deviation of 3 replicates)
```

**4.2 Determine Limit of Detection**
```
LOD = 3 × (standard deviation of blank) / (slope of calibration curve)
```

**4.3 The critical question:**

| LOD you get | What it means | What to do next |
|-------------|--------------|-----------------|
| **< 1 ng/mL** | You can detect PFOS at general-population blood levels. This is a strong result. | Immediately test in spiked serum (Phase 2). You may have a product. |
| **1 - 10 ng/mL** | You can detect PFOS in exposed populations (near contaminated sites). Still useful. | Try signal amplification: gold nanoparticle labels, or longer incubation time. |
| **10 - 100 ng/mL** | Only detects extreme occupational exposure. Marginal. | Try a different aptamer sequence, or switch to antibody. |
| **> 100 ng/mL or no signal** | This aptamer/electrode combo doesn't work. | Try: (a) different aptamer, (b) antibody instead, (c) EIS instead of SWV, (d) gold nanoparticle amplification. |

---

## What Success Looks Like

A successful Phase 1 produces this plot:

```
Signal Change (%)
    25% |                                    *
        |                               *
    20% |                          *
        |                     *
    15% |                *
        |           *
    10% |      *
        | *
     5% |
        |
     0% |___________________________________________
        0.01  0.1    1    10   100  1000
              PFOS Concentration (ng/mL)  [log scale]
```

A sigmoid or linear-in-log curve with clear dose-response, LOD in the single-digit ng/mL range, and control electrodes showing no response.

---

## If It Doesn't Work: Plan B Options

| Problem | Fix | Extra cost |
|---------|-----|-----------|
| No signal change at all | Try EIS instead of SWV — more sensitive to surface changes | $0 (software change) |
| Weak signal (<5% change) | Add gold nanoparticle amplification: coat AuNPs with complementary DNA, sandwich assay | +$100-200 |
| High noise (CV > 30%) | More careful electrode prep, use gold SPEs instead of carbon | +$100 |
| Aptamer doesn't bind PFOS | Try a different published sequence (Bala et al. 76-mer) | +$150 for new oligo |
| Everything fails | Switch to commercial anti-PFOS antibody approach | +$300-500 |

---

## Timeline

| Day | Activity | Hours |
|-----|----------|-------|
| 0 | Order supplies (2-3 week shipping) | 1 |
| 1 | Prepare all solutions | 2 |
| 2 | Functionalize electrodes | 3 + overnight |
| 3 | Run all measurements | 4 |
| 4 | Analyze data, plot results | 3 |
| **Total hands-on time** | | **~13 hours over 4 days** |

---

## Safety

- **PFOS is a persistent organic pollutant.** Wear nitrile gloves at all times. Work in a fume hood if available.
- **Do NOT pour PFOS solutions down the drain.** Collect all PFOS-containing waste in a labeled container. Dispose through hazardous waste services.
- **Ferricyanide is mildly toxic.** Avoid ingestion. Standard lab safety.
- **Methanol is flammable and toxic.** Use in ventilated area. No open flames.
- **The amounts are very small** (milligrams of PFOS, milliliters of solutions) — the risk is low with basic precautions, but follow proper chemical handling procedures.

---

## What You're Actually Proving

This experiment doesn't prove you have a product. It proves one thing:

**"An aptamer on an electrode can distinguish PFOS-containing solution from clean buffer at concentrations relevant to human blood levels."**

That's it. If that works, the next 4 phases (blood matrix, strip format, clinical validation, FDA) are engineering problems. Hard engineering, but solvable.

If it doesn't work, you've spent $700-1,100 and 4 days to find out — instead of $300K and 2 years. That's the value of Phase 1.
