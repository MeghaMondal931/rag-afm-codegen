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


<img width="1593" height="896" alt="rag_afm_codegen_archi_img" src="https://github.com/user-attachments/assets/7d923096-a9b3-44af-bb04-bdb318497e53" />
Figure: Model architecture of RAG based Code Generator

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
├── assets/
│   └── model_architecture.png
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

- **`assets/model_architecture.png`**  
  Model architecture figure used in this README.

---

## 4) Configure API keys

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

## 5) Evaluation Outputs in This Repo

Current final result files include:

- `result/question_AFM_gpt_fin.csv`
- `result/question_AFM_deepseek_fin.csv`
- `result/question_AFM_llama_fin.csv`
- `result/question_AFM_mistral_fin.csv`

These files are intended for cross-model comparison of AFM task code-generation quality.

---
## 6) Main findings
- RAG improved grounding by providing function-specific context to the LLM.
- Without external documentation, general LLMs often generated non-executable or hallucinated instrument-control code.
- Advanced tasks remained difficult due to reasoning errors, wrong function selection, and missing steps.
- A code validation layer is necessary before using LLM-generated scripts in physical instrument workflows.

