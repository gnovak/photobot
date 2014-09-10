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
import os.path

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


# Grar, this is already a PITA with 20k photos.  
class CachingFetcher(object):
    def __init__(self, api_key='82f7fe9f1801d2bc36a4351d938f4327',
                 filename_base='flickr'):        

        self._flickr = flickrapi.FlickrAPI(api_key)
        
        # photo info 
        self.photo_info = PersistentCache(self.slow_getInfo, 
                filename = filename_base + '-info.pkl')

        # photo favorites
        self.photo_favorites = PersistentCache(self.slow_getFavorites, 
                filename = filename_base + '-favorites.pkl')

                
    ##############################
    # Stuff that queries the flickr api
    def slow_getInfo(self, pid):
        return self._flickr.photos_getInfo(photo_id=pid)

    def slow_getFavorites(self, pid):
        return self._flickr.photos_getFavorites(photo_id=pid)

    ##############################
    # Stuff that just extracts scalars from the info given by flickr
    def views(self, pid):
        info = self.photo_info(pid)
        return int(info[0].attrib['views']) if info is not None else -1

    def has_people(self, pid):
        info = self.photo_info(pid)
        result = None
        if info is not None: 
            for el in info[0]:
                if el.tag == 'people':
                    result = bool(int(el.attrib['haspeople']))
        # if info's not there, return None
        return result
            
    def comments(self, pid):
        info = self.photo_info(pid)
        result = -1
        if info is not None:
            for el in info[0]:
                if el.tag == 'comments':
                    result = int(el.text)
        # if info's not there, return None
        return result

    def favorites(self, pid):
        info = self.photo_favorites(pid)
        result = -1
        if info is not None:
            result = int(info[0].attrib['total'])
        return result

    def date_uploaded(self, pid):
        info = self.photo_info(pid)
        result = 0
        if info is not None:
            result = int(info[0].attrib['dateuploaded'])
        return result

    def download_original_url(self, pid):
        template = 'https://farm%s.staticflickr.com/%s/%s_%s_o.%s'
        info = self.photo_info(pid)
        if info is not None:
            result = template % (info[0].attrib['farm'], info[0].attrib['server'], 
                                 info[0].attrib['id'], 
                                 info[0].attrib['originalsecret'],
                                 info[0].attrib['originalformat'])
        return result

    def download_generic_url(self, pid):
        template = 'https://farm%s.staticflickr.com/%s/%s_%s.jpg'
        info = self.photo_info(pid)
        if info is not None:
            result = template % (info[0].attrib['farm'], info[0].attrib['server'], 
                                 info[0].attrib['id'], info[0].attrib['secret'])
        return result

    # s     small square 75x75
    # q     large square 150x150
    # t     thumbnail, 100 on longest side
    # m     small, 240 on longest side
    # n     small, 320 on longest side
    # -     medium, 500 on longest side
    # z     medium 640, 640 on longest side
    # c     medium 800, 800 on longest side
    # b     large, 1024 on longest side*
    # o     original image, either a jpg, gif or png, depending on source format
    # 
    def download_url(self, pid, size_code='q'):
        template = 'https://farm%s.staticflickr.com/%s/%s_%s_%s.jpg'
        info = self.photo_info(pid)
        result = ''
        if info is not None:
            result = template % (info[0].attrib['farm'], info[0].attrib['server'], 
                                 info[0].attrib['id'], info[0].attrib['secret'], 
                                 size_code)
        return result

    def filename(self, pid, prefix='', size_code='q'):
        url = self.download_url(pid)
        fn = url.split('/')[-1]
        return os.path.join(prefix, fn)
            


