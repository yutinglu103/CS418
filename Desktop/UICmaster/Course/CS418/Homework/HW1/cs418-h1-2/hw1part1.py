import pandas as pd
import numpy as np

# 3% credit
def extract_mins(time):
    """
    Extracts minute information from military time
    
    Args: 
        time (float64): series of time given in military format.  
          Takes on values in 0.0-2359.0 due to float64 representation.
    
    Returns:
        array (float64): series of input dimension with minute information.  
          Should only take on integer values in 0-59
    """
    minute_list = []
    for t in time:
        if pd.isna(t):
            minute_list.append(np.nan)
        else:
            try:
                if t < 0 or t > 2359:
                    minute_list.append(np.nan)
                    continue
                
                time_int = int(t)
                hour = time_int // 100
                minute = time_int % 100 
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    minute_list.append(minute)
                else:
                    minute_list.append(np.nan)
            except ValueError:
                minute_list.append(np.nan)
    return pd.Series(minute_list)

# 2% credit
def convert_to_minofday(time):
    """
    Converts HH:MM:SS time to minute of day
    
    Args:
        time: series of time given as strings in HH:MM:SS format.  
          
    
    Returns:
        array (float64): series of input dimension with minute of day
    
    Example: 13:03 is converted to 783.0
    """
    min_of_day_list= []
    for t in time:
        try:
            if isinstance(t, str):
                parts = t.split(':')
                
                if len(parts) >= 2:
                    hours = float(parts[0])
                    minutes = float(parts[1])
                    
                    if 0 <= hours < 24 and 0 <= minutes < 60:
                        min_of_day = hours * 60 + minutes
                    else:
                        min_of_day = np.nan
                else:
                    min_of_day = np.nan
            else:
                min_of_day = np.nan
        except (ValueError, AttributeError):
            min_of_day = np.nan
        
        min_of_day_list.append(min_of_day)
    return pd.Series(min_of_day_list)

def find_closest_scheduled(arrival, scheduled_times):
    min_diff = float('inf') 
    closest_scheduled_time = None
    for scheduled_time in scheduled_times:
        diff = abs(arrival - scheduled_time)
        if diff < min_diff:
            min_diff = diff
            closest_scheduled_time = scheduled_time
    return closest_scheduled_time

# 4%credit
def assigned_scheduled_times(arrival_times, scheduled_times):
    """
    Calculates delay times y - x
    
    Args:
        arrival_times: series of scheduled times 
        scheduled_times: series of actual arrival times
    
    Returns:
        arrival_scheduled_times: pandas dataframe with two columns viz., arrival times and corresponding scheduled time
    """
    Update_scheduled_list = []
    for  arrival_time in arrival_times:
        closest_scheduled_time = find_closest_scheduled(arrival_time,scheduled_times)
        Update_scheduled_list.append(closest_scheduled_time)
    
    arrival_scheduled_times = pd.DataFrame({
        'Arrival Times': arrival_times,
        'Scheduled Times': Update_scheduled_list,
        
    })
    return arrival_scheduled_times



# 1% credit
def extract_hour(time):
    hour_list = []
    for t in time:
        if pd.isna(t):
            hour_list.append(np.nan)
        else:
            try:
                if t < 0 or t > 2359:
                    hour_list.append(np.nan)
                    continue
                
                time_int = int(t)
                hour = time_int // 100
                minute = time_int % 100 
                
                if 0 <= hour < 24 and 0 <= minute < 60:
                    hour_list.append(hour)
                else:
                    hour_list.append(np.nan)
            except ValueError:
                hour_list.append(np.nan)
    return pd.Series(hour_list)

def military_time_to_minutes(time):
    hour = extract_hour(time)
    minute = extract_mins(time)
    return hour * 60 + minute

def calc_delay(df_assigned_scheduled_times):
    """
    Calculates delay times y - x
    
    Args:
        df_assigned_scheduled_times: pandas dataframe with two columns viz., arrival times and corresponding scheduled time
    
    Returns: 
        pandas series of input dimension with delay time
    """
    if df_assigned_scheduled_times.columns.isnull().all():
        df_assigned_scheduled_times.columns = ['Scheduled Times', 'Arrival Times']
    if list(df_assigned_scheduled_times.columns) == [0, 1]:
        df_assigned_scheduled_times.columns = ['Scheduled Times', 'Arrival Times']
    
    delay_time = military_time_to_minutes(df_assigned_scheduled_times['Arrival Times']) - military_time_to_minutes(df_assigned_scheduled_times['Scheduled Times'])
    return delay_time