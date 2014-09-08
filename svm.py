# Fit SVCs to the images

def regularization(vv,yy,models):
    result = []
    for model in models:
        values = loocv(vv,yy,model)
        result.append(values.sum()/(1.0*len(values)))
        #result.append(values.sum())
    return result

