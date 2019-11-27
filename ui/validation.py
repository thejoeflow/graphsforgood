import re

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


def registration(username, password):
    """
    Returns True if the username and password meet the required length requirements and the username does not use any
    forbidden characters

    :param username:
    :param password:
    :return: True if username and password are valid, False otherwise
    """
    return validate_values['NAME_MIN_LEN'] <= len(username) <= validate_values['NAME_MAX_LEN'] and \
           validate_values['PWORD_MIN_LEN'] <= len(password) <= validate_values['PWORD_MAX_LEN'] and \
           re.fullmatch(validate_values['NAME_REGEX'], username, flags=re.IGNORECASE) is not None
