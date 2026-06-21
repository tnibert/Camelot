"""
Define constants that we use throughout the application
"""
import environ
from .envvars import ENV_SITE_DOMAIN

env = environ.Env()
SITEDOMAIN = env(ENV_SITE_DOMAIN)

# model sizes, will be used in forms and model definitions
GROUPNAMELEN=30
MAXPHOTODESC=150
MAXDISPLAYNAME=100
MAX_UPLOAD_SIZE=31457280  # 30 MB

MAX_ALBUM_NAME_LEN = 70

# enum
ALBUM_PUBLIC=1
ALBUM_ALLFRIENDS=2
ALBUM_GROUPS=3
ALBUM_PRIVATE=4

ACCESSTYPES = {ALBUM_PUBLIC: "public",
               ALBUM_ALLFRIENDS: "all friends",
               ALBUM_GROUPS: "specified groups",
               ALBUM_PRIVATE: "owner and contributors"}

PREFIX=""

THUMBHEIGHT=180
MIDHEIGHT=600

# enum
DEPLOYMENT_AWS = "aws"
DEPLOYMENT_LOCAL = "linux"
