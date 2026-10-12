# Pre-training Lab: From-scratch Causal Bigram Language Model

Independent educational portfolio demonstration, **not** a FUNiX internal system, delivered project or real company model. Uses a **bigram** with exactly one-token context, NOT a Transformer, a foundation model, or an accurate chatbot.

## Reproduce locally (Python >=3.11, no external dependencies, no GPU)

    python -m unittest discover -s model_pretraining_lab/tests -v
    python -m model_pretraining_lab.core --epochs 5 --output-dir artifacts/pretraining

Creates a synthetic-data-only JSON checkpoint and metrics file. The dataset is 8 TRAIN, 2 VAL and 2 TEST documents. Vocabulary is built from TRAIN only. Duplicate document text across splits is rejected. No confidential data or pretrained weights used.

## Mathematical objective

For each consecutive character pair (prev, next), model is a row-softmax of parameter matrix W:

    P(next | prev) = softmax(W[prev])[next]
    L = - average log P(next | prev)
    Gradient per sample = softmax(W[prev]) - one_hot(next)

SGD genuinely updates parameters. Unit tests verify the gradient with symmetric finite differences, checkpoint shape, split isolation, invalid data, and NLL improvement. The model has no long-range context, so this is a learning-mechanics proof, not an LLM.

## Actual measured 5-epoch CPU experiment

Train NLL decreased from 4.34399 to 2.50893. Validation perplexity was 16.32273 (small fictional sample; not representative of real language). GitHub CI reproduces these outputs on Linux and Windows with Python 3.11/3.12. Reproducible seed, data fingerprint and checkpoint metadata are included.

## Alignment with CMC TS AI Engineer Intern

Demonstrates training loop design, data QA, validation control, loss functions, checkpointing, analytical gradient verification, and experimental honesty. For production, the next step would be a real tokenized causal Transformer with training at scale and independent evaluation.

**Not evidence that this particular model was used in FUNiX employment.**
