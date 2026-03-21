"""Patch notebook for CPU-fast training: 500 samples, honor config values."""
import json

path = r'G:\Advanced AI Interview Simulator (Research-Level Project)\ml\02_model_training.ipynb'
with open(path, encoding='utf-8') as f:
    nb = json.load(f)

changes = 0
for i, cell in enumerate(nb['cells']):
    if cell['cell_type'] == 'code':
        new_source = []
        for line in cell['source']:
            # Change sample generation from 2000 to 500
            if 'n_per_dataset=2000' in line:
                line = line.replace('n_per_dataset=2000', 'n_per_dataset=500')
                changes += 1
            # Remove epoch overrides - let config.py values handle it
            if 'config.answer_quality.epochs = 3' in line:
                line = line.replace('config.answer_quality.epochs = 3', '# Using config defaults (epochs=2, max_length=128)')
                changes += 1
            if 'config.answer_quality.batch_size = 16' in line:
                line = line.replace('config.answer_quality.batch_size = 16', '# batch_size=16 from config')
                changes += 1
            if 'config.communication.epochs = 3' in line:
                line = line.replace('config.communication.epochs = 3', '# Using config defaults')
                changes += 1
            if 'config.star_analyzer.epochs = 3' in line:
                line = line.replace('config.star_analyzer.epochs = 3', '# Using config defaults')
                changes += 1
            if 'config.code_evaluator.epochs = 3' in line:
                line = line.replace('config.code_evaluator.epochs = 3', '# Using config defaults')
                changes += 1
            if 'config.code_evaluator.batch_size = 8' in line:
                line = line.replace('config.code_evaluator.batch_size = 8', '# batch_size=4 from config')
                changes += 1
            new_source.append(line)
        cell['source'] = new_source

with open(path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f'Made {changes} changes')
print('Config now: 500 samples, 2 epochs, max_length=128')
