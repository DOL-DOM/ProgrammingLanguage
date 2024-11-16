#정수 변수 next_token, 문자열 변수 token_string, 함수 lexical()을 포함하여야 한다
# lexical()은 입력 스트림을 분석하여 하나의 lexeme을 찾아낸 뒤, 
#그것의 token type을 next_token에 저장하고, lexeme 문자열을 token_string에 저장하는 함수
import re
from tokentype import Tokentype, Token

class Lexer:
    def __init__(self, input_text):
        self.input_text = input_text
        self.tokens = []
        self.current_position = 0
        self.next_token = None       # 현재 토큰 타입
        self.token_string = None      # 현재 토큰 값
        self.tokenize()

#tokenize(): 입력을 토큰 리스트로 반환
    def tokenize(self):
        # 토큰 유형, 정규 표현식 패턴 대응 리스트
        token_specification = [
            ('NUMBER', r'\d+'),          # 정수
            ('IDENT', r'[A-Za-z_]\w*'),  # 변수 식별자
            ('ASSIGN', r':='),           # 할당 연산자 :=
            ('PLUS', r'\+'),             # 덧셈 연산자 +
            ('MINUS', r'-'),             # 뺄셈 연산자 -
            ('MUL', r'\*'),              # 곱셈 연산자 *
            ('DIV', r'/'),               # 나눗셈 연산자 /
            ('SEMI', r';'),              # 세미콜론 ;
            ('LPAREN', r'\('),           # 왼쪽 괄호 (
            ('RPAREN', r'\)'),           # 오른쪽 괄호 )
            ('SKIP', r'[ \t\n]+'),         # 공백, 탭, 개행 (무시)
            ('MISMATCH', r'.'),          # 잘못된 문자 (오류 처리)
        ]

        # 정규 표현식을 하나의 패턴으로 컴파일
        # | 연산자로 여러 정규 표현식을 하나로 병합
        tok_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specification)
        get_token = re.compile(tok_regex).match
        pos = 0


# ###type = match.lastgroup  #토큰 타입 ( NUMBER, IDENT, ASSIGN, SKIP 등)
#                 value = match.group(type) #Lexeme 타입 (42, x, := 등) 
        while pos < len(self.input_text):
            #특정 위치 pos 에서 입력 텍스트 매칭
            match = get_token(self.input_text, pos)
            #1.  매칭 실패
            if match is None:
                print(f"DEBUG: (1)Unexpected character at position {pos}: '{self.input_text[pos]}'")
                raise RuntimeError(f'(2)Unexpected character at position {pos}')
            #2. 매칭 성공
            else:
                type = match.lastgroup  #토큰 타입 ( NUMBER, IDENT, ASSIGN, SKIP 등)
                value = match.group(type) #Lexeme 타입 (42, x, := 등)
                print(f"Match found - type: {type}, value: {value}")       
                if type == 'NUMBER':
                    value = int(value)  # 숫자 (숫자는 int로 저장)
                elif type == 'SKIP':    #공백
                    pos = match.end()
                    continue
                elif type == 'MISMATCH':  # 처리되지 않은 문자
                    print(f"(3)DEBUG: MISMATCH at position {pos}: '{value}'")
                    raise RuntimeError(f'(4)Unexpected character at position {pos}: {value}')
                #토큰 타입을 Tokentype 열거형으로 변환
                token_type = getattr(Tokentype, type, Tokentype.UNKNOWN)
                #토큰 추가
                if token_type == Tokentype.CONST:
                    value = int(value)
                    self.tokens.append(Token(token_type, value))
                pos = match.end()
            
            
#Parser에서 lexical() 함수 호출
# 1)입력 스트림 분석, 찾아낸 lexeme의 token type을 next_token에 저장
# 2)lexeme 문자열을 token_string에 저장
# 3)내부 변수 current_position을 사용해 다음 토큰으로 이동
    def lexical(self):
        """다음 토큰을 찾고, next_token과 token_string에 저장"""
        if self.current_position < len(self.tokens):
            token_type, value = self.tokens[self.current_position]
            self.current_position += 1
            return Token(token_type, value)  # 현재 토큰 반환
        else:
            self.next_token, self.token_string = 'EOF', 'EOF'  # 파일의 끝에 도달 시 EOF 반환
            return Token(Tokentype.EOF, None)  # EOF 토큰 반환
    def peek_token(self):
        """현재 토큰을 확인하지만 위치를 이동하지 않음"""
        if self.current_position < len(self.tokens):
            return self.tokens[self.current_position]
        else:
            return Tokentype('EOF', 'EOF')
