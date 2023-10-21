import datetime

import numpy
import numpy as np
import pandas as pd
from geopy.distance import distance


def get_activity_date(df):
    return pd.to_datetime(df[9].mode()[0]).strftime("%Y-%m-%d")


def clear_df(df):
    df = df[(df[0] == "$GPRMC") & (df[2] == "A")]
    df = df[[1, 3, 4, 5, 6, 9]]
    df = df.reset_index(drop=True)
    df[1] = np.where(df[1].str.len() != 9, np.nan, df[1])
    df[3] = np.where(df[3].str.len() != 10, np.nan, df[3])
    df[4] = np.where(df[4].str.len() != 1, np.nan, df[4])
    df[5] = np.where(df[5].str.len() != 11, np.nan, df[5])
    df[6] = np.where(df[6].str.len() != 1, np.nan, df[6])
    df[3] = np.where(df[4] == "S", "-" + df[3], df[3])
    df[5] = np.where(df[6] == "W", "-" + df[5], df[5])
    df[3] = df[3].dropna().apply(decimal_point_pos)
    df[5] = df[5].dropna().apply(decimal_point_pos)
    df['lat_dms'] = df[3].dropna().astype(float)
    df['long_dms'] = df[5].dropna().astype(float)
    df['lat_d'] = df[3].dropna().apply(convert_dms)
    df['long_d'] = df[5].dropna().apply(convert_dms)
    df['time_in_sec'] = df[1].dropna().apply(convert_time)
    df = df.interpolate()
    calculate_distance(df)
    calculate_speed(df)
    return df


def calculate_distance(df):
    df['point'] = df[['lat_d', 'long_d']].apply(tuple, axis=1)
    df['point_next'] = df['point'].shift(1)
    df['distance'] = df.apply(
        lambda row: distance(row['point'], row['point_next']).m, axis=1)
    df.drop(columns={'point', 'point_next'}, axis=1, inplace=True)
    return df


def calculate_speed(df):
    df['speed'] = df['distance'] / df['time_in_sec'].diff()
    df['pace'] = (1000 / df['distance'] * df['time_in_sec']).rolling(3).mean()
    df['speed_mps'] = df['speed'].rolling(3).mean()
    df['speed_kmph'] = df['speed_mps'] * 3.6
    df['speed_mpmin'] = df['speed_kmph'] * 1000 / 60


def decimal_point_pos(c_str):
    c_str = c_str.replace('.', '')
    return f"{c_str[:-7]}.{c_str[-7:]}"


def convert_dms(c_str):
    d = c_str[:-8]
    m = f"{c_str[-7:-5]}.{c_str[-5:]}"
    return round(float(d) + float(m) / 60, 7)


def convert_time(time):
    h = str(time)[0:2]
    m = str(time)[2:4]
    s = str(time)[4:]
    return (float(h) + 2) * 3600 + float(m) * 60 + float(s)
