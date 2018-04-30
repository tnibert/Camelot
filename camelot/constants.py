"""
Define constants that we use throughout the application
"""

# model sizes, will be used in forms and model definitions
GROUPNAMELEN=30
MAXPHOTODESC=150
MAXDISPLAYNAME=100

ALBUM_PUBLIC=1
ALBUM_ALLFRIENDS=2
ALBUM_GROUPS=3
ALBUM_PRIVATE=4

ACCESSTYPES = {ALBUM_PUBLIC: "public",
                   ALBUM_ALLFRIENDS: "all friends",
                   ALBUM_GROUPS: "specified groups",
                   ALBUM_PRIVATE: "owner and contributors"}
