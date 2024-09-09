import re

variables = {}
macros = {}


var_def_regex = r"NEW VAR (\w+)\s*=\s*(\d+)"
macro_def_regex = r"NEW MACRO\s*(\w+)\s*\((\w*\s*)\)*"
exec_block_regex = r"EXEC\s*\{(.*)\}"
command_regex = r"(turnToMy|turnToThe|walk|jump|drop|pick|grab|letGo|pop|moves|safeExe|nop)\s*\((.*)\s*\)"
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
        macro_name, params = match.groups()
        if macro_name in macros:
            raise ValueError(f"El macro '{macro_name}' ya fue definido.")
        macros[macro_name] = [param.strip() for param in params.split(",")]
        return True
    return False


def parse_exec_block(line):
    match = re.match(exec_block_regex, line)
    if match:
        block_content = match.group(1)  # Use group(1) to access the matched content
        return parse_block(block_content)
    return False


def parse_block(block):
    commands = block.split(";")
    for command in commands:
        command = command.strip()
        if command:  # Only process non-empty commands
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
    params_list = [p.strip() for p in params.split(",")] if params else []
    
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
        if not all(move in ["forward", "right", "left", "backwards", "back"] for move in params_list):
            raise ValueError(f"Invalid moves '{params_list}' in 'moves'")
    elif command_name == "safeExe":
        return parse_command(params_list[0])
    
    return True


def parse_control_structure(command):
    return bool(re.match(control_structure_regex, command))


def validate_value(value):
    return value.isdigit() or value in variables


def parse_lines(lines):
    global variables, macros
    variables.clear()
    macros.clear()
    
    try:
        for line in lines:
            line = line.strip()
            if line.startswith("NEW VAR"):
                if not parse_variable_definition(line):
                    return "no: Definicion de variable invalida."
            elif line.startswith("NEW MACRO"):
                if not parse_macro_definition(line):
                    return "no: definicion de Macro invalida."
            elif line.startswith("EXEC"):
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
            for line in file:
                result = parse_lines([line])
                if result != "si":
                    return result
        return "si"
    except FileNotFoundError:
        return "no: File not found."
    except Exception as e:
        return f"no: {e}"


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
        print("Opcion invalida. Por favor escoja entre 1 o 2.")

main()
