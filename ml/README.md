# ML Model Training Pipeline

This directory contains the full training infrastructure for the AI Interview Simulator's specialized ML models — from synthetic data generation to production inference.

## 📁 Structure

```
ml/
├── 01_dataset_exploration.ipynb    # Data generation & visualization notebook
├── 02_model_training.ipynb         # Model training & evaluation notebook
├── config.py                       # Hyperparameters & paths
├── dataset.py                      # Synthetic dataset generators
├── train.py                        # CLI training entry point
├── inference.py                    # Production inference service
└── models/
    ├── answer_quality.py           # DeBERTa-v3-small regression
    ├── communication.py            # DistilBERT multi-head
    ├── star_analyzer.py            # DeBERTa-v3-small 4-head
    ├── code_evaluator.py           # CodeBERT multi-head
    └── meta_scorer.py              # XGBoost aggregator
```

---

## 🧠 Models

| Model | Architecture | Input | Output | Dims |
|-------|-------------|-------|--------|------|
| **Answer Quality** | DeBERTa-v3-small | Q + A text | Score | 1 (0-10) |
| **Communication** | DistilBERT | Answer text | Clarity / Fluency / Structure | 3 (0-5) |
| **STAR Analyzer** | DeBERTa-v3-small | Behavioral answer | S / T / A / R scores | 4 (0-5) |
| **Code Evaluator** | CodeBERT | Source code | Quality / Efficiency / Style | 3 (0-5) |
| **Meta Scorer** | XGBoost | 16-feature vector | Final score | 1 (0-10) |

---

## 📥 Dataset Downloads & Sources

### Synthetic Datasets (Included)

Our training data is generated via `dataset.py`. Run the notebook or CLI to produce all 5 datasets locally:

```bash
python -m ml.dataset --output ./data/ml_training --n 2000
```

Or run **`01_dataset_exploration.ipynb`** Cell 2 to generate and visualize all datasets interactively.

### Public Datasets for Augmentation

To improve model accuracy beyond synthetic data, augment with these real-world datasets:

| Dataset | Source | Useful For | Link |
|---------|--------|-----------|------|
| **SQuAD 2.0** | Stanford | Answer quality scoring (QA correctness) | [🔗 Download](https://rajpurkar.github.io/SQuAD-explorer/) |
| **CoQA** | Stanford | Conversational QA (multi-turn) | [🔗 Download](https://stanfordnlp.github.io/coqa/) |
| **DS Interview Q&A** | Kaggle | Technical interview Q+A pairs | [🔗 Kaggle](https://www.kaggle.com/datasets/rtatman/data-science-interview-questions) |
| **HumanEval** | OpenAI | Code correctness evaluation | [🔗 GitHub](https://github.com/openai/human-eval) |
| **CodeXGLUE** | Microsoft | Code understanding & generation tasks | [🔗 GitHub](https://github.com/microsoft/CodeXGLUE) |
| **ASAP-AES** | Kaggle | Automated essay scoring (text quality) | [🔗 Kaggle](https://www.kaggle.com/c/asap-aes) |
| **CoNLL-2014** | NLP | Grammatical error detection (fluency) | [🔗 Download](https://www.comp.nus.edu.sg/~nlp/conll14st.html) |

### Pre-trained Model Weights

Base models are auto-downloaded from Hugging Face on first run:

| Model | Hugging Face ID | Size |
|-------|----------------|------|
| DeBERTa-v3-small | [`microsoft/deberta-v3-small`](https://huggingface.co/microsoft/deberta-v3-small) | ~140 MB |
| DistilBERT | [`distilbert-base-uncased`](https://huggingface.co/distilbert-base-uncased) | ~260 MB |
| CodeBERT | [`microsoft/codebert-base`](https://huggingface.co/microsoft/codebert-base) | ~480 MB |

---

## 📊 Datasets

All datasets are synthetically generated via `dataset.py` and saved to `data/ml_training/`.

### 1. Answer Quality (`answer_quality.json`)

| Field | Type | Description |
|-------|------|-------------|
| `question` | string | Technical interview question (drawn from 15-question pool) |
| `answer` | string | Candidate's answer (varied length 20-300+ chars) |
| `score` | float | Quality score 0-10 |

**Distribution:** ~60% good answers (6-10), ~20% medium (3.5-6.5), ~20% poor (0.5-3.5).
Score correlates with answer length and structural complexity.
**Default size:** 2,000 samples.

---

### 2. Communication Clarity (`communication.json`)

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `text` | string | — | Answer text to evaluate |
| `clarity` | float | 0-5 | How clearly ideas are expressed |
| `fluency` | float | 0-5 | Natural flow of language |
| `structure` | float | 0-5 | Logical organization of response |

**Distribution:** ~50% clear (3.5-5.0), ~20% medium (2.0-3.5), ~30% poor (0.5-2.0).
The three dimensions are intentionally correlated — clear answers tend to also be fluent and structured.
**Default size:** 2,000 samples.

---

### 3. STAR Behavioral Analyzer (`star_analyzer.json`)

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `text` | string | — | Behavioral interview answer |
| `situation_score` | float | 0-5 | Describes context/background |
| `task_score` | float | 0-5 | Defines responsibility/goal |
| `action_score` | float | 0-5 | Details specific actions taken |
| `result_score` | float | 0-5 | Quantifies outcomes/impact |

**Distribution:**
- ~40% **complete STAR** — all 4 components clearly present (3.5-5.0 each)
- ~30% **partial STAR** — has situation + task but vague action/result (mixed scores)
- ~30% **no STAR** — generic statements without structure (0.5-1.5 each)

Templates use randomized combinations of real-world scenarios (deadlines, bugs, conflicts), actions (standups, logging, meetings), and results (early delivery, fast resolution).
**Default size:** 2,000 samples.

---

### 4. Code Evaluator (`code_evaluator.json`)

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `code` | string | — | Python source code |
| `quality` | float | 0-5 | Correctness & robustness |
| `efficiency` | float | 0-5 | Time/space complexity |
| `style` | float | 0-5 | Readability & conventions |

**Distribution:** ~50% good code (optimal algorithms), ~20% poor code (brute force), ~30% minimal code (stubs).
Good code examples include hash-map Two Sum (O(n)), stack-based parentheses validation, and Kadane's max subarray.
Poor code examples include nested-loop brute force and string replacement hacks.
**Default size:** 1,500 samples.

---

### 5. Meta Scorer (`meta_scorer.json`)

The meta-scorer aggregates outputs from all 4 specialized models plus speech metrics into a final interview score.

| Feature | Range | Source |
|---------|-------|--------|
| `answer_quality_score` | 1-10 | Answer Quality model |
| `communication_clarity` | 0.5-5 | Communication model |
| `communication_fluency` | 0.5-5 | Communication model |
| `communication_structure` | 0.5-5 | Communication model |
| `star_situation` | 0.5-5 | STAR Analyzer |
| `star_task` | 0.5-5 | STAR Analyzer |
| `star_action` | 0.5-5 | STAR Analyzer |
| `star_result` | 0.5-5 | STAR Analyzer |
| `code_quality` | 0.5-5 | Code Evaluator |
| `code_efficiency` | 0.5-5 | Code Evaluator |
| `code_style` | 0.5-5 | Code Evaluator |
| `speech_wpm` | 80-200 | Speech Processor |
| `speech_confidence` | 0.2-1.0 | Speech Processor |
| `speech_filler_ratio` | 0-0.15 | Speech Processor |
| `question_difficulty_numeric` | 1-4 | Interview config |
| `answer_length_normalized` | 0.1-1.0 | Text processing |
| **`final_score`** (target) | **0.5-10** | **Weighted formula** |

**Score formula weights:** answer quality (25%), communication (15%), STAR (15%), code (15%), confidence (10%), answer length (10%), filler (5%), WPM (5%).
**Default size:** 3,000 samples.

---

## 🚀 Quick Start

### Using Notebooks (Recommended)

1. **Data exploration:** Open and run `01_dataset_exploration.ipynb`
   - Generates all datasets
   - Visualizes distributions, correlations, radar charts
   
2. **Model training:** Open and run `02_model_training.ipynb`
   - Trains all 5 models with evaluation plots
   - Shows pred-vs-true scatter, residuals, feature importance
   - Includes inference demo

### Using CLI

```bash
# Generate training data
python -m ml.dataset --output ./data/ml_training --n 2000

# Train all models
python -m ml.train --all --epochs 5

# Train specific model
python -m ml.train --model answer_quality --epochs 10

# Auto-generate data + train
python -m ml.train --all --generate-data --samples 3000
```

### Using Inference Service

```python
from ml.inference import get_ml_service

service = get_ml_service()

# Answer quality
score = service.predict_answer_quality("What is a hash table?", "A hash table maps keys to values...")

# Communication
scores = service.predict_communication("The concept involves three key areas...")

# STAR behavioral
scores = service.predict_star("At my previous company, we had a deadline...")

# Code quality
scores = service.predict_code_quality("def two_sum(nums, target): ...")

# Final aggregated score
final = service.predict_final_score({"answer_quality_score": 8.5, ...})
```

---

## ⚙️ Configuration

All hyperparameters are centralized in `config.py`:

| Model | Base Model | LR | Batch | Epochs | Max Length |
|-------|-----------|-----|-------|--------|-----------|
| Answer Quality | deberta-v3-small | 2e-5 | 16 | 5 | 512 |
| Communication | distilbert-base | 3e-5 | 16 | 5 | 384 |
| STAR Analyzer | deberta-v3-small | 2e-5 | 16 | 5 | 512 |
| Code Evaluator | codebert-base | 2e-5 | 8 | 5 | 512 |
| Meta Scorer | XGBoost | 0.1 | — | 200 trees | — |

---

## 🔌 API Endpoints

When the backend is running, ML predictions are available at:

```
GET  /api/ml/status                   # Check loaded models
POST /api/ml/predict/answer-quality   # {"question": "...", "answer": "..."}
POST /api/ml/predict/communication    # {"text": "..."}
POST /api/ml/predict/star             # {"text": "..."}
POST /api/ml/predict/code-quality     # {"code": "..."}
```
