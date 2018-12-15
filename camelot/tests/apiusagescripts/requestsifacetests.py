from login import login, HOST
from uploadphoto import upload_photo
from alterdescription import alter_description
from getalbums import get_albums

"""
This is a combined script to mix various API operations together
"""

if __name__ == '__main__':
    userid = 4

    s = login("testuser", "testpassword")
    photoid = upload_photo(s, 5)['id']
    alter_description(s, photoid, "a test description")
    resp = get_albums(s, userid)
    print(resp)
