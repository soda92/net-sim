"tests for my_model"
from my_model import MyGraphNode


def test_simple_node():
    "graph reference"
    node1 = MyGraphNode(1)
    node2 = MyGraphNode(2)

    node1.add_neighbor(node2)
    assert str(node1.neighbors) == "[node#2]"

    node2.name = "name"

    assert str(node1.neighbors) == "[name]"
