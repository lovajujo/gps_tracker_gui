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
        self.geometry('800x500')
        self.config(bg="#2c2c2c")
        self.df = None
        self.date=None
        self.selected_activity_type = tk.StringVar("")
        self.selected_activity_type.set("Select activity type")

        def on_enter(e):
            e.widget.config(bg="white")

        def on_leave(e):
            e.widget.config(bg="#cccccc")


        # load csv
        file_button = tk.Button(text="Select gps log", bg="#cccccc", activebackground="white", command=self.open_file)
        file_button.bind('<Enter>', on_enter)
        file_button.bind('<Leave>', on_leave)
        file_button.grid(row=0, column=0, padx=(30,10), pady=(10,10))
        options = ("Football", "Running", "Cycling")
        dropdown=tk.OptionMenu(self, self.selected_activity_type, *options)
        dropdown.config(bg="#cccccc")
        dropdown["highlightthickness"]=0
        dropdown.grid(row=0, column=1, padx=10, pady=(10,10))
        ok_button=tk.Button(text="Show activity", bg="#cccccc", activebackground="white", command=self.show_activity)
        ok_button.bind('<Enter>', on_enter)
        ok_button.bind('<Leave>', on_leave)
        ok_button.grid(row=0, column=2, padx=10, pady=(10,10))



    def show_activity(self):
        if self.df is None or self.selected_activity_type.get() == "Select activity type":
            messagebox.showerror("Python error","Select file and activity type")
        else:
            try:
                self.date=gt.get_activity_date(self.df)
                self.df=gt.clear_df(self.df)
                self.show_stats()
                self.show_map()
            except:
                messagebox.showerror("Python error", "Processing failed. Select other file!")


    def open_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.df = pd.read_csv(path, names=range(13), on_bad_lines="skip")

    def show_stats(self):
        d_time = self.df['time_in_sec'].iloc[-1] - self.df['time_in_sec'].iloc[0]
        duration = datetime.timedelta(seconds=d_time)
        distance = self.df["distance"].sum()
        if distance > 1000:
            distance = f"{round(distance / 1000, 1)} km"
        else:
            distance = f"{round(int(distance), 1)} m"
        max_speed = f"{round(self.df['speed_kmph'].max(), 1)} km/h"
        if self.selected_activity_type.get() == "Football":
            avg_speed = f"{round(self.df['speed_mpmin'].mean(), 1)} meter/min"
        elif self.selected_activity_type.get() == "Running":
            avg_speed = f"{round(self.df['pace'].mean(), 1)} min/km"
        else:
            avg_speed = f"{round(self.df['speed_kmph'].mean(), 1)} km/h"
        start_time = pd.to_datetime(self.df.iloc[0].loc['time_in_sec']).strftime('%H:%M:%S')
        tk.Label(self, text=f"Activity date: {self.date, start_time}").grid(row=1, column=0, columnspan=3, sticky=tk.W, padx=30)
        tk.Label(self, text=f"Duration: {duration}").grid(row=2, column=0, columnspan=3, sticky=tk.W, padx=30)
        tk.Label(self, text=f"Distance covered: {distance}").grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=30)
        tk.Label(self, text=f"Average speed: {avg_speed}").grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=30)
        tk.Label(self, text=f"Max speed: {max_speed}").grid(row=5, column=0, columnspan=3, sticky=tk.W, padx=30)

    def show_map(self):
        map_plot = tkintermapview.TkinterMapView(self, width=400, height=400, corner_radius=0)
        points = list(zip(*map(self.df.get, ['lat_d', 'long_d'])))
        map_plot.set_position(self.df['lat_d'].mean(), self.df['long_d'].mean())
        map_plot.set_zoom(12)
        map_plot.set_path(points)
        map_plot.grid(row=0, column=4, rowspan=10, columnspan=3, padx=30, pady=(30,10))


if __name__ == '__main__':
    app = GPStracker()
    app.mainloop()
