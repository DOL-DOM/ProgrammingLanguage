from Node import Node
from TokenType import TokenType
from Lexer import Lexer
from anytree import RenderTree
import re
class Parser(Lexer):#파서 클래스
    def __init__(self, input_source, verbose=False, test=False):
        super().__init__(input_source, verbose=verbose)
        #테스트
        self.test = test  

    def factor(self, parent=None):
        """Factor 처리"""
        node = Node("FACTOR", parent=parent)

        if self.next_token == TokenType.LEFT_PAREN:
            self.lexical()
            nodeDone = self.expression(node)
           
            self.lexical()

        elif self.next_token in (TokenType.IDENT, TokenType.CONST):
            # 식별자 또는 상수 처리
            Node(TokenType.get_name(self.next_token), value=self.stringToken, parent=node)
            self.lexical()

        else:
            # 유효하지 않은 토큰 처리
            if self.next_token == TokenType.CONST:
                self.const_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.stringToken)]
            elif self.next_token == TokenType.IDENT:
                self.id_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.stringToken)]
            self.wrongChar()
            self.ErrorSyntax()

        return node

    def term(self, parent=None):
        """Term 처리"""
        node = Node("TERM", parent=parent)
        self.factor(node)

        while self.next_token == TokenType.MULT_OP:
            # 연산자 노드 추가
            operator_node = Node(TokenType.get_name(self.next_token), value=self.stringToken, parent=node)
            self.lexical()
            self.factor(node)

        return node
    
    def expression(self, parent=None):
        """Expression 처리"""
        node = Node("EXPRESSION", parent=parent)
        self.term(node)

        while self.next_token == TokenType.ADD_OP:
            # 연산자 노드 추가
            operator_node = Node(TokenType.get_name(self.next_token), value=self.stringToken, parent=node)
            self.lexical()
            self.term(operator_node)

        # 후위 순회로 RHS 생성
        RHS = node.preorder()
        term = ""
        for i in RHS:
            if re.fullmatch(r'^\d+$', i):
                term += i
            elif re.fullmatch(r'^\d+\.\d+$', i):
                term += i
            elif re.fullmatch(r'^-\d+$', i):
                term += i
            elif re.fullmatch(r'^-\d+\.\d+$', i):
                term += i
            elif i in "+-*/()":
                term += i
            elif i in self.symbolTable and self.symbolTable[i] != "Unknown":
                term += str(self.symbolTable[i])
            elif not i in self.symbolTable or self.symbolTable[i] == "Unknown":
                # 정의되지 않은 변수 참조 - 에러이지만 파싱 계속 진행
                error = "(Error) Undefined variable is referenced(" + i + ")"
                self.list_message.append(error)
                self.is_error = True
            else:
                error = "Error: Invalid expression"
                self.list_message.append(error)
                return node, "Unknown"

        # 결과 계산
        try:
            result = eval(term)
            node.value = str(result)
            if self.test:
                print(f"Result: {result}")
            return node, result
        except:
            return node, "Unknown"
        

    def program(self):
        root = Node("PROGRAM")
        self.statements(root)
        return root

    def run(self):
        self.lexical()
        tree = self.program()

        # tree
        if self.test:
            for pre, _, node in RenderTree(tree):
                print(f"{pre}{node.name}")

        #result
        if not self.verbose:
            result_message = "Result ==>"
            
            if not self.symbolTable or (len(self.symbolTable) == 1 and None in self.symbolTable):
                result_message += "no identifier! "
            else:
                result_message += "".join(f" {key}: {value};" for key, value in self.symbolTable.items() if key is not None)
            
            print(result_message)

    def statement(self, parent=None):
        """Statement 처리 함수"""
        node = Node("STATEMENT", parent=parent)

        if self.next_token == TokenType.IDENT:
            self.id_of_now_stmt = self.stringToken

            # 심볼 테이블 업데이트
            if self.stringToken not in self.symbolTable or self.symbolTable[self.stringToken] is None:
                self.symbolTable[self.stringToken] = "Unknown"

            Node("IDENT", value=self.stringToken, parent=node)
            lhs_id = self.stringToken
            self.lexical()

            # 이전 에러 처리
            if self.is_error:
                if self.next_token not in (TokenType.SEMI_COLON, TokenType.EOF):
                    self.goNext()
                    self.lexical()
                return node

            # ASSIGN_OP 처리
            if self.next_token == TokenType.ASSIGN_OP:
                if self.opAndAssign():  # ASSIGN_OP 관련 에러 발생 시 처리
                    self.goNext()
                    return node
            else:
                # 형식 오류: <ident><assignment_op><expression> 형식이 아님
                error = "(Error) Missing assignment operator"
                self.list_message.append(error)
                self.symbolTable[lhs_id] = "Unknown"
                self.is_error = True
                self.goNext()
                if self.next_token not in (TokenType.SEMI_COLON, TokenType.EOF):
                    self.lexical()
                return node

            Node("ASSIGN_OP", value=self.stringToken, parent=node)
            self.lexical()

            # Expression 처리
            if not self.is_error:
                tmp_node, result = self.expression(node)
                self.symbolTable[lhs_id] = result
            else:
                self.symbolTable[lhs_id] = "Unknown"

        return node
 

    def statements(self, parent=None):
        node = Node("Statements", parent=parent)

        while self.next_token != TokenType.EOF:
            # 처리할 statement 노드 생성
            self.statement(node)
            # 세미콜론
            if self.next_token == TokenType.SEMI_COLON:  
                Node("SEMI_COLON", value=self.stringToken, parent=node)

                if not self.verbose:
                    self.end_of_stmt()

                # last statement
                if self.index == len(self.source):
                    warning = "(Warning) There is semicolon at the end of the program ==> ignoring semicolon"
                    self.listMessage.append(warning)
                    self.isWarning = True
                    self.now_stmt = self.now_stmt[:-1]

                self.lexical()
            # EOF
            elif self.next_token == TokenType.EOF:  
                if not self.verbose:
                    self.end_of_stmt()
                break
            #Error
            else:  
                if self.stringToken == ")":  # 괄호 누락 에러
                    error = "(Error) Missing left parenthesis"
                    self.listMessage.append(error)
                    self.is_error = True
                    self.symbolTable[self.id_of_now_stmt] = "Unknown"
                    self.goNext()
                    if not self.verbose:
                        self.end_of_stmt()
                    self.lexical()
                    continue

                # 이전 에러로 인한 건너뛰기
                if self.is_error:
                    continue

                # 기타 에러 처리
                if self.next_token == TokenType.CONST:
                    self.const_cnt -= 1
                    self.now_stmt = self.now_stmt[:-len(self.stringToken)]
                elif self.next_token == TokenType.IDENT:
                    self.id_cnt -= 1
                    self.now_stmt = self.now_stmt[:-len(self.stringToken)]

                self.wrongChar()
                self.ErrorSyntax()

                if not self.verbose:
                    self.end_of_stmt()

                self.lexical()

        # 마지막 남은 statement 처리
        if self.now_stmt:
            if not self.verbose:
                self.end_of_stmt()

        return node



