from TokenType import TokenType
import re


class Lexer:
    def __init__(self, input_source, verbose=False):
        self.source = input_source  
        self.index = 0  
        self.verbose = verbose  # -v
        self.stringToken = ""  # string of current token
        self.next_token = None  # type of next token
        self.before_token = None  # token before 
        self.id_cnt = 0  # 각 statement의 id, const, op의 개수
        self.const_cnt = 0
        self.op_cnt = 0
        self.symbolTable = {}  # symbol table
        self.id_of_now_stmt = None  # statement의 id
        self.now_stmt = ""  # statement
        self.listMessage = []  # saved message list
        self.is_error = False  # Error
        self.is_warning = False  # Warning

    def printV(self):
        """현재 토큰 정보 (-v 에서만)"""
        if self.verbose:
            print(f"{self.next_token} ({TokenType.get_name(self.next_token)})")

    def ErrorSyntax(self):
        """구문 오류를 처리"""
        error_message = (
            "(Error) Syntax error - invalid token"
        )
        
        # 현재 토큰 상태를 UNKNOWN으로 변경하여 오류 처리
        original_token = self.next_token
        self.next_token = TokenType.UNKNOWN
        
        # verbose 모드에 따라 출력
        self.printV()
        
        # 오류 메시지 추가
        self.listMessage.append(error_message)
        self.is_error = True

        # 다음 statement로 이동
        self.goNext()
        
        # EOF 또는 세미콜론이 아닌 경우 계속 lexical 분석
        if self.next_token not in (TokenType.SEMI_COLON, TokenType.EOF):
            self.lexical()

        # 원래 토큰 상태 복원 (결과물에 영향을 미치지 않도록)
        self.next_token = original_token


    def lexical(self):  # 다음 토큰을 읽어오는 함수
        """다음 토큰을 읽어와 설정"""
        if self.next_token == TokenType.EOF:  # 파일의 끝이면 종료
            return
        self.noMoreSpace()
        if self.detectEOF(): 
            return
        if self.detectId(): 
            return
        if self.detectConst(): 
            return
        if self.twoChars(): #연산자(2): 두 글자 연산자
            return
        if self.oneChar(): #연산자(1) : 한 글자 연산자
            return

        # 잘못된 문자 처리
        self.wrongChar()

        # 구문 오류 처리
        self.ErrorSyntax()


    def detectEOF(self):
        """파일의 끝을 감지하고 EOF 토큰 설정"""
        is_eof = self.index >= len(self.source)  # EOF 여부 확인
        if is_eof:
            self.stringToken = "EOF"
            self.next_token = TokenType.EOF
            if self.verbose:
                self.printV()  # verbose 모드에서는 현재 토큰 정보 출력
        return is_eof

    def detectId(self):  
        """식별자를 감지하고 처리"""
        matchIDENT = re.match(r"[a-zA-Z_][a-zA-Z0-9_]*", self.source[self.index:])
        if matchIDENT:  # 식별자가 감지되었을 경우
            self.stringToken = matchIDENT.group()  # 현재 토큰에 문자열 저장
            if self.before_token == TokenType.IDENT:  # 식별자가 연속됨 - warning
                warning = "(Warning) Too many identifiers, ignored "
                
                # 식별자가 끝날 때까지 경고 메시지 생성
                while self.index < len(self.source) and self.source[self.index] not in "+-*/();:= ":
                    warning += self.source[self.index]
                    self.index += 1

                self.listMessage.append(warning)  # 경고 메시지 추가
                self.is_warning = True  # 경고 플래그

                # 뒤에 나온 식별자 무시
                self.index += len(self.stringToken)
                self.noMoreSpace()
                self.lexical()  # 다음 토큰으로 이동
                return True
            
            else:  # 연속된 식별자가 아닐 경우
                self.next_token = TokenType.IDENT  # 다음 토큰을 식별자로 설정
                if self.verbose:
                    self.printV()  # verbose 모드에서 현재 토큰 출력
                self.now_stmt += self.stringToken  # 현재 statement에 추가

                self.index += len(self.stringToken)  # 인덱스 증가
                self.id_cnt += 1  # 식별자 카운트 증가

                # 식별자가 심볼 테이블에 없으면 "Unknown"으로 추가
                if self.stringToken not in self.symbolTable and not self.is_error:
                    self.symbolTable[self.stringToken] = "Unknown"
                return True
        return False


    def detectConst(self):  
        """상수를 감지하고 처리"""
        matchCONST = re.match(r'-?\d+(\.\d+)?', self.source[self.index:])  
        if matchCONST:  
            self.stringToken = matchCONST.group()  # 현재 토큰에 상수 문자열 저장

            if self.before_token == TokenType.CONST:  # 상수가 연속해서 나올 경우
                warning = f"(Warning) Too many constants - ignored other constants ({self.stringToken})"
                self.listMessage.append(warning)  
                self.is_warning = True  # 경고 플래그

                # 뒤에 나온 상수 무시
                self.index += len(self.stringToken)
                self.noMoreSpace()
                self.lexical()  # 다음 토큰으로 이동
                return True
            else:  # 연속된 상수가 아닐 경우
                self.next_token = TokenType.CONST  # 다음 토큰을 상수로 설정
                if self.verbose:
                    self.printV()  # verbose 모드에서 현재 토큰 출력
                self.now_stmt += self.stringToken  # 현재 statement에 추가

                self.index += len(self.stringToken)  # 인덱스 증가
                self.const_cnt += 1  # 상수 카운트 증가
            return True
        return False  # 상수가 감지되지 않음


    def twoChars(self):  # 두 글자 연산자를 감지하는 함수
        two_char_op = self.source[self.index:self.index + 2]  # 두 글자 연산자를 감지
        if two_char_op == ":=":  #:=가 나왔을 때
            self.stringToken = two_char_op  # stringToken := 저장
            self.next_token = TokenType.ASSIGN_OP  # 다음 토큰을 ASSIGN_OP으로 설정
            if self.verbose : self.printV()
            self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 := 추가

            self.index += 2  # 인덱스 증가

            self.opAndAssign()  #:= 다음 연산자 나오면 에러
            return True
        else:
            return False

    def oneChar(self):  # 한 글자 연산자를 감지하는 함수
        one_char_op = self.source[self.index]  # 한 글자 연산자를 감지

        if one_char_op in "+-*/();:=":  # 연산자가 나왔을 때
            self.stringToken = one_char_op  # stringToken 연산자 저장
            self.index += 1  # 인덱스 증가
            if one_char_op == "+":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.ADD_OP  # 다음 토큰을 ADD_OP으로 설정
                if self.verbose: self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                self.op_cnt += 1  # 연산자 개수 증가

                self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
            elif one_char_op == "-":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.ADD_OP  # 다음 토큰을 ADD_OP으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                self.op_cnt += 1  # 연산자 개수 증가

                self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
            elif one_char_op == "*":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.MULT_OP  # 다음 토큰을 MULT_OP으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                self.op_cnt += 1  # 연산자 개수 증가

                self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
            elif one_char_op == "/":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.MULT_OP  # 다음 토큰을 MULT_OP으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                self.op_cnt += 1  # 연산자 개수 증가

                self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
            elif one_char_op == ";":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.SEMI_COLON  # 다음 토큰을 SEMI_COLON으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

            elif one_char_op == "(":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.LEFT_PAREN  # 다음 토큰을 LEFT_PAREN으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                if self.before_token == TokenType.IDENT:  # 식별자 다음에 (가 나올 때 - error
                    error = "(Error) There is left parenthesis after identifier"  # error 메시지 저장
                    self.listMessage.append(error)  # error 메시지 저장
                    self.is_error = True  # error 발생 여부 플래그 설정

                    self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
                    self.goNext()  # 다음 statement로 이동
                    if self.next_token != TokenType.SEMI_COLON and self.next_token != TokenType.EOF: self.lexical()  # 세미콜론이 아니면 다음 토큰을 읽어옴
                    return True

                self.NoMultipleOp()  # 연산자가 여러개 연속해서 나올 때 - warning
            elif one_char_op == ")":  # 연산자에 따라 다음 토큰 설정
                self.next_token = TokenType.RIGHT_PAREN  # 다음 토큰을 RIGHT_PAREN으로 설정
                if self.verbose : self.printV()
                self.now_stmt += self.stringToken  # 현재 파싱 중인 statement에 연산자 추가

                self.noMoreSpace()  # 공백 무시
            elif one_char_op == "=" or one_char_op == ":":  # =나 :가 나올 때
                self.next_token = TokenType.ASSIGN_OP  # 다음 토큰을 ASSIGN_OP으로 설정
                if self.verbose: self.printV()
                # :=를 =로 쓴경우 - warning
                # :=를 :로 쓴경우 - warning
                # :=로 썼다고 가정하고 계속 진행
                self.stringToken = ":="

                self.now_stmt += self.stringToken

                if one_char_op == "=":  # :=를 =로 쓴경우 - warning
                    warning = "(Warning) Using = instead of := ==> assuming :="
                    self.listMessage.append(warning)
                elif one_char_op == ":":  # :=를 :로 쓴경우 - warning
                    warning = "(Warning) Using : instead of := ==> assuming :="
                    self.listMessage.append(warning)
                self.is_warning = True

                self.opAndAssign()  #:= 다음에 연산자가 나올 때 - error
            return True
        else:
            return False

    def noMoreSpace(self):
        """공백을 무시하고 소스 코드 처리"""
        while self.index < len(self.source):
            char = self.source[self.index]
            if char.isspace():  # 공백 문자인지 확인
                if char == " ":
                    self.now_stmt += " "  # 공백 추가
                self.index += 1  # 공백 문자는 건너뜀
            else:
                break  # 공백이 아니면 반복 종료


    def NoMultipleOp(self):  
        """연속된 연산자 무시 및 경고 메시지 추가"""
        self.noMoreSpace()
        if self.index < len(self.source) and self.source[self.index] in "+-*/:=)":
            self.is_warning = True
            # 기본 경고 메시지 설정
            warning = "(Warning) More than one operator ==> ignored other operators except the first one"
            first_operator = self.source[self.index]  # 첫 번째 연산자 저장
            warning += first_operator
            # 공백 처리
            while self.index < len(self.source) and self.source[self.index].isspace():
                self.index += 1  # 공백 건너뜀
            # 연속된 연산자 및 공백 무시
            while self.index < len(self.source) and self.source[self.index] in "+-*/:=)":
                self.index += 1  # 연산자 건너뜀

           
            self.listMessage.append(warning)  # 경고 메시지 추가


    def opAndAssign(self):  #:= 다음에 연산자가 나올 때 - error
        self.noMoreSpace()
        if self.index < len(self.source) and self.source[self.index] in "+-*/:=;)":
            # 대입 연산자 이후 다른 연산자가 나올때 - error
            self.is_error = True
            error = "(Error) Operator after :="
            self.listMessage.append(error)
            self.goNext()
            if self.next_token != TokenType.SEMI_COLON and self.next_token != TokenType.EOF: self.lexical()
            return True
        else:
            return False

    def goNext(self):  
        """다음 statement로 이동 - 오류 발생 시 처리"""
        while self.index < len(self.source) and self.next_token not in (TokenType.SEMI_COLON, TokenType.EOF):
            self.before_token = self.next_token
            self.noMoreSpace()  # 공백 무시

            if self.detectEOF(): 
                return

            if self.detectId():
                if self.stringToken not in self.symbolTable:
                    # 선언되지 않은 식별자 - error
                    error = f"(Error) Using undeclared identifier({self.stringToken})"
                    self.listMessage.append(error)
                    self.is_error = True
                continue

            if self.twoChars(): 
                continue
            if self.oneChar(): 
                continue
            if self.detectConst(): 
                continue

            

            # 잘못된 토큰 처리
            if self.next_token == TokenType.CONST:
                self.const_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.stringToken)]
            elif self.next_token == TokenType.IDENT:
                self.id_cnt -= 1
                self.now_stmt = self.now_stmt[:-len(self.stringToken)]
            self.wrongChar()  
            self.ErrorSyntax()

        # 파일 끝에서 세미콜론 처리
        if self.next_token == TokenType.SEMI_COLON and self.index == len(self.source):
            warning = "(Warning) Semicolon at the end of the program ==> ignored"
            self.is_warning = True
            self.index += 1
            self.now_stmt = self.now_stmt[:-1]
            self.listMessage.append(warning)
            


    def wrongChar(self):
        while self.index < len(self.source) and self.source[self.index] not in "+-*/();:= ":
            self.index += 1

    def end_of_stmt(self):  
        """각 statement의 종료 시 처리"""
        # 에러가 발생한 경우 해당 statement의 ID를 Unknown으로 설정
        if self.is_error and self.id_of_now_stmt in self.symbolTable:
            self.symbolTable[self.id_of_now_stmt] = "Unknown"

        if not self.verbose:  # -v 옵션이 없을 때
            print(self.now_stmt)  # 현재 파싱한 statement 출력

            # ID, CONST, OP 개수 출력
            print(f"ID: {self.id_cnt}; CONST: {self.const_cnt}; OP: {self.op_cnt};")

            # 에러, 경고 메시지 출력
            for message in self.listMessage:
                print(message)
            # 에러 및 경고가 없는 경우 OK 출력
            if not self.is_warning and not self.is_error:
                print("(OK)\n")

        # 상태 초기화
        self.reset_statement_state()
        
    def reset_statement_state(self):
        """현재 statement의 상태를 초기화"""
        self.now_stmt = ""
        self.id_cnt, self.const_cnt, self.op_cnt = 0, 0, 0
        self.is_error, self.is_warning, self.before_token = False, False, None
        self.listMessage = []
        self.id_of_now_stmt = None
