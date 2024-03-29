import os
import re
import sys
import prints
from datetime import datetime
from io import StringIO
import hashlib
from exceptions import UnknownExpression, VariableDefined
from utils.helpers import check_string, generate_final_line, get_variable_key, get_data_from_line
from utils.constants import VERSION, BASEDIR


STRING_FORMATTING_ERROR = "String formatting error"
JLANG_KEYWORDS = ["if", "elif", "else", "for", "while", "func", "class", "self.", "try", "except"]
VARIABLE_KEYWORDS = ["class", "func"]
JLANG_FUNCTION_KEYWORD = "func"
JLANG_SIGNS = ["{", "}"]
DEFAULT_MODULES = ["exceptions", "functions", "primatives"]
JCACHE_DIR_NAME = "__jcache__" # The directory name for the cached jpy files

variables = {}
typed_variables = {}
loaded_modules = []
transpiled = ""


def get_classes():
    """ Gets all of the classes in the jlang file to the point currently parsed. """

    classes = []

    for ele in variables:
        if variables[ele] == "class": classes.append(ele)

    return classes


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
        
        else:
            module = line[line.index("load ")+5:-1]
            loaded_modules.append(module.lower())
            return_line = ""

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

                return_line = line.replace(type_kwd, "", 1)
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

    # Checks to see if the string is valid python (TODO - REMOVE)
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
    modules = ""
    indent_level = 0

    with open(file, "r") as f:
        raw_hash = hashlib.sha256(f.read().encode("utf-8"))
        hex_hash = raw_hash.hexdigest()

    # Adds the file provided by the end user
    # FIX: Ident the loaded modules to optimize
    user_file, indent_level_main = generate_lang(f"{file}")

    # Adds all of the files in the provided library
    for file_name in os.listdir(BASEDIR + "lib"):
        if file.endswith(".jlang"):
            pstring, indent_level = generate_lang(f"{BASEDIR}lib/{file_name}")

            if file_name[0:file_name.index(".")] in DEFAULT_MODULES:
                modules += pstring
            elif file_name[0:file_name.index(".")] in loaded_modules:
                modules += pstring

    # Adds the file provided by the end user
    user_file, indent_level_main = generate_lang(f"{file}")
    python_string = modules + user_file
    transpiled = user_file

    # If an indentation error is found raise here
    if indent_level_main != 0:
        print(indent_level)
        raise IndentationError

    if not os.path.isdir(JCACHE_DIR_NAME):
        os.mkdir(JCACHE_DIR_NAME)

    block_string = python_string.encode("utf-8")

    if "/" in file:
        python_string = f"HASH_{file[file.rindex('/'):file.rindex('.')]}='{hex_hash}'\n" + python_string

    else:
        python_string = f"HASH_{file[:file.rindex('.')]}='{hex_hash}'\n" + python_string

    # Dumps the output into the nearest compiled_files folder
    with open(JCACHE_DIR_NAME + "\\" + file[:file.index(".")] + ".jpy", "wb+") as jpy:
        jpy.write(python_string.encode('utf-8'))

    return transpiled


def check_for_cache(directory, filename):
    """
    Checks if there is a jcache in the given directory. 
    If so checks for the existance of the file in the cache.
    If exists checks if the file is the same as the source file by hash.
    :param directory: The list of files in the directory
    :param filename: The name of the file being checked for in the cache
    :return bool: If the file is able to be used fro the cache 
    """

    if JCACHE_DIR_NAME in directory:
        cache = os.listdir(os.getcwd() + f"/{JCACHE_DIR_NAME}")
        if filename[:-5]+"jpy" in cache:
            with open(os.getcwd()+f"/{JCACHE_DIR_NAME}/"+filename[:-5]+"jpy", "r") as f:
                first_line = ""
                for line in f:
                    first_line = line
                    break

                hash = first_line[4+len(filename[:-5])+2:-2]
                raw_hash = ""
                
                with open(file, "r") as f:
                    raw_hash = hashlib.sha256(f.read().encode('utf-8'))
                    hex_hash = raw_hash.hexdigest() 

                if hash == hex_hash:
                    return True
    
    return False


if __name__ == "__main__":

    start_time = datetime.now()

    dir = os.listdir()

    dump_py = False
    run = True
    show_result = False
    debug = False

    if len(sys.argv) <= 1:
        prints.ColorPrints.printc(f"[ERROR]: The filename must be provided! \njlang <filename>", prints.ColorPrints.RED)
        exit()
    
    if "--version" in sys.argv[1] or "-v" in sys.argv[1]:
        print(f"JLang Version {VERSION}")
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

    if dump_py:
        print("\033[91mDumping Files to Python Not Yet Supported!\033[00m")
        exit()

    # Checks if the current version of the file has been compiled before
    if check_for_cache(dir, file):
        ofile = file
        file = os.getcwd()+f"\\{JCACHE_DIR_NAME}" + "\\" + ofile[:-5] +"jpy"

    # Checks if a source jlang file is being used 
    if file.endswith(".jlang"):

        filename = file.replace(".jlang", "")

        # Parses jlang in jpy
        transpiled = parse_lang(file, dump_py)

        with open(f"{JCACHE_DIR_NAME}/{filename}.jpy", "r") as jpy:
            compiled = jpy.read()

        if show_result:
            print(transpiled)

        # Evaluates the jpy as python (Allows for future implementations of interperter ...)
        if run: exec(str(compiled.strip()))

        end_time = datetime.now()


    elif file.endswith(".jpy"):

        with open(f"{file}", "r") as jpy:
            compiled = jpy.read()

        if show_result:
            print(compiled)

        if run: exec(str(compiled.strip()))
    
        end_time = datetime.now()

    if debug:
        print("#"*45,"\nDebug Information\n","#"*45, sep="")
        print(f"Typed Variables: {typed_variables}")
        print(f"Runtime: {(end_time - start_time).total_seconds()}s")

