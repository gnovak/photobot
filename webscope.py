# code to read and parse photo metadata from Yahoo Webscope dataset
# http://webscope.sandbox.yahoo.com/catalog.php?datatype=i&did=67

# convert datetime to time since epoch
# (datetime.datetime(2012,04,01,0,0) - datetime.datetime(1970,1,1)).total_seconds()

import csv

import flickr

##############################
# Give names to fields
#
# The webscope data file is an ordered list of tab-separated
# fields.  These are the names.
field_names = ['photo-id', 'user-id', 'user-name',
               'date-taken', 'date-uploaded',
               'camera', 'title', 'description',
               'user-tags', 'machine-tags',
               'longitude', 'latitude', 'accuracy',
               'url', 'download-url',
               'license-name', 'license-url',
               'server', 'farm',
               'secret', 'secret-original',
               'extension-original','video',]

##############################
# Type converters for individual fields
def to_tag_list(ss):
    """Convert from string to list of strings representing tags"""
    return ss.split(',') if ss != '' else []

def to_lat_lon(ss):
    """Convert from string to float"""
    try: 
        result = float(ss)
    except ValueError:
        result = None

def to_bool(ss):
    """Convert from string to boolean (0=False, 1=True)"""
    if ss == '1':
        return True
    elif ss == '0':
        return False
    raise ValueError

def to_accuracy(ss):
    """Convert from string to location accuracy parameter"""
    try:
        result = int(ss)
    except ValueError:
        result = None
    return result

##############################
# Dealing with whole lines
def to_python(line):
    """Convert from a line of the webscope tsv to a python object"""
    entry = dict([(kk, vv) for kk,vv in zip(field_names, line)])
    for name, type_ in field_types:
        entry[name] = type_(entry[name])
    return entry

##############################
# Dealing with the whole file
def read_all(fn):
    result = []
    with open(fn) as tsv:
        for line in csv.reader(tsv, delimiter="\t"): 
            result.append(to_python(line))
    return result

def read_and_fetch_photo_info(fn):
    ff = flickr.CachingFetcher()
    with open(fn) as tsv:
        for line in csv.reader(tsv, delimiter="\t"): 
            obj = to_python(line)
            # fetch photo metadata, relying on caching to record it.
            ff.photo_info(obj['photo-id'])
    ff._info_flush_cache()

# Do some type conversions.  This has to go at the end so the
# functions referenced below are defined.
#
# Might think that we want to convert date-taken and date-uploaded
# into some common format.  However, date-uploaded is GMT and
# date-taken is (usually) in the user's local timezone, which can
# be useful information.  However we don't know the user's time
# zone, and even if we did, converting to GMT would mean having to
# keep track of the time zone to find out what time of day the
# photo was taken.  So just don't fuck with the times, store them
# as-is.  (except for converting date-uploaded to an integer)

# list of tuples: field-name, type-converter-function
field_types = [('date-uploaded', int),
               ('user-tags', to_tag_list),
               ('machine-tags', to_tag_list),
               ('latitude', to_lat_lon),
               ('longitude', to_lat_lon),
               ('accuracy', to_accuracy),
               ('video', to_bool)]

def download_size_url(url, size_code):    
    extension = '.jpg'
    index = url.find(extension)
    return url[:index] + '_' + size_code + extension
