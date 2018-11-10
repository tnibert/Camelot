from login import login, HOST
from uploadphoto import upload_photo
from alterdescription import alter_description

"""
This is a combined script to mix various API operations together
"""

if __name__ == '__main__':
    s = login("testuser", "testpassword")
    photoid = upload_photo(s, 23)['id']
    alter_description(s, photoid, "a test description")
