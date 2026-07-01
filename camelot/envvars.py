import os

ENV_DEPLOYMENT = "DEPLOYMENT"
ENV_BUCKET = "BUCKET"
ENV_SITE_DOMAIN = "SITE_DOMAIN"
ENV_INVITE_CODE = "INVITE_CODE"
ENV_REGISTRATION_MODE = "REGISTRATION_MODE"
ENV_RECAPTCHA_ENABLE = "RECAPTCHA_ENABLE"
ENV_DEBUG = "DEBUG"

def load_boolean_from_env(var_name, default: bool):
    truthy = ("true", "1", "yes", "on")
    falsy = ("false", "0", "no", "off")

    s = os.getenv(var_name)
    if s is None:
        return default
    s = s.lower()
    if s in truthy:
        return True
    elif s in falsy:
        return False
    else:
        return default
