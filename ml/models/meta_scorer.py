"""
ML Model - Meta Scorer Aggregator
Architecture: XGBoost/LightGBM ensemble that aggregates all model scores into a final assessment.
"""
import os
import json
import pickle
import logging
import numpy as np

logger = logging.getLogger(__name__)


class MetaScorer:
    """
    XGBoost-based meta-model that combines outputs from all specialized models
    into a single final interview score (0-10).

    Features: answer_quality, communication (3), STAR (4), code (3),
              speech metrics (3), difficulty, answer_length = 16 features
    """

    def __init__(self, config):
        self.config = config
        self.model = None
        self.feature_names = config.feature_names

    def train(self, train_data: list[dict], val_data: list[dict] = None):
        """Train the XGBoost meta-model."""
        try:
            from xgboost import XGBRegressor
        except ImportError:
            logger.warning("XGBoost not installed, falling back to sklearn GradientBoosting")
            from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor

        X_train = np.array([[d[f] for f in self.feature_names] for d in train_data])
        y_train = np.array([d["final_score"] for d in train_data])

        try:
            self.model = XGBRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                learning_rate=self.config.learning_rate,
                subsample=self.config.subsample,
                colsample_bytree=self.config.colsample_bytree,
                random_state=42,
                verbosity=1,
            )
        except TypeError:
            # sklearn fallback doesn't have all params
            from sklearn.ensemble import GradientBoostingRegressor
            self.model = GradientBoostingRegressor(
                n_estimators=self.config.n_estimators,
                max_depth=self.config.max_depth,
                learning_rate=self.config.learning_rate,
                subsample=self.config.subsample,
                random_state=42,
            )

        self.model.fit(X_train, y_train)

        # Evaluate
        train_pred = self.model.predict(X_train)
        mse = np.mean((train_pred - y_train) ** 2)
        mae = np.mean(np.abs(train_pred - y_train))

        if val_data:
            X_val = np.array([[d[f] for f in self.feature_names] for d in val_data])
            y_val = np.array([d["final_score"] for d in val_data])
            val_pred = self.model.predict(X_val)
            val_mse = np.mean((val_pred - y_val) ** 2)
            val_mae = np.mean(np.abs(val_pred - y_val))
            print(f"  Train MSE: {mse:.4f} | MAE: {mae:.4f}")
            print(f"  Val   MSE: {val_mse:.4f} | MAE: {val_mae:.4f}")
        else:
            print(f"  Train MSE: {mse:.4f} | MAE: {mae:.4f}")

        return {
            "train_mse": float(mse),
            "train_mae": float(mae),
        }

    def predict(self, features: dict) -> float:
        """Predict final score from feature dictionary."""
        if self.model is None:
            raise RuntimeError("Model not trained or loaded")
        x = np.array([[features.get(f, 0) for f in self.feature_names]])
        score = float(self.model.predict(x)[0])
        return max(0.0, min(10.0, score))

    def feature_importance(self) -> dict:
        """Get feature importance scores."""
        if self.model is None:
            return {}
        try:
            importances = self.model.feature_importances_
        except AttributeError:
            return {}
        return dict(sorted(
            zip(self.feature_names, importances),
            key=lambda x: x[1], reverse=True,
        ))

    def save(self, path: str):
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "model.pkl"), "wb") as f:
            pickle.dump(self.model, f)
        with open(os.path.join(path, "config.json"), "w") as f:
            json.dump({"feature_names": self.feature_names}, f, indent=2)
        print(f"  Saved → {path}")

    def load(self, path: str):
        with open(os.path.join(path, "model.pkl"), "rb") as f:
            self.model = pickle.load(f)
        config_path = os.path.join(path, "config.json")
        if os.path.exists(config_path):
            with open(config_path) as f:
                cfg = json.load(f)
                self.feature_names = cfg.get("feature_names", self.feature_names)
