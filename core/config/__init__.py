from core.config.config_loader import parse_property
from core.config.parsers import string_parser, integer_parser, boolean_parser


def string_parse(property:str, default=""):
    return parse_property(property, string_parser(non_null=True, default=default))

def integer_parse(property:str, default:int = 0):
    return parse_property(property, integer_parser(default=default))

def bool_parse(property:str, default:bool = False):
    return parse_property(property, boolean_parser(default))

DATABASE_URL = string_parse('database.url')

#region JWT config
SECRET_KEY = string_parse("jwt.secret_key")
ALGORITHM = string_parse("jwt.algorithm")

ACCESS_TOKEN_EXPIRE_MINUTES = integer_parse("jwt.expiration.access_token")
REFRESH_TOKEN_EXPIRE_MINUTES = integer_parse("jwt.expiration.refresh_token")
#endregion

#region Mail config
MAIL_PORT = integer_parse("email_verification.server.port")
MAIL_SERVER = string_parse("email_verification.server.host")

MAIL_USERNAME = string_parse("email_verification.username")
MAIL_PASSWORD = string_parse("email_verification.password")

MAIL_FROM = string_parse("email_verification.from_data.mail")
MAIL_FROM_NAME = string_parse("email_verification.from_data.name")

USE_CREDENTIALS = bool_parse("email_verification.use_credentials")

MAIL_STARTTLS= bool_parse("email_verification.server.start_tls")
MAIL_SSL_TLS= bool_parse("email_verification.server.use_ssl")
VERIFICATION_TOKEN_EXPIRE_MINUTES = integer_parse("email_verification.token_expiration")
#endregion

if __name__ == "__main__":
    print(globals())