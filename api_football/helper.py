# adapted from https://stackoverflow.com/a/52081812
import math

def flatten(d):
    out = {}
    if isinstance(d, list):
        num_size = math.ceil(math.log10(len(d)))
        num_format = "{{:0{num_size}d}}".format(num_size=num_size)
        d = {num_format.format(n):val for n, val in enumerate(d)}
    for key, val in d.items():
        if isinstance(val, dict):
            val = [val]
        if isinstance(val, list):
            for subdict in val:
                deeper = flatten(subdict).items()
                out.update({'{}_{}'.format(key, key2): val2 for key2, val2 in deeper})
        else:
            out[key] = val
    return out