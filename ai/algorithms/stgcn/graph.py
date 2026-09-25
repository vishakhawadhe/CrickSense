"""
=============================================================================
MediaPipe 33-Joint Skeleton Graph Definition for ST-GCN
=============================================================================
This module defines the graph structure of the MediaPipe 33-joint skeleton
model for Spatial-Temporal Graph Convolutional Networks (ST-GCN).

Nodes: 33 body landmarks (0 to 32)
Edges: 35 physical body connections (from MediaPipe POSE_CONNECTIONS)
Partitioning Strategy: Spatial Configuration Partitioning (K = 3)
  - Partition 0: Self-loops (Identity)
  - Partition 1: Centripetal / Inward connections (nodes closer to center)
  - Partition 2: Centrifugal / Outward connections (nodes farther from center)

Author : CrickSense Team
Date   : 2026
=============================================================================
"""

import numpy as np
from typing import List, Tuple, Dict, Optional

# MediaPipe 33 Joint Names Mapping
JOINT_NAMES: Dict[int, str] = {
    0: "nose",
    1: "left_eye_inner", 2: "left_eye", 3: "left_eye_outer",
    4: "right_eye_inner", 5: "right_eye", 6: "right_eye_outer",
    7: "left_ear", 8: "right_ear",
    9: "mouth_left", 10: "mouth_right",
    11: "left_shoulder", 12: "right_shoulder",
    13: "left_elbow", 14: "right_elbow",
    15: "left_wrist", 16: "right_wrist",
    17: "left_pinky", 18: "right_pinky",
    19: "left_index", 20: "right_index",
    21: "left_thumb", 22: "right_thumb",
    23: "left_hip", 24: "right_hip",
    25: "left_knee", 26: "right_knee",
    27: "left_ankle", 28: "right_ankle",
    29: "left_heel", 30: "right_heel",
    31: "left_foot_index", 32: "right_foot_index"
}

# MediaPipe 33 Body Connections (35 Undirected Edges)
MEDIAPIPE_CONNECTIONS: List[Tuple[int, int]] = [
    # Facial landmarks
    (0, 1), (1, 2), (2, 3), (3, 7),
    (0, 4), (4, 5), (5, 6), (6, 8),
    (9, 10),
    # Upper body & Arms
    (11, 12), (11, 13), (13, 15), (15, 17), (15, 19), (15, 21), (17, 19),
    (12, 14), (14, 16), (16, 18), (16, 20), (16, 22), (18, 20),
    # Torso
    (11, 23), (12, 24), (23, 24),
    # Lower body & Legs
    (23, 25), (24, 26), (25, 27), (26, 28), (27, 29), (28, 30),
    (29, 31), (30, 32), (27, 31), (28, 32)
]

# Root node index for spatial distance calculation (midpoint of hips: 23, 24)
ROOT_NODES: List[int] = [23, 24]


class MediaPipeGraph:
    """
    Graph representation for MediaPipe 33-joint skeleton.
    Constructs normalized adjacency matrix A of shape (K, V, V).
    """

    def __init__(self, strategy: str = "spatial", max_hop: int = 1, dilation: int = 1) -> None:
        self.num_node: int = 33
        self.edges: List[Tuple[int, int]] = MEDIAPIPE_CONNECTIONS
        self.num_edges: int = len(self.edges)
        self.strategy: str = strategy
        self.max_hop: int = max_hop
        self.dilation: int = dilation

        # Distance matrix calculation between all node pairs
        self.hop_dis: np.ndarray = self._get_hop_distance()
        # Adjacency matrix (K, V, V)
        self.A: np.ndarray = self._get_adjacency()

    def _get_hop_distance(self) -> np.ndarray:
        """Calculate shortest hop distance matrix between all joint pairs (Floyd-Warshall)."""
        hop_dis = np.zeros((self.num_node, self.num_node), dtype=np.int32) + 999
        for i in range(self.num_node):
            hop_dis[i, i] = 0
        for i, j in self.edges:
            hop_dis[i, j] = 1
            hop_dis[j, i] = 1

        # Floyd-Warshall algorithm
        for k in range(self.num_node):
            for i in range(self.num_node):
                for j in range(self.num_node):
                    if hop_dis[i, k] + hop_dis[k, j] < hop_dis[i, j]:
                        hop_dis[i, j] = hop_dis[i, k] + hop_dis[k, j]
        return hop_dis

    def _get_adjacency(self) -> np.ndarray:
        """
        Construct normalized adjacency matrix A according to chosen strategy.
        Spatial partitioning (Yan et al., 2018):
          Partition 0: Self-loops (Identity)
          Partition 1: Nodes closer to root (hips) than reference node
          Partition 2: Nodes farther from root (hips) than reference node
        Returns:
          A: array of shape (3, 33, 33)
        """
        valid_hop = range(0, self.max_hop + 1, self.dilation)
        adjacency = np.zeros((self.num_node, self.num_node))
        for i in range(self.num_node):
            for j in range(self.num_node):
                if self.hop_dis[i, j] in valid_hop:
                    adjacency[i, j] = 1

        # Calculate distance of each joint to root nodes (hips)
        node_dist_to_root = np.mean([self.hop_dis[r] for r in ROOT_NODES], axis=0)

        if self.strategy == "uniform":
            A = np.zeros((1, self.num_node, self.num_node))
            A[0] = self._normalize_adjacency(adjacency)
            return A

        elif self.strategy == "spatial":
            A = np.zeros((3, self.num_node, self.num_node))
            for i in range(self.num_node):
                for j in range(self.num_node):
                    if self.hop_dis[i, j] in valid_hop:
                        if node_dist_to_root[j] == node_dist_to_root[i]:
                            A[0, i, j] = 1  # Self loop / same distance
                        elif node_dist_to_root[j] < node_dist_to_root[i]:
                            A[1, i, j] = 1  # Centripetal (closer to root)
                        else:
                            A[2, i, j] = 1  # Centrifugal (farther from root)
            
            # Degree normalization for each spatial partition
            for k in range(3):
                A[k] = self._normalize_adjacency(A[k])
            return A

        else:
            raise ValueError(f"Unknown partitioning strategy: {self.strategy}")

    def _normalize_adjacency(self, A: np.ndarray) -> np.ndarray:
        """Symmetric degree normalization D^{-1/2} A D^{-1/2}."""
        Dl = np.sum(A, axis=0)
        num_node = A.shape[0]
        Dn = np.zeros((num_node, num_node))
        for i in range(num_node):
            if Dl[i] > 0:
                Dn[i, i] = Dl[i] ** (-0.5)
        return np.dot(np.dot(Dn, A), Dn)
