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
            
