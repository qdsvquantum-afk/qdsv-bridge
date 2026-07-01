# QDSV Bridge Colab Notebooks

These notebooks are the quickest way to test the public Bridge flow:

```text
Problem spec -> Bridge artifact -> Bridge Report
```

They install `qdsv-bridge` from PyPI and call the QDSV Bridge API. No raw datasets
are sent; each notebook uses a compact semantic problem specification.

## Open In Colab

| Notebook | Purpose |
|---|---|
| [01 Semantic Candidate Marking](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/01_semantic_candidate_marking.ipynb) | Minimal fallback family for finite candidate marking. |
| [02 Predicate Oracle Marking](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/02_predicate_oracle_marking.ipynb) | Predicate-oriented marking and oracle artifact generation. |
| [03 Semantic Signal Classification](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/03_semantic_signal_classification.ipynb) | Prepared-signal classification flow inspired by EEG-style semantic signals. |
| [04 IBM/Qiskit Artifact Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/04_ibm_qiskit_bridge_demo.ipynb) | Problem-first Bridge artifact inspection and local Qiskit simulation path. |
| [05 AWS Braket OpenQASM Demo](https://colab.research.google.com/github/qdsvquantum-afk/qdsv-bridge/blob/main/notebooks/05_aws_braket_openqasm_demo.ipynb) | Problem-first Bridge artifact inspection and local Amazon Braket simulation path. |

## Optional Configuration

By default, the notebooks use the public QDSV Bridge API URL configured inside each notebook.
You can override it before creating the client:

```python
import os
os.environ["QDSV_BRIDGE_API_URL"] = "https://your-api.example.com/api"
```

If a private deployment requires a key, set:

```python
os.environ["QDSV_BRIDGE_API_KEY"] = "your_key"
```
