"""
ML Model - Technical Answer Quality Scorer
Architecture: DeBERTa-v3-small fine-tuned for regression (Q+A → score 0-10)
"""
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


class AnswerQualityModel(nn.Module):
    """
    DeBERTa-based answer quality regression model.
    Input: concatenated [question] [SEP] [answer]
    Output: quality score (0-10)
    """

    def __init__(self, model_name: str = "microsoft/deberta-v3-small", dropout: float = 0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size

        self.regressor = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 256),
            nn.GELU(),
            nn.LayerNorm(256),
            nn.Dropout(dropout),
            nn.Linear(256, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),  # Output in [0, 1], scale to [0, 10]
        )

    def forward(self, input_ids, attention_mask, **kwargs):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        # Use [CLS] token representation
        cls_output = outputs.last_hidden_state[:, 0, :]
        score = self.regressor(cls_output).squeeze(-1) * 10  # Scale to 0-10
        return score


class AnswerQualityTrainer:
    """Training wrapper for the Answer Quality model."""

    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = AnswerQualityModel(config.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def prepare_data(self, data: list[dict]) -> list[dict]:
        """Tokenize question-answer pairs."""
        encoded = []
        for sample in data:
            text = f"{sample['question']} [SEP] {sample['answer']}"
            tokens = self.tokenizer(
                text,
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            encoded.append({
                "input_ids": tokens["input_ids"].squeeze(0),
                "attention_mask": tokens["attention_mask"].squeeze(0),
                "label": torch.tensor(sample["score"], dtype=torch.float32),
            })
        return encoded

    def train(self, train_data: list[dict], val_data: list[dict] = None):
        """Train the model on prepared data."""
        from torch.utils.data import DataLoader, TensorDataset

        encoded = self.prepare_data(train_data)

        input_ids = torch.stack([e["input_ids"] for e in encoded])
        attention_mask = torch.stack([e["attention_mask"] for e in encoded])
        labels = torch.stack([e["label"] for e in encoded])

        dataset = TensorDataset(input_ids, attention_mask, labels)
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(
            self.model.parameters(),
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay,
        )
        criterion = nn.MSELoss()

        self.model.train()
        for epoch in range(self.config.epochs):
            total_loss = 0
            for batch in loader:
                ids, mask, targets = [b.to(self.device) for b in batch]
                optimizer.zero_grad()
                predictions = self.model(input_ids=ids, attention_mask=mask)
                loss = criterion(predictions, targets)
                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                optimizer.step()
                total_loss += loss.item()

            avg_loss = total_loss / len(loader)
            print(f"  Epoch {epoch+1}/{self.config.epochs} | Loss: {avg_loss:.4f}")

        return {"final_loss": avg_loss}

    def save(self, path: str):
        """Save model and tokenizer."""
        import os
        os.makedirs(path, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(path, "model.pt"))
        self.tokenizer.save_pretrained(path)
        print(f"  Saved → {path}")

    def load(self, path: str):
        """Load model from disk."""
        import os
        self.model.load_state_dict(torch.load(os.path.join(path, "model.pt"), map_location=self.device))
        self.model.eval()
