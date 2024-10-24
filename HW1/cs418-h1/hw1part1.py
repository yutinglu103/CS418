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
    time_list = time.tolist()
    minute_list =[]
    for time in time_list:
        if pd.isna(time):
            minute = np.nan
        else:
            minute = int(str(time)[2:4])
        minute_list.append(minute)

    update_minute_list =[]
    for minute in minute_list:
        if (minute >=0)&(minute <= 60):
            update_minute_list.append(minute)
        else:
            update_minute_list.append(np.nan)
        
    result = pd.Series(update_minute_list)
    return result

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
    time_list = time.tolist()
    min_of_day_list= []
    for time in time_list:
        hours = float(time.split(':')[0])
        minutes = float(time.split(':')[1])

        if((hours>=0) & (hours < 24) & (minutes >= 0) & (minutes < 60)):
            min_of_day = hours * 60 + minutes
        else:
            min_of_day = np.nan
            
        min_of_day_list.append(min_of_day)
        
    result = pd.Series(min_of_day_list)
     
    return result

def find_closest_scheduled(arrival, scheduled_times):
    min_diff = float('inf') 
    closest_scheduled_time = None
    for scheduled_time in scheduled_times:
        diff = arrival - scheduled_time
        
        if diff >= 0 and diff < min_diff:
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
        'Scheduled Times': Update_scheduled_list
    })
    return arrival_scheduled_times



# 1% credit
def calc_delay(df_assigned_scheduled_times):
    """
    Calculates delay times y - x
    
    Args:
        assigned_scheduled_times: pandas dataframe with two columns viz., arrival times and corresponding scheduled time
    
    Returns: 
        pandas series of input dimension with delay time
    """
    df_assigned_scheduled_times.columns = ['arrival_times', 'correspondin_scheduled_times']
    delay_time = df_assigned_scheduled_times['arrival_times'] - df_assigned_scheduled_times['correspondin_scheduled_times']
    
    return delay_time