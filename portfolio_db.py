import sqlite3
import os
from datetime import timedelta,date

from portfolio_util import fred_get

class SeriesDB:

    def __init__(self, db_name,db_subdir='db'):

        self.db_name = db_name
        self.db_subdir = db_subdir
        
        try:
            os.mkdir(db_subdir)
        except FileExistsError:
            pass #subdirectory db exists
        
        self.db_filepath = os.path.join(db_subdir,db_name) +'.db'
        self.conn = sqlite3.connect(self.db_filepath) #sqlite does not use a CREATE DATABASE command
            
    def delete_series(self,series_name):
        '''Delete a series with the given name'''
        self.conn.execute('DELETE FROM time_series WHERE name=?',series_name)
        self.conn.commit() #save changes to db
     
    def add_series(self,series_name,series_dict,units):
        '''add a new series or add additional data to an existing series time series are inserted into 
           a simple two part table, an ISO8601 date and value stored as a real
           Accepts: A str series name and dictionary with key: python date, and
           value: floating point value on date
        '''
        if not series_dict: #check for empty calls
            return
        
        self.conn.execute('CREATE TABLE IF NOT EXISTS time_series    \
            (obs_date TEXT, value REAL, name TEXT, units TEXT)')
        
        self.delete_series(series_name) #clear out existing data, old data could be corrupted, wrong
        
        for obs_date, value in series_dict.items():
            self.conn.execute('INSERT INTO time_series (obs_date, value, name, units) VALUES (?, ?, ?, ?)', (obs_date.isoformat(),value,series_name,units))
                
        self.conn.commit() #save changes to db
            
    def get_series(self,series_name,start_date,timespan):
        ''' get a series between and including the two given dates. 
        Accepts: a str series name, a python date start date, and a timespan float in years
        Returns: A dictionary with key: a python date, and value: floating point value
        '''
        series_dict = {}
        units = ''
        
        end_date = start_date+timedelta(days=timespan*365.25)
        for row in self.conn.execute('''SELECT DISTINCT obs_date, value, units from time_series 
            WHERE name=? AND obs_date BETWEEN date(?) AND date(?)''',(series_name,start_date.isoformat(),end_date.isoformat())):

            obs_date = date.fromisoformat(row[0])
            value = row[1]
            if not units: #only need to get the units once
                units = row[2]
            
            
            series_dict[obs_date] = value
            
        return (series_dict,units)


    def updated(self,series_name,tolerance=45):
        '''check if a series is more than 45 days, or the specified number of days old.
           Many datasets are updated monthly, 45 day tolerance will avoid needless updating
           for these sets.

           Accepts: str series name, optional number of days old to check as an int
           Returns: true or false if updated
        '''
        cutoff_date = date.today() - timedelta(days=tolerance)
        
        try:
            cursor = self.conn.execute('SELECT MAX(obs_date) FROM time_series WHERE name=?',(series_name,))
        except sqlite3.OperationalError: #table doesn't exist
            return False
            
        latest_date = cursor.fetchone()
        
        if not latest_date: #if no records exist assume the table has never been updated
            return False
        elif latest_date[0] == None:
            #the sql max function will return a (None,) tuple when it fails to find anything, which in Python evaluates to True
            return False
        if cutoff_date > date.fromisoformat(latest_date[0]):
            return False
        return True

if __name__ == '__main__':
    pass

