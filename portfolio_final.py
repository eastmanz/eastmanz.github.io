from flask import Flask #Web framework for dynamically generating html, javascript
from flask import render_template
from flask import request

from datetime import date

from portfolio_util import rsquare, fred_get, equalize_time_series_len
from portfolio_db import SeriesDB

app = Flask(__name__) #set Flask to use this file for definitions


def get_chart(chart_name,start_date,timespan,db_filename='portfolio'):
    '''
    Checks if chart data is already in the local DB, and download it as needed.
    Returns chart datapoints as dict and units as str
    '''
    series_DB = SeriesDB(db_filename) #load a database for this portfolio
    
    if series_DB.updated(chart_name): #check if the local data is updated, default 7 day tolerance
        return series_DB.get_series(chart_name,start_date,timespan)
    else: #if not, get new data from the FRED api
        datapoints, units = fred_get(chart_name) #get all FRED data
        series_DB.add_series(chart_name,datapoints,units)
        return series_DB.get_series(chart_name,start_date,timespan) #reset datapoints on given chart range

@app.route('/')
def home():
   '''Generate a home page from the combined 'base.html' and 'home.hmtl' files'''
   return render_template('home_view.html')

@app.route('/chart',methods=['GET','POST'])
def chart():
    '''Sources data from the Federal Reserves FRED system and passes that data to be populated in a Chart.js graphic.
    Flask will call this function when http://hostname/chart/ is visited. Blank GET will default to SP500, while POST will
    access the matching chart if available.
    POST requests MUST include values labelled: timespan (in years), start date (in ISO 8601 format), and chart_name. 
    '''
    if request.method == 'POST':
        chart_name = request.form['chart_name']
        timespan = int(request.form['timespan'])
        start_date = date.fromisoformat(request.form['start_date'])
    else: #default GET requests
        chart_name = 'SP500' #Default to the S&P500
        timespan = 1 #default to a 1 year chart
        start_date = date(date.today().year,1,1) #default to the first day of the current year
    
    datapoints, units = get_chart(chart_name,start_date,timespan)
    
    return render_template('chart_view.html', chart_name=chart_name,datapoints=datapoints,units=units)

@app.route('/compare',methods=['GET','POST'])
def compare():
    '''Sources data from the Federal Reserves FRED system and passes that data to be populated in a Chart.js graphic.
    Flask will call this function when http://hostname/chart/ is visited. Blank GET will default to SP500, while POST will
    access the matching chart if available.
    POST requests MUST include values labelled: timespan (in years), start date (in ISO 8601 format), and chart_name. 
    '''
    if request.method == 'POST':
        ind_chart_name = request.form['ind_chart_name']
        dep_chart_name = request.form['dep_chart_name']
        
        timespan = int(request.form['timespan'])
        start_date = date.fromisoformat(request.form['start_date'])
        offset = int(request.form['offset'])
        
    else: #default GET requests
        timespan = 2 #default to a 2 year chart
        start_date = date(date.today().year,1,1) #default to the first day of the current year
        offset = 0
        ind_chart_name = 'SP500'
        dep_chart_name = 'VIXCLS'
        
    series_independent, ind_units = get_chart(ind_chart_name,start_date,timespan)
    series_dependent, dep_units = get_chart(dep_chart_name,start_date,timespan)
    if series_independent and series_dependent: #only find r if both series have are not empty
        series_independent,series_dependent = equalize_time_series_len(series_independent,series_dependent,offset)
        r_value = rsquare(series_independent,series_dependent) #calculate the rsquare value to determine the correlation between two series_dependent
    else:
        r_value = 0
    
    return render_template('compare_view.html', r_value=r_value,ind_chart_name=ind_chart_name,ind_datapoints=series_independent,ind_units=ind_units, \
        dep_chart_name=dep_chart_name,dep_datapoints=series_dependent,dep_units=dep_units)
    
if __name__ == "__main__":
    app.run(host='localhost',port=80) #run the built-in development server, production should be replaced with a WSGI server like Apache
