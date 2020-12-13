from bottle import get, post, request, run
import json
import pymongo
from bson import json_util
import urllib

connection = pymongo.MongoClient('localhost',27017)
db = connection['market']
collection = db['stocks']

def create_document(doc):
    try:
        result=collection.insert_one(doc)
    except pymongo.errors.PyMongoError as e:
        print(e)
    if result:
        return True
    return False

def read_document(query):
    try:
        result_list = []
        result=collection.find(query)
        return json_util.dumps(result)

    except pymongo.errors.PyMongoError as e:
        return str(e)

def update_document(filter,update,upsert=False):
    try:
        result=collection.update_one(filter,update,upsert=upsert)
        return json_util.dumps(result.raw_result)
    except pymongo.errors.PyMongoError as e:
        return str(e)

def delete_document(filter):
    try:
        result=collection.delete_one(filter)
        return json_util.dumps(result.raw_result)
    except pymongo.errors.PyMongoError as e:
        return str(e)

def get_fang():
    query = {'$or':[{'Ticker':'FB'},{'Ticker':'AMZN'},\
                   {'Ticker':'NFLX'},{'Ticker':'GOOG'}]}
    projection = {'Ticker':1,'Price':1,'_id':0}
    result = collection.find(query,projection)
    return json_util.dumps(result)
  
def get_health():
    query = {'$or':[{'Ticker':'CELG'},{'Ticker':'TEVA'},\
                   {'Ticker':'ALXN'},{'Ticker':'ALGN'},{'Ticker':'ANTM'}]}
    projection = {'Ticker':1,'Price':1,'_id':0}
    result = collection.find(query,projection)
    return json_util.dumps(result)
  
@post('/strings')
def hello_post():
    client_data = request.json
    return json.dumps(client_data) + '\n'
  
@post('/create')
def create():
    status = create_document(request.json)
    return 'Document created (T/F) ' + str(status) + '\n'

@post('/read')
def read():
    return read_document(request.json) + '\n'

@post('/update')
def update():
    query_dict = request.json[0]
    set_dict = request.json[1]
    result = update_document(query_dict,set_dict)
    return result + '\n'
  
@post('/delete')
def delete():
    return delete_document(request.json) + '\n'

@get('/fang')
def fang():
    return get_fang() + '\n'

@get('/top-five-health')
def fang():
    return get_health() + '\n'

  
if __name__=='__main__':
    run(host='localhost',port=8080)
  