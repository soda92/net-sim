"""Information models"""
import enum
import types
import networkx as graph_tools


def gen_number(_static=types.SimpleNamespace(counter=0)):
    "number generator"
    _static.counter += 1
    return _static.counter


class Info(enum.Enum):
    "Information types"
    INFO_S = enum.auto()
    INFO1 = enum.auto()
    INFO2 = enum.auto()
    INFO3 = enum.auto()
    INFO4 = enum.auto()
    INFO5 = enum.auto()


class MyGraphNode:  # pylint: disable=too-many-instance-attributes
    """Graph nodes"""

    def __init__(self):
        self.name = f"node#{gen_number()}"
        self.node_state: Info = Info.INFO_S
        self.active: float = 0
        self.mass_frag: list[Info] = []  # 已知的信息片段列表，初始为空
        self.mass_count: float = 0  # 信息耦合值
        self.mass_rarity: float = 0  # 信息稀有性
        self.node_emotion_self: float = 0  # 自我认知产生的情感值
        self.node_emotion_neighbor: float = 0  # 周围邻居节点对节点i的情绪值的影响
        self.emotion_value: float = 0  # 情感值
        self.neighbors: list[MyGraphNode] = []

    def add_neighbor(self, neighbor):
        "as name described"
        self.neighbors.append(neighbor)

    def __repr__(self):
        return self.name


class MyGraph:
    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    node1 = MyGraphNode()
    node2 = MyGraphNode()

    node1.add_neighbor(node2)
    print(node1.neighbors)

    node2.name = "name"

    print(node1.neighbors)
