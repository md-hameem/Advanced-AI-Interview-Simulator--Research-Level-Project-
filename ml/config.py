"""
ML Model Training Pipeline - Configuration
Hyperparameters, paths, and model configurations.
"""
import os
from dataclasses import dataclass, field


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "ml_training")
MODEL_DIR = os.path.join(PROJECT_ROOT, "data", "ml_models")


@dataclass
class AnswerQualityConfig:
    """DeBERTa-based answer quality scorer."""
    model_name: str = "microsoft/deberta-v3-small"
    max_length: int = 512
    num_labels: int = 1  # regression
    learning_rate: float = 2e-5
    batch_size: int = 16
    epochs: int = 5
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    output_dir: str = os.path.join(MODEL_DIR, "answer_quality")


@dataclass
class CommunicationConfig:
    """DistilBERT-based communication clarity classifier."""
    model_name: str = "distilbert-base-uncased"
    max_length: int = 384
    num_labels: int = 3  # clarity, fluency, structure
    learning_rate: float = 3e-5
    batch_size: int = 16
    epochs: int = 5
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    output_dir: str = os.path.join(MODEL_DIR, "communication")


@dataclass
class StarAnalyzerConfig:
    """DeBERTa-based STAR component detector."""
    model_name: str = "microsoft/deberta-v3-small"
    max_length: int = 512
    num_labels: int = 4  # S, T, A, R scores
    learning_rate: float = 2e-5
    batch_size: int = 16
    epochs: int = 5
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    output_dir: str = os.path.join(MODEL_DIR, "star_analyzer")


@dataclass
class CodeEvaluatorConfig:
    """CodeBERT-based code quality evaluator."""
    model_name: str = "microsoft/codebert-base"
    max_length: int = 512
    num_labels: int = 3  # quality, efficiency, style
    learning_rate: float = 2e-5
    batch_size: int = 8
    epochs: int = 5
    warmup_ratio: float = 0.1
    weight_decay: float = 0.01
    output_dir: str = os.path.join(MODEL_DIR, "code_evaluator")


@dataclass
class MetaScorerConfig:
    """XGBoost meta-model aggregator."""
    n_estimators: int = 200
    max_depth: int = 6
    learning_rate: float = 0.1
    subsample: float = 0.8
    colsample_bytree: float = 0.8
    feature_names: list = field(default_factory=lambda: [
        "answer_quality_score",
        "communication_clarity", "communication_fluency", "communication_structure",
        "star_situation", "star_task", "star_action", "star_result",
        "code_quality", "code_efficiency", "code_style",
        "speech_wpm", "speech_confidence", "speech_filler_ratio",
        "question_difficulty_numeric",
        "answer_length_normalized",
    ])
    output_dir: str = os.path.join(MODEL_DIR, "meta_scorer")


@dataclass
class TrainingConfig:
    """Top-level training config."""
    answer_quality: AnswerQualityConfig = field(default_factory=AnswerQualityConfig)
    communication: CommunicationConfig = field(default_factory=CommunicationConfig)
    star_analyzer: StarAnalyzerConfig = field(default_factory=StarAnalyzerConfig)
    code_evaluator: CodeEvaluatorConfig = field(default_factory=CodeEvaluatorConfig)
    meta_scorer: MetaScorerConfig = field(default_factory=MetaScorerConfig)
    seed: int = 42
    data_dir: str = DATA_DIR
    model_dir: str = MODEL_DIR
