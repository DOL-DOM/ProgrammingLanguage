import sys
from lexical_analyzer import Lexer
from parser import Parser  

# cmd창에서 입력 받기, 인수가 2개 일 때만 실행
if len(sys.argv) != 2:
    sys.exit(1)

filename = sys.argv[1]

# txt파일 내용 가져옴
try:
    with open(filename, "r") as file:
        input_text = file.read()
except FileNotFoundError:
    print(f"Error: 파일 '{filename}'을(를) 찾을 수 없습니다.")
    sys.exit(1)

# Lexer와 Parser 초기화
lexer = Lexer(input_text)
parser = Parser(lexer)
parser.program()
parser.print_output_log()