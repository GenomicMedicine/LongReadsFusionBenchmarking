# Supplementary Materials

This folder contains **raw fusion-caller outputs** and **supplementary tables** used to reproduce the benchmark figures in our LongFuse paper. Only datasets included in the published figure analyses are provided here.

## Directory layout

```
supplementary materials/
├── README.md                 (this file)
├── Supplement_Table.xlsx     (Supplementary Tables S1–S4)
├── simulated/                (15 simulated datasets)
│   └── <dataset>/
│       └── <method>.txt
└── real/                     (28 real samples)
    └── <sample>/
        └── <method>.txt
```

---

## `simulated/` (n = 15 datasets)

Raw caller outputs for simulated benchmark datasets used in the paper. Each folder contains one text file per method (8 files when complete). Folder names use the full parameter encoding (no short aliases; each dataset is stored once).

### Naming convention

Folder names encode: `{platform}_{coverage}x_{identity}_{read_length}`

| Token | Example | Meaning |
|-------|---------|---------|
| Platform | `nanopore2018`, `pacbio2021` | Sequencing platform / error profile |
| Coverage | `10x`, `1x`, `100x` | Sequencing depth |
| Identity | `0.95`, `0.998`, `0.8` | Mean read identity |
| Read length | `15kb`, `300bp`, `1kb`, `5kb`, `50kb` | Mean read length (`15000` bp → `15kb`) |

### Included datasets

| Folder | Full dataset name (bp read length) |
|--------|-----------------------------------|
| `nanopore2018_10x_0.95_15kb` | nanopore2018_10x_0.95_15000 |
| `nanopore2020_10x_0.95_15kb` | nanopore2020_10x_0.95_15000 |
| `nanopore2023_10x_0.998_15kb` | nanopore2023_10x_0.998_15000 |
| `nanopore2023_10x_0.85_15kb` | nanopore2023_10x_0.85_15000 |
| `nanopore2023_10x_0.8_15kb` | nanopore2023_10x_0.8_15000 |
| `pacbio2016_10x_0.998_15kb` | pacbio2016_10x_0.998_15000 |
| `pacbio2021_1x_0.998_15kb` | pacbio2021_1x_0.998_15000 |
| `pacbio2021_10x_0.998_15kb` | pacbio2021_10x_0.998_15000 |
| `pacbio2021_100x_0.998_15kb` | pacbio2021_100x_0.998_15000 |
| `pacbio2021_10x_0.85_15kb` | pacbio2021_10x_0.85_15000 |
| `pacbio2021_10x_0.8_15kb` | pacbio2021_10x_0.8_15000 |
| `pacbio2021_10x_0.998_300bp` | pacbio2021_10x_0.998_300 |
| `pacbio2021_10x_0.998_1kb` | pacbio2021_10x_0.998_1000 |
| `pacbio2021_10x_0.998_5kb` | pacbio2021_10x_0.998_5000 |
| `pacbio2021_10x_0.998_50kb` | pacbio2021_10x_0.998_50000 |

---

## `real/` (n = 28 samples)

Raw caller outputs for the 28 real consensus samples used in the r3 precision–recall boxplot.

| Sample folder | Description |
|---------------|-------------|
| `A549-cDNA`, `A549-dcDNA`, `A549-dRNA` | A549 cell line, ONT libraries |
| `H9-cDNA`, `H9-dcDNA`, `H9-dRNA` | H9 cell line, ONT |
| `Hct116-cDNA`, `Hct116-dcDNA`, `Hct116-dRNA`, `Hct116-PacBio` | HCT116, ONT + PacBio |
| `HepG2-cDNA`, `HepG2-dcDNA`, `HepG2-dRNA` | HepG2, ONT |
| `HEYA8-cDNA`, `HEYA8-dcDNA`, `HEYA8-dRNA` | HEYA8, ONT |
| `K562-cDNA`, `K562-dcDNA`, `K562-dRNA` | K562, ONT |
| `MCF7-cDNA`, `MCF7-dcDNA`, `MCF7-dRNA`, `MCF7-PacBio` | MCF7, ONT + PacBio |
| `NA12878-cDNA`, `NA12878-dRNA` | NA12878 reference, ONT |
| `SKBR3-PacBio` | SKBR3, PacBio |
| `AML` | AML sample, ONT |
| `UHR` | Universal Human Reference, ONT |

Each sample folder contains up to **8 method files** (see Methods below).

---

## Methods (caller output files)

Eight long-read fusion callers were benchmarked. Each `<method>.txt` file is a copy of the tool’s primary fusion output (or parsed equivalent) for that sample/dataset:

| File name | Tool |
|-----------|------|
| `genion.txt` | genion |
| `JAFFAL.txt` | JAFFAL |
| `LongGF.txt` | LongGF |
| `CTAT-LR-Fusion.txt` | CTAT-LR-Fusion |
| `pbfusion.txt` | pbfusion |
| `FusionSeeker.txt` | FusionSeeker |
| `FLAIR-fusion.txt` | FLAIR-fusion |
| `IFDlong.txt` | IFDlong |

For IFDlong, the expected final product is `*_Fusion_quant_anchor10bp.csv` (provided here as `IFDlong.txt`).

---

## `Supplement_Table.xlsx`

Excel workbook with five sheets:

| Sheet | Supplementary table | Contents |
|-------|---------------------|----------|
| **Overview** | — | One-line description of S1–S4 |
| **S1** | Table S1 | Standardized execution commands and parameter settings for each benchmarked tool (genome build, annotation, auxiliary resources, notes) |
| **S2** | Table S2 | Simulated dataset catalog: platform, depth, identity, read length, error/qscore models, and badread simulation commands |
| **S3** | Table S3 | Public real-data samples: cell line, platform, biological origin, and data accessions (SRA / GoekeLab sg-nex-data) |
| **S4** | Table S4 | Curated fusion reference set (~2,900 gene pairs) with source labels (CCLE, breast cancer cohorts, etc.) used for real-data evaluation |

---

## Missing data and reasons

Only dataset × method combinations with no usable output are listed below. All other method files are present for the 8 callers.
Here, **peak RSS** means the maximum resident set size (the highest physical RAM usage) observed during a run.

### Simulated (1 missing)

| Dataset | Method | Reason |
|---------|--------|--------|
| `pacbio2021_100x_0.998_15kb` | IFDlong | **Runtime exceeded ~1.5 TB memory limit.** Mapping/intersect steps completed but IFDlong did not produce `Fusion_quant` output (peak RSS ~1.46 TB). |


### Present but empty (no predictions)

These method files exist in the package but contain no fusion calls:

| Sample / dataset | Method | Note |
|----------------|--------|------|
| `pacbio2021_1x_0.998_15kb` | genion | The file is present but contains no predictions. |
| `HepG2-dcDNA` | FLAIR-fusion | The file is present but contains no predictions. |

**Note:** Paper analyses treat IFDlong gaps explicitly (empty or absent for the affected samples). Empty genion/FLAIR-fusion files are valid zero-call results.
