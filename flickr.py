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

class CachingFetcher(object):
    def __init__(self, api_key='82f7fe9f1801d2bc36a4351d938f4327',
                 fn='flickr'):        
        self._flickr = flickrapi.FlickrAPI(api_key)

        # this could probably be nicely done with decorators
        self._info_fn = fn + '-info.pkl'
        self._info_cache_count = 0
        self._info_cache_limit = 1800 # about half an hour
        try:
            with open(self._info_fn) as ff:
                self._info_cache = cPickle.load(ff)
        except IOError:            
            self._info_cache = {}
            # ensure the file exists so that when it comes time to
            # backup, the file is there.
            with open(self._info_fn, 'wb') as ff:
                cPickle.dump(self._info_cache, ff, protocol=2)
            
            
    def _info_flush_cache(self):
        self._info_cache_count = 0
        shutil.copy(self._info_fn, self._info_fn + '.bak')
        with open(self._info_fn, 'wb') as ff:
            cPickle.dump(self._info_cache, ff, protocol=2)
            
    def photo_info(self, pid):
        if pid in self._info_cache:
            return self._info_cache[pid]

        try:
            result = self._flickr.photos_getInfo(photo_id=pid)
        except flickrapi.FlickrError:
            result = None

        self._info_cache[pid] = result
        self._info_cache_count += 1

        if self._info_cache_count > self._info_cache_limit:
            self._info_flush_cache()

        return result
