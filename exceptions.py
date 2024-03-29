class StringFormattingException(Exception):

    def __init__(self, string, index):
        self.string = string
        self.index = index

    def __str__(self):
        return f"String formatting error at index {self.index}. \nOn String: {self.string}"


class UnknownExpression(Exception):

    def __init__(self, string, line_number):
        self.string = string
        self.line_number = line_number

    def __str__(self):
        return f"Unknwon expression `{self.string}` in line {self.line_number}."


class VariableAssignmentError(Exception):

    def __init__(self, string, type_2=None):
        self.string = string
        self.type_2 = type_2

    def __str__(self):
        return f"Variable of type `{self.string}` incorrectly assigned to `{self.type_2}`"
        

class VariableTypeError(Exception):

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return f"Variable {self.string} incorrectly typed!"


class VariableDefined(Exception):

    def __init__(self, string):
        self.string = string

    def __str__(self):
        return f"Variable `{self.string}` has already been defined!"
        
