import re

variables = {}
macros = {}

var_def_regex = r"NEW VAR (\w+)\s*=\s*(\d+)"
macro_def_regex = r"NEW MACRO (\w+)\s*\(([\w\s,]*)\)\s*\{(.+)\}"
exec_block_regex = r"EXEC\s*\{(.+)\}"
command_regex = r"(turnToMy|turnToThe|walk|jump|drop|pick|grab|letGo|pop|moves|safeExe)\(([^)]*)\)"
control_structure_regex = r"(if|do|rep|fi|od|per|else)"

def parse_variable_definition(line):
    match = re.match(var_def_regex, line)
    if match:
        var_name, var_value = match.groups()
        if var_name in variables:
            raise ValueError(f"La variable '{var_name}' ya fue definida.")
        variables[var_name] = int(var_value)
        return True
    return False

def parse_macro_definition(line):
    match = re.match(macro_def_regex, line)
    if match:
        macro_name, params, block = match.groups()
        if macro_name in macros:
            raise ValueError(f"El macro '{macro_name}' ya fue definido.")
        macros[macro_name] = (params.split(","), block.strip())
        return True
    return False

def parse_exec_block(line):
    match = re.match(exec_block_regex, line)
    if match:
        block_content = match.groups()[0]
        return parse_block(block_content)
    return False

def parse_block(block):
    commands = block.split(";")
    for command in commands:
        command = command.strip()
        if not command:
            continue
        if not (parse_command(command) or parse_control_structure(command)):
            raise ValueError(f"Syntaxis invalida en el comando: '{command}'")
    return True

def parse_command(command):
    match = re.match(command_regex, command)
    if match:
        command_name, params = match.groups()
        return validate_command(command_name, params)
    return False

def validate_command(command_name, params):
    params_list = params.split(",") if params else []
    
    if command_name == "turnToMy":
        if params_list[0] not in ["left", "right", "back"]:
            raise ValueError(f"Invalid direction '{params_list[0]}' for turnToMy")
    elif command_name == "turnToThe":
        if params_list[0] not in ["north", "south", "east", "west"]:
            raise ValueError(f"Invalid orientation '{params_list[0]}' for turnToThe")
    elif command_name in ["walk", "jump", "drop", "pick", "grab", "letGo", "pop"]:
        if not validate_value(params_list[0]):
            raise ValueError(f"Invalid value '{params_list[0]}' for {command_name}")
    elif command_name == "moves":
        if not all(move in ["forward", "right", "left", "backwards"] for move in params_list):
            raise ValueError(f"Invalid moves '{params_list}' in 'moves'")
    elif command_name == "safeExe":
        return parse_command(params_list[0])
    
    return True

def parse_control_structure(command):
    if re.match(control_structure_regex, command):
        return True
    return False

def validate_value(value):
    if value.isdigit() or value in variables:
        return True
    return False

def parse_lines(lines):
    global variables, macros
    variables = {}
    macros = {}
    
    try:
        for line in lines:
            line = line.strip().lower()
            if line.startswith("new var"):
                if not parse_variable_definition(line):
                    return "no: Definicion de variable invalida."
            elif line.startswith("new macro"):
                if not parse_macro_definition(line):
                    return "no: definicion de Macro invalida."
            elif line.startswith("exec"):
                if not parse_exec_block(line):
                    return "no: bloque EXEC invalido."
            else:
                return f"no: syntaxis invalido '{line}'."
        return "si"
    except ValueError as e:
        return f"no: {e}"

def parse_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()
        return parse_lines(lines)
    except FileNotFoundError:
        return "No se encontró el archivo."
    except Exception as e:
        return f"{e}"

def main():
    print("Escoge una de las siguientes opciones:")
    print("1. Ingresa el input de forma manual")
    print("2. Ingresa el input desde un archivo.txt")
    
    choice = input("Escoja entre (1 or 2): ").strip()
    
    if choice == "1":
        user_input = []
        print("Ingresa el input del codigo:")
        while True:
            line = input()
            user_input.append(line)
            result = parse_lines(user_input)
            print(result)
    
    elif choice == "2":
        file_path = input("Ingrese la ruta del archivo .txt: ").strip()
        result = parse_file(file_path)
        print(result)
    
    else:
        print("Opcion invalida. porfavor escoja entre 1 o 2.")
main()
