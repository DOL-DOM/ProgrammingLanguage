class Node:
    def __init__(self, name, children=None):
        self.name = name  # 노드 이름 (e.g., "Expression", "Statement")
        self.children = children if children else []  # 자식 노드 리스트

    def add_child(self, child):
        """자식 노드를 추가"""
        self.children.append(child)

    def __repr__(self, level=0):
        """트리 구조를 보기 좋게 출력"""
        ret = " " * (level * 4) + f"{self.name}\n"
        for child in self.children:
            ret += child.__repr__(level + 1)
        return ret
