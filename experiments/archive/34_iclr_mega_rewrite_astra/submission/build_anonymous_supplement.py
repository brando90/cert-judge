#!/usr/bin/env python3
"""Build a narrow anonymous, offline reproduction supplement from frozen inputs.

This packaging script is local provenance, not part of the uploaded archive.
It never changes frozen sources or calls an inference service.
"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
EVIDENCE = ROOT / "experiments/archive/34_iclr_mega_rewrite_astra/analysis"
PACKAGE = HERE / "anonymous_supplement"
# The package keeps the pre-archive layout (experiment 34 moved to experiments/archive/ on 09-28-2026).
ANALYSIS = PACKAGE / "experiments/34_iclr_mega_rewrite_astra/analysis"
ARCHIVE = HERE / "anonymous_supplement.zip"


def sha(data):
    return hashlib.sha256(data).hexdigest()


def put(relative, data):
    path = PACKAGE / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def main():
    source_summary = json.loads((EVIDENCE / "results/summary.json").read_text())
    records = []
    changed = []
    for relative, evidence in source_summary["inputs"].items():
        data = (ROOT / relative).read_bytes()
        assert sha(data) == evidence["sha256"], relative
        if "exp25_geometric_qwen_r3_median_mono_stab_40_60_avg" in relative:
            decoded = json.loads(data)
            old_path = decoded["source_summary"]
            new_path = "experiments/archive/13_qwen_replication_exp16_exp19/results/exp16_qwen_r3_median/summary.json"
            # Replace only this metadata string; preserve every other byte.
            data = data.replace(json.dumps(old_path).encode(), json.dumps(new_path).encode())
            check = json.loads(data)
            decoded["source_summary"] = new_path
            assert check == decoded
            changed.append({"file": relative, "field": "source_summary", "change": "absolute host path replaced by package-relative path"})
        put(relative, data)
        records.append({"path": relative, "sha256": sha(data), "bytes": len(data)})
    manifest = {"format": 1, "inputs": records, "anonymization": changed}
    put("input_manifest.json", (json.dumps(manifest, indent=2) + "\n").encode())

    script = (EVIDENCE / "rebuild_paper_evidence.py").read_text()
    # Map the archived source back to the package layout, one directory shallower.
    script = script.replace("experiments/archive/34_iclr_mega_rewrite_astra/", "experiments/34_iclr_mega_rewrite_astra/")
    script = script.replace("Path(__file__).resolve().parents[4]", "Path(__file__).resolve().parents[3]")
    script = script.replace("import subprocess\n", "")
    start = script.index("INPUT_REVISION = ")
    end = script.index("\ndef load_json", start)
    script = script[:start] + '''EXPECTED = {row['path']: row['sha256'] for row in json.loads((ROOT / 'input_manifest.json').read_text())['inputs']}


def read(relative):
    data = (ROOT / relative).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED[relative]:
        raise ValueError('Input differs from anonymous manifest: ' + relative)
    INPUTS[relative] = {'sha256': digest}
    return data.decode()

''' + script[end:]
    script = script.replace("payload={'input_revision':INPUT_REVISION,\n             'inputs':INPUTS", "payload={'inputs':INPUTS")
    script = script.replace("from committed scores only", "from supplied frozen scores only")
    assert "subprocess" not in script and "INPUT_REVISION" not in script and "git_blob" not in script
    put("experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py", script.encode())
    put("requirements.txt", b"numpy==2.2.6\nscipy==1.16.3\nmatplotlib==3.10.7\n")
    put("PROMPTS_AND_MODELS.tex", (ROOT / "paper_latex/ICLR_2027_submission/995_appendix_judge_prompts.tex").read_bytes())
    readme = '''# Anonymous score-level reproduction supplement

**TLDR:** This package reproduces five current manuscript figures, fixed-index associations, and local weight-sensitivity summaries from frozen numerical artifacts, without model calls or network access. It is not the full research repository and does not rerun inference or recover missing experimental evidence.

## Reproduction

Requires Python 3.11 or newer. The dependencies are pinned to the versions used to verify this package.
From this extracted directory, create an isolated environment and install dependencies with `uv venv .venv` and `uv pip install --python .venv/bin/python -r requirements.txt`.
Then run:

```sh
.venv/bin/python experiments/34_iclr_mega_rewrite_astra/analysis/rebuild_paper_evidence.py
```

The calculation makes no network requests, reads no credentials, and requires no Git installation or history.
It checks all 28 input files against `input_manifest.json` before use.
Outputs are written to `experiments/34_iclr_mega_rewrite_astra/analysis/results/` and `paper_latex/ICLR_2027_submission/figures/` within this extracted package.
The package includes verified outputs in these locations for inspection without installing dependencies.

## Included coverage

- Fixed equal-weight index recomputation from the three recorded component columns for all three primary families and all three human-label views; eight configurations per family/view.
- Spearman, Pearson, and Kendall associations with recorded judge-level human agreement, and the 12-point local weight grid for each family/view.
- Frozen summaries for the arithmetic and pass1-selected geometric comparisons; their reported correlations are copied from those summaries rather than reconstructed from original human labels.
- Frozen Codex confidence-interval and permutation summaries with their recorded seed and repetition counts; the resampling procedure itself is not rerun here.
- Codex recorded repeated scores, bug-level averages, rewrite diagnostics, and local reversal counts; Claude Opus recorded repeated scores and bug-level averages.
- Five regenerated figures: `judge_agreement_fixed_index.pdf`, `codex_property_checks.pdf`, `codex_rewrite_diagnostics.pdf`, `codex_reversal_counts.pdf`, and `opus_bug_curves.pdf`.
- Exact current main-panel prompt text and documented model identifiers/repetition settings in `PROMPTS_AND_MODELS.tex`, matching the manuscript appendix. Missing historical decoding settings are not inferred.

Historical directory names are retained so paths in the manuscript remain traceable.
All 28 inputs preserve their source bytes except one absolute machine path in a nonnumeric `source_summary` field, replaced with its relative package path.
Numerical observations and configuration identifiers are unchanged.
No author names, repository URLs, machine paths, Git history, logs, private correspondence, or credentials are intentionally included.
`file_manifest.json` hashes every payload file except itself; `input_manifest.json` specifies the frozen numerical input set.

## Limitations

This is score-level reproduction, not a complete end-to-end rerun from Lean candidates and original human labels.
It does not contain the original human annotation instructions (which were not recovered), all task/gold/candidate files, raw model response text, inference clients, or every historical appendix experiment.
It does not regenerate the confidence-interval bootstrap, the different-rubric pool analyses, the threshold sweep, or the separate cross-pass fitted-weight experiments.
The supplied confidence summaries and comparison results are explicitly stored evidence, not fresh experimental runs.
The three label views are validation views of the same panel, not train/validation/test splits; there is no test-set result.
The historical alpha-rewrite probes were not established to preserve meaning, and the main panel contains no missing-specification ladder measurements.
Reproducing these descriptive numerical artifacts does not resolve those limitations.
'''
    put("README.md", readme.encode())

    run = subprocess.run([sys.executable, str(ANALYSIS / "rebuild_paper_evidence.py")], capture_output=True, text=True)
    if run.returncode:
        raise RuntimeError(run.stderr)
    generated = json.loads((ANALYSIS / "results/summary.json").read_text())
    for key in ["family_metrics", "headline_cis", "weight_grid", "sensitivity_summary", "limits"]:
        assert generated[key] == source_summary[key], key
    numerical_outputs = []
    for path in sorted((ANALYSIS / "results").glob("*.csv")):
        assert path.read_bytes() == (EVIDENCE / "results" / path.name).read_bytes(), path.name
        numerical_outputs.append(path.name)
    # A deterministic, conservative scan of every text payload and filename.
    prohibited = re.compile(r"brando|miranda|sanmi|koyejo|stanford|/Users/|/dfs/|/home/|github\.com|[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}|sk-(?:ant-)?[A-Za-z0-9]{16,}", re.I)
    files = sorted(p for p in PACKAGE.rglob("*") if p.is_file() and p.name != "file_manifest.json")
    findings = []
    for path in files:
        relative = str(path.relative_to(PACKAGE))
        if prohibited.search(relative):
            findings.append(relative + ":filename")
        if path.suffix in {".py", ".json", ".csv", ".md", ".txt", ".tex"} and prohibited.search(path.read_text()):
            findings.append(relative + ":text")
    assert not findings, findings
    payload = [{"path": str(p.relative_to(PACKAGE)), "sha256": sha(p.read_bytes()), "bytes": p.stat().st_size} for p in files]
    put("file_manifest.json", (json.dumps({"files": payload}, indent=2) + "\n").encode())
    files.append(PACKAGE / "file_manifest.json")
    with zipfile.ZipFile(ARCHIVE, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(files):
            info = zipfile.ZipInfo("anonymous_supplement/" + str(path.relative_to(PACKAGE)), (1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())
    receipt = {"archive": ARCHIVE.name, "sha256": sha(ARCHIVE.read_bytes()), "bytes": ARCHIVE.stat().st_size,
               "files": len(files), "inputs": len(records), "anonymized_metadata_fields": len(changed),
               "numerical_output_csvs_byte_equal": numerical_outputs, "summary_groups_equal": 5,
               "identity_scan_findings": findings, "limits": "Score-level reproduction only; see anonymous README."}
    (HERE / "supplement_build_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
