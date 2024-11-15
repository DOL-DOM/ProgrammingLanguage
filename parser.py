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
    def __init__(self, lexer):
        self.lexer = lexer  #객체 저장, 토큰 가져옴
        self.current_token = self.lexer.lexical() #현재 처리 중인 토큰(Token 객체)을 저장
        self.symbol_table = {}  #변수 이름과 값을 저장하는 테이블
        self.output_log = []    #Parsing 결과 저장
        self.current_line = ""
        self.parse_tree = Node("Program")  # 파스 트리의 루트 노드

    def eat(self, token_type):
        if self.current_token[0] == token_type:
            self.current_line += f"{self.current_token[1]} "  # 값은 튜플의 두 번째 요소
            self.current_token = self.lexer.lexical()
            
        else:
            self.output_log.append(f"Error! Expected: {token_type} Now: {self.current_token[0]}")

    def build_parse_tree(self):
        """파스 트리를 출력"""
        print("Parse Tree:")
        print(self.parse_tree)

    def program(self):
        while self.current_token[0] != EOF:
            self.statements()
        self.output_log.append("Parsing completed successfully! ")  #파싱 성공 append
        self.output_log.append("Symbol Table Result ==> " + "; ".join(f"{k}: {v}" for k, v in self.symbol_table.items()) + ";") #심볼 테이블 출력
        self.build_parse_tree() 

    def statements(self):
        self.statement()
        while self.current_token[0] == SEMI_COLON:
            self.eat(SEMI_COLON)
            self.statement()

    def statement(self):
        self.current_line = ""
        id_count, const_count, op_count = 0, 0, 0
        if self.current_token.type == IDENT:
            var_name = self.current_token.value
            self.eat(IDENT)
            id_count += 1
            self.eat(ASSIGN_OP)
            value = self.expression(id_count, const_count, op_count)
            self.symbol_table[var_name] = value
            self.log_statement(var_name, id_count, const_count, op_count)
            #Parsing 중 statement 함수 끝나면 로그 추가, 각 단계 결과 및 오류 확인 가능

        else:
            raise Exception("Syntax Error: unexpected IDENT")

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
        log_entry = f"프로그램에서 읽은 라인: {self.current_line.strip()}"
        log_entry += f"\nID: {id_count}; CONST: {const_count}; OP: {op_count};"
        log_entry += "\n(OK)"
        self.output_log.append(log_entry)

    def print_output_log(self):
        for log in self.output_log:
            print(log)

