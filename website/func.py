from . import ALLOWED_EXTENSIONS
import json

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def change(filename):
    return filename.rsplit('.', 1)[0] + '.json'


def write_json(FILTER_PATH, filename, cookie):
    #Store filter configuration
    filename = change(filename)
    with open(FILTER_PATH + filename, 'w') as file:
        json.dump(cookie, file)
        
        
def read_json(FILTER_PATH, filename):
    filename = change(filename)
    with open(FILTER_PATH + filename, 'r') as file:
        data = json.load(file)
    return data