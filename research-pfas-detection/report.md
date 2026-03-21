# State of the Art: PFAS Electrochemical Detection (2024-2025)

## Executive Summary

As of early 2026, **no rapid point-of-care blood test for PFAS exists**. The field is converging on three viable approaches: (1) **aptamer-based electrochemical sensors** with LODs of 0.1-5 ng/mL in buffer, (2) **MIP-based electrochemical sensors** with LODs as low as 0.28 ng/L in water, and (3) **genetically-encoded protein biosensors** (PFASense/Harvard, FREDsense) at early commercialization stage for water testing. The best demonstrated performance in a real biological matrix (serum/blood) remains 1-10 ng/mL, sufficient for detecting high-exposure populations but marginal for general screening. The most actionable near-term path is an **aptamer-on-screen-printed-electrode** approach using published PFOS aptamers (Kd ~6.8 uM) with signal amplification, targeting exposed communities (>20 ng/mL) as the first market.

---

## 1. Comparison Table — All Approaches Side by Side

| Approach | LOD (buffer) | LOD (real matrix) | Selectivity | Time to result | TRL | Cost/test | Key group |
|----------|-------------|-------------------|-------------|---------------|-----|-----------|-----------|
| **Aptamer + qPCR amplification** | 2.9 ng/L (5.8 pM) | Not tested in blood | High (PFOS-specific) | ~2 hr | Lab bench (3) | ~$20 | Published 2025, ES&T |
| **Aptamer + CRISPR/Cas12a + ECL** | 0.86 ng/L | Not tested in blood | Moderate | ~1 hr | Lab bench (3) | ~$15 | Jing et al. 2024 |
| **MIP (PEDOT-TEMPO)** | 0.28 ng/L | Surface water (7.8% vs 18.4% signal) | Excellent vs other PFAS (1.4-2.7% cross-react) | 5-240 min | Lab bench (3) | ~$5 | Hafeez et al. 2024, ES&T Letters |
| **MIP on screen-printed electrode** | ~1 ng/L (PFOS) | River water tested | Good | Minutes | Prototype (4) | ~$5-10 | ACS ES&T Water 2024 |
| **Graphene electrode (direct)** | 10.4 nM (~5 ng/mL PFOA) | Not in blood | Limited | Minutes | Lab bench (3) | ~$5 | Langmuir 2024 |
| **PFASense (protein biosensor + eRapid)** | Not disclosed | Water only | Tunable (engineered proteins) | Minutes | Validation (5) | Target: <$1 | Harvard Wyss / d'Oelsnitz |
| **FREDsense (genetically encoded)** | Not disclosed | Water (field testing) | Customizable | Hours | Pre-commercial (6) | ~$50-100/field test | FREDsense Technologies (Calgary) |
| **MIT lateral flow (polyaniline)** | 200 ppt (PFBA), 400 ppt (PFOA) | Drinking water | Total PFAS (not specific) | Minutes | Lab/prototype (4) | Target: <$1 | MIT / Swager lab |
| **MITRE MIP sensor** | ppt range | Water (field tested) | PFOS + PFOA | Minutes | Prototype (5) | Not disclosed | MITRE Corporation |
| **Antibody ELISA** | 0.01-0.1 ng/mL | Serum (validated) | Moderate cross-reactivity | 2-4 hours | Commercial (8) | $10-50 | Multiple (Bio-Techne) |
| **Dried blood spot + LC-MS/MS** | 0.1 ng/mL | Whole blood (validated) | Excellent (25 PFAS) | Days-weeks | Commercial (9) | $300-700 | Eurofins, empowerDX |

---

## 2. Aptamer-Based Detection (Most Promising for Blood)

### Published PFOS Aptamers

The first validated PFOS-specific aptamers were published in Environmental Science & Technology (2025). Seven sequences were characterized:

| Aptamer | Kd (uM) | Method |
|---------|---------|--------|
| PFOS_JYP_2 | 6.76 ± 0.20 | ThT displacement |
| PFOS_JYP_1 | 7.12 ± 0.35 | ThT displacement |
| PFOS_JYP_3-7 | 6.76 - 8.42 | ThT displacement |

**Critical assessment:** Kd of 6.76 uM is **weak binding** compared to typical aptamers (nM range). However, combined with amplification strategies (CRISPR, qPCR, nanoparticles), picomolar detection limits have been demonstrated.

### Best Demonstrated LODs with Aptamers

| Method | LOD | Matrix | Reference |
|--------|-----|--------|-----------|
| Aptamer + qPCR | 5.8 pM (2.9 ng/L) | Buffer only | ES&T 2025 |
| Aptamer + CRISPR/Cas12a + ECL | 0.861 ng/L | Buffer only | Jing et al. 2024 |
| Aptamer + fluorescence | ~0.5 ng/mL | Water | Multiple groups |

### The Blood Matrix Problem

**No PFAS aptamer sensor has been validated in undiluted human blood or serum.** All published LODs are in clean buffer or environmental water. The expected performance degradation in blood is **5-10x** based on analogous aptasensor systems (cortisol, cocaine, etc.).

### Structure-Switching Aptamers

Structure-switching electrochemical aptamer-based (E-AB) sensors are the gold standard for reagentless, real-time detection in complex matrices. They have been demonstrated in undiluted serum and even in vivo in living animals for targets like cocaine, tobramycin, and cortisol. However, **no structure-switching aptamer for PFAS has been published yet.** This is likely because the weak Kd (~uM) makes conformational-change-based signal transduction difficult.

**Key insight:** A 2025 paper in npj Biosensing ("General approach to achieving electrochemical aptamer-based sensor sensitivity of buffer in blood plasma") describes methods to overcome serum interference. If applied to PFAS aptamers, this could be transformative.

---

## 3. MIP-Based Detection

### Breakthrough: PEDOT-TEMPO MIP (2024)

Hafeez et al. (ES&T Letters, 2024) achieved **0.28 ng/L LOD for PFOA** using a novel conductive, redox-active MIP that doesn't need external redox probes:

- **Monomer:** EDOT-TEMPO
- **Detection:** Direct CV — TEMPO redox signal suppressed by PFOA binding
- **Selectivity:** 18.4% signal change for PFOA vs only 1.4-2.7% for PFBA, PFOS, 6:2 FTAB — **excellent selectivity**
- **Limitation:** Sensitivity drops in surface water (7.8% vs 18.4%)
- **Electrode:** Glassy carbon (not yet on SPE)

### MIP on Screen-Printed Electrodes

A 2024 paper in ACS ES&T Water demonstrated **portable PFOS detection using MIP-modified screen-printed electrodes**, achieving detection at regulatory-relevant concentrations. This is the closest to our Phase 1 experimental plan.

### MITRE Corporation MIP Sensor

MITRE has developed a field-deployable MIP sensor for PFAS screening. Details are limited (government research), but it targets ppt-level detection in water using screen-printed electrodes. This validates the MIP-on-SPE approach for practical use.

---

## 4. Novel Approaches

### PFASense — Harvard Wyss Institute (TRL 5)

**The most exciting near-term technology.** PFASense uses:
- Genetically engineered bacterial transcription factor proteins that change shape when binding PFAS
- Coupled to the Wyss Institute's **eRapid** electrochemical platform
- Target: field-portable, minutes-to-result, <$1/test for water
- Received second-year Validation Project funding (2024-2025)
- **Not yet targeting blood** — focused on water testing first
- Led by Simon d'Oelsnitz in Pamela Silver's lab

### FREDsense Technologies (TRL 6)

- Calgary-based startup, **$7M Series A (Sept 2025)**
- Genetically encoded whole-cell biosensor integrated with electrochemical platform
- Field-deployable for water testing ("FRED-PFAS")
- Launched lab services in 2024
- **Water only** — not blood

### MIT Lateral Flow Sensor (TRL 4)

- Published in PNAS 2024 (Swager lab)
- Polyaniline-based resistive sensor on nitrocellulose paper
- **LOD: 200 ppt (PFBA), 400 ppt (PFOA)**
- Works like a pregnancy test strip — drop water on it
- Total PFAS detection (not compound-specific)
- Working on 100x sensitivity improvement using membrane pre-concentration
- **Water only**

### CRISPR/Cas12a + Aptamer

Jing et al. (2024) combined PFOA aptamer with rolling circle amplification + CRISPR/Cas12a for electrochemiluminescence detection. LOD: 0.861 ng/L. Very sensitive but complex workflow (multiple steps, enzymes). Not practical for POC yet, but shows the theoretical sensitivity ceiling.

### Nanomaterials

- **Graphene:** Direct PFOA/PFDA detection on graphene electrodes achieved LOD ~10 nM (Langmuir 2024). No recognition element needed — exploits fluorophilic interaction with graphene surface.
- **MXene:** Being used as electrode modifier for enhanced sensitivity, but no PFAS-specific MXene sensor published yet.
- **MOF:** Metal-organic framework impedimetric sensor achieved 0.5 ng/L PFOS in 2020. Promising but no recent follow-up.

---

## 5. Sample Preparation for Blood Testing

### Dried Blood Spots (DBS) — Already Validated

Multiple 2023-2024 papers demonstrate that **finger-prick dried blood spots work for PFAS testing:**

- Correlation with venous serum: **r >= 0.91** (ES&T 2023)
- 25 PFAS compounds quantified from DBS (Analytical and Bioanalytical Chemistry 2024)
- Volumetric absorptive microsamplers (VAMS) validated for home self-collection
- **Still requires LC-MS/MS analysis** — but proves the finger-prick sample is sufficient

### What This Means for a POC Device

The DBS literature proves that **a finger-prick blood drop contains enough PFAS to detect.** The bottleneck is not sample collection — it's the detection method. A sensor that can detect 1-10 ng/mL PFAS in a drop of blood has a validated sample collection method ready to go.

---

## 6. Commercial Landscape

### Companies With PFAS Blood Tests (Lab-Based)

| Company | Product | Sample | Method | Turnaround | Price |
|---------|---------|--------|--------|------------|-------|
| **Quest Diagnostics** | PFAS Test Panel (9 compounds) | Venous blood | LC-MS/MS | 1-2 weeks | ~$400 |
| **Eurofins** | PFAS Exposure Self-Collection | Finger-prick DBS | LC-MS/MS | 2-4 weeks | ~$300-500 |
| **empowerDX** | PFAS Home Test (16 compounds) | Finger-prick | LC-MS/MS | 15-30 days | ~$300 |

### Companies Developing Rapid PFAS Sensors (Water)

| Company | Technology | Target Matrix | Stage |
|---------|-----------|--------------|-------|
| **FREDsense** (Calgary) | Genetically encoded electrochemical | Water | Pre-commercial, $7M Series A |
| **PFASense/Wyss** (Harvard) | Engineered protein + eRapid | Water | Validation project |
| **MITRE** | MIP on SPE | Water | Government prototype |
| **Cyclopure** (Chicago) | Cyclodextrin sorbents | Water (remediation, not sensing) | Commercial product |

### Gap in the Market

**No company is developing a rapid (<30 min) PFAS blood test.** Every commercial blood test uses LC-MS/MS with days-to-weeks turnaround. The water sensor companies (FREDsense, PFASense) are not targeting blood. This is an open market opportunity.

---

## 7. Recommended Approach

### For Phase 1 (Proof of Concept): MIP on Screen-Printed Electrode

Based on the literature review, the **MIP approach has surpassed aptamers** for practical electrochemical detection:

**Why MIP over aptamer for Phase 1:**
1. MIP LOD (0.28 ng/L) is 1000x better than aptamer LOD without amplification
2. MIPs are stable for months — no degradation concerns
3. MIP-on-SPE has been demonstrated (ACS ES&T Water 2024, MITRE)
4. The PEDOT-TEMPO MIP eliminates need for external redox probes
5. No biological components = simpler manufacturing, longer shelf life

**Why not aptamer:**
- Published PFOS aptamers have weak Kd (~7 uM)
- No validation in blood/serum matrix
- Require amplification strategies (CRISPR, qPCR) for good LOD, adding complexity
- DNA stability issues for long-term storage

### Updated Phase 1 Shopping List

| Item | Source | Est. Cost | Why |
|------|--------|-----------|-----|
| EmStat Pico potentiostat module | PalmSens / Mouser | $250-350 | CV + EIS capable |
| Gold screen-printed electrodes (50-pack) | Metrohm DropSens DRP-C220AT | $400-500 | Gold surface for MIP electropolymerization |
| EDOT monomer | Sigma-Aldrich #483028 | $50 | For PEDOT MIP synthesis |
| TEMPO (radical) | Sigma-Aldrich #214000 | $30 | Redox-active component |
| PFOA standard | Sigma-Aldrich | $60 | Template molecule |
| PFOS standard | Sigma-Aldrich #77282 | $60 | Selectivity testing |
| Supporting electrolytes (LiClO4, acetonitrile) | Sigma-Aldrich | $80 | For electropolymerization |
| **TOTAL** | | **~$930-1,130** | |

**Also run aptamer approach in parallel** (add ~$200 for IDT aptamer + MCH) to compare head-to-head.

### Experiment Priority

1. **Week 1-2:** Electropolymerize PEDOT-TEMPO MIP on gold SPE using PFOA as template (follow Hafeez et al. 2024 protocol)
2. **Week 2-3:** Run PFOA calibration curve by CV, determine LOD
3. **Week 3-4:** Test selectivity (PFOS, PFHxS, PFBA)
4. **Week 4:** Spike PFAS into 10% human serum, test matrix effects
5. **Parallel:** Set up aptamer-based sensor on separate SPEs for comparison

---

## 8. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MIP doesn't work on SPE (only published on glassy carbon) | Medium | High | Fallback: aptamer approach. Or use Micrux thin-film gold electrodes |
| LOD in serum degrades >100x | High | High | Pre-concentration step (10 min SPE cartridge). Or target high-exposure populations first (>20 ng/mL) |
| Selectivity fails in complex matrix | Medium | Medium | Total PFAS screening is still clinically useful (National Academies uses total PFAS thresholds) |
| Can't reproduce published LODs | Medium | High | Contact Hafeez/Xu group (University of Delaware) for protocol details. Common in MIP field |
| Regulatory pathway unclear for blood test | Low | Medium | Start with environmental water testing (lower regulatory bar), pivot to blood later |

---

## 9. References

### Aptamer-Based Detection
- [Development of Aptamer-Based qPCR for PFOS Detection](https://pubs.acs.org/doi/10.1021/acs.est.5c04730) — ES&T 2025, Kd = 6.76 uM
- [Biomimetic Sensors for PFAS — Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC10781331/) — Sensors 2024
- [Critical review of PFAS sensors](https://www.sciencedirect.com/science/article/abs/pii/S001393512500920X) — Analytica Chimica Acta 2025
- [General approach to aptamer sensor sensitivity in blood plasma](https://www.nature.com/articles/s44328-025-00066-7) — npj Biosensing 2025

### MIP-Based Detection
- [PEDOT-TEMPO MIP for PFOA, LOD 0.28 ng/L](https://pmc.ncbi.nlm.nih.gov/articles/PMC11325644/) — ES&T Letters 2024, Hafeez et al.
- [MIP on screen-printed electrode for PFOS](https://pubs.acs.org/doi/10.1021/acsestwater.4c01044) — ACS ES&T Water 2024
- [MITRE MIP Sensor Report](https://www.mitre.org/sites/default/files/2025-05/PR-25-0575-MIP-Based-Electrochemical-Sensors%20for-PFAS-Detection.pdf) — MITRE 2025
- [MIP + AC electrothermal for PFOA, LOD 0.45 fg/L](https://pmc.ncbi.nlm.nih.gov/articles/PMC11945770/) — PMC 2025

### Novel Approaches
- [PFASense — Harvard Wyss Institute](https://wyss.harvard.edu/technology/pfasense-fast-in-field-testing-for-forever-chemicals/)
- [FREDsense PFAS biosensor](https://fredsense.com/2023/02/fredsense-announces-rapid-and-accurate-electrochemical-biosensor-solution-for-pfas-detection/)
- [MIT lateral flow PFAS sensor, PNAS 2024](https://news.mit.edu/2024/new-sensor-detects-harmful-forever-chemicals-drinking-water-0311)
- [Graphene PFOA/PFDA sensor](https://pubs.acs.org/doi/10.1021/acs.langmuir.3c03666) — Langmuir 2024
- [Genetically encoded PFOA biosensor](https://www.nature.com/articles/s41598-023-41953-1) — Scientific Reports 2023

### Sample Preparation
- [Dried blood spots for PFAS — validated](https://pmc.ncbi.nlm.nih.gov/articles/PMC10248884/) — Science of Total Environment 2023
- [Volumetric microsamplers vs venous blood](https://pubs.acs.org/doi/10.1021/acs.est.2c09852) — ES&T 2023
- [UHPLC-MS/MS method for 25 PFAS in DBS](https://link.springer.com/article/10.1007/s00216-024-05484-6) — ABC 2024

### Commercial / Regulatory
- [Quest Diagnostics PFAS Test](https://www.questhealth.com/product/pfas-forever-chemicals-test-panel/13724M.html)
- [Eurofins PFAS Self-Collection Test](https://cdnmedia.eurofins.com/eurofins-us/media/12161728/pfas-exposure-self-collection-blood-test.pdf)
- [DoD $10M PFAS research funding 2025](https://www.ngwa.org/detail/news/2024/11/18/dod-invites-applications-for-$10-million-in-pfas-research-funding-in-2025)
- [ATSDR PFAS Blood Level Tool](https://www.atsdr.cdc.gov/pfas/blood-testing/estimation-tool.html)
