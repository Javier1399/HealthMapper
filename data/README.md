[data_README.md](https://github.com/user-attachments/files/27037578/data_README.md)

# Data

The raw patient survey data provided by INMEGEN is **not included in this repository**.

## Why

The dataset contains clinical information from geriatric patients collected under a research collaboration agreement with INMEGEN (Instituto Nacional de Medicina Genómica, Mexico). Distribution of individual patient records is not permitted under the terms of that agreement.

## What is included in the app

The files distributed alongside the Streamlit application contain only:

- **`nodos_stats_habitos.csv`** — aggregated statistics per Mapper node (mean health score, mean compliance per component, dominant diagnostic profile). No individual patient records.
- **`df_active_habitos.csv`** — anonymized derived features used for nearest-neighbor lookup. No personal identifiers (names, dates of birth, addresses, or any direct identifiers) are present.
- **`grafo_adyacencia.json`** — the NetworkX adjacency structure of the Mapper graph. Contains only node IDs and edge connections.

## For researchers

If you are a researcher interested in the methodology and wish to apply it to your own dataset, the pipeline in `notebooks/02_tda_mapper_pipeline.ipynb` is fully documented and designed to be reproducible on any tabular clinical dataset with appropriate variable mapping.

Contact: [f.romero0599@gmail.com]
