#LL(1) 문법 검사
# Recursive Descent Parsing의 input을 구문 분석
# 소스 코드의 문법 검사
# 유효성 검사 
# 심볼 테이블을 업데이트

from lexical_analyzer import Lexer
from tokentype import Tokentype, Token
from node import Node

# Token types
LEFT_PAREN = 'LEFT_PAREN'
RIGHT_PAREN = 'RIGHT_PAREN'
EOF = 'EOF'
SEMI_COLON = 'SEMI_COLON'
IDENT = 'IDENT'
ASSIGN_OP = 'ASSIGN_OP'
ADD_OP = 'ADD_OP'
MULT_OP = 'MULT_OP'
CONST = 'CONST'

#lexer에서 받은 토큰을 구조적으로 나타냄 + 검사
class Parser:
    def __init__(self, lexer, verbose=False, test=False):
        self.lexer = lexer  #객체 저장, 토큰 가져옴
        self.current_token = self.lexer.lexical() #현재 처리 중인 토큰(Token 객체)을 저장
        self.symbol_table = {}  #변수 이름과 값을 저장하는 테이블
        self.output_log = []    #Parsing 결과 저장
        self.current_line = ""
        self.parse_tree = Node("Program")  # 파스 트리의 루트 노드
        self.verbose = verbose  # 디버깅 모드 (-v 옵션)
        self.test = test  # 테스트 모드 (-t 옵션)

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            if self.verbose:
                print(f"Eating token: {self.current_token}")
            self.current_line += f"{self.current_token[1]} "  # 값은 튜플의 두 번째 요소
            self.current_token = self.lexer.lexical()
            
        else:
            self.output_log.append(f"Error! Expected: {token_type} Now: {self.current_token[0]}")

def build_parse_tree(self):
    #파스 트리를 출력
    if self.parse_tree is None:
        print("No parse tree available.")
        return
    print("Parse Tree:")
    for pre, fill, node in RenderTree(self.parse_tree):
        print(f"{pre}{node.name}")

def expression(self, parent_node):
    # Term 노드 생성
    term_node = self.term(parent_node)
    
    # ADD_OP 처리
    while self.current_token.type == Tokentype.ADD_OP:
        op_node = ParseTreeNode(f"ADD_OP({self.current_token.value})", parent=parent_node)
        self.eat(Tokentype.ADD_OP)
        right_term = self.term(op_node)
        op_node.children = [term_node, right_term]
        term_node = op_node

        return term_node

    def program(self):
        iteration = 0
        while self.current_token.type != Tokentype.EOF:
            print(f"DEBUG: Current token before statement: {self.current_token.type} ({self.current_token.value})")
            self.statements()
            print(f"DEBUG: Current token after statement: {self.current_token.type} ({self.current_token.value})")
            iteration += 1
            if iteration > 1000:  # 안전 장치: 1000번 이상 반복 시 강제 중단
                raise RuntimeError("Infinite loop detected in program()!")
            print("DEBUG: Program completed. EOF reached.")
        self.output_log.append("Parsing completed successfully! ")  #파싱 성공 append
        self.output_log.append("Symbol Table Result ==> " + "; ".join(f"{k}: {v}" for k, v in self.symbol_table.items()) + ";") #심볼 테이블 출력
        self.build_parse_tree() 

    def statements(self):
        # EOF에 도달하면 루프 종료
        while self.current_token.type != Tokentype.EOF:
            self.statement()
        #연속된 세미콜론 처리
        while self.current_token.type == SEMI_COLON and self.current_token.type != EOF:
            self.eat(SEMI_COLON)


    def statement(self):
        self.current_line = ""
        id_count, const_count, op_count = 0, 0, 0
        print(f"DEBUG: Current token: {self.current_token}")  # 디버깅 정보 추가
        
        # Statement 노드 생성
        statement_node = ParseTreeNode("Statement", parent=self.parse_tree)

        # 1. EOF 처리
        if self.current_token.type == Tokentype.EOF:
            print("DEBUG: End of File reached.")
            return   # EOF 처리 후 종료
        
        # 2. IDENT 처리
        elif self.current_token.type == Tokentype.IDENT:
            var_name = self.current_token.value
            self.eat(IDENT)
            id_count += 1
            self.eat(ASSIGN_OP)
            value = self.expression(id_count, const_count, op_count)
            self.symbol_table[var_name] = value
            self.log_statement(var_name, id_count, const_count, op_count)
            #Parsing 중 statement 함수 끝나면 로그 추가, 각 단계 결과 및 오류 확인 가능
            ParseTreeNode(f"IDENT({self.current_token.value})", parent=statement_node)

        # 3. CONST 처리
        elif self.current_token.type == Tokentype.CONST:
            self.eat(CONST)

        # 4. LEFT_PAREN, RIGHT_PAREN 처리
        elif self.current_token.type == Tokentype.LEFT_PAREN:
            self.eat(LEFT_PAREN)
            value = self.expression(id_count, const_count, op_count)
            self.eat(RIGHT_PAREN)

        # 5. ADD_OP 처리
        elif self.current_token.type == Tokentype.ADD_OP:
            self.eat(ADD_OP)

        # 6. MULT_OP 처리
        elif self.current_token.type == Tokentype.MULT_OP:
            self.eat(MULT_OP)

        # 7. SEMI_COLON 처리
        elif self.current_token.type == Tokentype.SEMI_COLON:
            self.eat(SEMI_COLON)

        # 8. UNKNOWN 처리
        elif self.current_token.type == Tokentype.UNKNOWN:
            self.eat(Tokentype.UNKNOWN)

        # 9. EOF 처리
        elif self.current_token.type == Tokentype.EOF:
            self.eat(Tokentype.EOF)

        # 10. 그 외 예외 처리
        else:
            raise Exception(f"Syntax Error: What is this token? {self.current_token.type} ({self.current_token.value})")

#_________________________________________________________________

    def expression(self, id_count, const_count, op_count):
        left_value = self.term(id_count, const_count, op_count)
        while self.current_token.type == ADD_OP:
            op = self.current_token.value
            self.eat(ADD_OP)

            op_count += 1
            if self.current_token.type == ADD_OP:
                self.output_log.append('(Warning) "중복 연산자(+) 제거"')
                self.eat(ADD_OP)  # 중복된 연산자를 무시
            right_value = self.term(id_count, const_count, op_count)
            left_value = self.evaluate_op(left_value, op, right_value)
        return left_value

    def term(self, id_count, const_count, op_count):
        left_value = self.factor(id_count, const_count, op_count)
        while self.current_token.type == MULT_OP:
            op = self.current_token.value
            self.eat(MULT_OP)
            op_count += 1
            right_value = self.factor(id_count, const_count, op_count)
            left_value = self.evaluate_op(left_value, op, right_value)
        return left_value

    def factor(self, id_count, const_count, op_count):
        if self.current_token.type == IDENT:
            var_name = self.current_token.value
            self.eat(IDENT)
            id_count += 1
            if var_name in self.symbol_table:
                return self.symbol_table[var_name]
            else:
                self.output_log.append(f"(Error) Undefined variable referenced:({var_name})가 참조됨")
                return "Unknown"
        elif self.current_token.type == CONST:
            value = int(self.current_token.value)
            self.eat(CONST)
            const_count += 1
            return value
        elif self.current_token.type == LEFT_PAREN:
            self.eat(LEFT_PAREN)
            value = self.expression(id_count, const_count, op_count)
            self.eat(RIGHT_PAREN)
            return value
        else:
            raise Exception(f"Unexpected token in factor: {self.current_token}")

    def evaluate_op(self, left, op, right):
        if left == "Unknown" or right == "Unknown":
            return "Unknown"
        if op == "+":
            return left + right
        elif op == "*":
            return left * right

    def log_statement(self, var_name, id_count, const_count, op_count):
        # 로그에 출력 형식에 맞게 기록
        log_entry = f"Program Line: {self.current_line.strip()}"
        log_entry += f"\nID: {id_count}; CONST: {const_count}; OP: {op_count};"
        if not self.test:  # 테스트 모드가 아니면 정상 처리 로그만 출력
            log_entry += "\n(OK)"
        self.output_log.append(log_entry)

    def print_output_log(self):
        for log in self.output_log:
            print(log)

