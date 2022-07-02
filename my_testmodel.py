class Gen:
    num = 0

    @classmethod
    def get(cls):
        cls.num += 1
        return cls.num


class MyGraphNode:
    def __init__(self) -> None:
        self.name = f"node{Gen.get()}"
        self.friends: list[MyGraphNode] = []

    def add_friend(self, node):
        self.friends.append(node)

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


node1 = MyGraphNode()
node2 = MyGraphNode()

node1.add_friend(node2)
print(node1.friends)

node2.name = "name2"
print(node1.friends)
