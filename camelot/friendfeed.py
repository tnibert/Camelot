#! /usr/bin/env python
from collections import OrderedDict


def generate_feed(profilecontrol):
    """
    Generate a feed of the number of photos uploaded by a particular uploader to a particular album on
    a given day
    :param profilecontrol: a profilecontroller object
    :return: a list of tuples in order of date, uploader, album, and the count of photos
    """
    feedphotos = profilecontrol.get_feed()
    grouped = OrderedDict()

    for p in feedphotos:
        uploadeddate = p.pub_date.date()
        if uploadeddate not in grouped.keys():
            grouped[uploadeddate] = {p.uploader: {p.album: 1}}
        else:
            if p.uploader not in grouped[uploadeddate].keys():
                grouped[uploadeddate][p.uploader] = {p.album: 1}
            else:
                if p.album not in grouped[uploadeddate][p.uploader].keys():
                    grouped[uploadeddate][p.uploader][p.album] = 1
                else:
                    grouped[uploadeddate][p.uploader][p.album] += 1

    feedentries = []
    for date, up in grouped.items():
        for uploader, alb in up.items():
            for album, count in alb.items():
                feedentries.append((date, uploader, album, count))

    return feedentries
