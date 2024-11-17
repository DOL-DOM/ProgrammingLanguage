import sys
import os
from parser import Parser

# cmd창에서 입력 받기, 인수는 최소 2개 이상
if len(sys.argv) < 2:
    print("사용법 예시: python main.py [-v] [-t] <filename>, -v, -t는 옵션")
    sys.exit(1)


v = "-v" in sys.argv # -v 
t = "-t" in sys.argv # -t 테스트 트리
file = sys.argv[-1] 
 

try:
    #파일 읽기
    with open(file, "r", encoding="utf-8") as file:
        read = file.read()
        if len(read)>=1 and read[-1] == '\n': read = read[:-1] #마지막 개행 문자 제거
        start = Parser(read, verbose=v, test=t) #verbose: -v 옵션, test: 트리, 변수에 대입할 값 출력
        start.run()    
except FileNotFoundError:
    print(f'{file} No such file!')
    sys.exit(1)