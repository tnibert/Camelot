from ..models import Album, Photo, Profile
from .utilities import *
from .friendcontroller import are_friends
from .genericcontroller import genericcontroller
from .groupcontroller import is_in_group
from ..constants import *
from django.utils import timezone
from os import makedirs, unlink
from io import BytesIO
from PIL import Image

class albumcontroller(genericcontroller):
    """
    Class for accessing albums for a given user
    This will make life easier in the long run
    All of this will need user permission checks at some point - in view layer... actually maybe in this layer
    All of this will need exception catching (in view layer? probably not I'm now thinking) as well

    Get a better handle on what objects are returned by the ORM and add docstrings to everything
    """

    def create_album(self, name, description):

        try:
            # check if the name already exists for the current user
            try:
                Album.objects.get(owner=self.uprofile, name=name)
            # if not, it's a go
            except Album.DoesNotExist:
                newalbum = Album(name=name, description=description, pub_date=timezone.now(), owner=self.uprofile,
                                 accesstype=ALBUM_ALLFRIENDS)
                newalbum.save()
                return newalbum
            raise AlreadyExistsException("Album needs unique name")    # may want to make this exception less general
        except:
            raise

    # may want to also add methods for edit permission
    def has_permission_to_view(self, album):
        """
        Check if the current user has permission to view the specified album
        :param album: the album who's permissions to check
        :return: boolean
        Damn this is some overhead...
        """
        # if public, can view
        if album.accesstype == ALBUM_PUBLIC:
            return True

        # owner and contributors can view, checks for ALBUM_PRIVATE access type
        if self.uprofile == album.owner or self.uprofile in album.contributors.all():
            return True

        # this may need to be a bit more fleshed out
        # what if owner wants to show to all friends, but contributor only to a group?
        if album.accesstype == ALBUM_ALLFRIENDS:
            for i in collate_owner_and_contrib(album):
                if are_friends(self.uprofile, i):
                    return True

        elif album.accesstype == ALBUM_GROUPS:
            # check uprofile against all groups
            for group in album.groups.all():
                if is_in_group(group, self.uprofile):
                    return True

        # if we have not returned True, no access
        return False

    def return_albums(self, profile=None, contrib=False):
        """
        Return albums owned or contributed to by a given profile, verifying permissions for albums to return
        Eventually we will want to return albums the profile contributes to as well
        :param profile: profile to find albums of
        :param contrib: If true, return albums contributed to, if false, owned
        :return: list of albums
        """
        if profile is None:
            profile = self.uprofile

        try:
            if contrib:
                albumset = Album.objects.filter(contributors=profile)
            else:
                albumset = Album.objects.filter(owner=profile)
        except Exception as e:
            raise e

        albums = []
        for album in albumset:
            if self.has_permission_to_view(album):
                albums.append(album)

        return albums
        
    def return_album(self, id):
        """
        Return an album by id, verifying permissions for album
        :param id:
        :return: album or raise exception
        """
        # we could reference this by primary key, depending on what we can get easiest from the front end
        try:
            album = Album.objects.get(id=id)
        except:
            raise
        if self.has_permission_to_view(album):
            return album
        else:
            raise PermissionException

    def add_photo_to_album(self, albumid, description, fi):
        """
        Saves photo to disk and adds it to the given album
        this could be done in something like celery
        :param albumid: id of the album to add to
        :param description: description of the photo
        :param fi: the image file
        :return: reference to the newly created photo object
        """

        album = self.return_album(albumid)

        # check that user has permission to add to album
        if not ((self.uprofile == album.owner) or (self.uprofile in album.contributors.all())):
            raise PermissionException("User is not album owner or contributor")

        # add file to database
        newphoto = Photo(description=description, album=album, uploader=self.uprofile)
        newphoto.save()

        # create filename with primary key
        # will it reuse ids?  I think it will.  But does that matter?  Maybe not..
        fname = PREFIX + 'userphotos/{}/{}/{}'.format(self.uprofile.user.id, album.id, newphoto.id)
        thumbname = PREFIX + 'thumbs/{}/{}/{}.jpg'.format(self.uprofile.user.id, album.id, newphoto.id)
        midname = PREFIX + 'mid/{}/{}/{}.jpg'.format(self.uprofile.user.id, album.id, newphoto.id)

        # update filename in db now that we have our primary key
        newphoto.filename = fname
        newphoto.thumb = thumbname
        newphoto.midsize = midname

        fi.seek(0)
        with Image.open(BytesIO(fi.read())) as img:
            newphoto.imgtype = Image.MIME[img.format]

        # save data structure to db
        newphoto.save()

        # well now we definitely depend on python 3.2+
        makedirs("/".join(fname.split("/")[:-1]), exist_ok=True)
        makedirs("/".join(thumbname.split("/")[:-1]), exist_ok=True)
        makedirs("/".join(midname.split("/")[:-1]), exist_ok=True)

        # save file in chunks to save memory
        fi.seek(0)
        CHUNK_SIZE = 430        # bytes
        with open(fname, 'wb+') as destination:
            chunk = fi.read(CHUNK_SIZE)
            while chunk:  # loop until the chunk is empty (the file is exhausted)
                destination.write(chunk)
                chunk = fi.read(CHUNK_SIZE)  # read the next chunk

        # do we need to adjust size parameters in exif tags?

        # save thumbnail
        fi.seek(0)
        ThumbFromBuffer(fi, thumbname)

        # save mid size image
        fi.seek(0)
        ThumbFromBuffer(fi, midname, MIDHEIGHT)

        # We will not set the rotation in the db with get_rotation() at this point.
        # It will be set upon first photo access.

        return newphoto

    def get_photos_for_album(self, album):
        """
        :param album: album model object, can feed straight from return_album()
        :return: queryset of photos
        Need to add unit test
        """
        if not self.has_permission_to_view(album):
            raise PermissionException

        try:
            photos = Photo.objects.filter(album=album)
            return photos
        except:
            raise

    def return_photo(self, photoid):
        """
        make unit test
        :param photoid: the id of the photo in the photos table
        :return: a single photo
        """
        try:
            photo = Photo.objects.get(id=photoid)
            return photo
        except:
            raise

    def update_photo_description(self, photo, desc):
        # check permissions - must be either photo uploader or album owner to change description
        if (self.uprofile != photo.uploader and self.uprofile != photo.album.owner) or self.uprofile is None:
            raise PermissionException

        photo.description = desc
        photo.save()

    def delete_album(self, album):
        if self.uprofile == album.owner:

            # delete album from db (cascades to photos, contributor manytomany table, group manytomany table, etc)
            status = album.delete()
            #print(status[0])
            #print(status[1])

            # this must be greater than or equal to 1 because we are deleting files as well as album
            if status[0] >= 1:
                return True
            elif status[0] == 0:
                return False
        else:
            raise PermissionException("Must be album owner to delete album")
        print("End - we should never reach this")

    def delete_photo(self, photo):
        """
        Delete a photo, checking permission
        :param photo: photo to delete
        :return: true if success, false if failure, raise on access violation
        """

        # check permission
        if self.uprofile == photo.album.owner or self.uprofile == photo.uploader:

            # remove from db
            status = photo.delete()
            if status[0] == 1:
                return True
            elif status[0] == 0:
                return False

        else:
            raise PermissionException

    def set_accesstype(self, album, type):
        """
        Set access type for an album, only owner can do this
        :param album: album to set
        :return: boolean of success or failure
        """
        if self.uprofile == album.owner and ALBUM_PUBLIC <= type <= ALBUM_PRIVATE and isinstance(type, int):
            album.accesstype = type
            album.save()
            return True
        else:
            return False

    def add_contributor_to_album(self, album, contributor):
        """
        Add a contributor to album
        :param album: album to add contributor to
        :param contributor: Profile of user to add as contributor
        :return: False if not friends, True on success
        """
        # check if users are friends?
        if not are_friends(album.owner, contributor):
            return False
        # todo: what happens if we add a contributor twice?
        album.contributors.add(contributor)
        return True

    def add_group_to_album(self, album, group):
        """
        Add a friendgroup access to an album
        Prevent adding group to album that is not own or contributor
        :param album:
        :param group:
        :return: boolean indicating success of failure
        """
        # if we don't own the group, no bueno
        if group.owner != self.uprofile:
            return False
        # if we aren't owner or contributor to the album, dame dame desu
        if album.owner != self.uprofile and self.uprofile not in album.contributors.all():
            return False

        album.groups.add(group)
        return True

    def remove_group_from_album(self, album, group):
        pass

    def remove_contributor_from_album(self, album, contributor):
        pass

    def return_groups(self, album):
        """
        Return all groups for an album
        :param album:
        :return: queryset of groups
        """
        # todo: unit test
        return album.groups.all()


def collate_owner_and_contrib(album):
    """
    Combine owner and contributors into list
    :param album: album to collate
    :return: list of owner and contributors
    """
    lst = list(album.contributors.all())
    lst.append(album.owner)
    return lst


def ThumbFromBuffer(buf, filename, baseheight=THUMBHEIGHT):
    """
    Take an image buffer, scale, and return a thumbnail
    :param buf: raw image data buffer
    :param filename: file name to save as
    :return: PIL Image thumbnail
    """
    img = Image.open(BytesIO(buf.read()))

    # if the image is smaller than our target height, don't resize it
    # this will leave us double saving sometimes, but right now, we need to do that for png uniformity
    # todo; resolve this redundancy
    if img.size[1] <= baseheight:
        newimg = img.convert('RGB')
        newimg.save(filename, 'jpeg')
        return newimg

    hpercent = (baseheight / float(img.size[1]))
    wsize = int((float(img.size[0]) * float(hpercent)))         # we can change 0 to 1 for a square

    # will this return approach leak memory?
    newimg = img.resize((wsize, baseheight), Image.ANTIALIAS).convert('RGB')

    newimg.save(filename, 'jpeg')

    return newimg
