# MorphoMatter

Research notes and bounded computational experiments on transitions, control, and evidence.

## Executable Experiment 063 pilot

This branch implements the **first bounded increment** of [Experiment 063](docs/EXPERIMENT_063_CAUSAL_DISAGREEMENT_RESOLUTION_MARKET.md): choose diagnostic experiments under a budget, verify their evidence, and evaluate resulting decisions. It is not a material-dynamics simulation, an autonomous laboratory, or completion of all preceding numbered roadmaps.

The pilot uses four independent diagnostic groups. Each group contains three unknown binary claims and one shared sensor-fault bit. A calibration audit can inform several claims; independent replication, aliased reports, failed measurements, and uninformative probes provide alternatives and controls. Exact finite Bayesian inference models the declared dependencies. The scheduler knows the candidate likelihood model but does not receive the evaluator's true latent state or future observations.

### Run

Python 3.10+; standard library only. Run from the repository root:

```bash
python -m unittest discover -s tests -v
python -m experiments.exp063 --stage smoke --output out/smoke --replay
python -m experiments.exp063 --stage development --output out/development --replay
# Freeze/review out/development/comparator_lock.json before exposing evaluation outcomes.
python -m experiments.exp063 --stage evaluation --lock out/development/comparator_lock.json --output out/evaluation --replay
```

Development uses worlds `0..31`; evaluation uses `1000..1127`. The best non-candidate baseline is selected only on development worlds. A lock binds the comparator to the manifest and implementation/test content hashes; evaluation rejects a stale lock. The checked-in CI workflow performs development until a reviewed lock is committed, then runs evaluation. A fresh reproduction may generate its own development lock, which should match the recorded one at the same scientific source version.

Outputs: `summary.json`, `endpoints.json`, complete `records.jsonl` with selection/receipt chains, and a separate `runtime.json`. `--replay` checks each full policy/world record twice. Negative scientific results do not fail CI; budget, known-invalid evidence-use, chain integrity, or replay failures do.

### Files

- `morphomatter/exp063.py`: finite model, verifier, scheduler, budget ledger, evaluator.
- `experiments/exp063.py`: split-specific runner, comparator locking, paired whole-world bootstrap.
- `experiments/exp063_manifest.json`: frozen pilot configuration and limitations.
- `tests/test_exp063.py`: correctness and negative-control tests, including a counterexample to greedy optimality.

The original broad protocol remains a draft; the manifest explicitly narrows this executable pilot. Protocol-scope freeze: `c90d4ab65ef8b37d02643d4322bab94c45a8366e`. Implementation and evaluation evidence must be identified separately; the freeze alone proves no result.

### What is deliberately not claimed

The simulator's synthetic claim bits do not measure a real assembly window, phase transition, or physical energy. The model assumes its stated likelihood family and known source grouping. Unknown shared bugs, full scope-split diagnosis, an omitted true mechanism, a regime-shift benchmark, full dependency DAG repair, and large-scale two-step planning remain unimplemented in this increment. Scope mismatch and stale-source removal are verifier unit controls, not evidence that the full scientific diagnosis exists.

Hashes/checks detect particular artifact changes; they do not certify empirical truth or external replication. Passing replay is software repeatability. Conditional uncertainty is not a guarantee against unknown model error.

The next work item is to evaluate and inspect this pilot, not append another numbered roadmap.
