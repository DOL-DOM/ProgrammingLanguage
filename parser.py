from Node import Node
from TokenType import TokenType
from Lexer import Lexer
from anytree import RenderTree
import re
class Parser(Lexer):#파서 클래스
    def __init__(self, input_source, verbose=False, test=False):#파서 생성자
        super().__init__(input_source, verbose=verbose)

        if input_source.replace(" ", "") == "":#입력받은 소스코드가 공백만 있을 때 - error
            error = "(Error) Grammer of this LL(1) parser cannot generate empty source code"
            self.listMessage.append(error)
            self.is_error = True
            self.end_of_stmt()
        self.test = test  # 파싱이 정상적으로 되었는지 확인하기 위한 트리 출력, 변수에 대입할 값이 제대로 계산되었는지 확인

    def factor(self, parent=None):
        """Factor 처리"""
        node = Node("FACTOR", parent=parent)

        if self.next_token == TokenType.LEFT_PAREN:
            self.lexical()
            expr_node = self.expression(node)
            if self.next_token != TokenType.RIGHT_PAREN:
                # 오른쪽 괄호가 없을 때 - 경고 메시지 추가
                self.is_warning = True
                warning = "(Warning) Missing right parenthesis ==> assuming right parenthesis at the end of statement"
                self.listMessage.append(warning)

                # 오른쪽 괄호를 가정하고 진행
                if self.next_token == TokenType.SEMI_COLON:
                    self.now_stmt = self.now_stmt[:-1] + ");"
                    self.next_token = TokenType.RIGHT_PAREN
                    if self.verbose:
                        self.print_v()
                    self.next_token = TokenType.SEMI_COLON
                    if self.verbose:
                        self.print_v()
                elif self.next_token == TokenType.EOF:
                    self.now_stmt = self.now_stmt + ")"
                    self.next_token = TokenType.RIGHT_PAREN
                    if self.verbose:
                        self.print_v()
                    self.next_token = TokenType.EOF
                    if self.verbose:
                        self.print_v()
                return node
            self.lexical()

        elif self.next_token in (TokenType.IDENT, TokenType.CONST):
            # 식별자 또는 상수 처리
            Node(TokenType.get_name(self.next_token), value=self.token_string, parent=node)
            self.lexical()

        else:
            # 유효하지 않은 토큰 처리
            if self.next_token == TokenType.CONST:
                self.const_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.token_string)]
            elif self.next_token == TokenType.IDENT:
                self.id_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.token_string)]
            self.after_invalid_char()
            self.syntax_error()

        return node

    def term(self, parent=None):
        """Term 처리"""
        node = Node("TERM", parent=parent)
        self.factor(node)

        while self.next_token == TokenType.MULT_OP:
            # 연산자 노드 추가
            operator_node = Node(TokenType.get_name(self.next_token), value=self.token_string, parent=node)
            div = (self.token_string == "/")
            self.lexical()

            if div and self.next_token == TokenType.CONST and self.token_string == "0":
                # 0으로 나누기 오류 처리
                error = "(Error) Invalid expression - division by zero"
                self.listMessage.append(error)
                self.is_error = True
            elif div and self.next_token == TokenType.IDENT:
                if self.token_string in self.symbolTable and self.symbolTable[self.token_string] == 0:
                    error = "(Error) Invalid expression - division by zero"
                    self.listMessage.append(error)
                    self.is_error = True

            self.factor(node)

        return node


    def term_tail(self, parent=None):
        node = Node("TERM_TAIL", parent=parent)
        while self.next_token == TokenType.ADD_OP:
            Node(TokenType.get_name(self.next_token), value=self.token_string, parent=node)
            self.lexical()
            self.term(node)
        return node
    
    def expression(self, parent=None):
        node = Node("EXPRESSION", parent=parent)
        self.term(node)
        self.term_tail(node)

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
                #정의되지 않은 변수 참조 - error - 에러이긴 하지만 syntax error가 아니라 semantic error이므로 파싱은 계속 진행
                error = "(Error) Undefined variable is referenced(" + i + ")"
                self.list_message.append(error)
                self.is_error = True
            else:
                error = "Error: Invalid expression"
                self.list_message.append(error)
                return node, "Unknown"
        try:
            result = eval(term)
            node.value = str(result)
            if(self.test):print(f"Result: {result}")
            return node, result
        except:
            return node, "Unknown"
        
    def statement(self, parent=None):
        """Statement 처리 함수"""
        node = Node("STATEMENT", parent=parent)

        if self.next_token == TokenType.IDENT:
            self.id_of_now_stmt = self.token_string

            # 심볼 테이블 업데이트
            if self.token_string not in self.symbolTable or self.symbolTable[self.token_string] is None:
                self.symbolTable[self.token_string] = "Unknown"

            Node("IDENT", value=self.token_string, parent=node)
            lhs_id = self.token_string
            self.lexical()

            # 이전 에러 처리
            if self.is_error:
                if self.next_token not in (TokenType.SEMI_COLON, TokenType.EOF):
                    self.goNext()
                    self.lexical()
                return node

            # ASSIGN_OP 처리
            if self.next_token == TokenType.ASSIGN_OP:
                if self.op_after_assign_op():  # ASSIGN_OP 관련 에러 발생 시 처리
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

            Node("ASSIGN_OP", value=self.token_string, parent=node)
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
                Node("SEMI_COLON", value=self.token_string, parent=node)

                if not self.verbose:
                    self.end_of_stmt()

                # last statement
                if self.index == len(self.source):
                    warning = "(Warning) There is semicolon at the end of the program ==> ignoring semicolon"
                    self.listMessage.append(warning)
                    self.is_warning = True
                    self.now_stmt = self.now_stmt[:-1]

                self.lexical()
            # EOF
            elif self.next_token == TokenType.EOF:  
                if not self.verbose:
                    self.end_of_stmt()
                break
            #Error
            else:  
                if self.token_string == ")":  # 괄호 누락 에러
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
                    self.now_stmt = self.now_stmt[:-len(self.token_string)]
                elif self.next_token == TokenType.IDENT:
                    self.id_cnt -= 1
                    self.now_stmt = self.now_stmt[:-len(self.token_string)]

                self.after_invalid_char()
                self.syntax_error()

                if not self.verbose:
                    self.end_of_stmt()

                self.lexical()

        # 마지막 남은 statement 처리
        if self.now_stmt:
            if not self.verbose:
                self.end_of_stmt()

        return node


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
