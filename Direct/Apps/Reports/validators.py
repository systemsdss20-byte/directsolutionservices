from datetime import datetime

from .query_config import FILTER_FIELDS, OPERATORS

class InvalidFilter(Exception):
    pass

def validate_filters(groups):
    """
    Validate structure of filters, fields, operators and values
    Raises InvalidFilter exception if any validation fails
    """

    if not isinstance(groups, list):
        raise InvalidFilter("Filters must be a list of groups")

    for group in groups:
        if "rules" not in group or not group["rules"]:
            raise InvalidFilter("Each group must have at least one rule")
        
        for rule in group["rules"]:
            field = rule.get("field")
            print(field)
            operator = rule.get("operator")
            value = rule.get("value")

            #Campo valido
            if field not in  FILTER_FIELDS:
                raise InvalidFilter(f"Invalid field: {field}")

            field_cfg = FILTER_FIELDS[field]
            field_type = field_cfg["type"]

            #Operador valido para el tipo
            valid_ops = [op[0] for op in OPERATORS[field_type]]
            if operator not in valid_ops:
                raise InvalidFilter(f"Invalid operator: '{operator}' for field '{field}'")
            
            #Valor obligatorio (excepto operadores especiales futuros)
            if value in ("", None):
                raise InvalidFilter(f"Empty value for field '{field}'")

            #Validacion por tipo
            validate_value_by_type(field, field_type, value)

def validate_value_by_type(field, field_type, value):
    match field_type:
        case "boolean":
            if value not in ("True", "False", True, False):
                raise InvalidFilter(f"Invalid boolean value for {field}")
        case "choice":
            if value not in FILTER_FIELDS[field]["choices"]:
                raise InvalidFilter(f"Invalid choice '{value}' for {field}")
        case "date":
            try:
               datetime.fromisoformat(value)
            except ValueError:
                raise InvalidFilter(f"Invalid date value for {field}")
        case "string":
            if not isinstance(value, str):
                raise InvalidFilter(f"Invalid value type for {field}")
        case _:
            pass
    
