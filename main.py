import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import tkintermapview
import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('agg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import gpstracker as gt


class GPStracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPS tracker")
        self.geometry('1100x500')
        self.config(bg="#2c2c2c")
        self.path = None
        self.df = None
        self.date = None
        self.selected_activity_type = tk.StringVar("")
        self.selected_activity_type.set("Select activity type")

        def on_enter(e):
            e.widget.config(bg="#cccccc", fg="black")

        def on_leave(e):
            e.widget.config(bg="#4c4c4c", fg="white")

        # load csv
        file_button = tk.Button(text="Select gps log", bg="#4c4c4c", fg="white",
                                font=("cursive", 12), command=self.open_file)
        file_button.bind('<Enter>', on_enter)
        file_button.bind('<Leave>', on_leave)
        file_button.grid(row=0, column=0, padx=(30, 10), pady=(10, 10), sticky=tk.W)
        options = ("Football", "Running", "Cycling")
        dropdown = tk.OptionMenu(self, self.selected_activity_type, *options)
        dropdown.config(bg="#4c4c4c", font=("cursive", 12), fg="white")
        dropdown["highlightthickness"] = 0
        dropdown.grid(row=0, column=1, padx=10, pady=(10, 10), sticky=tk.W)
        ok_button = tk.Button(text="Show activity", bg="#4c4c4c", fg="white",
                              font=("cursive", 12), command=self.show_activity)
        ok_button.bind('<Enter>', on_enter)
        ok_button.bind('<Leave>', on_leave)
        ok_button.grid(row=0, column=2, padx=10, pady=(10, 10), sticky=tk.W)

    def show_activity(self):
        self.df = pd.read_csv(self.path, names=range(13), on_bad_lines="skip")
        if self.df is None or self.selected_activity_type.get() == "Select activity type":
            messagebox.showerror("Python error", "Select file and activity type")
        else:
            try:
                self.date = gt.get_activity_date(self.df)
                self.df = gt.clear_df(self.df)
                self.show_stats()
                self.show_map()
                self.show_speed()
            except:
                messagebox.showerror("Python error", "Processing failed. Select other file!")

    def open_file(self):
        self.path = filedialog.askopenfilename()

    def show_stats(self):
        d_time = round(self.df['time_in_sec'].iloc[-1] - self.df['time_in_sec'].iloc[0], 2)
        duration = datetime.timedelta(seconds=d_time)
        distance = self.df["distance"].sum()
        if distance > 1000:
            distance = f"{round(distance / 1000, 1)} km"
        else:
            distance = f"{int(distance)} m"

        max_speed = f"{round(self.df['speed_kmph'].max(), 1)} km/h"
        avg_speed=self.calculate_avg_speed(d_time)

        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Activity started: "). \
            grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{self.date} {self.df['time'].iloc[0]}") \
            .grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Duration: ") \
            .grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{duration}") \
            .grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Distance covered: ") \
            .grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{distance}") \
            .grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Average speed: ") \
            .grid(row=4, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{avg_speed}") \
            .grid(row=4, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Top speed: ") \
            .grid(row=5, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{max_speed}") \
            .grid(row=5, column=2, columnspan=2, sticky=tk.W, padx=30)

    def calculate_avg_speed(self, duration):
        avg_speed = (self.df['distance'].sum()/1000) / (duration/3600)
        if self.selected_activity_type.get() == "Football":
            avg_speed = f"{int(avg_speed * 1000 / 60)} meter/min"
        elif self.selected_activity_type.get() == "Running":
            seconds = 60 / avg_speed * 60
            td = datetime.timedelta(seconds=seconds)
            dt = datetime.datetime(1, 1, 1) + td
            avg_speed = f"{dt.strftime('%M:%S')} min/km"
        else:
            avg_speed = f"{round(avg_speed, 1)} km/h"
        return avg_speed

    def show_map(self):
        map_plot = tkintermapview.TkinterMapView(self, width=400, height=400, corner_radius=0)
        points = list(zip(*map(self.df.get, ['lat_d', 'long_d'])))
        map_plot.set_position(self.df['lat_d'].mean(), self.df['long_d'].mean())
        map_plot.set_zoom(12)
        map_plot.set_path(points, color="#FF00BB")
        map_plot.grid(row=1, column=5, rowspan=20, columnspan=3, padx=20)

    def show_speed(self):
        plt.rcParams.update({'text.color': 'white',
                             'axes.facecolor': '#3c3c3c',
                             'axes.prop_cycle': 'cycler(color="#FF00BB")',
                             'axes.grid': True,
                             'axes.edgecolor': 'w',
                             'xtick.color': 'w',
                             'ytick.color': 'w',
                             'axes.labelcolor':'w',
                             'figure.facecolor': '#2c2c2c',
                             'grid.linewidth': '0.5'
                             })
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.plot(self.df['time'], self.df['speed_kmph'])
        ticks = self.df['time'][::len(self.df) // 5]
        plt.xticks(ticks)
        plt.ylabel("km/h", rotation=90)
        chart = FigureCanvasTkAgg(fig, self)
        chart.draw()
        chart.get_tk_widget().grid(row=6, column=0, columnspan=3, rowspan=15)


if __name__ == '__main__':
    app = GPStracker()
    app.mainloop()
