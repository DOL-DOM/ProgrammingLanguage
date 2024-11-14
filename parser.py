#LL(1) 문법 검사
# Recursive Descent Parsing 

from lexical_analyzer import Lexer

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
        self.lexer = lexer
        self.current_token = lexer.get_next_token()
        self.symbol_table = {}
        self.output_log = []    #Parsing 결과 저장
        self.current_line = ""

    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.current_line += f"{self.current_token.value} "
            self.current_token = self.lexer.get_next_token()
        else:
            self.output_log.append(f"(Error) Expected token {token_type} but got {self.current_token.type}")

    def program(self):
        while self.current_token.type != EOF:
            self.statements()
            self.output_log.append("Parsing completed successfully")
            self.output_log.append("Result ==> " + "; ".join(f"{k}: {v}" for k, v in self.symbol_table.items()) + ";")
            self.build_parse_tree()

    def statements(self):
        self.statement()
        while self.current_token.type == SEMI_COLON:
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
                self.output_log.append(f"(Error) 정의되지 않은 변수({var_name})가 참조됨")
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
            raise Exception("Syntax Error")

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

