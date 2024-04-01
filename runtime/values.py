from dataclasses import dataclass
from msilib.schema import Environment
from typing import Union, Callable, List
from frontend.ast import Stmt

# Define a type alias for the union of NullVal and NumberVal
ValueType = Union["NumberVal", "NullVal", "BooleanVal", "ObjectVal", "NativeFn", "FunctionVal",  "StringVal"]

# Define a base class for runtime values
@dataclass
class RuntimeVal:
    type: str

# Define a class for representing NullVal, extending RuntimeVal
@dataclass
class NullVal(RuntimeVal):
    type: str = "null"
    value: str = None

class BooleanVal(RuntimeVal):
    def __init__(self, value: bool = True):
        self.type = "boolean"
        self.value = value
 
# Define a class for representing NumberVal, extending RuntimeVal
@dataclass
class NumberVal(RuntimeVal):
    def __init__(self, value):
        self.type = "number"
        self.value = value
        number_type = ""
        if "." in str(self.value):
            number_type = "float"
            
        else: 
            number_type = "int"
        self.number_type = number_type

@dataclass
class ObjectVal(RuntimeVal):
    def __init__(self, properties: {}):
        self.type = "object"
        self.properties = properties  # Assuming properties is a dictionary in Python

def import_env():
    from runtime.environment import Environment
    FunctionCall = Callable[[List[RuntimeVal], Environment], RuntimeVal]
    return FunctionCall

@dataclass
class NativeFn(RuntimeVal):
    def __init__(self, call: import_env):
        self.type = "native_fn"
        self.call = call
    
@dataclass
class FunctionVal(RuntimeVal):
    def __init__(self, name, params, declaration_env, body):
        self.type = "function"
        self.name: str = name
        self.params: [] = params
        self.declaration_env = declaration_env
        self.body = body

@dataclass
class StringVal(RuntimeVal):
    def __init__(self, value: str):
        self.type = "string"
        self.value = value
 

