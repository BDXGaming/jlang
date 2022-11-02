import os
import re
import sys
from io import StringIO
from exceptions import UnknownExpression, VariableAssignmentError, VariableDefined
from utils.helpers import check_string


STRING_FORMATTING_ERROR = "String formatting error"
JLANG_KEYWORDS = ["if", "elif", "else", "for", "while", "func", "class", "self.", "try", "except"]
VARIABLE_KEYWORDS = ["class", "func"]
JLANG_FUNCTION_KEYWORD = "func"
JLANG_SIGNS = ["{", "}"]

variables = {}
typed_variables = {}
loaded_modules = []


def get_variable_key(line):
    """ This gets the name of a variable from the line and strips and leading text. """

    assignment = ""

    if "=" in line:
        assignment = "="

    if "||" in line:
        assignment = "||"

    if assignment != "":
        if line.index(" ") < line.index(assignment):
            var_key = line[line.index(" "):line.index(assignment)]
        else:
            var_key = line[0:line.index(assignment)]
        var_key = var_key.strip()
        return var_key

    raise VariableAssignmentError(line)


def get_classes():
    """ Gets all of the classes in the jlang file to the point currently parsed. """

    classes = []

    for ele in variables:
        if variables[ele] == "class": classes.append(ele)

    return classes


def get_data_from_line(line):
    """ Gets the data paired with a variable which follows a equals sign or a || """

    line = line.strip()
    line = line.replace("\n", "")

    if "//" in line:
        if re.findall(r'(".*\/\/.*")', line):
            line = line[0:line.index("//")]

    data = ""
    if "||" in line:
        data = line[line.index("||")+2:]

    elif "=" in line:
        data = line[line.index("=")+1:]

    return data


def generate_final_line(line, indent):
    """ Generates the line which is transcoded. """
    indent_line = ""

    for i in range(indent):
        indent_line += "    "

    return_line = indent_line + line
    return return_line


def compile(line, old_indent_level):
    """ Compiles the jlang into a python file which can be evaluated in python. """

    # Removes any existing whitespace from the line
    line = line.strip()
    line = line + "\n"
    indent_level = old_indent_level
    return_line = line

    # Handles the jlang
    if line.startswith("//"):
        return generate_final_line(return_line.replace("//", "#"), indent_level), indent_level

    # Handles all loading of external content
    if return_line.startswith("load"):
        load= line[line.index("load") +5:]

        if "python." in load:
            module = line[line.index("python.")+7:-1]
            loaded_modules.append(module)
            return_line = ""

            if module.startswith("module"):
                mod_type = line[line.index(module)+7:]
                return_line = f"import {mod_type}\n"

            return return_line, indent_level

    if any(line.startswith(keyword) for keyword in VARIABLE_KEYWORDS):
        first_word = line[0:line.index(" ")]
        if first_word in VARIABLE_KEYWORDS:
            key = ""

            if "=" in line:
                key = line[line.index(" ")+1:line.index("=")]

            elif "(" in line:
                key = line[line.index(" ")+1:line.index("(")]

            elif "{" in line:
                key = line[line.index(" ")+1:line.index("{")]

            elif ":" in line:
                key = line[line.index(" ")+1:line.index(":")]

            if key != "":
                variables[key] = first_word

    # Handles the use of native python functions
    if "python." in return_line:
        return_line = return_line.replace("python.", "")

    # Handles formatted strings
    if "${" in return_line:
        return_line = return_line.replace("${", "{")

    # Handles the specific odd syntax of the show function
    if return_line.__contains__("show | "):

        string_enclosing = []
        string = return_line.replace("show | ", "")
        if string.startswith(" "): string = string[1:]

        is_string = check_string(string)

        if is_string:
            # if string.__contains__("'"): string = string.replace("'", "")
            # if string.__contains__('"'): string = string.replace('"', "")
            string = string.strip()
            return_line  =  f"""show({string})""" + "\n"

        else:
            exit()

    # Handles all of the typed variables
    if any(return_line.startswith(type_keyword+" ") for type_keyword in get_classes()):
        for type_kwd in get_classes():
            if type_kwd in line:

                return_line = line.replace(type_kwd, "")
                if " " in type_kwd: type_kwd = type_kwd[0:-1]

                if get_variable_key(line) in typed_variables.keys():
                    if typed_variables[get_variable_key(line)] != type_kwd:
                        raise VariableDefined(get_variable_key(line))

                data = get_data_from_line(return_line)
                variables[get_variable_key(line)] = type_kwd
                return_line = f"{get_variable_key(line)} = {type_kwd}({data})"
                typed_variables[get_variable_key(line)] = type_kwd
                break

    elif "=" in line and "==" not in line:


        if " " not in (line[0:line.index("=")]).strip():
            var = (line[0:line.index("=")]).strip()
            if var in typed_variables.keys():
                data = return_line[return_line.index("=")+1:]
                return_line = var + ".reassign("+data.strip()+")"

    # elif(any(line.startswith(var) for var in typed_variables.keys())):
    #     print("VAR: ", line)

    # Handles all of the conditional functions that are the same in py and jlang
    if any(line.startswith(pstring) for pstring in JLANG_KEYWORDS):

        if ("{" in return_line and "}" in return_line) and "${" not in return_line:
            return_line = return_line.replace("{", ":")
            return_line = return_line.replace("}", "")

        elif "{" in return_line:
            return_line = return_line.replace("{", ":")
            indent_level += 1

        elif "}" in return_line:
            return_line = return_line.replace("}", "")
            indent_level -= 1

        return_line = return_line

    # Handles the JLANG indent form
    elif return_line.startswith("}"):
        return_line = return_line.replace("}", "")
        indent_level -= 1

    if line.startswith(JLANG_FUNCTION_KEYWORD):
        return_line = return_line.replace(JLANG_FUNCTION_KEYWORD, "def")
        variables[return_line[4:return_line.index("(")]] = "func"
        return_line = return_line

    # The jlang expression for variable assignemt
    if "||" in return_line:
        return_line =  return_line.replace("||","=")

    indent_line = ""

    for i in range(old_indent_level):
        indent_line += "    "

    return_line = indent_line + return_line

    if not return_line.endswith("\n"): return_line += "\n"

    return return_line, indent_level
    

def is_jlang(string: str, line=None):
    """ Checks if the string is valid jlang """

    string = string.strip()
    if string.startswith("show") or string.startswith("python."):
        return True

    if any(string.startswith(pstring) for pstring in JLANG_KEYWORDS):
        return True

    if any(string.startswith(pstring) for pstring in loaded_modules):
        return True

    if any(string.startswith(var) for var in JLANG_FUNCTION_KEYWORD):
        return True

    if string.startswith("//"):
        return True

    if string.startswith(JLANG_FUNCTION_KEYWORD):
        return True

    if any(string.startswith(var) for var in variables):
        return True

    if string.startswith("load"): return True

    # The jlang function format
    if string.startswith("func"):
        return True

    if "||" in string: return True

    if any(string.startswith(sign) for sign in JLANG_SIGNS):
        return True

    try:
        old_stdout = sys.stdout
        sys.stdout = mystdout = StringIO()

        exec(string)

        sys.stdout = old_stdout
        return True
    except:
        raise (UnknownExpression(string, line + 1))


def generate_lang(file_location):
    """
    Iterates over the given file and parses the file into a .jpy file which can later be run by the interpreter
    :param file_location:
    :return python_string, indent_leve:
    """
    indent_level = 0
    python_string = ""
    with open(f"{file_location}", "r") as lib_funcs:
        for index, line in enumerate(lib_funcs):
            python_output, indent_level = compile(line, indent_level)
            python_string += python_output
    return python_string, indent_level


def parse_lang(file, dump_py):

    python_string = "# Script generated by jLang \n"
    indent_level = 0

    # Adds all of the files in the provided library
    for file_name in os.listdir("lib"):
        if file.endswith(".jlang"):
            pstring, indent_level = generate_lang(f"lib/{file_name}")
            python_string += pstring

    # Adds the file provided by the end user
    pstring, indent_level = generate_lang(f"{file}")
    python_string += pstring

    # If an indentation error is found raise here
    if indent_level != 0:
        print(indent_level)
        raise IndentationError

    if not os.path.isdir("__jcache__"):
        os.mkdir("__jcache__")

    # Dumps the output into the nearest compiled_files folder
    with open("__jcache__\\" + file[:file.index(".")] + ".jpy", "wb+") as jpy:
        jpy.write(python_string.encode('utf-8'))


if __name__ == "__main__":

    dump_py = False
    run = True
    show_result = False
    debug = False

    if len(sys.argv) <= 1:
        print(f"[ERROR]: The filename must be provided! \n python jlang.py <filename>")
        exit()

    file = sys.argv[1]

    if len(sys.argv) > 2:
        if "--as_py" in sys.argv:
            dump_py = True

        if "--norun" in sys.argv:
            run = False

        if "--show_py" in sys.argv:
            show_result = True

        if "--debug" in sys.argv:
            debug = True

    if file.endswith(".jlang"):
        filename = file.replace(".jlang", "")
        parse_lang(file, dump_py)

        with open(f"__jcache__/{filename}.jpy", "r") as jpy:
            compiled = jpy.read()

        if show_result:
            print(compiled)

        if run: exec(str(compiled.strip()))

    elif file.endswith(".jpy"):
        with open(f"{file}", "r") as jpy:
            compiled = jpy.read()

        if show_result:
            print(compiled)

        if run: exec(str(compiled.strip()))

    if debug:
        print("#"*45,"\nDebug Information\n","#"*45, sep="")
        print(f"Typed Variables: {typed_variables}")

