from statistics import mean
from math import sqrt, isnan

from fredapi import Fred #python wrapper for accessing the Federal Reserves open API
from datetime import date, timedelta



def equalize_time_series_len(independent,dependent,offset=0):
    '''
    Accepts two dicts of date values tuples and an optional offset in days.
    
    The offset will shift all comparison dates in the number of days of the offset, positive or negative
    This is useful should want to if a series is a trailing or leading financial indicator
    
    Returns two equal length dicts of date value pairs, with both containing only dates that appear in both dicts
    '''
    dep_offset = {}
    for date,value in dependent.items(): #change dates in dep series to be subtracted by offset
        dep_offset[date-timedelta(days=offset)] = value
    ind_equalized = {}
    dep_equalized = {}
    for date in independent.keys(): #only add dates existing in both series to the return dicts
        if date in dep_offset:
            ind_equalized[date] = independent[date]
            dep_equalized[date] = dep_offset[date]
        
        
    assert len(ind_equalized) == len(dep_equalized), 'Unequal dict length return: ' + str(len(ind_equalized)) + ' != ' + str(len(dep_equalized))
    return ind_equalized, dep_equalized

def rsquare(ind_series,dep_series):
    '''Find the person product moment correlation coefficent
    The length of x and y must be the same and all values must exist

    '''
    x_values = ind_series.values() #strip out dates
    y_values = dep_series.values()
    
    assert len(x_values) == len(y_values), "rsquare(), series to be compared must be equal in length"
    
    x_mean = mean(x_values)
    y_mean = mean(y_values)
    
    numerator = 0
    denominator = 0
    
    #the denominator is composed of two summations multipled together then square rooted
    denom_sum_x = 0
    denom_sum_y = 0 
    
    for x,y in zip(x_values,y_values): #compute the summutation operators
        numerator = numerator + ((x - x_mean) * (y-y_mean))

        denom_sum_x = denom_sum_x + (x-x_mean)**2
        denom_sum_y = denom_sum_y + (y-y_mean)**2
        
    denominator = denom_sum_x * denom_sum_y
    denominator = sqrt(denominator)

    return round(numerator/denominator,4)
    
def fred_get(time_series):
    '''return a dict with key, value

    returns: ([(dates,values),...],units)
    
    '''
    fred = Fred(api_key='c210579b3c6567d016211fdd76cb465a') #Key would be specific to server in production, freely available from the Fed
    fred_time_series = fred.get_series(time_series)
    units = fred.get_series_info(time_series)['units'] #Get unit information, such as 'in millions of dollars'

    datapoints = {}
    for obs_date, value in fred_time_series.items(): #unpack fred data, strip time info from the date and build the dict
        obs_date = obs_date.date() #convert datetime obj to date
        if isnan(value): #skip empty values, usually from holidays
            continue        
        datapoints[obs_date] = value
        
    return (datapoints,units)
    
       


if __name__ == '__main__':
    pass