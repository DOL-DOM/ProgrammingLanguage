import sys
from lexical_analyzer import Lexer
from parser import Parser  

# cmd창에서 입력 받기, 인수는 최소 2개 이상
if len(sys.argv) < 2:
    print("사용법 예시: python main.py [-v] [-t] <filename>, -v, -t는 옵션")
    sys.exit(1)


v = "-v" in sys.argv  # -v option
t = "-t" in sys.argv  # -t option
#파서 파일명
filename = sys.argv[-1]

# txt파일 내용 가져옴
try:
    with open(filename, "r", encoding="utf-8") as file:
        input_text = file.read().strip()  # 파일 끝의 공백/개행 제거
except FileNotFoundError:
    print(f"Error: 파일 '{filename}'을(를) 찾을 수 없습니다.")
    sys.exit(1)

# Lexer와 Parser 초기화
lexer = Lexer(input_text) # Lexer 인스턴스 생성
parser = Parser(lexer, verbose=v, test=t) # Parser 인스턴스 생성
parser.program()  # program() 메서드를 통해 파싱 시작
parser.print_output_log()  # 파싱 결과 출력
print(parser.parse_tree)