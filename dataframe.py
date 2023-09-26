import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import folium

url = "https://raw.githubusercontent.com/lovajujo/stm32/main/logs/log20230925_c.csv"
df = pd.read_csv(url, names=range(13), on_bad_lines="skip")
df_pos = df[(df[0] == "$GPRMC") & (df[2] == "A")]
df_pos = df[(df[2] == "A")]
log_date = pd.to_datetime(df_pos[9].mode()[0]).strftime("%Y-%m-%d")
print(str(log_date))
df_pos = df_pos[[1, 3, 4, 5, 6]]
df_pos = df_pos.reset_index(drop=True)
df_pos[1] = np.where(df_pos[1].str.len() != 9, np.nan, df_pos[1])
df_pos[3] = np.where(df_pos[3].str.len() != 10, np.nan, df_pos[3])
df_pos[4] = np.where(df_pos[4].str.len() != 1, np.nan, df_pos[4])
df_pos[5] = np.where(df_pos[5].str.len() != 11, np.nan, df_pos[5])
df_pos[6] = np.where(df_pos[6].str.len() != 1, np.nan, df_pos[6])
df_pos[3] = np.where(df_pos[4] == "S", "-" + df_pos[3], df_pos[3])
df_pos[5] = np.where(df_pos[6] == "W", "-" + df_pos[5], df_pos[5])


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


df_pos[3] = df_pos[3].dropna().apply(decimal_point_pos)
df_pos[5] = df_pos[5].dropna().apply(decimal_point_pos)
df_pos['lat_dms'] = df_pos[3].dropna().astype(float)
df_pos['long_dms'] = df_pos[5].dropna().astype(float)
df_pos['lat_d'] = df_pos[3].dropna().apply(convert_dms)
df_pos['long_d'] = df_pos[5].dropna().apply(convert_dms)
df_pos['time_in_sec'] = df_pos[1].dropna().apply(convert_time)

coords = pd.DataFrame()
coords[['time_in_sec', 'lat_dms', 'long_dms', 'lat_d', 'long_d']] = df_pos[
    ['time_in_sec', 'lat_dms', 'long_dms', 'lat_d', 'long_d']].astype(float)
coords = coords.interpolate()
coords['dlat'] = coords['lat_d'].diff() * np.pi / 180
coords['dlong'] = coords['long_d'].diff() * np.pi / 180
coords['lat_rad'] = coords['lat_d'] * np.pi / 180
coords['a'] = pow(np.sin(coords['dlat'] / 2), 2) + pow(np.sin(coords['dlong'] / 2), 2) * np.cos(
    coords['lat_rad'].shift(1) * np.cos(coords['lat_rad']))
coords['c'] = 2 * np.arcsin(np.sqrt(coords['a']))
coords['distance'] = 6371000 * coords['c']
coords.drop(columns=['a', 'c', 'dlat', 'dlong', 'lat_rad'], inplace=True)
coords['speed_mps'] = coords['distance'] / coords['time_in_sec'].diff()

coords['speed_mps_moving'] = coords['speed_mps'].rolling(5).mean()

#print("activity started: ", log_date, pd.to_datetime(coords.iloc[0][7]).strftime("%H:%M:%S"))
duration = coords.loc[len(coords) - 1][0] - coords.loc[0][0]
print("duration (h:m:s): ", datetime.timedelta(seconds=duration))
dist = coords['distance'].sum()
if dist < 1000:
    print("distance: ", int(dist), "m")
else:
    print("distance: ", round(dist / 1000, 2), "km")
print("average speed :", round(dist / (coords.iloc[len(coords) - 1][0] - coords.iloc[0][0]) * 3.6, 2), "km/h")
