"""
ML Model - Communication Clarity Scorer
Architecture: DistilBERT fine-tuned for multi-output regression (text → clarity/fluency/structure)
"""
import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer


class CommunicationModel(nn.Module):
    """
    DistilBERT-based communication scorer.
    Input: answer text
    Output: 3 scores (clarity, fluency, structure) each 0-5
    """

    def __init__(self, model_name: str = "distilbert-base-uncased", dropout: float = 0.1):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(model_name)
        hidden_size = self.encoder.config.hidden_size  # 768 for distilbert

        self.shared_layer = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(hidden_size, 256),
            nn.GELU(),
            nn.LayerNorm(256),
        )

        # Separate heads for each dimension
        self.clarity_head = nn.Sequential(nn.Linear(256, 64), nn.GELU(), nn.Linear(64, 1), nn.Sigmoid())
        self.fluency_head = nn.Sequential(nn.Linear(256, 64), nn.GELU(), nn.Linear(64, 1), nn.Sigmoid())
        self.structure_head = nn.Sequential(nn.Linear(256, 64), nn.GELU(), nn.Linear(64, 1), nn.Sigmoid())

    def forward(self, input_ids, attention_mask, **kwargs):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        cls_output = outputs.last_hidden_state[:, 0, :]
        shared = self.shared_layer(cls_output)

        clarity = self.clarity_head(shared).squeeze(-1) * 5
        fluency = self.fluency_head(shared).squeeze(-1) * 5
        structure = self.structure_head(shared).squeeze(-1) * 5

        return torch.stack([clarity, fluency, structure], dim=-1)  # (batch, 3)


class CommunicationTrainer:
    """Training wrapper for the Communication model."""

    def __init__(self, config):
        self.config = config
        self.tokenizer = AutoTokenizer.from_pretrained(config.model_name)
        self.model = CommunicationModel(config.model_name)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def prepare_data(self, data: list[dict]) -> list[dict]:
        encoded = []
        for sample in data:
            tokens = self.tokenizer(
                sample["text"],
                max_length=self.config.max_length,
                padding="max_length",
                truncation=True,
                return_tensors="pt",
            )
            encoded.append({
                "input_ids": tokens["input_ids"].squeeze(0),
                "attention_mask": tokens["attention_mask"].squeeze(0),
                "labels": torch.tensor(
                    [sample["clarity"], sample["fluency"], sample["structure"]],
                    dtype=torch.float32,
                ),
            })
        return encoded

    def train(self, train_data: list[dict], val_data: list[dict] = None):
        from torch.utils.data import DataLoader, TensorDataset

        encoded = self.prepare_data(train_data)
        input_ids = torch.stack([e["input_ids"] for e in encoded])
        attention_mask = torch.stack([e["attention_mask"] for e in encoded])
        labels = torch.stack([e["labels"] for e in encoded])

        dataset = TensorDataset(input_ids, attention_mask, labels)
        loader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)

        optimizer = torch.optim.AdamW(
            self.model.parameters(), lr=self.config.learning_rate, weight_decay=self.config.weight_decay
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
        import os
        os.makedirs(path, exist_ok=True)
        torch.save(self.model.state_dict(), os.path.join(path, "model.pt"))
        self.tokenizer.save_pretrained(path)
        print(f"  Saved → {path}")

    def load(self, path: str):
        import os
        self.model.load_state_dict(torch.load(os.path.join(path, "model.pt"), map_location=self.device))
        self.model.eval()
