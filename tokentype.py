class Tokentype: #토큰 타입
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
    def get_name(cls, token):
        for name, value in cls.__dict__.items():
            if value == token:
                return name
        return "UNKNOWN"
    
    

class Token:
    def __init__(self, token_type, value):
        self.type = token_type  # 토큰 타입 (e.g., IDENT, CONST)
        self.value = value      # 토큰 값 (e.g., "x", 42)

    def __repr__(self):
        return f"Token(type={self.type}, value={self.value})"
