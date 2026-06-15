# Transformers and Large Language Models

## What is a Transformer?

The Transformer is a deep learning architecture introduced in the 2017 paper "Attention Is All You Need" by Vaswani et al. It replaced recurrent neural networks (RNNs) for sequence-to-sequence tasks and became the foundation for modern large language models (LLMs).

Unlike RNNs, transformers process all tokens in a sequence in parallel rather than sequentially. This makes them much faster to train on modern GPUs and allows them to capture long-range dependencies in text more effectively.

## Core Components

### Self-Attention Mechanism
Self-attention allows each token in a sequence to attend to every other token. For each token, the model computes three vectors: Query (Q), Key (K), and Value (V). Attention scores are computed as the dot product of Q and K, scaled by the square root of the key dimension, then passed through a softmax. These scores weight the V vectors to produce the output.

Formula: Attention(Q, K, V) = softmax(QK^T / sqrt(d_k)) * V

### Multi-Head Attention
Instead of one attention operation, multi-head attention runs several attention heads in parallel, each learning different relationships. The outputs are concatenated and projected.

### Positional Encoding
Since transformers have no built-in notion of order, positional encodings are added to token embeddings to inject information about position in the sequence. These can be sinusoidal (fixed) or learned.

### Feed-Forward Layers
Each transformer block contains a position-wise feed-forward network applied identically to each token. Typically, two linear layers with a ReLU or GELU activation.

### Layer Normalisation and Residual Connections
Residual connections (skip connections) and layer normalization are applied around each sub-layer to stabilize training and allow gradients to flow more easily.

## Encoder vs Decoder vs Encoder-Decoder

- **Encoder-only** (e.g. BERT): Bidirectional attention, good for classification and embeddings.
- **Decoder-only** (e.g. GPT, Gemini, Claude): Causal/autoregressive attention, used for text generation.
- **Encoder-Decoder** (e.g. T5, original transformer): Used for translation and summarization.

## Large Language Models (LLMs)

LLMs are transformer-based models trained on massive text corpora using self-supervised learning (predicting the next token). Key examples include GPT-4, Gemini, Claude, and LLaMA.

### Pre-training
LLMs learn general language patterns by predicting the next token across billions of documents. This gives them broad world knowledge and language understanding.

### Fine-tuning and RLHF
After pre-training, models are fine-tuned on curated datasets and aligned with human preferences using Reinforcement Learning from Human Feedback (RLHF). This improves helpfulness, safety, and instruction-following.

### Emergent Abilities
As models scale up in parameters and training data, they exhibit emergent abilities — capabilities that appear suddenly at scale, such as multistep reasoning, few-shot learning, and code generation.

### Context Window
The context window is the maximum number of tokens a model can attend to at once. Modern LLMs have context windows ranging from 8k to over 1 million tokens.

## Tokenization

Text is split into tokens — subword units — using methods like Byte-Pair Encoding (BPE) or SentencePiece. A single word may be one token or several. A token is roughly 3-4 characters in English.

## Temperature and Sampling

During inference, the model outputs a probability distribution over the vocabulary. Temperature controls the "sharpness" of this distribution:
- Temperature 0: Greedy decoding (always picks the highest probability token)
- Temperature 1: Samples from the original distribution
- High temperature: More random, creative outputs
- Low temperature: More focused, deterministic outputs

Other sampling strategies include top-k sampling and nucleus (top-p) sampling.
