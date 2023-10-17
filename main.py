import datetime
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import tkintermapview

import gpstracker as gt

class GPStracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPS tracker")
        self.geometry('800x600')
        self.df=None
        #load csv
        self.file_button=tk.Button(text="Select gps log", font=("Sans", 14), command=self.open_file).pack()
        # select activity type
        self.selected_activity_type = tk.StringVar("")
        self.selected_activity_type.set("Select activity type")
        self.options = ("Football", "Running", "Cycling")

    def select_activity_type(self):
        self.activity_types = tk.OptionMenu(self, self.selected_activity_type, *self.options, command=self.show_stats).pack()


    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.df = pd.read_csv(path, names=range(13), on_bad_lines="skip")
            gt.get_activity_date(self.df)
            self.select_activity_type()

    def show_stats(self):
        gt.clear_df(self.df)
        d_time = self.df.loc[len(self.df) - 1][0] - self.df.loc[0][0]
        duration = datetime.timedelta(seconds=d_time)
        distance = self.df["distance"].sum()
        if distance > 1000:
            distance = f"{round(distance / 1000, 2)} km"
        else:
            distance = f"{int(distance)} m"
        max_speed = f"{self.df['speed_kmph'].max()} km/h"
        if self.selected_activity_type.get() == "Football":
            avg_speed = f"{self.df['speed_mpmin'].mean()} meter/min"
        elif self.selected_activity_type.get() == "Running":
            avg_speed = f"{self.df['pace'].mean()} min/km"
        else:
            avg_speed = f"{self.df['speed_kmph'].mean()} km/h"
        start_time = pd.to_datetime(self.df.iloc[0].loc['time_in_sec']).strftime('%H:%M:%S')
        stats_label = tk.Label(self.root, justify=tk.RIGHT, padx=10, pady=10, text="Stats").pack()
        tk.Label(stats_label, text=f"Activity date: {self.date, start_time}").pack()
        tk.Label(stats_label, text=f"Duration: {duration}").pack()
        tk.Label(stats_label, text=f"Distance covered: {distance}")
        tk.Label(stats_label, text=f"Average speed: {avg_speed}").pack()
        tk.Label(stats_label, text=f"Max speed: {max_speed}").pack()
        self.show_map()

    def show_map(self):
        map_label = tk.LabelFrame(self)
        map_label.pack()
        map_plot = tkintermapview.TkinterMapView(map_label, width=400, height=400, corner_radius=0)
        points = list(zip(*map(self.df.get, ['lat_d', 'long_d'])))
        map_plot.set_position(self.df['lat_d'].mean(), self.df['long_d'].mean())
        map_plot.set_zoom(12)
        path = map_plot.set_path(points)
        map_plot.pack()


if __name__ == '__main__':
    app=GPStracker()
    app.mainloop()
