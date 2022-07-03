"""Information models"""
import enum
import random
import networkx as graph_tools


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

    def __init__(self, id_: int):
        self.id_ = id_
        self.name = f"node#{id_}"
        self.node_state: Info = Info.INFO_S
        self.node_state_next: Info = Info.INFO_S
        self.active: float = 0

        self.mass_frag: list[Info] = []
        "已知的信息片段列表，初始为空"
        self.mass_count: float = 0
        "信息耦合值"
        self.mass_rarity: float = 0
        "信息稀有性"
        self.node_emotion_self: float = 0
        "自我认知产生的情感值"
        self.node_emotion_neighbor: float = 0
        "周围邻居节点对节点i的情绪值的影响"
        self.emotion_value: float = 0
        "情感值"
        self.neighbors: list[MyGraphNode] = []

    def add_neighbor(self, neighbor):
        "as name described"
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
        if self not in neighbor.neighbors:
            neighbor.neighbors.append(self)

    def __repr__(self):
        return self.name


def info_list_to_str(info_list: list[Info]) -> str:
    "convert list of info to string"
    return ",".join(map(lambda x: x.name, info_list))


def str_to_info_list(string: str) -> list[Info]:
    "from string construct list of info"
    return list(map(lambda x: Info[x], string.split(",")))


class MyGraph:
    "My Graph"

    def __init__(self) -> None:
        self.nodes: list[MyGraphNode] = None
        "nodes"

    def create_graph(self, num_nodes, minium_edges_per_node):
        "create random graph use barabasi_albert method"
        nx_graph: graph_tools.Graph = (
            graph_tools.generators.random_graphs.barabasi_albert_graph(
                n=num_nodes, m=minium_edges_per_node
            )
        )
        self.nodes = [MyGraphNode(id_=i) for i in range(num_nodes)]
        for edge in nx_graph.edges():
            first, second = edge
            self.nodes[first].add_neighbor(self.nodes[second])

    def to_nx_graph(self) -> graph_tools.Graph:
        "convert to networkx graph format"
        nx_graph = graph_tools.Graph()
        for index, node in enumerate(self.nodes):
            nx_graph.add_node(index)
            nx_node = nx_graph.nodes[index]
            nx_node["source"] = node.name
            nx_node["node_state"] = node.node_state.name
            nx_node["active"] = node.active
            nx_node["mass_frag"] = info_list_to_str(node.mass_frag)
            nx_node["mass_count"] = node.mass_count
            nx_node["mass_rarity"] = node.mass_rarity
            nx_node["node_emotion_self"] = node.node_emotion_self
            nx_node["node_emotion_neighbor"] = node.node_emotion_neighbor
            nx_node["emotion_value"] = node.emotion_value

        for node in self.nodes:
            for neighbor in node.neighbors:
                nx_graph.add_edge(node.id_, neighbor.id_)
        return nx_graph

    # def from_nx_graph(self, nx_graph: graph_tools.Graph):
    #     self.nodes = [MyGraphNode(id_=i) for i in range(len(nx_graph.nodes))]

    def clock(self):
        "spread one time"
        for node in self.nodes:
            if node.node_state != Info.INFO_S:
                for neighbor in node.neighbors:
                    spread_rate = 0.5
                    if random.random() > spread_rate:
                        neighbor.node_state_next = node.node_state
        for node in self.nodes:
            if node.node_state_next != Info.INFO_S:
                node.node_state = node.node_state_next
                node.node_state_next = Info.INFO_S

    def clockn(self, times: int):
        "spread n times"
        for _ in range(times):
            self.clock()


if __name__ == "__main__":
    mygraph = MyGraph()
    mygraph.create_graph(num_nodes=100, minium_edges_per_node=3)
    mygraph.nodes[0].node_state = Info.INFO1
    mygraph.clockn(3)
    converted = mygraph.to_nx_graph()
    graph_tools.write_graphml(G=converted, path="converted.graphml")
