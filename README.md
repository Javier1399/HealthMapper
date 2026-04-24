# 🧬 Health Topology Mapper — INMEGEN

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live_App-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![TDA](https://img.shields.io/badge/Method-Topological_Data_Analysis-2d6a4f?style=flat)](https://github.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-RandomForest-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat)](LICENSE)

> **A Topological Data Analysis pipeline that maps geriatric patient profiles, computes a clinically-grounded health score, and generates personalized habit recommendations by navigating a Mapper graph — identifying the minimum behavioral changes needed to reach a healthier profile.**

---

## Overview

This project was developed in collaboration with **INMEGEN** (Instituto Nacional de Medicina Genómica, Mexico), where a clinical researcher provided a survey dataset of geriatric patients and sought analytical insights from the data.

The dataset contains clinical measurements, metabolic markers, lifestyle habits, and pharmacological treatment information from **966 elderly patients**. No ground-truth longitudinal follow-up was available — a constraint that shaped every methodological decision in this project.

**The core question evolved over three research phases:**

1. *Are there identifiable patient clusters based on clinical and lifestyle profiles?*
2. *Can we predict whether a patient's hypertension treatment is effective?*
3. *Can we build a tool that tells a patient what minimum habit changes would improve their health score — based on similar real patients who already achieved it?*

---

## Research Journey

### Act 1 — Exploratory Analysis: PCA & Hierarchical Clustering

The initial phase used **Principal Component Analysis** and **hierarchical clustering** on the full patient dataset.

**Key findings:**

- PCA generated **3 separable clusters**, providing a useful first segmentation — but the separation was significantly influenced by the arbitrary BMI-based split we imposed (taking only extreme cases: BMI > 30 and BMI < 25, excluding the messy middle). This reduced noise and improved the dendrogram structure considerably.
- The **heatmap + hierarchical clustering** revealed that when a "healthy profile" threshold was defined *a priori*, patients clustered cleanly inside and outside that boundary. Seemingly intuitive, but the patterns *within* each group showed surprisingly diverse and well-defined behavioral subgroups.
- One practically relevant finding: there were detectable patterns in how frequently patients needed medical checkups to stay stable — some patients, particularly those with low cholesterol and low sugar intake, showed profiles consistent with reduced monitoring needs without increased risk.
- **Critical limitation:** meaningful separation only emerged at the extremes. The middle — most of the real clinical world — was too heterogeneous for PCA to structure. PCA flattens multidimensional data into a 2D shadow; it cannot preserve local structure across 20+ variables simultaneously.

This limitation motivated the shift to Topological Data Analysis.

---

### Act 2 — From Linear to Topological: Why Mapper?

PCA projects data onto a flat plane, discarding the local geometry that distinguishes similar-but-not-identical patient profiles. For a dataset with 25+ clinical and behavioral variables, this information loss is severe.

**Topological Data Analysis (TDA)** — specifically the **Mapper algorithm** — addresses this by:

- Preserving local structure through overlapping covers of the data space.
- Representing the dataset as a **graph where each node is a cluster of similar patients** and edges connect overlapping clusters.
- Being robust to outliers that would distort PCA.
- Allowing any variable to be used as a "lens" to color the graph and reveal patterns — without retraining.

The Mapper graph was built using:

| Component | Choice | Rationale |
|---|---|---|
| Lens | PCA (2 components) | Captures dominant variance for cover construction |
| Clusterer | DBSCAN (eps=4.0, min_samples=5) | Density-based, no assumed cluster shape |
| Cover | 10 cubes, 50% overlap | Balanced resolution vs. connectivity |
| Input space | 29 standardized clinical variables | Full feature set after preprocessing |

This produced a graph with **66 nodes, 171 edges**, and an average of 30.7 patients per node — interpretable at the clinical level.

---

### Act 3 — Topological Findings & The Medication Hypothesis

The Mapper graph was colored by 8 clinical variables independently. The most structurally significant finding came from comparing `presion_controlada` (blood pressure control), `n_medicamentos` (number of medications), and metabolic markers.

**The graph revealed 4 connected components:**

| Component | Nodes | Unique Patients | % Controlled BP | Avg Meds | Diabetes % | Hypertension % |
|---|---|---|---|---|---|---|
| Main body | 50 | 522 | 69.9% | 0.46 | 9.8% | 25.9% |
| Intermediate | 11 | 157 | 66.7% | 1.00 | 0.0% | 64.9% |
| Healthy | 4 | 12 | 58.3% | 0.00 | 0.0% | 0.0% |
| **Isolated node** | **1** | **7** | **42.9%** | **1.00** | **100%** | **100%** |

The **isolated node** — topologically separated from the main structure — contained 7 patients with dual diagnosis, on medication, and the lowest blood pressure control rate. The Mapper identified them as a clinically distinct subpopulation automatically.

**Testing the medication effectiveness hypothesis:**

We defined `tratamiento_inefectivo = 1` when a patient was on ≥1 antihypertensive medication but still had uncontrolled blood pressure. **188 of 507 medicated patients (37%)** met this criterion.

Comparing effective vs. ineffective treatment groups revealed a striking pattern:

| Variable | Ineffective Treatment | Effective Treatment |
|---|---|---|
| SBP mean | 151.1 mmHg | 122.6 mmHg |
| IMC mean | 29.2 | 28.2 |
| Age mean | 69.8 | 69.2 |
| Glucose mean | 112.9 | 112.5 |
| Diuretic use | 17% | **25%** |
| BB use | 17.5% | **22%** |
| ARA2 use | 56.4% | 54.5% |

IMC, age, and glucose were nearly identical between groups. The difference was *which* medication, not *how many*. Diuretics and beta-blockers appeared more frequently in the controlled group.

**The critical finding — proven with Random Forest feature importance:**

We trained a classifier to predict blood pressure control using all 22 clinical and pharmacological features. The top predictors by permutation importance were:

1. HDL cholesterol
2. Triglycerides
3. Waist circumference
4. Waist/hip ratio
5. LDL cholesterol
6. BMI
7. Total cholesterol
8. Glucose
9. Pulse

Medications appeared **at the bottom of the ranking** with importance scores of 0.012–0.015. When we trained two separate models — one with only lifestyle/metabolic variables, one with only medications — their ROC-AUC scores were virtually identical (~0.54 each).

**Conclusion: in this cohort, metabolic and body composition variables predicted blood pressure control far better than pharmacological scheme. The data suggests that without addressing lifestyle factors, medication alone has limited impact.**

The best Random Forest model achieved **ROC-AUC = 0.661** — not clinically reliable enough for individual-level prediction. Given the absence of longitudinal follow-up data, this was expected and the predictive model was discarded.

---

### Act 4 — The Health Score & Topological Routing Algorithm

Rather than predicting outcomes we couldn't reliably forecast, we redesigned the objective around what the data *could* support: **personalized habit recommendations grounded in the topological structure of real patient profiles.**

**Health Score (0–8)**

A clinically-grounded composite score based on WHO/AHA thresholds:

| Component | Healthy threshold | Points |
|---|---|---|
| BMI | 18.5–24.9 kg/m² | 1 |
| Waist circumference | <102cm (M) / <88cm (F) | 1 |
| Triglycerides | < 150 mg/dL | 1 |
| HDL cholesterol | >40 (M) / >50 (F) mg/dL | 1 |
| Fasting glucose | < 100 mg/dL | 1 |
| Added sugar | ≤ 2 tbsp/day | 1 |
| Salt habits | Does not add salt before tasting | 1 |
| Sedentary days | ≤ 3.5 days/week | 1 |

**Clinical Risk Score (0–3)**

A separate, non-comparable dimension:

- Hypertension diagnosis: +1.0
- Diabetes diagnosis: +1.5

These two scores are kept separate intentionally. A score of 6/8 means something different for a patient without chronic conditions versus one with both hypertension and diabetes. By separating habit quality from clinical burden, the system avoids misleading comparisons across diagnostic profiles.

**Topological Routing Algorithm**

For a given patient, the algorithm:

1. Calculates their Health Score and assigns them to a diagnostic profile group (no diagnosis / HTA only / DM only / HTA + DM).
2. Searches the Mapper graph for **nodes within the same diagnostic group** that have a higher average Health Score.
3. Identifies the **destination node** — the one with the highest Health Score among candidates.
4. Computes the **gap by component**: which Health Score components does the patient fail that the destination node's patients predominantly pass (>60% compliance)?
5. Returns the top 3 recommendations ordered by gap magnitude.

The key insight: because the destination node is part of the **same topological complex** — connected by edges or within the same cycle — we can assert with greater confidence that it represents a *clinically similar* profile, not an arbitrary reference point. The patient is being compared to real patients like them who already achieved better habits.

---

## Key Findings

- **Topology reveals what PCA cannot:** 4 structurally distinct patient components were identified, including an isolated subpopulation of dual-diagnosis patients with the worst treatment outcomes — invisible in standard PCA.
- **Medications are not the primary driver of blood pressure control in this cohort.** Metabolic and lifestyle variables consistently outranked pharmacological variables across all feature importance analyses.
- **Without lifestyle change, pharmacological adjustment has limited marginal impact** — demonstrated by comparable predictive power between medication-only and lifestyle-only models.
- **A clinically-grounded Health Score (0–8)** provides a transparent, auditable single metric that structures the recommendation system without black-box opacity.
- **The Mapper graph enables a novel recommendation paradigm:** instead of statistical predictions, patients receive guidance derived from the minimum topological distance to similar real patients with better profiles.

---

## Methodology

```
Raw survey data (966 patients, 40+ variables)
        │
        ▼
Data Fusion & Cleaning
  · Multi-sheet Excel join on Paciente_ID
  · Height unit correction (mixed m/cm)
  · BMI recalculation
  · Medication binary imputation (NaN → 0)
  · Ordinal activity encoding (midpoint mapping)
  · NA filtering on 23 core variables → 884 patients
        │
        ▼
Feature Engineering
  · Waist/hip ratio
  · n_medicamentos (sum of 5 binary medication columns)
  · actividad_historica_promedio (mean across age brackets)
  · Health Score components (s_IMC, s_CINTURA, s_TG, ...)
  · Diagnostic profile (4 categories)
        │
        ▼
TDA Mapper
  · Lens: PCA (2 components)
  · Clusterer: DBSCAN (eps=4.0, min_samples=5)
  · Cover: 10 cubes, 50% overlap
  · Output: 66 nodes, 171 edges
  · Graph stored as NetworkX adjacency
        │
        ▼
Analysis Layer
  · Component analysis (4 connected components)
  · Medication effectiveness comparison
  · Random Forest (ROC-AUC 0.661) — discarded
  · Feature importance (permutation-based)
  · Health Score construction
        │
        ▼
Recommendation Engine
  · Profile assignment (diagnostic group)
  · Topological nearest-neighbor search
  · Gap analysis by score component
  · Ranked habit recommendations
        │
        ▼
Streamlit Application
  · Health Score visualization
  · Diagnostic profile & clinical risk
  · Topological routing output
  · Personalized top-3 recommendations
```

**Stack:** Python 3.10 · pandas · scikit-learn · kmapper · networkx · DBSCAN · Random Forest · scipy · Streamlit · Plotly

---

## App Demo

🚀 **[Live App — Streamlit Cloud](https://your-app-url.streamlit.app)** *(replace with your deployment URL)*

The app accepts clinical inputs — metabolic markers, anthropometric measurements, lifestyle habits, and diagnostic status — and returns:

- A **Health Score (0–8)** with component breakdown
- A **Clinical Risk Score (0–3)** based on chronic diagnoses
- A **topological routing result**: what the closest higher-scoring real patients in the dataset look like
- **Top 3 personalized recommendations** ordered by gap magnitude, with concrete actionable advice

> *"Your Health Score is 4/8. Patients with your same profile (Hypertension) have reached 6.7/8. The highest-impact changes for your profile are: 1) Reduce waist circumference, 2) Lower triglycerides, 3) Increase physical activity."*

---

## Limitations & Future Work

**Current limitations:**

- No longitudinal data — the dataset is a single cross-sectional survey. The system recommends based on similar profiles that *already exist* in the data, not on observed changes over time.
- Extreme profiles may fall outside all Mapper nodes, producing no topological reference for comparison.
- The Health Score weights all components equally; clinically, some variables may warrant higher weight depending on the patient's condition.
- Sample size (n=884 after filtering) limits the density of certain diagnostic subgroups, particularly `Solo_DM` (n=41).

**Future directions:**

- **Longitudinal follow-up:** with repeated measurements over time, a model could evaluate whether a specific treatment is working for a given patient profile — the original clinical question this project could not fully answer with available data.
- **Continuous dataset growth:** each new patient enriches the Mapper graph, making recommendations increasingly precise as the graph density grows.
- **Treatment effectiveness model:** if prescription changes and outcomes were tracked, a physician-facing tool could estimate the viability of a given pharmacological scheme for a specific patient profile.
- **Weighted Health Score:** incorporate clinical literature weights per component, potentially stratified by diagnostic profile.
- **Topological persistence:** apply persistent homology to quantify the stability of identified patient clusters across parameter variations.

---

## Skills Demonstrated

| Domain | Methods & Tools |
|---|---|
| **Topological Data Analysis** | Mapper algorithm, simplicial complexes, graph connectivity analysis |
| **Unsupervised Learning** | DBSCAN, K-Means, hierarchical clustering, PCA |
| **Supervised Learning** | Random Forest, feature importance (Gini + permutation), cross-validation |
| **Statistical Analysis** | ROC-AUC, Brier Score, Mann-Whitney U, Spearman correlation |
| **Data Engineering** | Multi-source data fusion, missing data strategy, ordinal encoding |
| **Algorithm Design** | Topological routing algorithm, gap-based recommendation engine |
| **Clinical Methodology** | WHO/AHA threshold-based scoring, diagnostic stratification |
| **Software Development** | Streamlit deployment, modular Python pipeline, reproducible notebooks |
| **Visualization** | Plotly, KeplerMapper HTML graphs, heatmaps, biplots |

---

## Project Structure

```
inmegen-tda-health/
│
├── README.md
├── LICENSE
│
├── notebooks/
│   ├── 01_exploratorio_pca.ipynb        # PCA, heatmap, hierarchical clustering
│   └── 02_tda_mapper_pipeline.ipynb     # Full TDA pipeline + score + recommendations
│
├── app/
│   ├── app.py                           # Streamlit application
│   ├── requirements.txt
│   └── assets/
│       ├── mapper_presion_controlada.html
│       ├── mapper_SBP.html
│       ├── mapper_glu.html
│       ├── mapper_n_meds.html
│       ├── mapper_IMC.html
│       └── mapper_edad.html
│
├── data/
│   └── README.md                        # Data access policy
│
└── figures/
    ├── heatmap_extremos.png
    ├── dendograma_perfil_sano.png
    ├── pca_biplot_kmeans.png
    ├── mapper_overview.png
    └── score_distribution.png
```

---

## How to Run

**Requirements**
```bash
pip install -r app/requirements.txt
```

**Local**
```bash
streamlit run app/app.py
```

**Required files** (place in same directory as `app.py`):
```
metadata.pkl
df_active_habitos.csv
nodos_stats_habitos.csv
grafo_adyacencia.json
```

> The patient dataset is confidential and not distributed in this repository per agreement with INMEGEN. The app files above contain only derived, non-identifiable statistical summaries.

---

## Data Policy

The raw survey data was provided by INMEGEN under a research collaboration agreement. Individual patient records are not included in this repository. The files distributed with the app (`df_active_habitos.csv`, `nodos_stats_habitos.csv`) contain only aggregated node statistics and anonymized derived features — no personal identifiers.

---

## Authors

**Javier Romero Santos** · Data Science & Mathematics, Tecnológico de Monterrey  
**Raúl Infante Padilla** · Tecnológico de Monterrey  
**Mauro Artemio Sotelo** · Tecnológico de Monterrey  

*In collaboration with Dr. Claudia Rangel — INMEGEN*

---

## Acknowledgments

This project was developed as part of the *Análisis de Ciencia de Datos* course at Tecnológico de Monterrey, Querétaro Campus. We thank INMEGEN and Dr. Claudia Rangel for providing the dataset and clinical context that made this research possible.

---

*Análisis de Ciencia de Datos · Tecnológico de Monterrey · 2025*

---

## Resumen en Español

Este proyecto desarrolla un pipeline de **Análisis Topológico de Datos (TDA)** sobre una base de datos de pacientes geriátricos del INMEGEN. A partir de un grafo Mapper construido sobre 29 variables clínicas y de hábitos, diseñamos un **score de salud basado en umbrales clínicos establecidos** y un **algoritmo de recomendación topológica** que identifica los cambios mínimos de hábitos que un paciente necesita para alcanzar un perfil más saludable — comparándolo con pacientes reales similares que ya lo lograron.

El hallazgo central del análisis: en esta cohorte, **los medicamentos no son la variable determinante del control de presión arterial**. Las variables metabólicas y de composición corporal predicen el control de presión significativamente mejor que el esquema farmacológico. Sin cambios en hábitos, el ajuste de medicación tiene impacto marginal.
