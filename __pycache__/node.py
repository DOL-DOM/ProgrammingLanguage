from anytree import AnyNode
class Node(AnyNode):
    def __init__(Node, type, value=None, parent=None): 
        super().__init__(parent=parent)
        Node.type = type
        Node.value = value
        #노드의 속성 1)type 2)value

  #문자열 제시
    def __repr__(Node):
        return f"{Node.value} (Type: {Node.type})"
  
#arr 리스트에 자식 순회 결과 저장
# 1)Node.value is not None이면, 현재 노드 값을 결과 리스트에 추가, 자식 순회
# 2) 모든 자식노드 preorder()로 arr 에 추가
# 3) None이면 Node.value 추가 x, 자식 노드들의 결과만 수집하여 반환
    def preorder(Node):
        return (
            [Node.value] + [val for child in Node.children for val in child.preorder()]
            if Node.value is not None
            else [val for child in Node.children for val in child.preorder()]
        )

    #결과: 노드 값들의 순서, 리스트로 반환
    #ex) ['x', ':=', '1', '+', '2', '*', '3']