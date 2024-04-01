from sys import exception
from runtime.environment import createGlobalEnv, Environment
from frontend.parser import Parser
from runtime.interpreter import evaluate
from runtime.values import BooleanVal, NumberVal, NativeFn
import os



def repl():
    parser = Parser()
    env = Environment()
    print("BeamScript Language v0.3.2 Dev")

    # Continue Repl Until User Stops Or Types `exit`
    while True:
        env.variables.clear()
        env.constants.clear()
        env = createGlobalEnv()
        input_text = input(">>> ")
        # Check for no user input or exit keyword.
        if not input_text or "exit" in input_text:
            exit(0)
        
        input_list = input_text.split()
        # 
        if input_list[0] == "run":
            with open(f"{os.getcwd()}\{input_list[1]}") as file:
                source = file.read()
        else:
            source = input_text
        # Produce AST From source code
        program = parser.produceAST(source)
        # print(program)
        
        evaluate(program, env)
        # print(result)   #.value)

if __name__ == "__main__":
    repl()
