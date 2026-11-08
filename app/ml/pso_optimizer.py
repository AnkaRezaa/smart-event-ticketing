import random
from typing import Dict, Any, List, Tuple, Callable, Optional
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

class Particle:
    """
    A single particle in the PSO swarm representing candidate KNN hyperparameters:
    x = [k, threshold]
    """
    def __init__(
        self,
        bounds: List[Tuple[float, float]],
        seed: int = None
    ):
        if seed is not None:
            np.random.seed(seed)

        self.bounds = bounds
        self.dim = len(bounds)

        # Initialize position uniformly within bounds
        self.position = np.array([
            np.random.uniform(b[0], b[1]) for b in bounds
        ], dtype=np.float32)

        # Initialize velocity randomly in [-range, +range] * 0.1
        self.velocity = np.array([
            np.random.uniform(-(b[1] - b[0]) * 0.1, (b[1] - b[0]) * 0.1)
            for b in bounds
        ], dtype=np.float32)

        self.pbest_position = np.copy(self.position)
        self.pbest_fitness = -float("inf")
        self.current_fitness = -float("inf")

class ParticleSwarmOptimizer:
    """
    Particle Swarm Optimization for tuning KNN parameters (k and distance threshold)
    based on the scientific reference method.
    """
    def __init__(
        self,
        num_particles: int = 15,
        max_iter: int = 20,
        w: float = 0.7,        # Inertia weight
        c1: float = 1.5,       # Cognitive coefficient
        c2: float = 1.5,       # Social coefficient
        bounds: List[Tuple[float, float]] = None,
        random_state: int = 42
    ):
        self.num_particles = num_particles
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2
        self.random_state = random_state

        # Default bounds: k in [1, 9], threshold in [0.40, 1.20]
        self.bounds = bounds or [(1.0, 9.0), (0.40, 1.20)]

        self.gbest_position = None
        self.gbest_fitness = -float("inf")
        self.fitness_history: List[float] = []
        self.iteration_records: List[Dict[str, Any]] = []

    def optimize(
        self,
        X_train: np.ndarray,
        y_train: List[str],
        X_val: np.ndarray,
        y_val: List[str],
        X_unknown: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """
        Executes PSO optimization to discover the optimal k and rejection threshold.
        """
        np.random.seed(self.random_state)
        random.seed(self.random_state)

        # Initialize particles
        particles = [
            Particle(self.bounds, seed=self.random_state + i)
            for i in range(self.num_particles)
        ]

        self.gbest_position = np.copy(particles[0].position)
        self.gbest_fitness = -float("inf")
        self.fitness_history = []
        self.iteration_records = []

        # Fitness function closure
        def evaluate_fitness(k_val: int, thresh_val: float) -> Tuple[float, Dict[str, float]]:
            k_val = max(1, min(int(round(k_val)), len(y_train)))

            clf = KNeighborsClassifier(n_neighbors=k_val, metric="euclidean")
            clf.fit(X_train, y_train)

            # Predict on validation set
            dists, indices = clf.kneighbors(X_val)
            preds = clf.predict(X_val)

            correct = 0
            fr_count = 0  # false rejections (genuine classified as unknown)
            for i in range(len(y_val)):
                min_d = dists[i][0]
                pred_label = preds[i]
                if min_d <= thresh_val and pred_label == y_val[i]:
                    correct += 1
                elif min_d > thresh_val:
                    fr_count += 1

            known_acc = correct / len(y_val) if len(y_val) > 0 else 0.0

            # Evaluate unknown-face rejection if unknown set is provided
            unknown_rejected_rate = 1.0
            far = 0.0
            if X_unknown is not None and len(X_unknown) > 0:
                unk_dists, _ = clf.kneighbors(X_unknown)
                accepted_impostors = sum(1 for d in unk_dists if d[0] <= thresh_val)
                far = accepted_impostors / len(X_unknown)
                unknown_rejected_rate = 1.0 - far

            # Fitness: combine accuracy while penalizing false acceptance
            fitness = known_acc * 0.7 + unknown_rejected_rate * 0.3 - (1.5 * far)
            return fitness, {
                "accuracy": known_acc,
                "unknown_rejection": unknown_rejected_rate,
                "far": far
            }

        # Optimization loop
        for it in range(self.max_iter):
            for p in particles:
                k_candidate = int(round(p.position[0]))
                thresh_candidate = float(p.position[1])

                fit, metrics = evaluate_fitness(k_candidate, thresh_candidate)
                p.current_fitness = fit

                # Update personal best
                if fit > p.pbest_fitness:
                    p.pbest_fitness = fit
                    p.pbest_position = np.copy(p.position)

                # Update global best
                if fit > self.gbest_fitness:
                    self.gbest_fitness = fit
                    self.gbest_position = np.copy(p.position)

            self.fitness_history.append(float(self.gbest_fitness))

            # Update velocity and position for next step
            for p in particles:
                r1 = np.random.uniform(0.0, 1.0, size=len(self.bounds))
                r2 = np.random.uniform(0.0, 1.0, size=len(self.bounds))

                cognitive = self.c1 * r1 * (p.pbest_position - p.position)
                social = self.c2 * r2 * (self.gbest_position - p.position)
                p.velocity = (self.w * p.velocity) + cognitive + social

                # Position update
                p.position = p.position + p.velocity

                # Clip within search bounds
                for dim_idx, (low, high) in enumerate(self.bounds):
                    p.position[dim_idx] = np.clip(p.position[dim_idx], low, high)

            self.iteration_records.append({
                "iteration": it + 1,
                "best_fitness": float(self.gbest_fitness),
                "best_k": int(round(self.gbest_position[0])),
                "best_threshold": float(round(self.gbest_position[1], 4))
            })

        optimized_k = int(round(self.gbest_position[0]))
        optimized_threshold = float(round(self.gbest_position[1], 4))

        return {
            "optimized_k": optimized_k,
            "optimized_threshold": optimized_threshold,
            "best_fitness": float(self.gbest_fitness),
            "fitness_history": self.fitness_history,
            "iterations": self.iteration_records
        }

