"""Patch the training notebook to force reload fixed modules."""
import json

path = r'G:\Advanced AI Interview Simulator (Research-Level Project)\ml\02_model_training.ipynb'
with open(path, encoding='utf-8') as f:
    nb = json.load(f)

# Find any cell that already has importlib.reload and update it,
# OR find the cell with AnswerQualityTrainer import and prepend reload
patched = False
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'importlib' in src and 'reload' in src:
            # Replace existing reload cell
            cell['source'] = [
                "# Force reload fixed modules (DebertaV2Tokenizer fix)\n",
                "import importlib\n",
                "import ml.models.answer_quality as _aq_mod\n",
                "import ml.models.star_analyzer as _star_mod\n",
                "importlib.reload(_aq_mod)\n",
                "importlib.reload(_star_mod)\n",
                "from ml.models.answer_quality import AnswerQualityTrainer\n",
                "\n",
                "with open(os.path.join(DATA_DIR, 'answer_quality.json')) as f:\n",
                "    aq_data = json.load(f)\n",
                "\n",
                "split = int(len(aq_data) * 0.8)\n",
                "aq_train, aq_val = aq_data[:split], aq_data[split:]\n",
                "print(f'Train: {len(aq_train)} | Val: {len(aq_val)}')\n",
                "\n",
                "config.answer_quality.epochs = 3\n",
                "config.answer_quality.batch_size = 16\n",
                "\n",
                "print(f'\\nConfig:')\n",
                "print(f'  Model: {config.answer_quality.model_name}')\n",
                "print(f'  Epochs: {config.answer_quality.epochs}')\n",
                "print(f'  LR: {config.answer_quality.learning_rate}')\n",
                "print(f'  Batch: {config.answer_quality.batch_size}')"
            ]
            patched = True
            print(f'Updated reload cell at index {i}')
            break

if not patched:
    # Find the AnswerQualityTrainer import cell
    for i, cell in enumerate(nb['cells']):
        if cell['cell_type'] == 'code':
            src = ''.join(cell['source'])
            if 'AnswerQualityTrainer' in src and 'from' in src:
                # Insert reload lines at top
                reload_lines = [
                    "# Force reload fixed modules (DebertaV2Tokenizer fix)\n",
                    "import importlib\n",
                    "import ml.models.answer_quality as _aq_mod\n", 
                    "import ml.models.star_analyzer as _star_mod\n",
                    "importlib.reload(_aq_mod)\n",
                    "importlib.reload(_star_mod)\n",
                    "\n",
                ]
                cell['source'] = reload_lines + cell['source']
                patched = True
                print(f'Prepended reload to cell {i}')
                break

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print('Done!')
