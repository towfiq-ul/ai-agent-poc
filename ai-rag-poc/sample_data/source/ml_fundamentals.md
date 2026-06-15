# Machine Learning Fundamentals

## What is Machine Learning?

Machine Learning (ML) is a branch of artificial intelligence where systems learn patterns from data rather than being explicitly programmed with rules. The goal is to build models that generalize to new, unseen data.

## Types of Machine Learning

### Supervised Learning
The model learns from labeled data — input-output pairs. The goal is to learn a mapping from inputs to outputs.

- **Classification**: Predict a discrete category (e.g. spam/not spam, cat/dog)
- **Regression**: Predict a continuous value (e.g. house price, temperature)

Common algorithms: Linear Regression, Logistic Regression, Decision Trees, Random Forests, SVMs, Neural Networks.

### Unsupervised Learning
The model finds patterns in unlabelled data.

- **Clustering**: Group similar data points (e.g. K-Means, DBSCAN)
- **Dimensionality reduction**: Compress high-dimensional data (e.g. PCA, t-SNE, UMAP)
- **Generative models**: Learn the data distribution (e.g. VAEs, GANs)

### Reinforcement Learning (RL)
An agent learns by interacting with an environment, receiving rewards or penalties. Used in game playing (AlphaGo), robotics, and RLHF for LLM alignment.

### Self-Supervised Learning
A form of unsupervised learning where the model creates its own supervision signal from the data structure. LLMs use this — predicting the next token is self-supervised.

## The ML Workflow

1. **Problem definition**: What are you predicting? What metric matters?
2. **Data collection**: Gather and label data
3. **Exploratory Data Analysis (EDA)**: Understand distributions, missing values, correlations
4. **Feature engineering**: Transform raw data into useful model inputs
5. **Model selection**: Choose algorithm(s) to try
6. **Training**: Fit the model to training data
7. **Evaluation**: Measure performance on held-out test data
8. **Iteration**: Tune, retrain, improve
9. **Deployment**: Serve the model in production

## Key Concepts

### Train / Validation / Test Split
- **Training set**: The model learns from this
- **Validation set**: Used to tune hyperparameters and prevent overfitting
- **Test set**: Held out until the very end to estimate real-world performance

A common split is 70% train / 15% validation / 15% test, or k-fold cross-validation.

### Overfitting and Underfitting
- **Overfitting**: Model memorizes training data, performs poorly on new data. High variance.
- **Underfitting**: Model is too simple, misses patterns. High bias.
- **Regularisation** techniques (L1/L2, dropout, early stopping) help prevent overfitting.

### Loss Functions
A loss function measures how wrong the model's predictions are. Training minimizes this.
- **MSE** (Mean Squared Error): Common for regression
- **Cross-entropy**: Common for classification
- **Binary cross-entropy**: For binary classification

### Gradient Descent
The optimization algorithm used to minimize the loss. Computes the gradient of the loss with respect to model parameters and updates them in the opposite direction.

Variants: Stochastic Gradient Descent (SGD), Adam, RMSProp, AdaGrad.

### Learning Rate
Controls how large each parameter update step is. Too high: training diverges. Too low: training is slow. Learning rate schedulers adjust it during training.

### Backpropagation
The algorithm for computing gradients in neural networks. Uses the chain rule to propagate the error signal from the output layer back through each layer.

## Neural Networks

### Perceptron and MLP
A perceptron is a single neuron: a weighted sum of inputs passed through an activation function. A Multi-Layer Perceptron (MLP) stacks layers of perceptrons.

### Activation Functions
Introduce non-linearity so the network can learn complex functions.
- **ReLU**: max(0, x) — most commonly used
- **GELU**: Smooth version of ReLU, used in transformers
- **Sigmoid**: Squashes output to (0, 1), used in output layers for binary classification
- **Softmax**: Converts logits to a probability distribution over classes

### Batch Normalisation
Normalizes activations within a mini-batch during training. Speeds up training and reduces sensitivity to initialization.

## Evaluation Metrics

### Classification
- **Accuracy**: Fraction of correct predictions
- **Precision**: Of predicted positives, how many are truly positive
- **Recall**: Of actual positives, how many did we catch
- **F1 Score**: Harmonic mean of precision and recall
- **ROC-AUC**: Area under the receiver operating characteristic curve

### Regression
- **MAE** (Mean Absolute Error)
- **RMSE** (Root Mean Squared Error)
- **R²** (Coefficient of determination)

## Python Libraries for ML

- **scikit-learn**: Classical ML algorithms, preprocessing, evaluation
- **NumPy / Pandas**: Data manipulation
- **Matplotlib / Seaborn**: Visualisation
- **PyTorch / TensorFlow**: Deep learning frameworks
- **Hugging Face Transformers**: Pre-trained transformer models
- **XGBoost / LightGBM**: Gradient boosting (often wins on tabular data)
