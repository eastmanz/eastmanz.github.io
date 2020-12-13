#Zachariah Eastman
#Final - Document Manipulation

import datetime
import pymongo
from bson import json_util

connection = pymongo.MongoClient('localhost',27017)
db = connection['market']
collection = db['stocks']

def insert_document(test_stock):
    try:
        print('Executing collection.insert_one(stock)')
        result=collection.insert_one(test_stock)
    except pymongo.errors.PyMongoError as e:
        print(e)
    if result:
        return True
    return False

def read_document(query):
    try:
        result_list = []
        print('Executing collection.find(query)')
        result=collection.find(query)
        return json_util.dumps(result)

    except pymongo.errors.PyMongoError as e:
        return e

def update_document(filter,update,upsert=False):
    try:
        print('Executing collection.update_one(filter, update, upsert=False')
        result=collection.update_one(filter,update,upsert=upsert)
        return json_util.dumps(result.raw_result)
    except pymongo.errors.PyMongoError as e:
        return(e)

def delete_document(filter):
    try:
        print('Executing collection.delete_one(filter)')
        result=collection.delete_one(filter)
        return json_util.dumps(result.raw_result)
    except pymongo.errors.PyMongoError as e:
        return(e)
    
      
if __name__ == '__main__':
  
    test_stock = {}
    test_stock['Ticker'] = 'TEST'
    test_stock['Volume'] = 12345
    test_stock['Industry'] = 'Nothing' 
    insert_result = insert_document(test_stock)
    print('Insert result: ' + str(insert_result) + '\n\n')
    
    read_result = read_document({'Ticker': 'TEST'})
    print('Read result: ' + str(read_result) + '\n\n')
    
    update_result = update_document({'Ticker':'TEST'},\
                                    {'$set': {'Volume':99999}})
    print('Updated result: ' + str(update_result) + '\n\n')
    
    delete_result = delete_document({'Ticker':'TEST'})
    print('Delete result: ' + str(delete_result) + '\n\n')
    
    
    
    