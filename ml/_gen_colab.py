"""Generate a self-contained Google Colab notebook for ML training."""
import json, textwrap

cells = []

def md(src):
    cells.append({"cell_type": "markdown", "metadata": {}, "source": src if isinstance(src, list) else [src]})

def code(src):
    if isinstance(src, str):
        src = src.split("\n")
        src = [line + "\n" for line in src[:-1]] + [src[-1]]
    cells.append({"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": src})

# ═══════════════════════════════════════════════════════════════
# CELL 0: Title
# ═══════════════════════════════════════════════════════════════
md([
    "# \U0001f9e0 AI Interview Simulator — Complete ML Training Pipeline\n",
    "### Self-Contained Google Colab Notebook\n",
    "\n",
    "This notebook is **fully self-contained** — no external files required. It includes:\n",
    "\n",
    "| Step | Description |\n",
    "|------|-------------|\n",
    "| 1 | \U0001f4e6 Install dependencies |\n",
    "| 2 | \U0001f3d7 Define all model architectures inline |\n",
    "| 3 | \U0001f4ca Generate synthetic training datasets |\n",
    "| 4 | \U0001f525 Train 5 models with advanced pipeline |\n",
    "| 5 | \U0001f4c8 Evaluate with professional visualizations |\n",
    "| 6 | \U0001f50d Run live inference demo |\n",
    "\n",
    "**Models:** DeBERTa-v3-small \u00d7 2 \u2022 DistilBERT \u2022 CodeBERT \u2022 XGBoost\n",
    "\n",
    "> \u26a1 **GPU recommended**: Runtime \u2192 Change runtime type \u2192 T4 GPU"
])

# ═══════════════════════════════════════════════════════════════
# CELL 1: Install dependencies
# ═══════════════════════════════════════════════════════════════
code(textwrap.dedent("""\
    !pip install -q torch transformers sentencepiece xgboost scikit-learn seaborn
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\\u2713 PyTorch {torch.__version__} | Device: {device}")
    if device == "cuda":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 1.5: Mount Google Drive
# ═══════════════════════════════════════════════════════════════
code(textwrap.dedent("""\
    from google.colab import drive
    drive.mount('/content/drive')

    DRIVE_DIR = '/content/drive/MyDrive/AI_Interview_ML'
    import os
    os.makedirs(f'{DRIVE_DIR}/models', exist_ok=True)
    os.makedirs(f'{DRIVE_DIR}/figures', exist_ok=True)
    print(f"\\u2713 Drive mounted. Output -> {DRIVE_DIR}")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 2: Imports + Theme
# ═══════════════════════════════════════════════════════════════
code(textwrap.dedent("""\
    import os, json, time, copy, random, pickle, warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.gridspec as gridspec
    import seaborn as sns
    import torch.nn as nn
    from torch.utils.data import DataLoader, TensorDataset
    from transformers import AutoModel, AutoTokenizer, DebertaV2Tokenizer
    from scipy.stats import spearmanr
    warnings.filterwarnings("ignore")

    plt.style.use("dark_background")
    plt.rcParams.update({
        "font.size": 10, "axes.titlesize": 13, "axes.titleweight": "bold",
        "axes.facecolor": "#0a0a0a", "figure.facecolor": "#000000",
        "axes.edgecolor": "#222222", "axes.grid": True, "grid.alpha": 0.08,
        "xtick.color": "#888888", "ytick.color": "#888888",
        "text.color": "#e5e5e7", "axes.labelcolor": "#aaaaaa",
        "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.facecolor": "#000000",
    })

    INDIGO="#6366f1"; CYAN="#22d3ee"; GREEN="#22c55e"; AMBER="#f59e0b"
    ROSE="#f43f5e"; VIOLET="#8b5cf6"; PINK="#ec4899"
    PALETTE = [INDIGO, CYAN, GREEN, AMBER, ROSE, VIOLET, PINK]

    FIG_DIR = "figures"
    os.makedirs(FIG_DIR, exist_ok=True)
    os.makedirs("models", exist_ok=True)

    def save_fig(fig, name):
        fig.savefig(f"{FIG_DIR}/{name}.png", dpi=200, bbox_inches="tight", facecolor="#000000")
        print(f"  \\U0001f4be Saved -> {FIG_DIR}/{name}.png")

    print("\\u2713 All imports loaded")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 3: Dataset Generation
# ═══════════════════════════════════════════════════════════════
md("---\n## 1. \\U0001f4ca Synthetic Dataset Generation")

code(textwrap.dedent("""\
    def _rand(lo, hi): return round(random.uniform(lo, hi), 2)

    TECH_QUESTIONS = [
        "Explain the difference between a process and a thread.",
        "What is a hash table and how does it handle collisions?",
        "Describe the CAP theorem and its implications.",
        "What are the SOLID principles?",
        "Explain how garbage collection works in Python.",
        "What is the difference between TCP and UDP?",
        "Describe database normalization.",
        "Microservices vs monolithic architecture?",
        "Explain Big-O notation with examples.",
        "What is dependency injection?",
        "REST API vs GraphQL?",
        "Explain eventual consistency.",
        "What is a BST and its complexities?",
        "Describe the MVC pattern.",
        "How does Docker work?",
    ]

    def gen_answer_quality(n=500):
        data = []
        for _ in range(n):
            q = random.choice(TECH_QUESTIONS)
            r = random.random()
            if r < 0.6:
                a = ("This is a well-structured technical explanation. " * 3)[:random.randint(80,200)]
                s = _rand(6, 10)
            elif r < 0.85:
                a = ("The concept relates to the topic. " * 2)[:random.randint(40,120)]
                s = _rand(3.5, 6.5)
            else:
                a = "I think its something about that. Not sure."
                s = _rand(0.5, 3.5)
            data.append({"question": q, "answer": a, "score": s})
        return data

    def gen_communication(n=500):
        data = []
        for _ in range(n):
            r = random.random()
            if r < 0.5:
                t = "I'll break it down. First, components interact. Second, real-world usage. Finally, trade-offs."
                c, f, st = _rand(3.5,5), _rand(3.5,5), _rand(3.5,5)
            elif r < 0.8:
                t = "So basically this thing works by doing stuff. It's like important for reasons."
                c, f, st = _rand(2,3.5), _rand(2,3.5), _rand(1.5,3)
            else:
                t = "um yeah so like I think its uh related to like that concept"
                c, f, st = _rand(0.5,2), _rand(0.5,2), _rand(0.5,1.5)
            data.append({"text": t, "clarity": c, "fluency": f, "structure": st})
        return data

    def gen_star(n=500):
        sits = ["behind on deadlines", "critical bug in production", "conflicting requirements"]
        tasks = ["deliver MVP on time", "fix within 24h", "align stakeholders"]
        acts = ["organized standups", "implemented logging", "scheduled meetings"]
        ress = ["shipped 2 days early", "resolved in 8h", "all agreed"]
        data = []
        for _ in range(n):
            r = random.random()
            if r < 0.4:
                t = f"At my company, {random.choice(sits)}. My task was to {random.choice(tasks)}. I {random.choice(acts)} and followed up. Result: {random.choice(ress)}."
                s,tk,a,re = _rand(3.5,5), _rand(3.5,5), _rand(3.5,5), _rand(3.5,5)
            elif r < 0.7:
                t = f"We had {random.choice(sits)}. I needed to {random.choice(tasks)}. Did some stuff. It worked."
                s,tk,a,re = _rand(2,4), _rand(1.5,3.5), _rand(1,3), _rand(0.5,2.5)
            else:
                t = "I'm good at teamwork and solving problems."
                s,tk,a,re = _rand(0.5,1.5), _rand(0.5,1.5), _rand(0.5,1.5), _rand(0.5,1.5)
            data.append({"text": t, "situation_score": s, "task_score": tk, "action_score": a, "result_score": re})
        return data

    GOOD_CODE = [
        "def two_sum(nums, target):\\n    seen = {}\\n    for i, num in enumerate(nums):\\n        c = target - num\\n        if c in seen: return [seen[c], i]\\n        seen[num] = i\\n    return []",
        "def is_valid(s):\\n    stack, pairs = [], {')':'(','}':'{',']':'['}\\n    for c in s:\\n        if c in pairs.values(): stack.append(c)\\n        elif c in pairs:\\n            if not stack or stack[-1]!=pairs[c]: return False\\n            stack.pop()\\n    return not stack",
    ]
    POOR_CODE = [
        "def two_sum(nums, t):\\n    for i in range(len(nums)):\\n        for j in range(len(nums)):\\n            if nums[i]+nums[j]==t: return [i,j]",
        "def maxsub(n):\\n    m=-9999999\\n    for i in range(len(n)):\\n        for j in range(i,len(n)):\\n            s=sum(n[i:j+1])\\n            if s>m: m=s\\n    return m",
    ]

    def gen_code_eval(n=375):
        data = []
        for _ in range(n):
            r = random.random()
            if r < 0.5:
                code = random.choice(GOOD_CODE); q,e,s = _rand(3.5,5), _rand(3.5,5), _rand(3.5,5)
            elif r < 0.8:
                code = random.choice(POOR_CODE); q,e,s = _rand(1,3), _rand(0.5,2.5), _rand(1,3)
            else:
                code = "pass # TODO"; q,e,s = _rand(0.5,1.5), _rand(0.5,1), _rand(0.5,1.5)
            data.append({"code": code, "quality": q, "efficiency": e, "style": s})
        return data

    def gen_meta(n=750):
        data = []
        for _ in range(n):
            aq=_rand(1,10); cc,cf,cs=_rand(.5,5),_rand(.5,5),_rand(.5,5)
            ss,st,sa,sr=_rand(.5,5),_rand(.5,5),_rand(.5,5),_rand(.5,5)
            cq,ce,cst=_rand(.5,5),_rand(.5,5),_rand(.5,5)
            wpm=_rand(80,200); conf=_rand(.2,1); filler=_rand(0,.15)
            diff=random.choice([1,2,3,4]); al=_rand(.1,1)
            final = aq*0.25 + ((cc+cf+cs)/3)*0.15 + ((ss+st+sa+sr)/4)*0.15 + ((cq+ce+cst)/3)*0.15 + conf*2*0.10 + (1-filler*5)*0.05 + (min(wpm,160)/160)*0.05 + al*0.10
            final = max(0.5, min(10.0, round(final + _rand(-0.5,0.5), 2)))
            data.append({"answer_quality_score":aq,"communication_clarity":cc,"communication_fluency":cf,
                "communication_structure":cs,"star_situation":ss,"star_task":st,"star_action":sa,
                "star_result":sr,"code_quality":cq,"code_efficiency":ce,"code_style":cst,
                "speech_wpm":wpm,"speech_confidence":conf,"speech_filler_ratio":filler,
                "question_difficulty_numeric":diff,"answer_length_normalized":al,"final_score":final})
        return data

    # Generate all datasets
    random.seed(42)
    aq_data = gen_answer_quality(5000)
    comm_data = gen_communication(5000)
    star_data = gen_star(5000)
    code_data = gen_code_eval(3000)
    meta_data = gen_meta(8000)

    print(f"\\u2713 Answer Quality:  {len(aq_data)} samples")
    print(f"\\u2713 Communication:   {len(comm_data)} samples")
    print(f"\\u2713 STAR Analyzer:   {len(star_data)} samples")
    print(f"\\u2713 Code Evaluator:  {len(code_data)} samples")
    print(f"\\u2713 Meta Scorer:     {len(meta_data)} samples")
    print(f"\\u2713 Total:           {len(aq_data)+len(comm_data)+len(star_data)+len(code_data)+len(meta_data)} samples")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 4: Model Definitions
# ═══════════════════════════════════════════════════════════════
md("---\n## 2. \\U0001f3d7 Model Architectures\nAll 5 model classes defined inline — DeBERTa, DistilBERT, CodeBERT, XGBoost.")

code(textwrap.dedent("""\
    # ━━━ Model 1: Answer Quality (DeBERTa-v3-small) ━━━
    class AnswerQualityModel(nn.Module):
        def __init__(self, model_name="microsoft/deberta-v3-small", dropout=0.1):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(model_name)
            h = self.encoder.config.hidden_size
            self.regressor = nn.Sequential(
                nn.Dropout(dropout), nn.Linear(h, 256), nn.GELU(), nn.LayerNorm(256),
                nn.Dropout(dropout), nn.Linear(256, 64), nn.GELU(), nn.Linear(64, 1), nn.Sigmoid())
        def forward(self, input_ids, attention_mask, **kw):
            cls = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0, :].float()
            return self.regressor(cls).squeeze(-1) * 10

    # ━━━ Model 2: Communication (DistilBERT) ━━━
    class CommunicationModel(nn.Module):
        def __init__(self, model_name="distilbert-base-uncased", dropout=0.1):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(model_name)
            h = self.encoder.config.hidden_size
            self.shared = nn.Sequential(nn.Dropout(dropout), nn.Linear(h, 256), nn.GELU(), nn.LayerNorm(256))
            self.clarity = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.fluency = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.structure = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
        def forward(self, input_ids, attention_mask, **kw):
            s = self.shared(self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0, :].float())
            return torch.stack([self.clarity(s).squeeze(-1)*5, self.fluency(s).squeeze(-1)*5, self.structure(s).squeeze(-1)*5], dim=-1)

    # ━━━ Model 3: STAR Analyzer (DeBERTa-v3-small) ━━━
    class StarAnalyzerModel(nn.Module):
        def __init__(self, model_name="microsoft/deberta-v3-small", dropout=0.1):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(model_name)
            h = self.encoder.config.hidden_size
            self.shared = nn.Sequential(nn.Dropout(dropout), nn.Linear(h, 256), nn.GELU(), nn.LayerNorm(256), nn.Dropout(dropout/2))
            self.sit = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.task = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.act = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.res = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
        def forward(self, input_ids, attention_mask, **kw):
            s = self.shared(self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0, :].float())
            return torch.stack([self.sit(s).squeeze(-1)*5, self.task(s).squeeze(-1)*5, self.act(s).squeeze(-1)*5, self.res(s).squeeze(-1)*5], dim=-1)

    # ━━━ Model 4: Code Evaluator (CodeBERT) ━━━
    class CodeEvaluatorModel(nn.Module):
        def __init__(self, model_name="microsoft/codebert-base", dropout=0.15):
            super().__init__()
            self.encoder = AutoModel.from_pretrained(model_name)
            h = self.encoder.config.hidden_size
            self.shared = nn.Sequential(nn.Dropout(dropout), nn.Linear(h, 256), nn.GELU(), nn.LayerNorm(256), nn.Dropout(dropout/2))
            self.quality = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.efficiency = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
            self.style = nn.Sequential(nn.Linear(256,64), nn.GELU(), nn.Linear(64,1), nn.Sigmoid())
        def forward(self, input_ids, attention_mask, **kw):
            s = self.shared(self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state[:, 0, :].float())
            return torch.stack([self.quality(s).squeeze(-1)*5, self.efficiency(s).squeeze(-1)*5, self.style(s).squeeze(-1)*5], dim=-1)

    print("\\u2713 All 4 transformer model classes defined")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 5: Training Engine
# ═══════════════════════════════════════════════════════════════
md("---\n## 3. \\U0001f527 Advanced Training Engine\nWarmup + cosine LR, early stopping, per-epoch validation, metric tracking.")

code(textwrap.dedent("""\
    class AdvancedTrainer:
        def __init__(self, model, device):
            self.model = model
            self.device = device
            self.history = {"train_loss": [], "val_loss": [], "lr": []}
            self.best_val_loss = float("inf")
            self.best_state = None

        def _scheduler(self, optimizer, total_steps, warmup=0.1):
            nw = int(total_steps * warmup)
            def lr_fn(step):
                if step < nw: return float(step) / max(1, nw)
                prog = float(step - nw) / max(1, total_steps - nw)
                return max(0.0, 0.5 * (1.0 + np.cos(np.pi * prog)))
            return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_fn)

        def train(self, train_dl, val_dl, epochs=2, lr=2e-5, patience=3):
            opt = torch.optim.AdamW(self.model.parameters(), lr=lr, weight_decay=0.01)
            sched = self._scheduler(opt, len(train_dl) * epochs)
            crit = nn.MSELoss()
            wait = 0
            for ep in range(epochs):
                self.model.train()
                tl = 0
                for ids, mask, tgt in train_dl:
                    ids, mask, tgt = ids.to(self.device), mask.to(self.device), tgt.to(self.device)
                    opt.zero_grad()
                    loss = crit(self.model(input_ids=ids, attention_mask=mask), tgt)
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(self.model.parameters(), 1.0)
                    opt.step(); sched.step()
                    tl += loss.item()
                tl /= len(train_dl)
                self.model.eval()
                vl = 0
                with torch.no_grad():
                    for ids, mask, tgt in val_dl:
                        ids, mask, tgt = ids.to(self.device), mask.to(self.device), tgt.to(self.device)
                        vl += crit(self.model(input_ids=ids, attention_mask=mask), tgt).item()
                vl /= len(val_dl)
                cur_lr = sched.get_last_lr()[0]
                self.history["train_loss"].append(tl)
                self.history["val_loss"].append(vl)
                self.history["lr"].append(cur_lr)
                tag = "\\u2b06"
                if vl < self.best_val_loss:
                    self.best_val_loss = vl
                    self.best_state = copy.deepcopy(self.model.state_dict())
                    wait = 0; tag = "\\u2b07 \\u2713 best"
                else: wait += 1
                print(f"  Epoch {ep+1}/{epochs} | Train: {tl:.4f} | Val: {vl:.4f} | LR: {cur_lr:.2e} | {tag}")
                if wait >= patience:
                    print(f"  \\u26a0 Early stop at epoch {ep+1}"); break
            if self.best_state: self.model.load_state_dict(self.best_state)
            return self.history

    def prep_data(tokenizer, data, text_key, label_keys, max_len=128, pair_key=None):
        ids_l, mask_l, lab_l = [], [], []
        for s in data:
            text = f"{s[pair_key]} [SEP] {s[text_key]}" if pair_key else s[text_key]
            tok = tokenizer(text, max_length=max_len, padding="max_length", truncation=True, return_tensors="pt")
            ids_l.append(tok["input_ids"].squeeze(0))
            mask_l.append(tok["attention_mask"].squeeze(0))
            labs = [s[k] for k in label_keys] if isinstance(label_keys, list) else [s[label_keys]]
            lab_l.append(torch.tensor(labs, dtype=torch.float32))
        ds = TensorDataset(torch.stack(ids_l), torch.stack(mask_l), torch.stack(lab_l))
        n = len(ds); vn = int(n * 0.2)
        tr, va = torch.utils.data.random_split(ds, [n-vn, vn])
        return DataLoader(tr, batch_size=16, shuffle=True), DataLoader(va, batch_size=16)

    def evaluate(model, val_dl, device):
        model.eval()
        preds, trues = [], []
        with torch.no_grad():
            for ids, mask, tgt in val_dl:
                p = model(input_ids=ids.to(device), attention_mask=mask.to(device))
                p_np = p.cpu().numpy()
                if p_np.ndim == 1: p_np = p_np.reshape(-1, 1)
                t_np = tgt.numpy()
                if t_np.ndim == 1: t_np = t_np.reshape(-1, 1)
                preds.append(p_np); trues.append(t_np)
        return np.vstack(preds), np.vstack(trues)

    def metrics_table(preds, trues, names):
        rows = []
        for i, n in enumerate(names):
            p, t = preds[:,i], trues[:,i]
            mse = np.mean((p-t)**2); mae = np.mean(np.abs(p-t))
            ss_r, ss_t = np.sum((t-p)**2), np.sum((t-t.mean())**2)
            r2 = 1 - ss_r/ss_t if ss_t > 0 else 0
            rho, _ = spearmanr(p, t)
            rows.append({"Dim": n, "MSE": f"{mse:.4f}", "MAE": f"{mae:.4f}", "R2": f"{r2:.4f}", "Spearman": f"{rho:.4f}"})
        return pd.DataFrame(rows)

    def plot_curves(h, name, color=INDIGO):
        fig, ax = plt.subplots(1, 2, figsize=(14, 4))
        fig.suptitle(f"{name} — Training Curves", fontsize=14, fontweight="bold", color="white")
        ep = range(1, len(h["train_loss"])+1)
        ax[0].plot(ep, h["train_loss"], "o-", color=color, lw=2, label="Train")
        ax[0].plot(ep, h["val_loss"], "s--", color=ROSE, lw=2, label="Val")
        ax[0].legend(frameon=False); ax[0].set_title("Loss Curve")
        ax[1].plot(ep, [lr*1e5 for lr in h["lr"]], "o-", color=AMBER, lw=2)
        ax[1].set_title("LR Schedule (x1e-5)")
        plt.tight_layout(); return fig

    def plot_preds(preds, trues, names, title, colors=None, mx=5):
        n = len(names); fig, axes = plt.subplots(1, n, figsize=(6*n, 5))
        if n == 1: axes = [axes]
        fig.suptitle(f"{title} — Pred vs True", fontsize=14, fontweight="bold", color="white", y=1.02)
        colors = colors or PALETTE
        for i, (nm, ax) in enumerate(zip(names, axes)):
            p, t = preds[:,i], trues[:,i]
            ax.scatter(t, p, alpha=0.4, s=15, c=colors[i%len(colors)], edgecolors="none")
            ax.plot([0, mx], [0, mx], "--", color=ROSE, alpha=0.6)
            z = np.polyfit(t, p, 1); ax.plot(np.linspace(t.min(),t.max(),50), np.poly1d(z)(np.linspace(t.min(),t.max(),50)), color="white", lw=1.5, alpha=0.7)
            r2 = 1 - np.sum((t-p)**2)/max(np.sum((t-t.mean())**2),1e-8)
            rho, _ = spearmanr(p, t)
            ax.set_title(f"{nm}\\nMSE={np.mean((p-t)**2):.3f} | R\\u00b2={r2:.3f} | \\u03c1={rho:.3f}")
            ax.set_xlabel("True"); ax.set_ylabel("Predicted")
        plt.tight_layout(); return fig

    print("\\u2713 Training engine + evaluation helpers ready")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 6-9: Train Model 1 - Answer Quality
# ═══════════════════════════════════════════════════════════════
md("---\n## 4. \\U0001f4dd Train: Answer Quality (DeBERTa-v3-small)\n`question [SEP] answer` \\u2192 score 0-10")

code(textwrap.dedent("""\
    print("\\u2501" * 60)
    print("  MODEL 1: Answer Quality (DeBERTa-v3-small)")
    print("\\u2501" * 60)

    tok_aq = DebertaV2Tokenizer.from_pretrained("microsoft/deberta-v3-small")
    model_aq = AnswerQualityModel().float().to(device)  # .float() prevents NaN on T4 FP16
    train_aq, val_aq = prep_data(tok_aq, aq_data, "answer", "score", max_len=256, pair_key="question")
    print(f"  Train batches: {len(train_aq)} | Val batches: {len(val_aq)}")

    trainer_aq = AdvancedTrainer(model_aq, device)
    t0 = time.time()
    hist_aq = trainer_aq.train(train_aq, val_aq, epochs=10, lr=2e-5)
    print(f"\\n\\u2713 Done in {time.time()-t0:.1f}s | Best val: {trainer_aq.best_val_loss:.4f}")

    torch.save(model_aq.state_dict(), "models/answer_quality.pt")
    tok_aq.save_pretrained("models/answer_quality_tok")
    print("  Saved -> models/answer_quality.pt")"""))

code(textwrap.dedent("""\
    p_aq, t_aq = evaluate(model_aq, val_aq, device)
    print(metrics_table(p_aq, t_aq, ["Score (0-10)"]))
    fig = plot_curves(hist_aq, "Answer Quality", INDIGO); save_fig(fig, "train_01_aq_curves"); plt.show()
    fig = plot_preds(p_aq, t_aq, ["Score"], "Answer Quality", [INDIGO], mx=10); save_fig(fig, "train_02_aq_preds"); plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# CELL 10-11: Train Model 2 - Communication
# ═══════════════════════════════════════════════════════════════
md("---\n## 5. \\U0001f5e3\\ufe0f Train: Communication (DistilBERT)\nAnswer text \\u2192 clarity / fluency / structure (0-5)")

code(textwrap.dedent("""\
    print("\\u2501" * 60)
    print("  MODEL 2: Communication Clarity (DistilBERT)")
    print("\\u2501" * 60)

    tok_comm = AutoTokenizer.from_pretrained("distilbert-base-uncased")
    model_comm = CommunicationModel().to(device)
    train_comm, val_comm = prep_data(tok_comm, comm_data, "text", ["clarity","fluency","structure"], max_len=256)

    trainer_comm = AdvancedTrainer(model_comm, device)
    t0 = time.time()
    hist_comm = trainer_comm.train(train_comm, val_comm, epochs=10, lr=3e-5)
    print(f"\\n\\u2713 Done in {time.time()-t0:.1f}s")

    torch.save(model_comm.state_dict(), "models/communication.pt")
    tok_comm.save_pretrained("models/communication_tok")"""))

code(textwrap.dedent("""\
    p_co, t_co = evaluate(model_comm, val_comm, device)
    print(metrics_table(p_co, t_co, ["Clarity","Fluency","Structure"]))
    fig = plot_curves(hist_comm, "Communication", CYAN); save_fig(fig, "train_03_comm_curves"); plt.show()
    fig = plot_preds(p_co, t_co, ["Clarity","Fluency","Structure"], "Communication", [CYAN,GREEN,AMBER]); save_fig(fig, "train_04_comm_preds"); plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# CELL 12-13: Train Model 3 - STAR
# ═══════════════════════════════════════════════════════════════
md("---\n## 6. \\u2b50 Train: STAR Analyzer (DeBERTa-v3-small)\nBehavioral answer \\u2192 S/T/A/R scores (0-5)")

code(textwrap.dedent("""\
    print("\\u2501" * 60)
    print("  MODEL 3: STAR Behavioral Analyzer (DeBERTa)")
    print("\\u2501" * 60)

    tok_star = DebertaV2Tokenizer.from_pretrained("microsoft/deberta-v3-small")
    model_star = StarAnalyzerModel().float().to(device)  # .float() prevents NaN on T4 FP16
    train_star, val_star = prep_data(tok_star, star_data, "text", ["situation_score","task_score","action_score","result_score"], max_len=256)

    trainer_star = AdvancedTrainer(model_star, device)
    t0 = time.time()
    hist_star = trainer_star.train(train_star, val_star, epochs=10, lr=2e-5)
    print(f"\\n\\u2713 Done in {time.time()-t0:.1f}s")

    torch.save(model_star.state_dict(), "models/star_analyzer.pt")
    tok_star.save_pretrained("models/star_tok")"""))

code(textwrap.dedent("""\
    p_st, t_st = evaluate(model_star, val_star, device)
    print(metrics_table(p_st, t_st, ["Situation","Task","Action","Result"]))
    fig = plot_curves(hist_star, "STAR Analyzer", VIOLET); save_fig(fig, "train_05_star_curves"); plt.show()
    fig = plot_preds(p_st, t_st, ["Situation","Task","Action","Result"], "STAR", ["#3b82f6",VIOLET,GREEN,AMBER]); save_fig(fig, "train_06_star_preds"); plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# CELL 14-15: Train Model 4 - Code Evaluator
# ═══════════════════════════════════════════════════════════════
md("---\n## 7. \\U0001f4bb Train: Code Evaluator (CodeBERT)\nSource code \\u2192 quality / efficiency / style (0-5)")

code(textwrap.dedent("""\
    print("\\u2501" * 60)
    print("  MODEL 4: Code Evaluator (CodeBERT)")
    print("\\u2501" * 60)

    tok_code = AutoTokenizer.from_pretrained("microsoft/codebert-base")
    model_code = CodeEvaluatorModel().to(device)
    train_code, val_code = prep_data(tok_code, code_data, "code", ["quality","efficiency","style"], max_len=256)

    trainer_code = AdvancedTrainer(model_code, device)
    t0 = time.time()
    hist_code = trainer_code.train(train_code, val_code, epochs=10, lr=2e-5)
    print(f"\\n\\u2713 Done in {time.time()-t0:.1f}s")

    torch.save(model_code.state_dict(), "models/code_evaluator.pt")
    tok_code.save_pretrained("models/code_tok")"""))

code(textwrap.dedent("""\
    p_cd, t_cd = evaluate(model_code, val_code, device)
    print(metrics_table(p_cd, t_cd, ["Quality","Efficiency","Style"]))
    fig = plot_curves(hist_code, "Code Evaluator", PINK); save_fig(fig, "train_07_code_curves"); plt.show()
    fig = plot_preds(p_cd, t_cd, ["Quality","Efficiency","Style"], "Code Evaluator", [CYAN,GREEN,PINK]); save_fig(fig, "train_08_code_preds"); plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# CELL 16-17: Train Model 5 - Meta Scorer
# ═══════════════════════════════════════════════════════════════
md("---\n## 8. \\U0001f3af Train: Meta Scorer (XGBoost)\n16-feature vector \\u2192 final score (0-10)")

code(textwrap.dedent("""\
    print("\\u2501" * 60)
    print("  MODEL 5: Meta Scorer (XGBoost)")
    print("\\u2501" * 60)

    try:
        from xgboost import XGBRegressor
    except ImportError:
        from sklearn.ensemble import GradientBoostingRegressor as XGBRegressor

    FEAT_NAMES = ["answer_quality_score","communication_clarity","communication_fluency","communication_structure",
        "star_situation","star_task","star_action","star_result","code_quality","code_efficiency","code_style",
        "speech_wpm","speech_confidence","speech_filler_ratio","question_difficulty_numeric","answer_length_normalized"]

    split = int(len(meta_data) * 0.8)
    meta_tr, meta_va = meta_data[:split], meta_data[split:]
    X_tr = np.array([[d[f] for f in FEAT_NAMES] for d in meta_tr])
    y_tr = np.array([d["final_score"] for d in meta_tr])
    X_va = np.array([[d[f] for f in FEAT_NAMES] for d in meta_va])
    y_va = np.array([d["final_score"] for d in meta_va])

    t0 = time.time()
    try:
        xgb_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.8, colsample_bytree=0.8, random_state=42, verbosity=0)
    except TypeError:
        xgb_model = XGBRegressor(n_estimators=200, max_depth=6, learning_rate=0.1, subsample=0.8, random_state=42)
    xgb_model.fit(X_tr, y_tr)
    elapsed = time.time() - t0

    tr_pred = xgb_model.predict(X_tr)
    va_pred = xgb_model.predict(X_va)
    print(f"  Train MSE: {np.mean((tr_pred-y_tr)**2):.4f}")
    print(f"  Val   MSE: {np.mean((va_pred-y_va)**2):.4f}")
    print(f"\\n\\u2713 Done in {elapsed:.1f}s")

    with open("models/meta_scorer.pkl", "wb") as f:
        pickle.dump(xgb_model, f)
    print("  Saved -> models/meta_scorer.pkl")"""))

code(textwrap.dedent("""\
    mse_m = np.mean((va_pred-y_va)**2); mae_m = np.mean(np.abs(va_pred-y_va))
    r2_m = 1 - np.sum((y_va-va_pred)**2)/np.sum((y_va-y_va.mean())**2)
    rho_m, _ = spearmanr(va_pred, y_va)
    print(f"\\U0001f4ca Meta: MSE={mse_m:.4f} | MAE={mae_m:.4f} | R\\u00b2={r2_m:.4f} | \\u03c1={rho_m:.4f}")

    try: importances = xgb_model.feature_importances_
    except: importances = np.zeros(len(FEAT_NAMES))
    fig, axes = plt.subplots(1, 2, figsize=(16, 5))
    fig.suptitle("Meta Scorer (XGBoost)", fontsize=14, fontweight="bold", color="white", y=1.02)
    si = np.argsort(importances)
    axes[0].barh([FEAT_NAMES[i].replace("_"," ").title() for i in si], importances[si], color=INDIGO, edgecolor="none")
    axes[0].set_title("Feature Importance")
    axes[1].scatter(y_va, va_pred, alpha=0.4, s=10, c=VIOLET, edgecolors="none")
    axes[1].plot([0,10],[0,10], "--", color=ROSE, alpha=0.6)
    axes[1].set_title(f"Pred vs True | R\\u00b2={r2_m:.3f}")
    axes[1].set_xlabel("True"); axes[1].set_ylabel("Predicted")
    plt.tight_layout(); save_fig(fig, "train_09_meta_eval"); plt.show()"""))

# ═══════════════════════════════════════════════════════════════
# CELL 18: Final Dashboard
# ═══════════════════════════════════════════════════════════════
md("---\n## 9. \\U0001f3c6 Final Model Comparison Dashboard")

code(textwrap.dedent("""\
    m_aq = metrics_table(p_aq, t_aq, ["Score"]).assign(Model="Answer Quality")
    m_co = metrics_table(p_co, t_co, ["Clarity","Fluency","Structure"]).assign(Model="Communication")
    m_st = metrics_table(p_st, t_st, ["Situation","Task","Action","Result"]).assign(Model="STAR")
    m_cd = metrics_table(p_cd, t_cd, ["Quality","Efficiency","Style"]).assign(Model="Code Evaluator")
    m_me = pd.DataFrame([{"Dim":"Final Score","MSE":f"{mse_m:.4f}","MAE":f"{mae_m:.4f}","R2":f"{r2_m:.4f}","Spearman":f"{rho_m:.4f}","Model":"Meta Scorer"}])
    all_m = pd.concat([m_aq, m_co, m_st, m_cd, m_me], ignore_index=True)
    print("\\n" + "\\u2550" * 85)
    print("  \\U0001f3c6 FINAL TRAINING REPORT")
    print("\\u2550" * 85)
    print(all_m.to_string(index=False))
    print("\\u2550" * 85)

    print(f"\\n\\U0001f4be Saved figures:")
    for f in sorted(os.listdir(FIG_DIR)):
        if f.endswith(".png"):
            print(f"  {f} ({os.path.getsize(f'{FIG_DIR}/{f}')/1024:.0f} KB)")

    print(f"\\n\\U0001f4be Saved models:")
    for f in sorted(os.listdir("models")):
        sz = os.path.getsize(f"models/{f}")
        if os.path.isdir(f"models/{f}"):
            sz = sum(os.path.getsize(f"models/{f}/{x}") for x in os.listdir(f"models/{f}"))
        print(f"  {f} ({sz/1024/1024:.1f} MB)")"""))

# ═══════════════════════════════════════════════════════════════
# CELL 19: Inference Demo
# ═══════════════════════════════════════════════════════════════
md("---\n## 10. \\U0001f50d Live Inference Demo")

code(textwrap.dedent("""\
    print("\\U0001f52e Sample Predictions:")
    print("\\u2500" * 60)

    model_aq.eval()
    for label, ans in [("Good", "A hash table maps keys to values using a hash function with O(1) avg lookup."),
                       ("Bad", "Its like a table thing I guess.")]:
        tok = tok_aq(f"What is a hash table? [SEP] {ans}", max_length=128, padding="max_length", truncation=True, return_tensors="pt")
        with torch.no_grad():
            sc = model_aq(**{k:v.to(device) for k,v in tok.items()}).item()
        print(f"  Answer Quality ({label}): {sc:.2f}/10")

    model_comm.eval()
    tok = tok_comm("I'll break it down into clear parts. First the concept, then the application.", max_length=128, padding="max_length", truncation=True, return_tensors="pt")
    with torch.no_grad():
        cs = model_comm(**{k:v.to(device) for k,v in tok.items()}).squeeze(0).cpu().numpy()
    print(f"\\n  Communication: Clarity={cs[0]:.2f} Fluency={cs[1]:.2f} Structure={cs[2]:.2f}")

    model_star.eval()
    tok = tok_star("At my company, we had a production outage. I was tasked with leading response. I set up monitoring. We resolved in 2h.", max_length=128, padding="max_length", truncation=True, return_tensors="pt")
    with torch.no_grad():
        ss = model_star(**{k:v.to(device) for k,v in tok.items()}).squeeze(0).cpu().numpy()
    print(f"  STAR: S={ss[0]:.2f} T={ss[1]:.2f} A={ss[2]:.2f} R={ss[3]:.2f}")

    feats = {k: 4.0 for k in FEAT_NAMES}
    feats["answer_quality_score"] = 8.0; feats["speech_wpm"] = 140; feats["speech_confidence"] = 0.85
    x = np.array([[feats[f] for f in FEAT_NAMES]])
    print(f"\\n  \\U0001f3af Meta Score: {xgb_model.predict(x)[0]:.2f}/10")

    print("\\n\\u2713 All models trained, evaluated, and tested!")"""))

# ═══════════════════════════════════════════════════════════════
# CELL: Save to Google Drive
# ═══════════════════════════════════════════════════════════════
md("---\n## 11. \\U0001f4be Save to Google Drive")

code(textwrap.dedent("""\
    import shutil

    # Copy models to Drive
    for item in os.listdir('models'):
        src = f'models/{item}'
        dst = f'{DRIVE_DIR}/models/{item}'
        if os.path.isdir(src):
            if os.path.exists(dst): shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        sz = os.path.getsize(src) if os.path.isfile(src) else sum(
            os.path.getsize(f'{src}/{f}') for f in os.listdir(src))
        print(f"  \\u2713 models/{item} -> Drive ({sz/1024/1024:.1f} MB)")

    # Copy figures to Drive
    for item in os.listdir('figures'):
        if item.endswith('.png'):
            shutil.copy2(f'figures/{item}', f'{DRIVE_DIR}/figures/{item}')
            print(f"  \\u2713 figures/{item} -> Drive")

    print(f"\\n\\U0001f389 All saved to Google Drive: {DRIVE_DIR}")
    print(f"  Models: {DRIVE_DIR}/models/")
    print(f"  Figures: {DRIVE_DIR}/figures/")"""))

# ═══════════════════════════════════════════════════════════════
# Write notebook
# ═══════════════════════════════════════════════════════════════
nb = {
    "cells": cells,
    "metadata": {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10.0"},
        "colab": {"provenance": [], "gpuType": "T4"},
        "accelerator": "GPU"
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

path = r"G:\Advanced AI Interview Simulator (Research-Level Project)\ml\colab_training.ipynb"
with open(path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f"Written {len(cells)} cells to {path}")
