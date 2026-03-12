"""
ML Pipeline - Unified Training Entry Point
Train one or all models from the command line.

Usage:
    python -m ml.train --all --epochs 5
    python -m ml.train --model answer_quality --epochs 10
    python -m ml.train --model meta_scorer
"""
import os
import sys
import json
import time
import argparse
import logging

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.config import TrainingConfig
from ml.dataset import generate_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

AVAILABLE_MODELS = [
    "answer_quality",
    "communication",
    "star_analyzer",
    "code_evaluator",
    "meta_scorer",
]


def train_answer_quality(config: TrainingConfig, data_dir: str) -> dict:
    """Train the Technical Answer Quality model."""
    from ml.models.answer_quality import AnswerQualityTrainer

    logger.info("═" * 60)
    logger.info("Training: Answer Quality Model (DeBERTa-v3-small)")
    logger.info("═" * 60)

    data_path = os.path.join(data_dir, "answer_quality.json")
    with open(data_path) as f:
        data = json.load(f)

    # Split 80/20
    split = int(len(data) * 0.8)
    train_data, val_data = data[:split], data[split:]

    trainer = AnswerQualityTrainer(config.answer_quality)
    results = trainer.train(train_data, val_data)
    trainer.save(config.answer_quality.output_dir)

    return results


def train_communication(config: TrainingConfig, data_dir: str) -> dict:
    """Train the Communication Clarity model."""
    from ml.models.communication import CommunicationTrainer

    logger.info("═" * 60)
    logger.info("Training: Communication Clarity Model (DistilBERT)")
    logger.info("═" * 60)

    data_path = os.path.join(data_dir, "communication.json")
    with open(data_path) as f:
        data = json.load(f)

    split = int(len(data) * 0.8)
    train_data, val_data = data[:split], data[split:]

    trainer = CommunicationTrainer(config.communication)
    results = trainer.train(train_data, val_data)
    trainer.save(config.communication.output_dir)

    return results


def train_star_analyzer(config: TrainingConfig, data_dir: str) -> dict:
    """Train the STAR Behavioral Analyzer model."""
    from ml.models.star_analyzer import StarAnalyzerTrainer

    logger.info("═" * 60)
    logger.info("Training: STAR Behavioral Analyzer (DeBERTa-v3-small)")
    logger.info("═" * 60)

    data_path = os.path.join(data_dir, "star_analyzer.json")
    with open(data_path) as f:
        data = json.load(f)

    split = int(len(data) * 0.8)
    train_data, val_data = data[:split], data[split:]

    trainer = StarAnalyzerTrainer(config.star_analyzer)
    results = trainer.train(train_data, val_data)
    trainer.save(config.star_analyzer.output_dir)

    return results


def train_code_evaluator(config: TrainingConfig, data_dir: str) -> dict:
    """Train the Code Quality Evaluator model."""
    from ml.models.code_evaluator import CodeEvaluatorTrainer

    logger.info("═" * 60)
    logger.info("Training: Code Quality Evaluator (CodeBERT)")
    logger.info("═" * 60)

    data_path = os.path.join(data_dir, "code_evaluator.json")
    with open(data_path) as f:
        data = json.load(f)

    split = int(len(data) * 0.8)
    train_data, val_data = data[:split], data[split:]

    trainer = CodeEvaluatorTrainer(config.code_evaluator)
    results = trainer.train(train_data, val_data)
    trainer.save(config.code_evaluator.output_dir)

    return results


def train_meta_scorer(config: TrainingConfig, data_dir: str) -> dict:
    """Train the XGBoost Meta-Scorer."""
    from ml.models.meta_scorer import MetaScorer

    logger.info("═" * 60)
    logger.info("Training: Meta Scorer Aggregator (XGBoost)")
    logger.info("═" * 60)

    data_path = os.path.join(data_dir, "meta_scorer.json")
    with open(data_path) as f:
        data = json.load(f)

    split = int(len(data) * 0.8)
    train_data, val_data = data[:split], data[split:]

    scorer = MetaScorer(config.meta_scorer)
    results = scorer.train(train_data, val_data)
    scorer.save(config.meta_scorer.output_dir)

    # Log feature importance
    importance = scorer.feature_importance()
    if importance:
        logger.info("Feature Importance:")
        for feat, imp in list(importance.items())[:10]:
            logger.info(f"  {feat}: {imp:.4f}")

    return results


TRAINERS = {
    "answer_quality": train_answer_quality,
    "communication": train_communication,
    "star_analyzer": train_star_analyzer,
    "code_evaluator": train_code_evaluator,
    "meta_scorer": train_meta_scorer,
}


def main():
    parser = argparse.ArgumentParser(description="Train ML models for AI Interview Simulator")
    parser.add_argument("--model", type=str, choices=AVAILABLE_MODELS, help="Train a specific model")
    parser.add_argument("--all", action="store_true", help="Train all models")
    parser.add_argument("--epochs", type=int, default=None, help="Override epoch count")
    parser.add_argument("--generate-data", action="store_true", help="Generate training data first")
    parser.add_argument("--data-dir", type=str, default=None, help="Data directory")
    parser.add_argument("--samples", type=int, default=2000, help="Samples per dataset when generating")
    args = parser.parse_args()

    config = TrainingConfig()

    if args.data_dir:
        config.data_dir = args.data_dir

    if args.epochs:
        config.answer_quality.epochs = args.epochs
        config.communication.epochs = args.epochs
        config.star_analyzer.epochs = args.epochs
        config.code_evaluator.epochs = args.epochs

    # Generate data if requested or if data directory doesn't exist
    if args.generate_data or not os.path.exists(config.data_dir):
        logger.info("Generating training datasets...")
        generate_all(config.data_dir, args.samples)

    if not args.model and not args.all:
        parser.print_help()
        print("\n  Specify --model <name> or --all to train models.")
        return

    models_to_train = AVAILABLE_MODELS if args.all else [args.model]
    all_results = {}

    total_start = time.time()
    for model_name in models_to_train:
        start = time.time()
        try:
            results = TRAINERS[model_name](config, config.data_dir)
            elapsed = time.time() - start
            results["training_time_seconds"] = round(elapsed, 2)
            all_results[model_name] = results
            logger.info(f"✓ {model_name} trained in {elapsed:.1f}s")
        except Exception as e:
            logger.error(f"✗ {model_name} failed: {e}")
            all_results[model_name] = {"error": str(e)}

    total_elapsed = time.time() - total_start

    # Save training report
    report = {
        "total_time_seconds": round(total_elapsed, 2),
        "models": all_results,
    }
    report_path = os.path.join(config.model_dir, "training_report.json")
    os.makedirs(config.model_dir, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    logger.info("═" * 60)
    logger.info(f"Training complete! Total time: {total_elapsed:.1f}s")
    logger.info(f"Report saved → {report_path}")
    logger.info("═" * 60)


if __name__ == "__main__":
    main()
