#정수 변수 next_token, 문자열 변수 token_string, 함수 lexical()을 포함하여야 한다
# lexical()은 입력 스트림을 분석하여 하나의 lexeme을 찾아낸 뒤, 그것의 token type을 next_token에 저장하고, lexeme 문자열을 token_string에 저장하는 함수

# Token types
IDENT = 'IDENT'
CONST = 'CONST'
ASSIGN_OP = 'ASSIGN_OP'
ADD_OP = 'ADD_OP'
MULT_OP = 'MULT_OP'
SEMI_COLON = 'SEMI_COLON'
LEFT_PAREN = 'LEFT_PAREN'
RIGHT_PAREN = 'RIGHT_PAREN'
ERROR = 'ERROR'
EOF = 'EOF'

# Token class
class Token:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value

    def __str__(self):
        return f'Token({self.type}, {self.value})'

    def __repr__(self):
        return self.__str__()
    

# Lexer, 토큰 단위로 속성 정의하여 parser에게 전달
class Lexer:
    def __init__(self, input_text):
        self.text = input_text
        self.pos = 0
        self.current_char = self.text[self.pos]

    def advance(self):
        self.pos += 1
        if self.pos < len(self.text):
            self.current_char = self.text[self.pos]
        else:
            self.current_char = None

    def get_next_token(self):
        while self.current_char is not None:
            if self.current_char.isspace():
                self.advance()
                continue
            if self.current_char.isalpha():
                ident = self.current_char
                self.advance()
                while self.current_char and self.current_char.isalnum():
                    ident += self.current_char
                    self.advance()
                return Token(IDENT, ident)
            if self.current_char.isdigit():
                num = self.current_char
                self.advance()
                while self.current_char and self.current_char.isdigit():
                    num += self.current_char
                    self.advance()
                return Token(CONST, int(num))
            if self.current_char == ':':
                self.advance()
                if self.current_char == '=':
                    self.advance()
                    return Token(ASSIGN_OP, ':=')
            if self.current_char == '+':
                self.advance()
                return Token(ADD_OP, '+')
            if self.current_char == '*':
                self.advance()
                return Token(MULT_OP, '*')
            if self.current_char == ';':
                self.advance()
                return Token(SEMI_COLON, ';')
            if self.current_char == '(':
                self.advance()
                return Token(LEFT_PAREN, '(')
            if self.current_char == ')':
                self.advance()
                return Token(RIGHT_PAREN, ')')
            self.advance()
            return Token(ERROR, self.current_char)
        return Token(EOF)
