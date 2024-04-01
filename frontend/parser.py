from frontend.ast import AssignmentExpression, BinaryExpression, BlockStatement, CallExpression, Expr, FunctionDeclaration, Identifier, IfStatement, LogicalExpression, MemberExpression, NullLiteral, NumericLiteral, ObjectExpression, Program, Property, Stmt, UnaryExpression, VariableDeclaration, StringLiteral, WhileStatement
from frontend.lexer import TokenType, tokenize, pos
from typing import List, Self
import json

class Parser:
    def __init__(self):
        self.tokens = []

    def not_eof(self):
        return self.tokens[0].type != TokenType.EOF

    def at(self):
        return self.tokens[0]

    def eat(self):
        prev = self.tokens.pop(0)
        return prev

    def expect(self, token_type: TokenType, err):
        prev = self.eat()
        if not prev or prev.type != token_type:
            print("Parser Error:\n", err, prev, " - Expecting: ", token_type)
            exit(0) 
        return prev

    # def eat_comment(self):
    #     if self.at().type == TokenType.SingleLineComment:
    #         while self.at().type != TokenType.EOF and self.at().value != '\n':
    #             self.eat()
    #     elif self.at().type == TokenType.MultiLineCommentStart:
    #         while self.not_eof:
    #             if self.at().type == TokenType.MultiLineCommentEnd:
    #                    self.eat()
    #                 if self.not_eof():
    #                     self.eat()
    #         raise Exception("Unterminated multi-line comment")

    def produceAST(self, sourceCode) -> Program:
        self.tokens = tokenize(sourceCode)
        self.length = pos(sourceCode)
        body = []
        while self.not_eof():
            body.append(self.parse_stmt())
            
        program = Program(0, self.length, body).__dict__
        
        # with open("parser_output.json", "w") as f:
        #     json.dump(program, f, indent=4)

        return program

    def parse_stmt(self) -> Stmt:
        statements = {}
        # if self.at().type in {TokenType.SingleLineComment, TokenType.MultiLineCommentStart, TokenType.MultiLineCommentEnd}:
        #     self.eat_comment()
        if self.at().type == TokenType.If:
            statements = self.parse_if_stmt()
        elif self.at().type == TokenType.While:
            statements = self.parse_while_loop()
        elif self.at().type in {TokenType.Declare, TokenType.Const, TokenType.Var}:
            statements = self.parse_var_declaration()
        elif self.at().type == TokenType.Def:
            return self.parse_fn_declaration()
        else:
            statements = self.parse_expr_statement()
        return statements

    def parse_fn_declaration(self) -> Stmt:
        self.eat()
        identifier = str(self.expect(
                TokenType.Identifier,
                "Expected identifier name following declare | var| const keywords."
        ))
        
        args = self.parse_args()
        params = []

        for arg in args:
            if arg["type"] != "Identifier":
                    raise Exception("Expected")
            params.append(arg)
            
        self.expect(TokenType.OpenBrace, "Expected function body following declaration")
        
        body = self.parse_block()
        
        self.expect(TokenType.CloseBrace, "Missing Closing Brace inside function declaration")
        ident = {
                "type": identifier.split(":")[2].strip().split(",")[0],
                "name": identifier.split(":")[1].strip().split(",")[0]
        }
        fn = FunctionDeclaration(ident, params, body).dict()
        return fn

    def parse_var_declaration(self) -> Stmt:
        is_constant = self.at().type == TokenType.Const
        if is_constant:
            self.eat()
            if self.at().type in {TokenType.Declare, TokenType.Var}:
                pass
            else:
                err = "Expected declare | var keywords after const keyword."
                prev = self.eat()
                token_type = "Declare or Var keywords"
                print("Parser Error:\n", err, prev, " - Expecting: ", token_type)
            key = self.at().type
        else:
            key = self.at().type
        if key == TokenType.Declare:
            key = "declare"
        elif key == TokenType.Var:
            key = "var"
        else:
            err = "Unknown keywords."
            prev = self.eat()
            token_type = "Declare or Var keywords"
            print("Parser Error:\n", err, prev, " - Expecting: ", token_type)
         
        self.eat()
        
        declarations = []
        value = None

        while True:

            identifier = str(self.expect(
                TokenType.Identifier,
                "Expected identifier name following declare | var| const keywords."
            ))
            
            if self.at().type == TokenType.Equals:
                self.eat()
                value = self.parse_expr()
            else:
                if is_constant:
                
                    raise Exception(
                        "Must assign value to constant expression. No value provided."
                    )
            
                else:
                    value = None
            
            declarations.append(
                {
                    "type": "VariableDeclarator",
                    "id": {
                         "type": identifier.split(":")[2].strip().split(",")[0],
                         "name": identifier.split(":")[1].strip().split(",")[0]
                    },
                    "init": value
                }  
            )
            
            if self.at().type == TokenType.Comma:
                self.eat()
            else:
                break

        declaration = VariableDeclaration(declarations, key, is_constant).__dict__
        
        return declaration
    
    def parse_if_stmt(self) -> Stmt:  
        self.eat()
        condition = self.parse_expr()
        self.expect(TokenType.OpenBrace, "Expected '{' after 'if' condition")
        consequent = self.parse_block()
        alternate = None
        self.expect(TokenType.CloseBrace, "Expected '}' after closing 'if' statement")
        if self.at().type == TokenType.Else:
            self.eat()  # Consume the 'else' token
            if self.at().type == TokenType.If:
                alternate = self.parse_if_else_stmt()  # Nested if-else
            else:
                self.expect(TokenType.OpenBrace, "Expected '{' after 'else'")
                alternate = self.parse_block()
                self.expect(TokenType.CloseBrace, "Expected '}' after closing 'else' statement")
                
        st = IfStatement(condition, consequent, alternate).__dict__
        return st

    def parse_while_loop(self) -> Stmt:
        self.eat()
        condition = self.parse_expr()
        self.expect(TokenType.OpenBrace, "Expected '{' after 'while' condition")
        body = self.parse_block()
        self.expect(TokenType.CloseBrace, "Expected '}' after closing 'while' statement")
        st = WhileStatement(condition, body).__dict__
        return st
        
    def parse_expr_statement(self) -> Stmt:
        expression = self.parse_assignment_expr()
        expr_stmt = Expr(expression).__dict__
        return expr_stmt
        
    def parse_block(self):
        body = []  # Initialize index
        while self.not_eof() and self.at().type != TokenType.CloseBrace:
           body.append(self.parse_stmt()) # Assign statement to index key
        # self.expect(TokenType.CloseBrace, "Expected '}' after block")
        statements = BlockStatement(body).__dict__   
        return statements

    def parse_expr(self) -> Expr:
        return self.parse_assignment_expr()
    

    def parse_assignment_expr(self) -> Expr:    
        left = self.parse_object_expr()
        
        if self.at().type == TokenType.Equals:
            self.eat();
            value = self.parse_assignment_expr()
            left = AssignmentExpression(left, value).__dict__
        
        return left
    
    def parse_object_expr(self):
        if self.at().type != TokenType.OpenBrace:
            return self.parse_logical_expr()

        self.eat()
        properties = []

        while self.not_eof() and self.at().type != TokenType.CloseBrace:
            key = self.expect(TokenType.Identifier, "Object literal key expected").value

            if self.at().type == TokenType.Comma:
                self.eat()
                properties.append(Property(key).__dict__)
                continue
            elif self.at().type == TokenType.CloseBrace:
                properties.append(Property(key, value).__dict__)
                continue

            self.expect(TokenType.Colon, "Missing colon following identifier in ObjectExpr")
            value = self.parse_expr()

            properties.append(Property(key, value).__dict__)
            if self.at().type != TokenType.CloseBrace:
                self.expect(TokenType.Comma, "Expected comma or closing bracket following property")

        self.expect(TokenType.CloseBrace, "Object literal missing closing brace.")
        
        expr = ObjectExpression(properties).__dict__
        return expr

    # def parse_array_expr(self):
    #     if self.at().type != TokenType.OpenBracket:
    #         return self.parse_logical_expr()
        
    #     self.eat()
    #     elements = []
        
    #     while self.not_eof and self.at().type != TokenType.CloseBracket:
    #         while self.at().type != TokenType.Comma and self.at().type != TokenType.CloseBracket and self.at().type != TokenType.EOF:
    #             elements.append(self.parse_expr())
    #         self.eat()
    #         if self.at().type == TokenType.Comma:
    #             self.eat()
                
    #     self.expect(TokenType.CloseBracket, "Expected ']' at the end of array expression")
        
    #     return {
    #         "type": "ArrayExpression",
    #         "elements": elements
    #     }
            
            


    def parse_logical_expr(self) -> Expr:
        left = self.parse_unary_expr()
        while self.at().type in {TokenType.And, TokenType.Or}:
            operator = self.eat().value
            right = self.parse_unary_expr()
            left = LogicalExpression(left, operator, right).__dict__
        return left

    def parse_unary_expr(self) -> Expr:
        if self.at().type in {TokenType.Not, TokenType.UnaryPlus, TokenType.UnaryMinus}:
            operator = self.eat().value
            operand = self.parse_comparison_expr()
            expr = UnaryExpression(operator, operand).__dict__
            return expr
        else:
            return self.parse_comparison_expr()

    def parse_comparison_expr(self) -> Expr:
        left = self.parse_additive_expr()
        while self.at().type in {
            TokenType.DoubleEquals,
            TokenType.NotEquals,
            TokenType.LessThan,
            TokenType.LessThanOrEquals,
            TokenType.GreaterThan,
            TokenType.GreaterThanOrEquals,
        }:
            operator = self.eat().value
            right = self.parse_additive_expr()
            left = BinaryExpression(left, operator, right).__dict__
        return left 

    def parse_additive_expr(self) -> Expr:
        left = self.parse_multiplicative_expr()
        while self.at().value == "+" or self.at().value == "-":
            operator = self.eat().value
            right = self.parse_multiplicative_expr()
            left = BinaryExpression(left, operator, right).__dict__
        return left

    def parse_multiplicative_expr(self) -> Expr:
        left = self.parse_power_expr()
        while self.at().value in ["/", "*", "%"]:
            operator = self.eat().value
            right = self.parse_power_expr()
            left = BinaryExpression(left, operator, right).__dict__
        return left
    
    def parse_power_expr(self) -> Expr:
        left = self.parse_call_member_expr()
        while self.at().value in "^":
            operator = self.eat().value
            right = self.parse_call_member_expr()
            left = BinaryExpression(left, operator, right).__dict__
        return left

    def parse_call_member_expr(self) -> Expr:
        member = self.parse_member_expr()
        
        if self.at().type == TokenType.OpenParen:
            return self.parse_call_expr(member)
        
        return member
        
    def parse_call_expr(self, callee: Expr) -> Expr:
        args = self.parse_args()
        call_expr = CallExpression(callee, args). __dict__
        if self.at().type == TokenType.OpenParen:
            call_expr = self.parse_call_expr(call_expr)
            
        return call_expr
        
    def parse_args(self) -> List[Expr]:
        self.expect(TokenType.OpenParen, "Expected open parenthesis")      
        args = self.at().type == TokenType.CloseParen
        if args:
            args = []
        else:
            args = self.parse_arguments_list()
        self.expect(TokenType.CloseParen, "Missing closing parenthesis inside the arguments list")
        return args
            
        
    def parse_arguments_list(self) -> List[Expr]:
        args = [self.parse_assignment_expr()]
        
        while self.at().type == TokenType.Comma and self.eat():
            args.append(self.parse_assignment_expr())
            
        return args
        
    def parse_member_expr(self) -> Expr:
        member_object = self.parse_primary_expr()
        
        while self.at().type == TokenType.Dot or self.at().type == TokenType.OpenBracket:
            operator = self.eat()
            computed = False
            
            # Non-computed aka obj.expr
            if operator.type == TokenType.Dot:
                computed = False   
                member_property = self.parse_primary_expr()
                    

                if member_property["type"] != "Identifier":
                    raise Exception("Cannot use dot operator without right hand side being a identifier")
            else:
                computed = True
                member_property = self.parse_expr()
                self.expect(TokenType.CloseBracket, "Missing closing bracket in computed value.")
            
            member_object = MemberExpression(member_object, member_property, computed).__dict__
            
        return member_object
                
        
        # Orders of Precedence
        # Assignment
        # Object
        # LogicalExpr
        # ComparisonExpr
        # AdditiveExpr
        # MultiplicativeExpr
        # PowerExpr
        # UnaryExpr
        # Call
        # Member
        # PrimaryExpr

    def parse_primary_expr(self) -> Expr:
        tk = self.at().type
        if tk == TokenType.Identifier:
            return Identifier(self.eat().value).__dict__
        elif tk == TokenType.String:
            return StringLiteral(self.eat().value).__dict__
        elif tk == TokenType.Null:
            self.eat()
            return NullLiteral().__dict__
        elif tk == TokenType.Int:
            return NumericLiteral(int(self.eat().value)).__dict__
        elif tk == TokenType.Float:
            return NumericLiteral(float(self.eat().value)).__dict__
        elif tk == TokenType.OpenParen:
            self.eat()  # eat the opening paren
            value = self.parse_expr()
            self.expect(TokenType.CloseParen, "Unexpected token found inside parenthesised expression. Expected closing parenthesis.")
            return value
        # elif tk == TokenType.CloseParen:
        #     pass
        else:
            print("Unexpected token found during parsing!", self.at())
            exit(1)


