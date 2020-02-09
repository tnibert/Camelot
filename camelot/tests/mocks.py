from datetime import datetime

class photomock:
    def __init__(self, uploader, album, pub_date):
        self.uploader = uploader
        self.pub_date = pub_date
        self.album = album

class profilecontrolmock:
    def get_feed(self):
        feed = [
            photomock("testuser1", "testalbum1", datetime(2012, 9, 16)),
            photomock("testuser1", "testalbum1", datetime(2012, 9, 16)),
            photomock("testuser1", "testalbum2", datetime(2012, 9, 16)),
            photomock("testuser2", "testalbum1", datetime(2012, 9, 16)),
            photomock("testuser2", "testalbum3", datetime(2012, 8, 14)),
            photomock("testuser3", "testalbum3", datetime(2012, 8, 14))
        ]
        return feed

