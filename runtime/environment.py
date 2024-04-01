from typing import Optional
from runtime.values import NumberVal, RuntimeVal, BooleanVal, NullVal, ObjectVal

class Environment:
    def __init__(self, parentENV: Optional['Environment'] = None):
        env_global: bool
        if isinstance(parentENV, Environment):
            env_global = True
        else:
            env_global = False
            
        self.parent: Optional['Environment'] = parentENV
        self.variables = {}
        self.constants = []
        
        # if env_global:
        #     setupGlobalScope(self)
            

    def declareVar(self, varname: str, value: RuntimeVal, constant: bool) -> RuntimeVal:
        if varname in self.variables:
            raise ValueError(f"Cannot declare variable {varname}. As it already is defined.")
        self.variables[varname] = value
        
        if constant:
            self.constants.append(varname)
        return value

    def assignVar(self, varname: str, value) -> RuntimeVal:
        env = self.resolve(varname)
        if varname in env.constants:
            raise ValueError(f"Cannot assign a value to variable {varname} as it was declared a constant.")
        env.variables[varname] = value
        return NumberVal(value)

    def lookupVar(self, varname: str) -> RuntimeVal:
        env = self.resolve(varname)
        return env.variables[varname]

    def resolve(self, varname: str) -> 'Environment':  
        if varname in self.variables:
            return self
        if self.parent is None:
            raise ValueError(f"Cannot resolve '{varname}' as it does not exist.")
        return self.parent.resolve(varname)
   
def createGlobalEnv():
    env = Environment()
    env.declareVar("true", BooleanVal(True), True) 
    env.declareVar("false", BooleanVal(False), True)

    from runtime.values import NativeFn
    def printout(args, scope):
        print(*args)
    def printlnout(args, scope):
        print(*args, "\n")
    def inputin(args, scope):
        prompt = args[0] if args else ""
        return input(prompt)
    # env.declareVar("print", NativeFn(printout), True)
    # env.declareVar("println", NativeFn(printlnout), True)
    # env.declareVar("input", NativeFn(inputin), True)

    env.declareVar("con", ObjectVal({'out': ObjectVal({'print': NativeFn(printout), 'println': NativeFn(printlnout)}), 'in': NativeFn(inputin)}), True)

    return env