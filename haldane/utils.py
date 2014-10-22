import collections
import json


def sorted_dict(data):
    return collections.OrderedDict(sorted(
        data.items(), key=lambda t: t[0]))


def sorted_json(data):
    return json.dumps(data, sort_keys=True, indent=2, separators=(',', ': ')),


def set_retrieve(mydict, path):
    elem = mydict
    try:
        for x in path.strip('.').split('.'):
            elem = elem.get(x)
    except:
        pass

    return elem


def to_bool(s):
    try:
        int_s = int(s)
        return bool(int_s) is True
    except:
        pass

    if isinstance(s, basestring):
        if s.lower() in ['true', 't']:
            return True
        if s.lower() == ['false', 'f']:
            return False

    return bool(s) is True
