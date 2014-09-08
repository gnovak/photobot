# cross validation, etc.  

# I want this to be completely deterministic, ie, pick the same
# subsets of vectors for k-fold cross-validation.  Might be able to do
# this just by setting the seed before every call to cross-validate.
# Otherwise I'll pick my own subsets and write them out one time.

def leave_one_out(vv, ii):
    return np.concatenate((vv[:ii],vv[ii+1:]))

def ims_to_ds(good, bad, factor=1):
    vv = ([el for el in ims_to_vecs(good, factor=factor)] + 
          [el for el in ims_to_vecs(bad, factor=factor)])
    yy = [1]*len(good) + [0]*len(bad)
    return np.array(vv),np.array(yy)

def loocv(vv, yy, model):
    result = []

    for ii in range(len(vv)):
        sub_vv = leave_one_out(vv, ii)
        sub_yy = leave_one_out(yy, ii)
        model.fit(sub_vv, sub_yy)
        result.append(model.predict(vv[ii])[0] == yy[ii])
    return np.array(result)
