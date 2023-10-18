import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import tkintermapview

import gpstracker as gt


class GPStracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPS tracker")
        self.geometry('800x600')
        self.df = None
        self.date=None

        # load csv
        self.file_button = tk.Button(text="Select gps log", font=("Sans", 14), command=self.open_file).pack()
        self.selected_activity_type = tk.StringVar("")
        self.selected_activity_type.set("Select activity type")
        options = ("Football", "Running", "Cycling")
        tk.OptionMenu(self, self.selected_activity_type, *options).pack()
        tk.Button(text="Show activity", command=self.show_activity).pack()



    def show_activity(self):
        if self.df is None or self.selected_activity_type.get() == "Select activity type":
            messagebox.showerror("Python error","Select file and activity type")
        else:
            self.date=gt.get_activity_date(self.df)
            self.df=gt.clear_df(self.df)
            self.show_stats()
            self.show_map()

    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.df = pd.read_csv(path, names=range(13), on_bad_lines="skip")

    def show_stats(self):
        d_time = self.df['time_in_sec'].iloc[-1] - self.df['time_in_sec'].iloc[0]
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
        stats_label = tk.Label(self, justify=tk.RIGHT, padx=10, pady=10, text="Stats").pack()
        tk.Label(stats_label, text=f"Activity date: {self.date, start_time}").pack()
        tk.Label(stats_label, text=f"Duration: {duration}").pack()
        tk.Label(stats_label, text=f"Distance covered: {distance}")
        tk.Label(stats_label, text=f"Average speed: {avg_speed}").pack()
        tk.Label(stats_label, text=f"Max speed: {max_speed}").pack()

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
    app = GPStracker()
    app.mainloop()
