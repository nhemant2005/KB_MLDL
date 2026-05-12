# What are Tensors

## Why This Math Matters
Ignoring tensor structure leads to shape errors that break custom models; this formalization shows how a single numeric container generalizes from scalars to $n$-dimensional arrays and why TensorFlow treats everything as a tensor. Interview importance is 1/10—only a high‑level definition is expected.

## Prerequisites Assumed
- None

## Full Derivation

1. **Scalar (rank‑0 tensor)**  
   A single real number, e.g., $42$, is a tensor with an empty shape.  
   $$42 \in \mathbb{R}$$  
   (HOML ch.12: “it can also hold a scalar … such as 42”)

2. **Vector (rank‑1 tensor)**  
   An ordered list of numbers along one axis. In a dataset, an instance’s feature values form a vector.  
   $$\mathbf{x}^{(i)} \in \mathbb{R}^{d}$$  
   (HOML ch.2: “x is a vector of all the feature values”)

3. **Matrix (rank‑2 tensor)**  
   A 2‑dimensional grid of numbers with rows (instances) and columns (features). The full feature set is a matrix.  
   $$\mathbf{X} \in \mathbb{R}^{m \times d}$$  
   (HOML ch.2: “X is a matrix containing all the feature values … one row per instance”)

4. **Generalization to rank‑$k$ tensors**  
   A tensor extends the pattern to an arbitrary number of axes. A rank‑$k$ tensor has $k$ dimensions, each with a size.  
   $$\mathcal{T} \in \mathbb{R}^{d_1 \times d_2 \times \dots \times d_k}$$  
   The order (rank) is the number of axes. For a scalar $k=0$, for a vector $k=1$, for a matrix $k=2$, and for a 3D array $k=3$.  
   (HOML ch.12: “A tensor is usually a multidimensional array (exactly like a NumPy ndarray) … [it can] hold a scalar … a matrix …”)

5. **Shape and data type**  
   Every tensor has a shape (a tuple of dimension sizes) and a `dtype` (e.g., `float32`). For example,  
   ```python
   t = tf.constant([[1., 2., 3.], [4., 5., 6.]])   # shape (2,3), dtype float32
   ```
   (HOML ch.12: “Just like an ndarray, a tf.Tensor has a shape and a data type”)

6. **Operations preserve tensor structure**  
   Element‑wise operations (addition, squaring), matrix multiplication (`@`), and reductions (`tf.reduce_sum`) all consume and produce tensors. For instance,  
   $$\mathbf{C} = \mathbf{A} + \mathbf{B}, \quad \mathbf{D} = \mathbf{A} \mathbf{B}^\top$$  
   (HOML ch.12: “all sorts of tensor operations are available: t + 10, tf.square(t), t @ tf.transpose(t)…”)

7. **Variables are mutable tensors**  
   Model weights are stored as `tf.Variable` tensors that can be updated in place via `assign()`.  
   (HOML ch.12: “A tf.Variable acts much like a tf.Tensor … it can also be modified in place using the assign() method”)

## Key Result
$$\boxed{\mathcal{T} \in \mathbb{R}^{d_1 \times d_2 \times \dots \times d_k}}$$
Geometrically, this states that a tensor is a point in a $k$‑dimensional grid of real numbers; each axis corresponds to an independent mode of variation (e.g., batch, height, width, channels).

## Intuition Behind The Math
The derivation simply stacks familiar structures: a scalar is a zero‑dimensional point, a vector is a line of numbers, a matrix is a table, and a higher‑rank tensor is a cube (or hyper‑cube) of numbers. The rank tells you how many indices are needed to locate one element. TensorFlow adopts this uniform view so that every piece of data—from a single scalar to a batch of images—flows through the same operation graph.

## Where This Formula Appears
- Batch training data representation (feature matrix $\mathbf{X}$)  
- Custom TensorFlow loss functions and layers (e.g., `HuberLoss`, `MyDense`)  
- Keras model inputs and weight variables  
- GPU/TPU accelerated linear algebra kernels

## Interview Angle
At importance 1/10, an interviewer will only ask “What is a tensor?” and expect the answer “a multidimensional array generalizing scalars/vectors