import requests_func
import pandas as pd
import numpy as np
import math
import pytz
from sklearn.preprocessing import MinMaxScaler


KST = pytz.timezone('Asia/Seoul')

def angle_to_cos(x):
    return np.cos(np.pi/180*(x-90))
    
def angle_to_sin(x):
    return np.sin(np.pi/180*(x+90))

def time_to_sin(x):
    return np.sin(2*np.pi*x/24)

def time_to_cos(x):
    return np.cos(2*np.pi*x/24)

def yday_to_EOT(x): #균시차
    d2r = math.pi/180
    B = (x - 1) * 360/365
    EOT = 229.2 * (0.000075
                   + 0.001868 * math.cos(d2r  * B)
                   - 0.032077* math.sin(d2r  * B)
                   - 0.014615 * math.cos(d2r  * 2 * B)
                   - 0.04089 * math.sin(d2r * 2 * B))
    return EOT

def EOT_to_sin(x):
    return np.sin(np.pi*x*365/360)

def EOT_to_cos(x):
    return np.cos(np.pi*x*365/360)

def month_to_sin(x):
    return np.sin(2*np.pi*x/12)

def month_to_cos(x):
    return np.cos(2*np.pi*x/12)


def fin_processing(weather, gen):
    input_data = weather.merge(gen, how='left', on='time')
    
    # 시간 변수
    input_data.time = input_data.time.map(lambda x: x.astimezone(KST))
    input_data['hour'] = input_data.time.dt.hour
    input_data['month'] = input_data.time.dt.month
    input_data["week"] = input_data.time.dt.isocalendar().week
    input_data['day'] = input_data.time.dt.day_of_year
    input_data['yday'] = input_data.time.dt.dayofyear

    # 일 별 자외선지수 평균 
    day_uv = input_data.pivot_table(index="day", values="uv_idx", aggfunc=np.mean).reset_index()
    input_data = input_data.merge(day_uv, on="day", suffixes=('', '_day'))
    input_data.drop("day", axis=1, inplace=True)

    #푸리에 변환
    input_data['sin_time'] = np.sin(2*np.pi*input_data.hour/24)
    input_data['cos_time'] = np.cos(2*np.pi*input_data.hour/24)

    input_data['sin_month'] = np.sin(2*np.pi*input_data.month/12)
    input_data['cos_month'] = np.cos(2*np.pi*input_data.month/12)

    # 균시차
    input_data['eot'] = input_data.yday.map(lambda x: yday_to_EOT(x))

    input_data['azimuth_sin'] = input_data.azimuth.map(lambda x: angle_to_sin(x))
    input_data['azimuth_cos'] = input_data.azimuth.map(lambda x: angle_to_cos(x))
    
    input_data.drop(columns=['time','hour','month','yday'], inplace=True)
    input_data.rename(columns = {'model1':'pred1','model2':'pred2','model3':'pred3','model4':'pred4','model5':'pred5'}, inplace=True)
    return input_data

def model1_processing(weather, gen):
    df = weather.merge(gen, how='left', on='time')
    df.time = df.time.map(lambda x: x.astimezone(KST))
    
    df['wind_dir_sin'] = df.wind_dir.map(lambda x: angle_to_sin(x))
    df['wind_dir_cos'] = df.wind_dir.map(lambda x: angle_to_cos(x))

    df['azimuth_sin'] = df.azimuth.map(lambda x: angle_to_sin(x))
    df['azimuth_cos'] = df.azimuth.map(lambda x: angle_to_cos(x))

    df['elevation_sin'] = df.elevation.map(lambda x: angle_to_sin(x))
    df['elevation_cos'] = df.elevation.map(lambda x: angle_to_cos(x))

    df['hour'] = df.time.dt.hour
    df['yday'] = df.time.dt.dayofyear
    df['month'] = df.time.dt.month
    df["week"] = df.time.dt.isocalendar().week

    
    df['eot'] = df.yday.map(lambda x: yday_to_EOT(x))
    df['eot_sin'] = df.eot.map(lambda x: EOT_to_sin(x))
    df['eot_cos'] = df.eot.map(lambda x: EOT_to_cos(x))

    df['wday_sin'] = df.eot.map(lambda x: wday_to_sin(x))
    df['wday_cos'] = df.eot.map(lambda x: wday_to_cos(x))
    
    df['hour_sin'] = df.eot.map(lambda x: wday_to_sin(x))
    df['hour_cos'] = df.eot.map(lambda x: wday_to_cos(x))
    
    df = df.drop(columns =['time','rain','snow','vis','wday','hour','month','eot','yday'])
    
    return df



