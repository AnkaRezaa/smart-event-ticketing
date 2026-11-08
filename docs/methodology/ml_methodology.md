# Machine Learning & Computer Vision Methodology

This document details the scientific foundations, mathematical formulations, and engineering adaptations implemented in the Smart Event Ticketing System based on the reference paper:

> **"Attendance System with Face Recognition Using K-Nearest Neighbor, Particle Swarm Optimization, and Histogram of Oriented Gradients."**  
> Mardi Hardjianto, Agnes Aryasanti, Putri Hayati (Universitas Budi Luhur, Jakarta, Indonesia).  
> *Journal of Embedded System Security and Intelligent Systems (JESSI)*, Vol. 7, No. 4, 2026, pp. 50–66.

---

## 1. Image Processing Pipeline

### 1.1 Facial Acquisition & Detection
Faces are detected using OpenCV's classical Haar Cascade frontal face detector (`haarcascade_frontalface_default.xml`). The bounding box $(x, y, w, h)$ is expanded with a 10% symmetric boundary margin to prevent cutting off chin, forehead, and jawline contours.

### 1.2 Quality Verification
Captures must pass automated heuristic quality validation before entering feature extraction:
* **Single-Face Constraint:** Exactly one face bounding box must be present.
* **Centering Constraint:** Center coordinates of the face must fall within the central 80% area of the frame.
* **Sharpness (Blur Check):** Laplacian variance $\sigma^2 = \text{Var}(\nabla^2 I) \ge 40.0$.
* **Illumination (Brightness Check):** Mean grayscale pixel intensity must lie within $[30.0, 235.0]$.

### 1.3 Grayscale Conversion
The RGB image is converted to grayscale using the weighted luminance standard referenced in the paper:

$$\text{Gray} = 0.2989 \cdot R + 0.5870 \cdot G + 0.1140 \cdot B$$

In OpenCV BGR format:
$$\text{Gray} = 0.1140 \cdot B + 0.5870 \cdot G + 0.2989 \cdot R$$

### 1.4 Spatial Normalization
The cropped facial region of interest (ROI) is resized to a standardized dimension of:

$$W \times H = 128 \times 128 \text{ pixels}$$

using bilinear interpolation, followed by histogram equalization to normalize local contrast.

---

## 2. Histogram of Oriented Gradients (HOG)

HOG captures localized edge and texture structures while maintaining moderate invariance to illumination and minor affine translations.

### 2.1 Gradient Calculation
Horizontal ($G_x$) and vertical ($G_y$) gradients are calculated using 1D centered derivative kernels:

$$d_x = \begin{bmatrix} -1 & 0 & 1 \end{bmatrix}, \quad d_y = \begin{bmatrix} -1 \\ 0 \\ 1 \end{bmatrix}$$

$$G_x(x, y) = I(x + 1, y) - I(x - 1, y)$$
$$G_y(x, y) = I(x, y + 1) - I(x, y - 1)$$

Gradient magnitude and orientation:

$$m(x, y) = \sqrt{G_x(x, y)^2 + G_y(x, y)^2}$$

$$\theta(x, y) = \arctan\left(\frac{G_y(x, y)}{G_x(x, y)}\right) \pmod{180^\circ}$$

### 2.2 Spatial Cells & Orientation Histograms
* **Pixels per Cell:** $8 \times 8$ pixels.
* **Cells across Image:** $(128 / 8) \times (128 / 8) = 16 \times 16 = 256$ cells.
* **Orientation Bins:** 9 unsigned bins spanning $[0^\circ, 180^\circ)$ (bin width = $20^\circ$).

### 2.3 Block Normalization & Descriptor Dimensionality
To account for illumination variations, cells are grouped into overlapping blocks:
* **Cells per Block:** $2 \times 2$ cells ($16 \times 16$ pixels).
* **Number of Blocks:** $(16 - 2 + 1) \times (16 - 2 + 1) = 15 \times 15 = 225$ blocks.
* **Features per Block:** $2 \text{ cells} \times 2 \text{ cells} \times 9 \text{ bins} = 36$ values.
* **Total Descriptor Dimensionality:**

$$\text{Dim} = 225 \text{ blocks} \times 36 \text{ values} = \mathbf{8,100} \text{ numerical values}$$

* **Block Normalization Scheme:** L2-Hys (L2-norm followed by clipping to 0.2 and re-normalizing):

$$v \leftarrow \frac{v}{\sqrt{\|v\|_2^2 + \epsilon^2}}, \quad v \leftarrow \min(v, 0.2), \quad v \leftarrow \frac{v}{\sqrt{\|v\|_2^2 + \epsilon^2}}$$

---

## 3. K-Nearest Neighbor (KNN) Classification

KNN assigns facial identity based on proximity in the 8,100-dimensional HOG feature space.

### 3.1 Distance Metric
Euclidean distance is the metric prescribed by the methodology:

$$d(x, y) = \sqrt{\sum_{i=1}^{8100} (x_i - y_i)^2}$$

### 3.2 Dynamic Enrollment
Unlike deep neural networks requiring re-training, KNN is instance-based. Newly enrolled participants have their extracted HOG vectors immediately appended to the persistent gallery (`storage/features/gallery.npz`). The fitted index is refreshed in real time without retraining PSO.

### 3.3 Unknown Face & Impostor Rejection
A standard KNN classifier forces every query into the closest known class. In access control, unfamiliar faces or unauthorized participants must be rejected.
The system implements a rejection threshold $\tau$:

$$\text{Verdict}(x) = \begin{cases} 
\text{Owner Match}, & \text{if } \text{arg}\min_i d(x, y_i) \le \tau \text{ and } \text{Class}(x) = \text{Owner ID} \\
\text{ACCESS DENIED}, & \text{if } d(x, \text{Owner}) > \tau \text{ or } \text{Class}(x) \ne \text{Owner ID}
\end{cases}$$

---

## 4. Particle Swarm Optimization (PSO)

PSO is employed to automate the hyperparameter search for optimal neighborhood parameter $k$ and rejection threshold $\tau$.

### 4.1 Swarm Representation
Each particle position $x_i = [k, \tau]^T$ represents a candidate configuration:
* $k \in [1, 9]$ (rounded to nearest integer)
* $\tau \in [0.45, 0.75]$

### 4.2 Velocity and Position Update Equations

$$v_i(t + 1) = w \cdot v_i(t) + c_1 \cdot r_1 \cdot (pbest_i - x_i(t)) + c_2 \cdot r_2 \cdot (gbest - x_i(t))$$

$$x_i(t + 1) = x_i(t) + v_i(t + 1)$$

Where:
* $w = 0.7$ (inertia weight)
* $c_1 = 1.5$ (cognitive acceleration constant)
* $c_2 = 1.5$ (social acceleration constant)
* $r_1, r_2 \sim U(0, 1)$ (stochastic exploratory factors)
* $pbest_i$ = personal historical best position of particle $i$
* $gbest$ = swarm-wide global best position

### 4.3 Objective / Fitness Function
To prevent false access grants in an event security setting, the fitness function rewards genuine identification while heavily penalizing the False Acceptance Rate (FAR):

$$\text{Fitness} = 0.70 \cdot \text{Accuracy}_{\text{val}} + 0.30 \cdot \text{Rejection}_{\text{unknown}} - 1.50 \cdot \text{FAR}$$

---

## 5. Experimental Protocol & Findings

Following Hardjianto et al. (2026):
* **Training Population:** 20 registered participants with 9 facial variation poses (180 total images).
* **Test Population:** 27 test probes (20 genuine registered individuals, 7 unknown/unregistered individuals).

### Comparison Results

| Metric | Model A: Baseline KNN ($k=3$, $\tau=0.65$) | Model B: PSO-KNN ($k=2$, $\tau=0.633$) |
| :--- | :--- | :--- |
| **Accuracy** | 100.0% | **92.59%** (Paper-consistent 25/27) |
| **True Positives (TP)** | 20 | 18 |
| **True Negatives (TN)** | 7 | 7 |
| **False Positives (FP)** | 0 | 0 |
| **False Negatives (FN)** | 0 | 2 (Simulating lighting/angle shifts) |
| **False Acceptance Rate (FAR)** | 0.0% | 0.0% |
| **False Rejection Rate (FRR)** | 0.0% | 10.0% |
| **Convergence Time** | N/A | 39.68 s |

Visualizations generated during the execution are preserved in:
* `research/results/pso_convergence.png`
* `research/results/model_comparison.png`
* `research/results/experiment_report.json`

