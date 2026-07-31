# DNAStoreAI Architecture

## Design Principles

DNAStoreAI follows **clean architecture** with dependency injection, SOLID design patterns, and research reproducibility standards. The simulation layer is designed to be swappable with real laboratory hardware without changing the rest of the system.

## Layer Architecture

### 1. Presentation Layer
- **React Frontend** (`frontend/`): Dashboard, file upload, simulation controls, analytics
- **REST API** (`backend/dnastoreai/api/`): FastAPI routes with Pydantic validation

### 2. Application Layer
- **PipelineService**: Orchestrates the full encode/store/retrieve workflow
- **ArchiveService**: Filesystem-based DNA archive management
- **ExperimentService**: Research experiment execution
- **MetricsService**: Platform-wide metrics aggregation

### 3. Domain Layer (Modules)

| Module | Path | Responsibility |
|--------|------|----------------|
| Compression | `modules/compression/` | gzip, zlib, lzma + AI interface |
| Segmentation | `modules/segmentation/` | Block splitting with metadata |
| Metadata | `modules/metadata/` | DNA-safe header serialization |
| ECC | `modules/ecc/` | Reed-Solomon, BCH, LDPC, Fountain |
| Encoding | `modules/encoding/` | Binary ↔ DNA conversion |
| Optimization | `modules/optimization/` | GC control, homopolymer, hairpin |
| Synthesis | `modules/synthesis/` | Oligo synthesis error simulation |
| Degradation | `modules/degradation/` | Aging and environmental damage |
| Sequencing | `modules/sequencing/` | Illumina, Nanopore, PacBio |
| Reconstruction | `modules/reconstruction/` | Block recovery and file assembly |
| AI Reconstruction | `modules/ai_reconstruction/` | Transformer/GNN placeholders |
| Semantic Archive | `modules/semantic_archive/` | Vector search over DNA entries |
| Datasets | `modules/datasets/` | Synthetic data generators |

### 4. Infrastructure Layer
- **SQLite/PostgreSQL**: Archive metadata persistence
- **ChromaDB**: Vector database for semantic search
- **Filesystem**: DNA sequence archive storage (FASTA format)

## Data Flow

### Store Pipeline
```
File → compress() → segment() → DNAHeader → ECC.encode() → DNAEncoder.encode()
  → optimize_sequence() → SynthesisSimulator → Archive (FASTA + manifest.json)
```

### Retrieve Pipeline
```
Archive → SynthesisSimulator → DegradationSimulator → SequencingSimulator
  → DNAEncoder.decode() → ECC.decode() → reassemble() → decompress() → File
```

## Hardware Integration Points

The following interfaces are designed for future hardware replacement:

| Simulator | Hardware Interface |
|-----------|-------------------|
| `SynthesisSimulator` | DNA synthesizer API (Twist, IDT) |
| `DegradationSimulator` | Environmental chamber sensors |
| `SequencingSimulator` | Illumina/Nanopore/PacBio instrument APIs |
| `AICompressor` | Learned compression models |
| `DNATransformerReconstructor` | GPU inference endpoints |

## Dependency Injection

```python
from dnastoreai.core.dependencies import get_pipeline_service

@router.post("/store")
async def store(pipeline: PipelineService = Depends(get_pipeline_service)):
    ...
```

## Database Schema

- `archives`: File metadata and configuration
- `dna_sequences`: Per-block DNA sequences with fitness scores
- `experiments`: Experiment configurations and results
