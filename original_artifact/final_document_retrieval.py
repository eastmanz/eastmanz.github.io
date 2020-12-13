#Document Retrieval
#Final
#Zachariah Eastman

import pymongo
connection = pymongo.MongoClient('localhost',27017)
db = connection['market']
collection = db['stocks']

def count_between_moving_averages(low,high):
    return collection.find({'50-Day Simple Moving Average':{'$gt':low,'$lt':high}}).count()

  
def get_industry_tickers(industry):
    return collection.find({'Industry':industry},{'Ticker':1,'_id':0})
    

def find_sector_grouped_by_industry(sector):
    pipeline = [{'$match':{'Sector':sector}},{'$group':{'_id':'Industry','stocks': {'$sum':'$Shares Outstanding'}}}]
    return collection.aggregate(pipeline)
    
if __name__ == '__main__':
    print('Count between -0.1 and 0.1: ' + str(count_between_moving_averages(-0.1,0.1)))
    
    ticker_string = ''
    for ticker in get_industry_tickers('Medical Laboratories & Research'):
        ticker_string = ticker_string + str(ticker) + ' '
    print(ticker_string)

    document_string = ''
    for document in find_sector_grouped_by_industry('Healthcare'):
        document_string = document_string + str(document) + ' '
    print(document_string)