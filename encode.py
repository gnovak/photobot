# The heavy lifting is going to be defining the feature space.  These
# could be be objects that encode an image on demand (if I want to
# delay encoding) or just functions (if it's ok to just encode all the
# images in a dataset at once.

def read_ds():
    good = ski.io.ImageCollection('good-sq/*.jpg')
    bad = ski.io.ImageCollection('bad-sq/*.jpg')
    return good, bad

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


# def ims_to_vecs(ims, factor=1):
#     # go to greyscale + make vector in dumbest way possible
#     # downsample...
#     return np.array([ski.color.rgb2grey(im).reshape(-1)[::factor] for im in ims])

def ims_to_vecs(ims, factor=1):
    # include color, make vector in dumbest way possible
    # but want to make sure keep color data from the same pixels
    # downsample...
    # doing this in rgb, normalize, make floating point
    return np.array([np.concatenate(((1/256.0)*im[:,:,0].reshape(-1)[::factor],
                                     (1/256.0)*im[:,:,1].reshape(-1)[::factor],
                                     (1/256.0)*im[:,:,2].reshape(-1)[::factor]))
                     for im in ims])
