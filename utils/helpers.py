from exceptions import StringFormattingException


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

