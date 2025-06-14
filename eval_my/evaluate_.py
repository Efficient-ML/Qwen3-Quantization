import torch
import torch.nn as nn
from tqdm import tqdm
import os
from datautils import get_eval_loaders
# from lm_eval.base import BaseLM
from lm_eval.models.huggingface import HFLM
from lm_eval import evaluator
import time
import argparse
import json

from transformers import AutoModelForCausalLM, AutoTokenizer

class EvalLM(HFLM):
    def __init__(
        self,
        model,
        tokenizer,
        device="cuda",
        batch_size=1,
    ):
        super().__init__()

        assert isinstance(device, str)
        assert isinstance(batch_size, int)

        self._device = torch.device(device)

        self.model = model.to(self.device)
        self.model.eval()

        self.tokenizer = tokenizer

        self.vocab_size = self.tokenizer.vocab_size

        self.batch_size_per_gpu = batch_size  # todo: adaptive batch size

        self.seqlen = 2048
        # self.seqlen = 512

    @property
    def eot_token_id(self):
        # we use EOT because end of *text* is more accurate for what we're doing than end of *sentence*
        return self.tokenizer.eos_token_id

    @property
    def max_length(self):
        try:
            return self.model.config.n_ctx
        except AttributeError:
            # gptneoconfig doesn't have n_ctx apparently
            return self.model.config.max_position_embeddings

    @property
    def max_gen_toks(self):
        return 256

    @property
    def batch_size(self):
        # TODO: fix multi-gpu
        return self.batch_size_per_gpu  # * gpus

    @property
    def device(self):
        # TODO: fix multi-gpu
        return self._device

    def tok_encode(self, string: str):
        return self.tokenizer.encode(string, add_special_tokens=False)

    def tok_decode(self, tokens):
        return self.tokenizer.decode(tokens)

    def _model_call(self, inps):
        """
        inps: a torch tensor of shape [batch, sequence]
        the size of sequence may vary from call to call

        returns: a torch tensor of shape [batch, sequence, vocab] with the
        logits returned from the model
        """
        with torch.no_grad():
            return self.model(inps)["logits"]
        
    def _model_generate(self, context, max_length, eos_token_id):
        return self.model.generate(
            context, max_length=max_length, eos_token_id=eos_token_id, do_sample=False
        )


@torch.no_grad()
def evaluate_model(
    model,
    tokenizer,
    tasks,
    eval_ppl="",
    num_fewshot=0,
    limit=-1,
    batch_size=1,
):
    # lm = EvalLM(model, tokenizer, batch_size=batch_size)
    lm = HFLM(pretrained=model, tokenizer=tokenizer, batch_size=batch_size)
    lm.seqlen = 2048
    results = {}
    if eval_ppl:
        for dataset in eval_ppl.split(","):
            testloader = get_eval_loaders(dataset, tokenizer)
            # print(dataset)
            testenc = testloader.input_ids
            nsamples = testenc.numel() // lm.seqlen
            use_cache = lm.model.config.use_cache
            lm.model.config.use_cache = False
            lm.model.eval()
            nlls = []
            for i in tqdm(range(nsamples)):
                batch = testenc[:, (i * lm.seqlen) : ((i + 1) * lm.seqlen)].to(lm.device)
                outputs = lm.model.model(batch)
                hidden_states = outputs[0]  # .to(lm.model.lm_head.weight.device)
                logits = lm.model.lm_head(hidden_states)
                #logits = outputs[0]
                shift_logits = logits[:, :-1, :]  # .contiguous()
                shift_labels = testenc[:, (i * lm.seqlen) : ((i + 1) * lm.seqlen)][:, 1:].to(lm.device)
                loss_fct = nn.CrossEntropyLoss()
                loss = loss_fct(shift_logits.view(-1, shift_logits.size(-1)), shift_labels.view(-1))
                # print(loss)
                # import pdb; pdb.set_trace()
                # for param in lm.model.state_dict(): param
                neg_log_likelihood = loss.float() * lm.seqlen
                nlls.append(neg_log_likelihood)

            ppl = torch.exp(torch.stack(nlls).sum() / (nsamples * lm.seqlen))
            print(dataset, ppl.item())
            lm.model.config.use_cache = use_cache
            # pprint(model)
            results[dataset] = ppl.item()
    if tasks != "":
        # assert False
        csr_results = evaluator.simple_evaluate(
            model=lm,
            tasks=tasks.split(","),
            batch_size=batch_size,
            num_fewshot=num_fewshot,
            limit=None if limit == -1 else limit,
            # use_cache=False,
        )

        csr_results = csr_results["results"]
        results.update(csr_results)
        print(results)

    return results

from transformers.models.qwen3.modeling_qwen3 import apply_rotary_pos_emb,repeat_kv

def eval_ours(model, tokenizer):

    # Evaluate
    zeroshot_task = "hellaswag,winogrande,boolq"
    # ppl_task = "wikitext2"
    # ppl_task = "c4"
    ppl_task = "wikitext2,c4"
    results = evaluate_model(
        model,
        tokenizer,
        tasks=zeroshot_task,
        batch_size=16,
        eval_ppl=ppl_task,
    )

    # from mmlu.evaluate_hf import mmlu_main
    # mmlu_main(model, tokenizer, ntrain=5)

if __name__ == "__main__":
    model_id = "/mnt/disk3/zxy3/models/Qwen3/Base/Qwen3-0.6B-Base"
    # model_id = "/mnt/disk2/zxy2/W1W8LLM/models/llama-3-8B"
    tokenizer = AutoTokenizer.from_pretrained(model_id, device_map="auto", use_fast=False, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_id, device_map='auto', torch_dtype=torch.bfloat16)

    eval_ours(model, tokenizer)
