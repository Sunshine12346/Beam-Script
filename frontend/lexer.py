from enum import Enum
from re import MULTILINE

class TokenType(Enum):
   # Literal Types
    Null = 1
    Int = 2 
    Float = 3
    Identifier = 4
    String = 5

    # Keywords
    Var = 6
    Declare = 7
    Const = 8
    Def = 9
    If = 10
    Else = 11
    While = 12

    And = 13
    Or = 14
    Not = 15
    UnaryPlus = 16
    UnaryMinus = 17
    BinaryOperator = 18
    Equals = 19
    Comma = 20
    Dot = 21
    Colon = 22
    Semicolon = 23
    SingleLineComment = 24
    MultiLineCommentStart = 25
    MultiLineCommentEnd = 26
    OpenParen = 27
    CloseParen = 28
    OpenBrace = 29
    CloseBrace = 30
    OpenBracket = 31
    CloseBracket = 32
    DoubleEquals = 33
    NotEquals = 34
    LessThan = 35
    GreaterThan = 36
    LessThanOrEquals = 37
    GreaterThanOrEquals = 38
    EOF = 39

KEYWORDS = {
    "var": TokenType.Var,
    "declare": TokenType.Declare,
    "const": TokenType.Const,
    "def": TokenType.Def,
    "null": TokenType.Null,
    "and": TokenType.And,
    "or": TokenType.Or,
    "not": TokenType.Not,
    "if": TokenType.If,
    "else": TokenType.Else,
    "while": TokenType.While
}

class Token:
    def __init__(self, value, token_type):
        self.value = value
        self.type = token_type
        
    def __str__(self):
        return f"{{ value: {self.value}, type_name: {self.type.name}, type: {self.type.value} }}"

def token(value : str, token_type : TokenType):
    return Token(value, token_type)

def isalpha(src):
    return src.upper() != src.lower()

def isskippable(str):
    return str == " " or str == "\n" or str == "\t" or str == "\r"

def isnum(char):
    return char.isnumeric()

def isint(char):
    return char.isdigit()
    
def isfloat(char):
    return char.isdecimal()

def pos(sourceCode):
    src = list(sourceCode)
    return len(src)

def tokenize(sourceCode):
    tokens = []
    src = list(sourceCode)
    while len(src) > 0:
        if src[0] == "(":
            tokens.append(token(src.pop(0), TokenType.OpenParen))
        elif src[0] == ")":
            tokens.append(token(src.pop(0), TokenType.CloseParen))
        elif src[0] == "{":
            tokens.append(token(src.pop(0), TokenType.OpenBrace))
        elif src[0] == "}":
            tokens.append(token(src.pop(0), TokenType.CloseBrace))
        elif src[0] == "[":
            tokens.append(token(src.pop(0), TokenType.OpenBracket))
        elif src[0] == "]":
            tokens.append(token(src.pop(0), TokenType.CloseBracket))
        elif src[0] == "%" or src[0] == "^":
            tokens.append(token(src.pop(0), TokenType.BinaryOperator))
        elif src[0] == "=":
            # Count the number of consecutive equals signs
            sign_count = 1
            idx = 1
            while idx < len(src) and src[idx] == "=":
                sign_count += 1
                idx += 1
    
            # Determine the appropriate token type based on the number of equals signs
            if sign_count == 1:
                tokens.append(token(src.pop(0), TokenType.Equals))
            elif sign_count == 2:
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.DoubleEquals))
            else:
                print("Unrecognized character found in source: ", ord(src[0]), src[0])
                exit(1)
        elif src[0] == "!":
            if src[1] == "=":
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.NotEquals))
            elif src[1] != "=":
                tokens.append(token(src.pop(0), TokenType.Not))
            else:
                print("Unrecognized character found in source: ", ord(src[0]), src[0])
                exit(1)
        elif src[0] == "<":
            if src[1] == "=":
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.LessThanOrEquals))
            else:
                tokens.append(token(src.pop(0), TokenType.LessThan))
        elif src[0] == ">":
            if src[1] == "=":
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.GreaterThanOrEquals))
            else:
                tokens.append(token(src.pop(0), TokenType.GreaterThan))
        elif src[0] == "&":
            # Count the number of consecutive & signs
            sign_count = 1
            idx = 1
            while idx < len(src) and src[idx] == "&":
                sign_count += 1
                idx += 1
    
            # Determine the appropriate token type based on the number of equals signs
            if sign_count == 2:
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.And))
            else:
                print("Unrecognized character found in source: ", ord(src[0]), src[0])
                exit(1)
        elif src[0] == "|":
            # Count the number of consecutive & signs
            sign_count = 1
            idx = 1
            while idx < len(src) and src[idx] == "|":
                sign_count += 1
                idx += 1
    
            # Determine the appropriate token type based on the number of equals signs
            if sign_count == 2:
                tokens.append(token(src.pop(0) + src.pop(0), TokenType.Or))
            else:
                print("Unrecognized character found in source: ", ord(src[0]), src[0])
                exit(1)
        elif src[0] == "+":
            if len(tokens) == 0 or tokens[-1].type == TokenType.BinaryOperator:
                tokens.append(token(src.pop(0), TokenType.BinaryOperator))
            else:
                tokens.append(token(src.pop(0), TokenType.UnaryPlus))
        elif src[0] == "-":
            if len(tokens) == 0 or tokens[-1].type == TokenType.BinaryOperator:
                tokens.append(token(src.pop(0), TokenType.BinaryOperator))
            else:
                tokens.append(token(src.pop(0), TokenType.UnaryMinus))
        elif src[0] == "*":
            if src[1] == "/":
                tokens.append(token(src.pop(0)+src.pop(0), TokenType.MultiLineCommentEnd))
        elif src[0] == "/":
            if src[1] == "/":
                tokens.append(token(src.pop(0)+src.pop(), TokenType.SingleLineComment))
            elif src[2] == "*":
                tokens.append(token(src.pop(0)+src.pop(0), TokenType.MultiLineCommentStart))
            else:
                tokens.append(token(src.pop(0), TokenType.SingleLineComment))
        elif src[0] == ":":
            tokens.append(token(src.pop(0), TokenType.Colon))
        elif src[0] == ",":
            tokens.append(token(src.pop(0), TokenType.Comma))
        elif src[0] == ".":
            tokens.append(token(src.pop(0), TokenType.Dot))
        elif src[0] == '"' or src[0] == "'":
            quote = src.pop(0)
            string_content = ""
            while len(src) > 0 and src[0] != '"' and src[0] != "'":
                string_content += src.pop(0)
                
            if len(src) == 0 or src[0] != quote:
                print("Error: Unterminated string literal")
                exit(1)
            src.pop(0)  # Discard the closing quote
            tokens.append(token(string_content, TokenType.String))
        elif isnum(src[0]):
            num = ""
            while len(src) > 0 and (isint(src[0]) or src[0] == '.'):
                num += src.pop(0)
            if "." in num:
                tokens.append(token(num, TokenType.Float))
            else:
                tokens.append(token(num, TokenType.Int))
        elif isalpha(src[0]):
            ident = ""
            while len(src) > 0 and src[0].isalnum():
                ident += src.pop(0)
            reserved = KEYWORDS.get(ident)

            if reserved:
                tokens.append(token(ident, reserved))
            else:
                tokens.append(token(ident, TokenType.Identifier))
        elif isskippable(src[0]):
            src.pop(0)
        else:
            print("Unrecognized character found in source: ", ord(src[0]), src[0])
            exit(1)
    tokens.append(token('EndOfFile', TokenType.EOF))
    return tokens

