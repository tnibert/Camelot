"""
Define constants that we use throughout the application
"""

# model sizes, will be used in forms and model definitions
GROUPNAMELEN=30
MAXPHOTODESC=150
MAXDISPLAYNAME=100
MAX_UPLOAD_SIZE=31457280  # 30 MB

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

MIN_FREE_THRES = 1024 * 1024 * 1024  # 1 GB
DATA_PARTITION_PATH = "/"