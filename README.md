# Qwen3 Quantization Toolkit: An Empirical Study of Qwen3 Quantization

**Visual Intelligence 4, Article 11 · 2026**

Xingyu Zheng, Yuye Li, Haoran Chu, Yue Feng, Xudong Ma, Zining Wang, Jie Luo, Jinyang Guo, Haotong Qin, Michele Magno, Xianglong Liu

[Published paper](https://doi.org/10.1007/s44267-026-00114-4) | [arXiv](https://arxiv.org/abs/2505.02214) | [Citation](#citation)

**This toolkit accompanies a systematic evaluation of five post-training quantization methods on Qwen3 across 1–8-bit settings.** It helps choose quantization baselines and understand quality loss across language modeling, commonsense reasoning, and knowledge evaluation; it does not introduce a new quantizer.

## Published results

Selected **Qwen3-8B** results from Table 4 of the **2026 journal version**, per-group quantization with group size 128 and 16-bit activations. Calibration uses 128 C4 sequences of length 2048 (Section 2.1). WikiText2 perplexity (PPL) is lower-is-better; MMLU is five-shot and higher-is-better.

| Method | Weight bits | Activation bits | WikiText2 PPL | MMLU (%) |
| --- | --- | --- | --- | --- |
| FP16 reference | 16 | 16 | 9.71 | 74.7 |
| AWQ | 8 | 16 | 9.72 | 74.5 |
| GPTQ | 8 | 16 | 9.70 | 74.7 |
| AWQ | 4 | 16 | 11.3 | 69.3 |
| GPTQ | 4 | 16 | 9.96 | 73.4 |
| AWQ | 3 | 16 | 27.5 | 33.2 |
| GPTQ | 2 | 16 | 52.1 | 25.0 |
| BiLLM | 1.05 (effective) | 16 | 90.4 | 32.8 |

The effective bit-width includes the method's mixed/residual representation. These are quality measurements from the paper, not new runs or measured speedups. Parameter compression does not by itself establish proportional reductions in runtime memory or latency.

### What this paper supports

- Quantization quality depends on bit-width, method, model size, and whether a base or post-trained model is evaluated (Section 2.2; Tables 1–4).
- At W8A16G128, the selected Qwen3-8B results stay close to FP16; W4A16G128 distinguishes GPTQ and AWQ markedly (Table 4).
- Ultra-low bit-width can cause severe degradation; a smaller bit-width is not automatically a useful deployment choice (Section 2.2; Table 4).
- Weight-only and weight/activation quantization must be evaluated separately (Tables 1–4); outlier analysis helps explain their different behavior (Figures 6–9).
- In the Qwen3-8B GPTQ W4A16 calibration ablation, 128–512 samples yield similar WikiText2 perplexity, while smaller sets can degrade it (Table 7). This is a setting-specific observation, not a universal calibration-size rule.

## Supported quantization methods

| Method | Technical role | Code and documentation |
| --- | --- | --- |
| AWQ | Activation-aware weight-only quantization | [AWQ](llm-awq/readme.md) |
| GPTQ | Weight-only PTQ with approximate second-order reconstruction/error compensation | [GPTQ](GPTQ-for-Qwen/README.md) |
| RTN | Round-to-nearest quantization baseline | [RTN](RTN/README.md) |
| SmoothQuant | Activation smoothing for weight-and-activation quantization | [SmoothQuant](SmoothQuant-for-Qwen3/README.md) |
| BiLLM | Near-1-bit post-training weight quantization with residual approximation | [BiLLM](BiLLM/README.md) |

## Reproduction

Choose a method above and follow its own environment, calibration, checkpoint, and evaluation instructions. Compare the same Qwen3 checkpoint, grouping, activation precision, calibration set, and evaluation protocol. The paper uses one NVIDIA A800 80 GB for its experiments; this is an experimental resource specification, not a speed benchmark.

### Evaluation data not included in GitHub

Due to GitHub's file size restrictions, the following five files cannot be directly uploaded to our code repository:

- `eval_my/mmlu/data/auxiliary_train/race.csv`
- `eval_my/ppl_datasets/wikitext/wikitext-2-raw-v1/test`
- `eval_my/ppl_datasets/wikitext/wikitext-2-raw-v1/train`
- `eval_my/ppl_datasets/allenai/c4/allenai--c4/train`
- `eval_my/ppl_datasets/allenai/c4/allenai--c4/validation`

You can download these files from Hugging Face. We will also update them to our project's Hugging Face repository in the future.
## Contributions

Contributions to this project are welcome! If you have suggestions for improvements or find issues, please submit an issue or pull request.




## Citation

Please cite the published paper below. Open paper versions are linked at the top of this README.

```bibtex
@article{zheng2026qwen3quantization,
  title = {An Empirical Study of {Qwen3} Quantization},
  author = {Xingyu Zheng and Yuye Li and Haoran Chu and Yue Feng and Xudong Ma and Zining Wang and Jie Luo and Jinyang Guo and Haotong Qin and Michele Magno and Xianglong Liu},
  journal = {Visual Intelligence},
  year = {2026},
  volume = {4},
  pages = {11},
  doi = {10.1007/s44267-026-00114-4},
  url = {https://doi.org/10.1007/s44267-026-00114-4}
}
```
