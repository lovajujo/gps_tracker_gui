import datetime
import tkinter as tk
from tkinter import filedialog, Label
import pandas as pd
import tkintermapview

import gpstracker as gt

root = tk.Tk()
root.geometry("800x500")
root.title("GPS tracker")

date=""
def open_file():
    path = filedialog.askopenfilename()
    df = pd.read_csv(path, names=range(13), on_bad_lines="skip")
    date=gt.get_activity_date(df)
    gpstracker(df)


def gpstracker(df):
    df = gt.clear_df(df)
    df = gt.calculate_distance(df)
    show_map(df)
    #stats(df)


def show_map(df):
    map_label = tk.LabelFrame(root)
    map_label.pack()
    map_plot = tkintermapview.TkinterMapView(map_label, width=400, height=400, corner_radius=0)
    points = list(zip(*map(df.get, ['lat_d', 'long_d'])))
    map_plot.set_position(df['lat_d'].mean(), df['long_d'].mean())
    map_plot.set_zoom(12)
    path = map_plot.set_path(points)
    map_plot.pack()


def stats(df):
    d_time=df.loc[len(df)-1][0]-df.loc[0][0]
    duration=datetime.timedelta(seconds=d_time)
    distance=df["distance"].sum()
    if distance > 1000:
        distance=f"{round(distance/1000,2)} km"
    else:
        distance=f"{int(distance)} m"
    max_speed = f"{df['speed_kmph'].max()} km/h"
    if activity_type==1:
        avg_speed=f"{df['speed_mpmin'].mean()} meter/min"
    elif activity_type==2:
        avg_speed=f"{df['pace'].mean()} min/km"
    else:
        avg_speed=f"{df['speed_kmph'].mean()} km/h"
    stats_label=tk.Label(root, justify=tk.RIGHT, padx=10, pady=10, text="Stats").pack()
    tk.Label(stats_label, text=f"Activity date: {date, pd.to_datetime(df.iloc[0].loc['time_in_sec']).strftime('%H:%M:%S')}").pack()
    tk.Label(stats_label, text=f"Duration: {duration}").pack()
    tk.Label(stats_label, text=f"Average speed: {avg_speed}").pack()
    tk.Label(stats_label, text=f"Max speed: {max_speed}")



def show_speed(df):
    pass


def plot_speed_cycling(df):
    pass


def plot_speed_running(df):
    pass


def plot_speed_football(df):
    pass


file_button = tk.Button(text="choose gps log", command=open_file)
file_button.pack()
activity_type=tk.IntVar(root, 1)
type_options={"Football": 1,
              "Running": 2,
              "Cycling": 3}
for text, value in type_options.items():
    tk.Radiobutton(root, text=text, variable=activity_type, value=value).pack()
choose_type=tk.Radiobutton(root, )

# log_date = pd.to_datetime(df[9].mode()[0]).strftime("%Y-%m-%d")


root.mainloop()
