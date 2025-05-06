import torch
from datasets import load_dataset


def get_calib_dataset(data="c4", tokenizer=None, n_samples=128, block_size=512):
    if data == "c4":
        dataset = load_dataset("arrow",
            data_files={
                "train": "/mnt/disk2/zxy2/W1W8LLM/datasets/allenai/c4/allenai--c4/train/*.arrow"
            },
            split="train")
    else:
        raise NotImplementedError
    dataset = dataset.shuffle(seed=42)
    samples = []
    n_run = 0
    for data in dataset:
        line = data["text"]
        line = line.strip()
        line_encoded = tokenizer.encode(line)
        if len(line_encoded) > 512:
            continue
        sample = torch.tensor([line_encoded])
        if sample.numel() == 0:
            continue
        samples.append(sample)
        n_run += 1
        if n_run == n_samples:
            break
    # now concatenate all samples and split according to block size
    cat_samples = torch.cat(samples, dim=1)
    n_split = cat_samples.shape[1] // block_size
    print(f" * Split into {n_split} blocks")
    return [
        cat_samples[:, i * block_size : (i + 1) * block_size] for i in range(n_split)
    ]
