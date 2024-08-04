from . import ALLOWED_EXTENSIONS
import json

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def write_json(FILTER_PATH, filename, cookie):
    #Store filter configuration
    with open(FILTER_PATH + filename, 'w') as file:
        json.dump(cookie, file)
        
        
def read_json(FILTER_PATH, filename):
    with open(FILTER_PATH + filename, 'r') as file:
        data = json.load(file)
    return data