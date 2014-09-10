# The heavy lifting is going to be defining the feature space.  These
# could be be objects that encode an image on demand (if I want to
# delay encoding) or just functions (if it's ok to just encode all the
# images in a dataset at once.

import os.path
import datetime

import numpy as np
import gsn_util as util

import flickr
import skimage as ski
import skimage.io

def beach_ds(fkr):
    # as a sample of what to do...
    ids = util.uncan('beach-ids.pkl')
    ids = ids[0:10]
    inc_ids, ims, yy = raw_ds(fkr, ids, prefix='square')
    yy = encode_ys(yy)
    xx = ims_to_bw_vecs(ims, factor=256)
    # desc = 'description'
    # fn = 'blah'
    return inc_ids, xx, yy # , desc, fn
    
def make_ds(fkr, ids, xx_func, prefix='square-mountain', downsample=1):
    inc_ids, ims, views, times = raw_ds(fkr, ids, prefix=prefix)
    xx = xx_func(ims, downsample)
    yy = encode_ys(views, times)
    return inc_ids, xx, yy

def raw_ds(fkr, ids, prefix, size_code='q'):
    """Load a dataset with minimal processing"""
    # want this to be one loop so I coherently decide whether to
    # include/exclude things
    all_views = []
    image_filenames = []
    included_ids = []
    upload_times = []

    for ii in ids:
        views = fkr.views(ii) 
        fn = fkr.filename(ii, prefix, size_code)
        time = fkr.date_uploaded(ii)

        # include/exclude decision here:
        if views >= 0 and os.path.isfile(fn):
            included_ids.append(ii)
            image_filenames.append(fn)
            all_views.append(views)            
            upload_times.append(time)

    ims = ski.io.ImageCollection(image_filenames)
    return included_ids, ims, all_views, upload_times

def encode_ys(views, times):
    """Map views to log10(views+1) to deal with zero views"""
    views, times = np.asarray(views), np.asarray(times)
    
    # Date on yahoo files is Aug 25, 2014, so all upload dates
    # (should) be before then.  I'm getting view information as of
    # ~Sept 10, 2014, so to avoid negative numbers (the future!)
    # consider the present time to be Sept 10, 2014

    #today = datetime.datetime(2014,8,25)
    sec_per_year = 3.15e7
    today = datetime.datetime(2014,9,10)
    epoch = datetime.datetime(1970,1,1)    
    sec_since_epoch = (today - epoch).total_seconds()
    years = (sec_since_epoch - times)/sec_per_year

    # use views + 2 so that there are no neg numbers b/c I'm
    # going to take a log.
    rate = (views + 2) / years
    return np.log10(rate)

def classify_by_median(yy):
    """Map views to log10(views+1) to deal with zero views"""
    return (yy > np.median(yy)).astype('d')

def log_power_spect(im, kbins=30):
    grey = ski.color.rgb2grey(im)
    kx = np.fft.fftfreq(im.shape[0])  # Check this!
    ky = np.fft.fftfreq(im.shape[1])  # Check this!
    KX, KY = nu.make_grid(kx, ky)
    kmag = np.sqrt(KX**2 + KY**2)
    spectrum = abs(np.fft.fft2(grey))
    
    # Now make the 1d spectrum
    kb = np.linspace(0, kmag.max(), kbins)
    kidx = kb.searchsorted(kmag)
    mean = []
    sig = []
    for ii in range(1,len(kb)):
        # zeros are underflows
        amplitudes = spectrum[kidx==ii]
        # Do mean and sig in log space
        mean.append(np.log10(amplitudes).mean())
        sig.append(np.log10(amplitudes).std())
    return nu.ave(kb), np.array(mean), np.array(sig)

def ims_to_bw_vecs(ims, downsample=1):
    # go to greyscale + make vector in dumbest way possible
    # downsample...
    return np.array([ski.color.rgb2grey(im).reshape(-1)[::downsample] for im in ims])

def ims_to_color_vecs(ims, downsample=1):
    # include color, make vector in dumbest way possible
    # but want to make sure keep color data from the same pixels
    # downsample...
    # doing this in rgb, normalize, make floating point
    return np.array([np.concatenate(((1/256.0)*im[:,:,0].reshape(-1)[::downsample],
                                     (1/256.0)*im[:,:,1].reshape(-1)[::downsample],
                                     (1/256.0)*im[:,:,2].reshape(-1)[::downsample]))
                     for im in ims])
