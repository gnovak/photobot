# sandbox

import gsn_util as util


def count_all_tags(fns):
    result = {}
    for fn in fns:
        input = util.uncan(fn)
        count_tags(input, result)
    return result

def count_tags(input, partial=None):
    result = partial if partial is not None else {}

    for el in input:
        for tag in el['user-tags']:
            if tag in result:
                result[tag] += 1
            else:
                result[tag] = 1
    return result
            
def fetch_all_beach_ids():
    fns = ['beaches-%d.pkl'%ii for ii in range(7)]    
    result = []
    for fn in fns:
        dat = util.uncan(fn)
        partial = fetch_beach_ids(dat)
        result += partial
    util.can(result, 'webscope-beach-tagged-set.pkl')
    ids = [el['photo-id'] for el in result]
    util.can(ids, 'webscope-beach-tagged-ids.pkl')

def fetch_beach_ids(dat):
    result = []
    for el in dat:
        tags = el['user-tags']
        if (('beach' in tags and
             ('ocean' in tags or 'sea' in tags) and 
             'people' not in tags and
             'family' not in tags) and 
            not el['video']):
            result.append(el)
    return result

def fetch_all_mountain_ids():
    fns = ['landscapes-%d.pkl'%ii for ii in range(3)]    
    result = []
    for fn in fns:
        dat = util.uncan(fn)
        partial = fetch_mountain_ids(dat)
        result += partial
    util.can(result, 'webscope-mountain-tagged-set.pkl')
    ids = [el['photo-id'] for el in result]
    util.can(ids, 'webscope-mountain-tagged-ids.pkl')

def fetch_mountain_ids(dat):
    result = []
    for el in dat:
        tags = el['user-tags']
        if (('mountain' in tags or
             'mountains' in tags) and 
            not el['video']):
            result.append(el)
    return result
