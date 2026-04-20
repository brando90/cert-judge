# VeriBench Verina Format

This directory contains the VeriBench dataset converted to the Verina benchmark format.

## Directory Structure

```
veribench_verina_format/
├── datasets/
│   └── veribench/           # 163 converted VeriBench tasks
│       └── veribench_*/     # Individual task directories
├── lakefile.lean            # Lean project configuration
├── Verina.lean             # Lean entry point
├── lean-toolchain          # Lean version specification
├── lake-manifest.json      # Lake dependencies
├── prefect.toml            # Prefect workflow configuration
└── README.md               # This file
```

**Note:** Configuration files have been moved to `py_src/veribench/verina/configs/` as part of the reorganization.

## Running the Benchmark

The Verina benchmark code has been migrated to `py_src/veribench/verina/` as a submodule of the main veribench package.

### From the veribench root directory:

```bash
# Install dependencies
uv sync

# Run the benchmark
python -m veribench.verina.scripts.benchmark \
    -c py_src/veribench/verina/configs/gpt-4o.toml

# Run on a specific task
python -m veribench.verina.scripts.benchmark \
    -c py_src/veribench/verina/configs/gpt-4o.toml \
    --only veribench_easy_myadd
```

### Configuration

Configuration files are in `py_src/veribench/verina/configs/`:
- `gpt-4o.toml` - GPT-4o model configuration
- `gpt-5.2-all-veribench.toml` - GPT-5.2 configuration for all VeriBench tasks
- `claude-sonnet.toml` - Claude Sonnet configuration
- `template.toml` - Template for creating new configurations
- `test-single.toml` - Test configuration for single tasks

### Environment Variables

Set your API keys in a `.env` file at the veribench root:

```bash
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key
```

## Building Lean Dependencies

Before running benchmarks, ensure Mathlib is built:

```bash
cd veribench_dataset/veribench_verina_format
lake exe cache get  # Fetch pre-compiled Mathlib
lake build
```

## Output

Benchmark results are saved to the `output/` directory specified in the configuration file.

## Notes

- The Python code for Verina has been merged into `py_src/veribench/verina/`
- This directory contains only the datasets, Lean files, and configurations
- See the main veribench README for full documentation
