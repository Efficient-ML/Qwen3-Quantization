
# AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration (Qwen3)

## Installation Setup

1. Clone the AWQ repository and navigate to the AWQ folder
```bash
git clone https://github.com/mit-han-lab/llm-awq
cd llm-awq
```

2. Install required packages
```bash
conda create -n awq python=3.10 -y
conda activate awq
pip install --upgrade pip  # enable PEP 660 support
pip install -e .
```

## File Replacement

Before starting quantization, you need to replace some files to support the Qwen3 model:

1. **Add eval_my directory**: Place the eval_my directory at the same level as the llm-awq folder.

2. **Replace entry.py file**: Replace the file at llm-awq/awq/entry.py with our modified version. Make sure to modify line 271 to use your absolute path.

3. **Replace quantize files**: Replace the following files with our versions:
   - llm-awq/awq/quantize/pre_quant.py
   - llm-awq/awq/quantize/quantizer.py

## Quantization and Evaluation

### Group-wise Quantization

#### 1. Perform AWQ search and save results
```bash
CUDA_VISIBLE_DEVICES=0 python -m awq.entry --model_path /Path/to/Qwen3/Qwen3-32B \
    --w_bit 4 --q_group_size 128 \
    --run_awq --dump_awq awq_cache/qwen3-32b-w4-g128.pt
```

#### 2. Evaluate the quantized model
```bash
CUDA_VISIBLE_DEVICES=0 python -m awq.entry --model_path /Path/to/Qwen3/Qwen3-32B \
    --w_bit 4 --q_group_size 128 \
    --load_awq awq_cache/qwen3-32b-w4-g128.pt \
    --q_backend fake
```

### Per-channel Quantization

#### 1. Perform AWQ search and save results (note: q_group_size parameter is removed)
```bash
CUDA_VISIBLE_DEVICES=0 python -m awq.entry --model_path /Path/toQwen3/Qwen3-32B \
    --w_bit 4 \
    --run_awq --dump_awq awq_cache/qwen3-32b-w4-perchannel.pt
```

#### 2. Evaluate the quantized model
```bash
CUDA_VISIBLE_DEVICES=0 python -m awq.entry --model_path /Path/to/Qwen3/Qwen3-32B \
    --w_bit 4 \
    --load_awq awq_cache/qwen3-32b-w4-perchannel.pt \
    --q_backend fake
```

## Notes

- Available quantization bit-widths (w_bit): 2, 3, 4, 8.
- Use the `--q_group_size` parameter (e.g., 128) for group-wise quantization
- Remove the `--q_group_size` parameter for per-channel quantization
- Make sure you have sufficient GPU memory to run a 32B-sized model
