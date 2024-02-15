import json

def display_formatted_response(res):
    clean_res = clean_output(json.loads(repr(res.data)))
    return clean_res


def clean_output(res):
    '''
    Recursively removes all None values from the input json
    '''
    if isinstance(res, list):
        return [clean_output(x) for x in res if x is not None]
    elif isinstance(res, dict):
        return {
            key: clean_output(val)
            for key, val in res.items()
            if val is not None and val != []
        }
    else:
        return res