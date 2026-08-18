# LongFuse k2/k3/k5 Pipeline Docker

This directory provides a containerized one-command entrypoint for:

- `longFuse/longfuse_k235_pipeline.py`

## One-command usage

Run from repository root:

```bash
bash dockerfiles/longfuse-k235-pipeline_docker/run_longfuse_k235_pipeline.sh \
  kickstart \
  --method-results-root /path/to/method_results \
  --output-dir /path/to/output/longfuse_kickstart \
  --cohort real \
  --execution parallel \
  --workers 3
```

The wrapper script will:

1. Auto-build the Docker image if it does not exist.
2. Auto-mount required host directories inferred from path arguments.
3. Run the pipeline in the container with your current UID/GID.

## Rebuild image manually

```bash
bash dockerfiles/longfuse-k235-pipeline_docker/run_longfuse_k235_pipeline.sh --rebuild --help
```

## Image details

- Base image: `python:3.11-slim`
- Python package: `pandas`
- Entrypoint: `python /app/longfuse_k235_pipeline.py`
