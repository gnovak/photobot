# Fit SVCs to the images
import numpy as np

import validation

def regularization(vv,yy,models):
    result = []
    means, errs = [], []
    for model in models:
        mean, err = validation.kfoldcv(vv,yy,model, 5)
        means.append(mean)
        errs.append(err)
    return np.array(means), np.array(errs)

