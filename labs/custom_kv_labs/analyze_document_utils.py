from urllib.parse import urlparse
import pandas as pd

def is_url(url):
    '''
    Returns True is the input is a Valid URL, otherwise False
    '''
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
    
def create_processor_job_callback(times_called, response):
    print("Waiting for processor lifecycle state to go into succeeded state:", response.data)

def takeSecond(elem):
    return elem[2]
    
def display_classes(clean_res):
    '''
    Returns the DataFrame containing Class labels with their Confidence Levels
    '''
    pages = clean_res['pages']
    data=[]
    for page in pages:
        Document_field = page['documentFields']
        for documentfield in Document_field:
            fieldname = documentfield['fieldLabel']['name']
            fieldconfidence = documentfield['fieldLabel']['confidence']
            fieldvalue = documentfield['fieldValue']['value']
            data.append([fieldname, fieldvalue, fieldconfidence])
    list = ["Key", "Value", "Confidence"]
    data.sort(key=takeSecond)
    df= pd.DataFrame((data), columns=list)
    display(df)

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
