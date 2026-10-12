# Post-training Lab: Assistant-only SFT and DPO Preference Optimization

Independent educational portfolio demonstration, **not** a FUNiX internal dataset, model or delivered project.

## Reproduce locally

    python -m model_pretraining_lab.core --epochs 5 --output-dir artifacts/pretraining
    python -m unittest discover -s model_posttraining_lab/tests -v
    python -m model_posttraining_lab.core --pretrained artifacts/pretraining/tiny_pretrained.json --output-dir artifacts/posttraining

Loads the actual pretraining checkpoint, performs supervised fine-tuning (SFT), freezes a deep-copied reference distribution, then trains a policy with real Direct Preference Optimization (DPO). Runs on CPU with Python standard library only, no external model or API key.

## Objectives and safeguards

SFT minimizes token negative log likelihood **only on chosen assistant response tokens**, without teaching the model to repeat user questions.

DPO uses:

    delta = (log policy_chosen - log policy_rejected) -
            (log reference_chosen - log reference_rejected)
    loss = -log sigmoid(beta * delta)

Exact DPO gradient is implemented for the toy bigram weight matrix and numerically checked via finite differences. When policy equals reference, DPO loss equals log(2). Reference parameters remain unchanged during optimization. No PPO, reward-model training or real RLHF is claimed.

Data includes 8 TRAIN, 2 VAL, 2 TEST fictional prompts/preferences. All are synthetic and have unique prompts across partitions. Only training examples update parameters.

## Measured performance: failure disclosure

With default settings, SFT TRAIN NLL falls from ~3.02767 to ~3.01711. DPO validation preference margin DROPS from 3.59558 to 3.52396. This illustrates the gap between successfully computing an objective and real generalization, particularly with a character bigram (one-token context). Do not claim better real-world alignment from the experiment.

## CMC TS relevance

Shows response-only masking, SFT data preparation, preference dataset validation, logistic optimization, frozen reference, experimental metrics, gradient tests and failure analysis. Future extensions: real causal Transformer, proper tokenization, robust blinded preference evaluation, human annotation, and safe deployment.

**This newly created portfolio lab is separate from the candidate's reported FUNiX pre-/post-training employment experience.**
