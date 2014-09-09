# code to fetch metadata from Flickr api

##############################
# API NOTES
##############################

### Sample code: 
# flickr = flickrapi.FlickrAPI(api_key)
# photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
# sets = flickr.photosets_getList(user_id='73509078@N00')

### important info: 
# https://www.flickr.com/services/api/misc.dates.html
# https://www.flickr.com/services/api/misc.urls.html

### really interesting API calls:
# https://www.flickr.com/services/api/flickr.photos.search.html
# https://www.flickr.com/services/api/flickr.photos.getInfo.html

### pretty interesting
# # get list of people in a photo
# https://www.flickr.com/services/api/flickr.photos.people.getList.html
# https://www.flickr.com/services/api/flickr.photos.getSizes.html
# https://www.flickr.com/services/api/flickr.stats.getPopularPhotos.html
# # get photo favorites etc for given dates
# https://www.flickr.com/services/api/flickr.stats.getPhotoStats.html

### eventually...
# https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
# https://www.flickr.com/services/api/flickr.cameras.getBrandModels.html
# https://www.flickr.com/services/api/flickr.cameras.getBrands.html
# https://www.flickr.com/services/api/flickr.photos.getExif.html
# https://www.flickr.com/services/api/flickr.photos.getFavorites.html (list of people who have favorited the file)
# https://www.flickr.com/services/api/flickr.photos.comments.getList.html
# # eventually (machine tags):
# https://www.flickr.com/services/api/flickr.machinetags.getNamespaces.html
# https://www.flickr.com/services/api/flickr.machinetags.getPairs.html
# https://www.flickr.com/services/api/flickr.machinetags.getPredicates.html
# https://www.flickr.com/services/api/flickr.machinetags.getValues.html
# # eventually (geo) 
# https://www.flickr.com/services/api/flickr.photos.geo.getLocation.html
# https://www.flickr.com/services/api/flickr.photos.geo.photosForLocation.html
# # eventually (places, named places, not by lat lon)
# https://www.flickr.com/services/api/flickr.places.findByLatLon.html
# https://www.flickr.com/services/api/flickr.places.find.html

### probably not interesting... but maybe
# # interesting photos for specific day
# https://www.flickr.com/services/api/flickr.interestingness.getList.html

### Sample code: 
# flickr = flickrapi.FlickrAPI(api_key)
# photos = flickr.photos_search(user_id='73509078@N00', per_page='10')
# sets = flickr.photosets_getList(user_id='73509078@N00')

import os.path
import cPickle
import shutil

import flickrapi

def flickr_obj(api_key='82f7fe9f1801d2bc36a4351d938f4327'):
    return flickrapi.FlickrAPI(api_key)

class PersistentCache(object):
    def __init__(self, function, filename, backup_ext='bak',
                 flush_every=1000):

        self._function = function
        self._flush_every = flush_every
        self._filename = filename
        self._backup_filename = filename + '.' + backup_ext

        self._count = 0

        # Try to read the cache, create if doesn't exist
        try:
            with open(self._filename) as ff:
                self._cache = cPickle.load(ff)
        except IOError:
            self._cache = {}
            # ensure the file exists so that when it comes time to
            # backup, the file is there.
            with open(self._filename, 'wb') as ff:
                cPickle.dump(self._cache, ff, protocol=2)

    def __call__(self, key):
        # ok, I could do something clever with arg parsing to make
        # this general, but I'm just using this to store flickr info
        # based on photo-id.  So make it simple.

        if key in self._cache:
            return self._cache[key]

        # Do I want to catch exceptions here or elsewhere?  Want this
        # to be pretty transparent... so further specialize to the
        # flicker case here:
        try:
            result = self._function(key)
        except flickrapi.FlickrError:
            result = None

        self._cache[key] = result
        self._count += 1

        if self._count > self._flush_every:
            self.flush()

        return result
    
    def flush(self):
        self._count = 0
        shutil.copy(self._filename, self._backup_filename)
        with open(self._filename, 'wb') as ff:
            cPickle.dump(self._cache, ff, protocol=2)


class CachingFetcher(object):
    def __init__(self, api_key='82f7fe9f1801d2bc36a4351d938f4327',
                 filename_base='flickr'):        

        self._flickr = flickrapi.FlickrAPI(api_key)
        info_fn = filename_base + '-info.pkl'
        self.photo_info = PersistentCache(self.slow_getInfo, 
                filename = filename_base + '-info.pkl')
                
    def slow_getInfo(self, pid):
        return self._flickr.photos_getInfo(photo_id=pid)

