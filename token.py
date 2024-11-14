class token: #토큰 타입
    UNKNOWN = 0
    IDENT = 1
    CONST = 2
    ASSIGN_OP = 3
    SEMI_COLON = 4
    ADD_OP = 5
    MULT_OP = 6
    LEFT_PAREN = 7
    RIGHT_PAREN = 8
    EOF = 9

    @classmethod
    def get_name(cls, token_type): #토큰 타입 숫자->문자열
    
        for name, value in cls.__dict__.items():
            if value == token:
                return name
        return "UNKNOWN"

