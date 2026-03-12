# ML Model Training Pipeline

This directory contains the training infrastructure for the AI Interview Simulator's specialized ML models.

## Architecture

```
ml/
├── config.py           # Training configurations & hyperparameters
├── dataset.py          # Synthetic dataset generation for all models
├── models/             # Model definitions
│   ├── answer_quality.py       # Technical Answer Quality (DeBERTa)
│   ├── communication.py        # Communication Clarity classifier
│   ├── star_analyzer.py        # STAR Behavioral component detector
│   ├── code_evaluator.py       # Code Quality evaluator (CodeBERT)
│   └── meta_scorer.py          # Meta-model aggregator (XGBoost)
├── train.py            # Unified training entry point
└── inference.py        # Production inference service
```

## Models

| Model | Architecture | Task | Input | Output |
|-------|-------------|------|-------|--------|
| Answer Quality | DeBERTa-v3-small | Regression | Q+A text | Score 0-10 |
| Communication | DistilBERT | Multi-label | Answer text | Clarity/Fluency/Structure |
| STAR Analyzer | DeBERTa-v3-small | Multi-task | Answer text | S/T/A/R scores |
| Code Evaluator | CodeBERT | Multi-output | Code text | Quality/Efficiency/Style |
| Meta Scorer | XGBoost | Regression | Feature vector | Final score 0-10 |

## Quick Start

```bash
# Generate training data
python -m ml.dataset --output ./data/ml_training

# Train all models
python -m ml.train --all --epochs 5

# Train a specific model
python -m ml.train --model answer_quality --epochs 10
```
