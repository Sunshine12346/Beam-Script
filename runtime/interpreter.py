from frontend.ast import AssignmentExpression, BinaryExpression, CallExpression, LogicalExpression, MemberExpression, ObjectExpression, Stmt, Program, UnaryExpression, VariableDeclaration, NumericLiteral, Identifier, StringLiteral, IfStatement, WhileStatement
from runtime.values import FunctionVal, NativeFn, NullVal, NumberVal, ObjectVal, RuntimeVal, StringVal, BooleanVal
from frontend.lexer import TokenType
from runtime.environment import Environment
from math import pow

def eval_program(program: Program, env: Environment) -> RuntimeVal:
    last_evaluated: RuntimeVal = NullVal().__dict__
    for statement in program["body"]:
        last_evaluated = evaluate(statement, env)
    return last_evaluated

def eval_var_declaration(declaration: VariableDeclaration, env: Environment) -> RuntimeVal:
    for declarator in declaration["declarations"]:
        identifier = declarator["id"]["name"]
        value = evaluate(declarator["init"], env)
        env.declareVar(identifier, value, declaration["constant"])
        
def eval_fn_declaration(declaration: VariableDeclaration, env: Environment) -> RuntimeVal:
    fn = FunctionVal(declaration["id"]["name"], declaration["params"], env, declaration["body"])
    
    env.declareVar(declaration["id"]["name"], fn, True)

def eval_if_stmt(stmt: IfStatement, env: Environment) -> RuntimeVal:
    condition = evaluate(stmt["condition"], env)
    if condition["value"]:
        evaluate(stmt["consequent"], env)
    else:
        evaluate(stmt["alternate"], env)

def eval_while_loop(stmt: WhileStatement, env: Environment):
    while True:
        condition = evaluate(stmt["condition"], env)
        
        if not condition.value: break
        
        evaluate(stmt["body"], env)
            
            
        

def eval_numeric_binary_expr(lhs: NumberVal, rhs: NumberVal, operator: str) -> NumberVal:
    result: int
    if operator == "+":
        result = lhs + rhs
    elif operator == "-":
        result = lhs - rhs
    elif operator == "*":
        result = lhs * rhs
    elif operator == "/":
        if rhs == 0:
            raise Exception("Cannot Divide by Zero")
        else:
            result = lhs / rhs
    elif operator == "%":
        result = lhs % rhs
    elif operator == "^":
        result = lhs ** rhs

    return NumberVal(result).__dict__

def eval_comparison_expr(lhs: NumberVal, rhs: NumberVal, operator: str) -> RuntimeVal:
    # Evaluate based on the operator
    if operator == "==":
        return BooleanVal(lhs == rhs).__dict__
    elif operator == "!=":
        return BooleanVal(lhs != rhs).__dict__
    elif operator == "<":
        return BooleanVal(lhs < rhs).__dict__
    elif operator == "<=":
        return BooleanVal(lhs <= rhs).__dict__
    elif operator == ">":
        return BooleanVal(lhs > rhs).__dict__
    elif operator == ">=":
        return BooleanVal(lhs >= rhs).__dict__
    else:
        raise ValueError("Invalid operator in comparison expression")


def eval_binary_expr(binop: BinaryExpression, env: Environment) -> RuntimeVal:
    lhs = evaluate(binop['left'], env)
    rhs = evaluate(binop['right'], env)

    if lhs["type"] == "number" and rhs["type"] == "number":
        if binop["operator"] in {"+", "-", "*", "/", "%", "^"}:
            return eval_numeric_binary_expr(lhs["value"], rhs["value"], binop['operator'])
        else:
            return eval_comparison_expr(lhs["value"], rhs["value"], binop['operator'])

    return NullVal().__dict__

def eval_identifier(ident: Identifier, env: Environment) -> RuntimeVal:
    val = env.lookupVar(ident["name"])
    return val

def eval_assignment(node: AssignmentExpression, env: Environment) -> RuntimeVal:
    if (node["assigne"]["type"] != "Identifier"):
        raise Exception("Invalid LHS inside assignment expression")
    
    varname = node["assigne"]["name"]
    return env.assignVar(varname, evaluate(node["value"], env))

def eval_unary_expr(expr: UnaryExpression, env: Environment) -> RuntimeVal:
    operator = expr["operator"]
    operand = evaluate(expr["argument"], env)
    if operator == "+":
        # Evaluate plus
        if operand["type"] == "number":
            return NumberVal(+operand["value"])
        else:
            raise ValueError("Unary plus operator can only be applied to numbers.")
    if operator == "-":
        # Evaluate negation
        if operand["type"] == "number":
            return NumberVal(-operand["value"])
        else:
            raise ValueError("Unary negation can only be applied to numbers.")
    if operator in {"not", "!"}:
        # Evaluate logical negation
        if operand["type"] == "boolean":
            return BooleanVal(not operand["value"])
        else:
            raise ValueError("Logical not can only be applied to booleans.")
    else:
        raise ValueError("Unsupported unary operator: " + operator)

def eval_logical_expr(expr: LogicalExpression, env: Environment) -> RuntimeVal:
    left_val = evaluate(expr["left"], env)
    right_val = evaluate(expr["right"], env)
    
    # Evaluate logical AND
    if expr["operator"] in {"and", "&&"}:
        if left_val == right_val:
            return left_val
        else:
            return BooleanVal(False).__dict__
    
    # Evaluate logical OR
    if expr["operator"] in {"or", "||"}:
        if left_val["value"] == "True":
            return BooleanVal(True).__dict__
        return right_val

    raise ValueError("Invalid operator in logical expression")

def eval_object_expr(obj: ObjectExpression, env: Environment) -> RuntimeVal:
    # Create an instance of ObjectVal
    object_val = {
        "properties": {}
    }

    # Iterate over properties of the object
    for prop in obj["properties"]:
        key = prop["key"]
        value = prop["value"]
        # Lookup variable if value is None, otherwise evaluate the expression
        runtime_val = env.lookupVar(key) if value is None else evaluate(value, env)
    
        # Update properties of the ObjectVal instance
        object_val["properties"][key] = runtime_val    

    # Return the ObjectVal instance
    return ObjectVal(object_val["properties"]).__dict__

def eval_member_expr(expr: MemberExpression, env: Environment) -> RuntimeVal:
    if expr["object"]["type"] == "Identifier":
        value = env.lookupVar(expr["object"]["name"])
    elif expr["object"]["type"] == "MemberExpression":
        value = evaluate(expr["object"], env)

    if expr["property"]["name"] in value.properties:
        return value.properties[expr["property"]["name"]]
    else:
        raise Exception("The Member couldn't be found")
    

def eval_call_expr(expr: CallExpression, env: Environment) -> RuntimeVal:
    args = [evaluate(arg, env) for arg in expr["arguments"]]
    fn = evaluate(expr["callee"], env)

    if fn.type == "native_fn":
        result = fn.call(args, env)
        return result
    if fn.type == "function":
        func = fn
        scope = Environment(func.declaration_env)
        
        i = 0
        for i in range(len(func.params)):
            # TODO Check the bounds here.
            # verify arity of function
            varname = func.params[i]["name"]
            scope.declareVar(varname, args[i], False)
            
        return evaluate(func.body, scope)

    raise ValueError("Cannot call value that is not a function: " + str(fn))

def evaluate(astNode: Stmt, env: Environment) -> RuntimeVal:
    if astNode == None:
        return NullVal()
    if astNode == {}:
        return None
    
    if astNode["type"] == "StringLiteral":
        return StringVal(astNode["value"]).__dict__
    elif astNode["type"] == "NumericLiteral":
        return NumberVal(astNode["value"]).__dict__
    elif astNode["type"] == "NullLiteral":
        return NullVal().__dict__
    elif astNode["type"] == "Identifier":
        return eval_identifier(astNode, env)
    elif astNode["type"] == "MemberExpression":
        return eval_member_expr(astNode, env)
    elif astNode["type"] == "CallExpression":
        return eval_call_expr(astNode, env)
    elif astNode["type"] == "UnaryExpression":
        return eval_unary_expr(astNode, env)
    elif astNode["type"] == "LogicalExpression":
        return eval_logical_expr(astNode, env)
    elif astNode["type"] == "ObjectExpression":
        return eval_object_expr(astNode, env)
    elif astNode["type"] == "AssignmentExpression":
        return eval_assignment(astNode, env)
    elif astNode["type"] == "BinaryExpression":
        return eval_binary_expr(astNode, env)
    elif astNode["type"] == "Program":
        return eval_program(astNode, env)
    elif astNode["type"] == "VariableDeclaration":
        return eval_var_declaration(astNode, env)
    elif astNode["type"] == "FunctionDeclaration":
        return eval_fn_declaration(astNode, env)
    elif astNode["type"] == "IfStatement":
        return eval_if_stmt(astNode, env)
    elif astNode["type"] == "WhileStatement":
        return eval_while_loop(astNode, env)
    elif astNode["type"] == "BlockStatement":
        return eval_program(astNode, env)
    elif astNode["type"] == "ExpressionStatement":
        return evaluate(astNode["expression"], env)
    else:
        print("This AST Node has not yet been set up for interpretation:", astNode)


