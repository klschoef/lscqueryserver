# Evaluation

This module provides multiple python scripts to evaluate the performance of LifeXplore techniques.

## Examples

### Evaluate clip based models
Multiple steps are required.

1. Get a topic file
   The topic file is a json file with different queries with ids, hints and possible answers. 
   This is needed to evaluate the results.
2. Evaluate with CLIP model
   ```bash
   python3 evaluate-with-clip.py topic_files/lsc-full-topics.json your_faiss_folder --model_name ViT-H-14 --pretrained_name laion2b_s32b_b79k
   ```
3. Get recall@k
    ```bash
    python3 get_recall_at_k.py results/results_ViT-H-14_laion2b_s32b_b79k.json
    ```