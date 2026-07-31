# Experimental Methodology

## Standard Benchmark Protocol

### 1. Dataset Preparation
```python
from dnastoreai.experiments.runner import Experiment

experiment = Experiment.from_dataset(
    dataset_type="mixed",
    count=20,
    encoding="gc_balanced",
    ecc="reed_solomon",
    sequencing="illumina",
)
```

### 2. Encoding Comparison
Run experiments across all encoding schemes with fixed ECC and sequencing:
- basic, rotating, gc_balanced, custom

### 3. ECC Comparison
Run experiments across all ECC strategies with fixed encoding:
- reed_solomon (nsym=10), bch, ldpc, fountain

### 4. Sequencing Platform Comparison
Run with identical archives across platforms:
- Illumina (150bp, error_rate=0.001)
- Nanopore (10kb, error_rate=0.05)
- PacBio (15kb, error_rate=0.001)

### 5. Degradation Study
Vary environmental parameters:
- Temperature: 4°C, 25°C, 37°C
- Humidity: 30%, 50%, 80%
- Time: 1, 5, 10, 50 years

## Metrics Collection

### Storage Metrics
- Compression ratio = original_size / compressed_size
- DNA density = logical_bits / physical_bases
- Overhead = encoded_size / original_size

### Biological Metrics
- GC content (target: 40-60%)
- Homopolymer count (target: 0 runs ≥ 5)
- Hairpin risk score (target: < 0.7)
- Fitness score (target: > 0.8)

### Recovery Metrics
- Recovery accuracy = blocks_recovered / total_blocks
- Bit error rate = erroneous_bits / total_bits
- Checksum validation (binary pass/fail)

## Reproducibility

All experiments record:
- Random seeds
- Full configuration JSON
- Input file checksums
- Timestamp and version

Reports are generated in three formats:
- `report.json` — machine-readable full results
- `report.csv` — tabular per-file results
- `report.html` — human-readable summary

## Statistical Analysis

For comparative studies, run each configuration with n ≥ 5 replicates. Report:
- Mean and standard deviation
- 95% confidence intervals
- Effect sizes between configurations
