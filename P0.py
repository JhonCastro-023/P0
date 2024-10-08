import re


##Numero
numero = r"^-?\d+(\.\d+)?$"

##bloque
bloque = r"\n*{.*;*}\n*"

##var
var_def_regex = rf"NEW VAR (\w+)\s*=\s*{numero}]"

##Macro
macro_def_regex = rf"NEW MACRO\s*(\w+)\s*\((\w*\s*)\)*{bloque}*"

##EXEC
exec_block_regex = rf"EXEC\s*{bloque}"

##Valores
lista_valores = ["size", "myX", "myY", "myChips", "myBalloons", "balloonsHere", "chipsHere", "roomForChips"]
Valores_Patron = "|".join(re.escape(palabra) for palabra in lista_valores)
valores_regex = rf"({Valores_Patron})"

##Comandos
    ##direcciones
direcciones_simples = r"\s*(forward|left|right|back|backwards)\s*"
direcciones_complejas = r"\s*(north|south|east|west)\s*"
    ##Todos los comandos
turnToMy = rf"turnToMy\s*\(\s*{direcciones_simples}\s*\)"
turnToThe = rf"turnToMy\s*\(\s*{direcciones_complejas}\s*\)"
comandos_para_w_j_d_p_g_lG_pop = r"(walk|jump|drop|pick|grab|letGo|pop)\s*"
w_j_d_p_g_lG_pop = rf"{comandos_para_w_j_d_p_g_lG_pop}\(\s*{numero}\s*\\)"
moves = rf"moves\s*\(\s*({direcciones_simples},)*\s*\)"
nop = r""
todos_comandos_msafeExe = rf"\s*({turnToMy}|{turnToThe}|{w_j_d_p_g_lG_pop}|{moves}|{nop})\s*"
safeExe = rf"safeExe\s*\({todos_comandos_msafeExe}\)"
##para añadir valores añadir a la lista 
lista_comandos = [r"{turnToMy}", r"{turnToThe}", r"{w_j_d_p_g_lG_pop}", r"{moves}", r"{safeExe}", r"{nop}"]
comandos_Patron = "|".join(re.escape(palabra) for palabra in lista_comandos)
command_regex = rf"({comandos_Patron})\s*\(\s*(.*)\s*\)"

##Condicionales y condicion
isBlocked = rf"isBlocked\?\s*\(\s*{direcciones_simples}\s*\)"
isFacing = rf"isFacing\?\s*\(\s*{direcciones_complejas}\s*\)"
zero = rf"zero\?)\s*\(\s*{numero}\s*\)"
condicion = rf"({isBlocked}|{isFacing}|{zero})"
condicional_then = rf"\n+then\s*{bloque}"
condicional_else = rf"(\n+else\s*{bloque})?"
condicional_then_else = rf"({condicional_then}{condicional_else})*"
condicinoal_not = r"\s+(not?)"
condicional = rf"if{condicinoal_not}\s*\(({condicion})\s*\){condicional_then_else}"

##Loop
loop = rf"do\s*{condicion}\s*{bloque})\s*"

##repetirnumveces
Repeticion = rf"rep\s*{numero}\s*{bloque}"


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
    lista_palabras=[]
    if match:
        macro_name, params = match.groups()
        if macro_name in macros:
            raise ValueError(f"El macro '{macro_name}' ya fue definido.")
        macros[macro_name] = [param.strip() for param in params.split(",")]
        lista_palabras.append(macro_name)
        Palabras_Patron = "|".join(re.escape(palabra) for palabra in lista_palabras)
        command_regex = rf"({Palabras_Patron})\s*\((.*)\s*\)"
        print(command_regex)
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
    print(command)
    match = re.match(command_regex, command)
    print(match)
    if match:
        command_name, params = match.groups()
        return validate_command(command_name, params)
    return False

def validate_command(command_name, params):
    params_list = params.split(",") if params else []
    cleaned_params_list = [move.strip() for move in params_list]
    if command_name == "turnToMy":
        if cleaned_params_list[0] not in ["left", "right", "back"]:
            raise ValueError(f"Invalid direction '{cleaned_params_list[0]}' for turnToMy")
    elif command_name == "turnToThe":
        if cleaned_params_list[0] not in ["north", "south", "east", "west"]:
            raise ValueError(f"Invalid orientation '{cleaned_params_list[0]}' for turnToThe")
    elif command_name in ["walk", "jump", "drop", "pick", "grab", "letGo", "pop"]:
        if not validate_value(cleaned_params_list[0]):
            raise ValueError(f"Invalid value '{cleaned_params_list[0]}' for {command_name}")
    elif command_name == "moves":
        if not all(move in ["forward", "right", "left", "backwards","back"] for move in cleaned_params_list):
            raise ValueError(f"Invalid moves '{cleaned_params_list}' in 'moves'")
    elif command_name == "safeExe":
        return parse_command(cleaned_params_list[0])
    
    return True

def parse_control_structure(command):
    control_structure_regex= rf"({condicional}|{loop}|{Repeticion})"
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
