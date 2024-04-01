import operator
from tracemalloc import start
from typing import List, Union, Optional

NodeType = Union[
    # STATEMENTS
    "Program",
    "VariableDeclaration",
    "IfStatement",
    "WhileStatement"
    "FunctionDeclaration",
    "Expr",
    "BlockStatement"
    
    # EXPRESSIONS
    "AssignmentExpression",
    "ObjectExpression",
    "BinaryExpression",
    "UnaryExpression",
    "LogicalExpression",
    "MemberExpression",
    "CallExpression"
    
    # LITERALS
    "StringLiteral"
    "Property",
    "NumericLiteral",
    "NullLiteral",
    "Identifier"
]
"""
Statements do not result in a value at runtime.
They contain one or more expressions internally
"""
class Stmt:
    type: NodeType

"""
Defines a block which contains many statements.
- Only one program will be contained in a file.
"""
class Program(Stmt):
    def __init__(self, start, end, body: List[Stmt]):
        self.type = "Program"
        self.start = start
        self.end = end
        self.body = body
        
class VariableDeclaration(Stmt):
    def __init__(self, declarations, kind: str, constant: bool):
        self.type = "VariableDeclaration"
        self.declarations = declarations
        self.kind = kind
        self.constant = constant
        
class FunctionDeclaration(Stmt):
    def __init__(self, ident, params, body):
        self.type = "FunctionDeclaration"
        self.id = ident
        self.params = params
        self.body = body

class IfStatement(Stmt):
    def __init__(self, condition, consequent, alternate=None):
        self.type = "IfStatement"
        self.condition = condition
        self.consequent = consequent
        self.alternate = alternate
        
class WhileStatement(Stmt):
    def __init__(self, condition, body):
        self.type = "WhileStatement"
        self.condition = condition
        self.body = body

class BlockStatement(Stmt):
    def __init__(self, body):
        self.type = "BlockStatement"
        self.body = body

"""
Expressions will result in a value at runtime unlike Statements
"""
class Expr(Stmt):
    def __init__(self, expr):
        self.type = "ExpressionStatement"
        self.expression = expr

class AssignmentExpression(Expr):
    def __init__(self, assigne: Expr, value: Expr):
        self.type = "AssignmentExpression"
        self.operator = "="
        self.left = assigne
        self.right = value

"""
A operation with two sides seperated by a operator.
Both sides can be ANY Complex Expression.
- Supported Operators -> + | - | / | * | %
"""

class UnaryExpression(Expr):
    def __init__(self, operator: str, argument):
        self.type = "UnaryExpression"
        self.operator = operator
        self.argument = argument

class LogicalExpression(Expr):
    def __init__(self, left: Expr, operator: str, right: Expr):
        self.type = "LogicalExpression"
        self.left = left
        self.operator = operator
        self.right = right
           
class BinaryExpression(Expr):
    def __init__(self, left: Expr, operator: str, right: Expr):
        self.type = "BinaryExpression"
        self.left = left
        self.operator = operator
        self.right = right
        
class CallExpression(Expr):
    def __init__(self, callee: Expr, args: List[Expr]):
        self.type = "CallExpression"
        self.callee = callee
        self.arguments = args
        
class MemberExpression(Expr):
    def __init__(self, member_object: Expr, member_property: Expr, computed: bool):
        self.type = "MemberExpression"
        self.object = member_object
        self.property = member_property
        self.computed = computed

# LITERAL / PRIMARY EXPRESSION TYPES

"""
Represents a user-defined variable or symbol in source.
"""
class Identifier(Expr):
    def __init__(self, name: str):
        self.type = "Identifier"
        self.name = name

"""
Represents a numeric constant inside the soure code.
"""
class NumericLiteral(Expr):
    def __init__(self, value: int):
        self.type = "NumericLiteral"
        self.value = value

class NullLiteral(Expr):
    def __init__(self):
        self.type = "NullLiteral"
        self.value = None
        
class Property(Expr):
    def __init__(self, key: str, value: Expr = None):
        self.type = "Property"
        self.key = key
        self.value = value
 
class ObjectExpression(Expr):
    def __init__(self, properties: List[Property]):
        self.type = "ObjectExpression"
        self.properties = properties

class StringLiteral(Expr):
    def __init__(self, value: str):
        self.type = "StringLiteral"
        self.value = value