# rag-afm-codegen
**Evaluating Code Generation Quality in RAG-Enhanced LLMs Across Diverse AFM Tasks**

A reproducible evaluation pipeline for AFM-oriented code generation using Retrieval-Augmented Generation (RAG) and multiple LLM backends (GPT, DeepSeek, Llama, Mistral).

---

## 1) Project Objective

This repository studies whether grounding LLMs with AFM manual-derived retrieval context improves code generation quality for AFM scripting tasks.  
The workflow:

1. Build/prepare a function knowledge base from AFM documentation.
2. Retrieve task-relevant function snippets via vector search.
3. Generate AFM Python code from natural-language queries.
4. Compare model outputs across multiple LLMs and summarize results.

---

## 2) Repository Structure

```text
rag-afm-codegen/
├── model/
│   ├── creat_database.py
│   └── rag_code.py
├── questions/
│   └── question_AFM.csv
├── result/
│   ├── automation_part.ipynb
│   ├── chroma_db/
│   ├── plots_fin/
│   ├── all results csv and plot/
│   ├── question_AFM_gpt_fin.csv
│   ├── question_AFM_deepseek_fin.csv
│   ├── question_AFM_llama_fin.csv
│   └── question_AFM_mistral_fin.csv
├── .gitignore
└── README.md
```

---

## 3) What Each Component Does

- **`model/creat_database.py`**  
  Builds the AFM function database / retrieval-ready representation from manual-derived data.

- **`model/rag_code.py`**  
  Main RAG generation pipeline: query processing, retrieval, and code generation.

- **`questions/question_AFM.csv`**  
  Evaluation prompt set of AFM tasks (natural-language questions/instructions).

- **`result/question_AFM_*_fin.csv`**  
  Final per-model generated outputs and/or evaluation exports.

- **`result/automation_part.ipynb`**  
  Notebook for execution/analysis/aggregation and plotting.

- **`result/chroma_db/`**  
  Persisted Chroma vector store used during retrieval.

- **`result/plots_fin/`** and **`result/all results csv and plot/`**  
  Final plots and merged evaluation artifacts.

---

## 4) Reproducibility Setup

> Recommended: Python 3.10+ in a clean virtual environment.

### 4.1 Create environment

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows PowerShell
```

### 4.2 Install dependencies

If you already have a `requirements.txt`, run:

```bash
pip install -r requirements.txt
```

If not, install the common stack used by this project:

```bash
pip install pandas numpy jupyter notebook chromadb sentence-transformers langchain openai matplotlib seaborn
```

> If your scripts use provider-specific SDKs (DeepSeek, Mistral, etc.), install those too.

### 4.3 Configure API keys

Set environment variables before running generation scripts:

```bash
export OPENAI_API_KEY="your_key"
# export DEEPSEEK_API_KEY="your_key"
# export MISTRAL_API_KEY="your_key"
# export TOGETHER_API_KEY="your_key"   # if applicable for Llama endpoint
```

(Windows PowerShell)

```powershell
setx OPENAI_API_KEY "your_key"
```

---

## 5) Reproduction Protocol

### Step A — Prepare / refresh retrieval database

Run:

```bash
python model/creat_database.py
```

Expected outcome:
- AFM function knowledge base is processed and/or embedded.
- Chroma artifacts are available (typically under `result/chroma_db/` or configured path).

### Step B — Run RAG code generation

Run:

```bash
python model/rag_code.py
```

Expected outcome:
- Model-wise output CSVs are generated/updated in `result/`.
- Generated code responses align with `questions/question_AFM.csv`.

### Step C — Aggregate and visualize results

Open and run:

```bash
jupyter notebook result/automation_part.ipynb
```

Expected outcome:
- Consolidated metrics/tables.
- Plots exported to `result/plots_fin/` and/or `result/all results csv and plot/`.

---

## 6) Evaluation Outputs in This Repo

Current final result files include:

- `result/question_AFM_gpt_fin.csv`
- `result/question_AFM_deepseek_fin.csv`
- `result/question_AFM_llama_fin.csv`
- `result/question_AFM_mistral_fin.csv`

These files are intended for cross-model comparison of AFM task code-generation quality.

---

## 7) Suggested Reporting Template (for paper appendix)

When reproducing, report:

1. **Environment**: OS, Python version, package versions  
2. **Embedding setup**: model name, chunking/indexing parameters  
3. **Retriever config**: top-k, ranking/reranking strategy  
4. **LLM config**: model name, temperature, max tokens  
5. **Prompt protocol**: system instructions / safety constraints  
6. **Dataset**: `question_AFM.csv` version/hash  
7. **Metrics**: syntax validity, API/function correctness, task completion rate, safety-constraint adherence  
8. **Randomness control**: seeds / deterministic settings if used

---

## 8) Notes on Determinism

LLM outputs can vary run-to-run due to provider nondeterminism.  
For tighter reproducibility:

- set temperature to low values (e.g., 0–0.2),
- fix prompts and retrieval parameters,
- log exact model versions and timestamps,
- archive raw generations before post-processing.

---

## 9) Safety Disclaimer

This project targets AFM code generation that may control real laboratory instruments.  
Generated scripts must be validated by qualified personnel before any physical execution.  
Never execute unverified control code on live hardware.

---

## 10) Citation

If you use this repository in your work, please cite your associated paper/preprint (add BibTeX here once available).

```bibtex
@misc{mondal2026ragafm,
  title={Evaluating Code Generation Quality in RAG-Enhanced LLMs Across Diverse AFM Tasks},
  author={Megha Mondal},
  year={2026},
  note={GitHub repository}
}
```
