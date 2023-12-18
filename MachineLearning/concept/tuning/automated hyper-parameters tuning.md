# Introduction

A learning algorithm trains a machine learning model on a training dataset. The parameters of a learning algorithm-
called "hyper-parameters"-control how the model is trained and impact its quality.

There are three main approaches to select the hyper-parameter values:

1. The default approach: Learning algorithms come with default values. While not ideal in all cases, those values produce reasonable results in most situations. This approach is recommended as the first approach to use in any modeling. This page lists the default values of TF Decision Forests.

2. The template hyper-parameter approach: In addition to the default values, TF Decision Forests also exposes the hyper-parameter templates. Those are benchmark-tuned hyper-parameter values with excellent performance but high training cost (e.g. hyperparameter_template="benchmark_rank1").

3. The manual tuning approach: You can manually test different hyper-parameter values and select the one that performs best. This guide give some advice.

4. The automated tuning approach: A tuning algorithm can be used to find automatically the best hyper-parameter values. This approach gives often the best results and does not require expertise. The main downside of this approach is the time it takes for large datasets.


# Hyper-parameter tuning algorithms

Automated tuning algorithms work by generating and evaluating a large number of hyper-parameter values.

Tuning algorithm are configured as follow:
### The number of trials

The number of trials defines how many models will be trained and evaluated. Larger number of trials generally leads to better models, but takes more time.

### The optimizer

The optimizer selects the next hyper-parameter to evaluate the past trial evaluations. The simplest and often reasonable optimizer is the one that selects the hyper-parameter at random.

### The objective / trial score

The objective is the metric optimized by the tuner. Often, this metric is a measure of quality (e.g. accuracy, log loss) of the model evaluated on a validation dataset.