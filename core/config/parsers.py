from core.config.config_loader import ParseConfigResult

def string_parser(
    default="",
    non_null=True, 
    min_length:int|None=None, 
    max_length:int|None=None
):

    def parser(value:str|None) -> ParseConfigResult:
        
        if non_null and value == None:
            return False, "This value cannot be None.", None
        elif not non_null:
            return True, None, default

        length = len(value)

        if min_length and length < min_length:
            return False, f"Min length is {min_length}. Value has {length}."
        
        if max_length != None:
            value = value[0:max_length]

        return True, None, value

    return parser

def boolean_parser(
    default=0,
    non_null=True
):

    def parser(value:bool|None) -> ParseConfigResult:
        
        if non_null and value == None:
            return False, "This value cannot be None.", None
        elif not non_null:
            return True, None, default

        if not isinstance(value, bool):
            return False, "Value must be true or false.", None

        return True, None, value

    return parser

def integer_parser(
    default=False,
    non_null=True
):

    def parser(value:int|None) -> ParseConfigResult:
        
        if non_null and value == None:
            return False, "This value cannot be None", None
        elif not non_null:
            return True, None, default
        
        if not isinstance(value, int):
            return False, "Value must be integer", None

        return True, None, value

    return parser
