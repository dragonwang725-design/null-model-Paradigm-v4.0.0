"""
Causal Skeleton - 因果骨架

最小因果骨架：跨领域、形式化、无实体语义。
节点是"状态/条件"，边是"因果/影响"方向。

设计原则：
- 不知道"Chrome是什么"，但知道"进程占用资源 → 资源耗尽"
- 不知道"Ollama是什么"，但知道"服务端口关闭 → 服务不可用"
"""

from collections import defaultdict, deque
from typing import Dict, List, Tuple


class CausalSkeleton:
    """
    最小因果骨架——系统监控领域的形式DAG
    """

    def __init__(self):
        self.graph = defaultdict(list)  # 邻接表
        self.nodes = set()
        self._build_skeleton()

    def _add_edge(self, from_node: str, to_node: str, relation: str, weight: float = 1.0):
        self.graph[from_node].append((to_node, relation, weight))
        self.nodes.add(from_node)
        self.nodes.add(to_node)

    def _build_skeleton(self):
        """构建系统监控领域的最小因果骨架"""
        # === 资源子系统 ===
        self._add_edge("memory_high_usage", "memory_pressure", "causal", 0.95)
        self._add_edge("memory_low_free", "memory_pressure", "causal", 0.90)
        self._add_edge("memory_pressure", "system_performance_degradation", "causal", 0.85)
        self._add_edge("memory_pressure", "oom_risk", "causal", 0.80)

        self._add_edge("cpu_high_usage", "cpu_pressure", "causal", 0.95)
        self._add_edge("cpu_pressure", "system_performance_degradation", "causal", 0.90)

        self._add_edge("disk_high_usage", "disk_pressure", "causal", 0.85)
        self._add_edge("disk_pressure", "system_performance_degradation", "causal", 0.70)
        self._add_edge("disk_pressure", "write_failure_risk", "causal", 0.75)

        # === Ollama 服务子系统 ===
        self._add_edge("service_not_running", "service_unavailable", "causal", 0.98)
        self._add_edge("port_not_listening", "service_not_running", "causal", 0.95)
        self._add_edge("port_listening", "service_running", "causal", 0.90)
        self._add_edge("service_running", "service_available", "causal", 0.95)
        self._add_edge("service_unavailable", "model_unavailable", "causal", 0.90)
        self._add_edge("model_missing", "model_unavailable", "causal", 0.95)
        self._add_edge("service_available", "model_loadable", "conditional", 0.85)

        # === 错误与稳定性子系统 ===
        self._add_edge("system_error_present", "system_stability_risk", "causal", 0.75)
        self._add_edge("system_stability_risk", "system_performance_degradation", "causal", 0.60)
        self._add_edge("tpm_error", "system_stability_risk", "causal", 0.50)

        # === 进程子系统 ===
        self._add_edge("process_high_cpu", "cpu_high_usage", "causal", 0.95)
        self._add_edge("process_high_memory", "memory_high_usage", "causal", 0.90)

        # === 反向边（诊断推理）===
        self._add_edge("system_performance_degradation", "memory_pressure", "diagnostic", 0.85)
        self._add_edge("system_performance_degradation", "cpu_pressure", "diagnostic", 0.90)
        self._add_edge("system_performance_degradation", "disk_pressure", "diagnostic", 0.70)

    def get_neighbors(self, node: str) -> List[Tuple[str, str, float]]:
        return self.graph.get(node, [])

    def bfs_distance(self, start_nodes: List[str], max_depth: int = 3) -> Dict[str, Tuple[float, int, str]]:
        """
        从起始节点出发，计算到所有可达节点的距离。
        返回：{node: (累积权重, 跳数, 路径关系类型)}
        """
        distances = {}
        queue = deque()

        for start in start_nodes:
            if start in self.nodes:
                queue.append((start, 1.0, 0, "direct"))
                distances[start] = (1.0, 0, "direct")

        while queue:
            current, acc_weight, depth, relation = queue.popleft()
            if depth >= max_depth:
                continue

            for neighbor, rel_type, weight in self.graph.get(current, []):
                new_weight = acc_weight * weight
                new_depth = depth + 1

                if neighbor not in distances or distances[neighbor][0] < new_weight:
                    distances[neighbor] = (new_weight, new_depth, rel_type)
                    queue.append((neighbor, new_weight, new_depth, rel_type))

        return distances
