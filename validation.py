# cross validation, etc.  

# I want this to be completely deterministic, ie, pick the same
# subsets of vectors for k-fold cross-validation.  Might be able to do
# this just by setting the seed before every call to cross-validate.
# Otherwise I'll pick my own subsets and write them out one time.

import numpy as np

def leave_one_out(vv, ii):
    return np.concatenate((vv[:ii],vv[ii+1:]))

def fold(aa,kk,ii):
    assert 0 <= ii and ii < kk
    nn = len(aa)
    fold_size = int(nn/(1.0*kk) + 0.5)
    partition = fold_size*np.arange(kk+1)
    partition[0] = 0
    partition[-1] = nn

    validation = aa[partition[ii]:partition[ii+1]]
    if ii==0:
        train = aa[partition[1]:]
    elif ii==kk-1:
        train = aa[:partition[-2]]
    else:
        lower = aa[partition[0]:partition[ii]]
        upper = aa[partition[ii+1]:partition[-1]]
        train = np.concatenate((lower, upper))
    return train, validation

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

def kfoldcv(vv, yy, model, kk=10):
    result = []

    for ii in range(kk):
        sub_vv, cv_vv = fold(vv, kk, ii)
        sub_yy, cv_yy = fold(yy, kk, ii)
        
        model.fit(sub_vv, sub_yy)

        # Beware rounding in classification vs. regression
        correct = sum(model.predict(cv_vv) == cv_yy)
        tot = 1.0*len(cv_yy)
        result.append(correct/tot)

    return np.mean(result), np.std(result)
