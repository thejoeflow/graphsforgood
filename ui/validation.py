from ui import webapp

validate_values = {
    'PWORD_MIN_LEN': 6,
    'PWORD_MAX_LEN': 20,
    'NAME_MIN_LEN': 3,
    'NAME_MAX_LEN': 20,
    'NAME_REGEX': '^([0-9a-z_\\-\\s])+$'
}


@webapp.context_processor
def add_validate_values():
    """
    This function returns a validation values dictionary which contains constraints we want to use for client side
    validation AND server-side validation - while only specifying them in one place. These values are accessible from
    any template using the following syntax: {{KEY}}

    e.g In client side javascript:
    checkLength( username, "username", {{NAME_MIN_LEN}}, {{NAME_MAX_LEN}} )

    :return: A dictionary containing values needed for validation
    """
    return validate_values
