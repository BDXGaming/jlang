import re
from exceptions import StringFormattingException, VariableAssignmentError


STRING_CONTAINERS = ["'", '"']


def check_string(line_string):
    """ Checks if the string is correctly formatted. """

    if not line_string.__contains__('"') or line_string.__contains__("'"):
        raise (StringFormattingException(line_string, 0))

    has_start = False
    string_type = ""
    final_index = 0
    for index, char in enumerate(line_string):
        if char in STRING_CONTAINERS:

            if char in string_type:
                has_start = False
                final_index = index

            else:
                has_start = True
                string_type += f"{char}"

    if has_start == True:
        raise (StringFormattingException(line_string, final_index))

    return True

def generate_final_line(line, indent):
    """ Generates the line which is transcoded. """
    indent_line = ""

    for i in range(indent):
        indent_line += "    "

    return_line = indent_line + line
    return return_line

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