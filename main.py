import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import tkintermapview
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
matplotlib.use('agg')

import gpstracker as gt


class GPStracker(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GPS tracker")
        self.geometry('1000x500')
        self.config(bg="#2c2c2c")
        self.df = None
        self.date=None
        self.selected_activity_type = tk.StringVar("")
        self.selected_activity_type.set("Select activity type")

        def on_enter(e):
            e.widget.config(bg="#cccccc", fg="black")

        def on_leave(e):
            e.widget.config(bg="#4c4c4c", fg="white")


        # load csv
        file_button = tk.Button(text="Select gps log", bg="#4c4c4c",  fg="white",
                                font=("cursive", 12), command=self.open_file)
        file_button.bind('<Enter>', on_enter)
        file_button.bind('<Leave>', on_leave)
        file_button.grid(row=0, column=0, padx=(30,10), pady=(10,10), sticky=tk.W)
        options = ("Football", "Running", "Cycling")
        dropdown=tk.OptionMenu(self, self.selected_activity_type, *options)
        dropdown.config(bg="#4c4c4c", font=("cursive", 12), fg="white")
        dropdown["highlightthickness"]=0
        dropdown.grid(row=0, column=1, padx=10, pady=(10,10), sticky=tk.W)
        ok_button=tk.Button(text="Show activity", bg="#4c4c4c",  fg="white",
                            font=("cursive", 12),  command=self.show_activity)
        ok_button.bind('<Enter>', on_enter)
        ok_button.bind('<Leave>', on_leave)
        ok_button.grid(row=0, column=2, padx=10, pady=(10,10), sticky=tk.W)



    def show_activity(self):
        if self.df is None or self.selected_activity_type.get() == "Select activity type":
            messagebox.showerror("Python error","Select file and activity type")
        else:
            #try:
            self.date=gt.get_activity_date(self.df)
            self.df=gt.clear_df(self.df)
            self.show_stats()
            self.show_map()
            self.show_speed()
            #except:
                #messagebox.showerror("Python error", "Processing failed. Select other file!")


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
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Activity date: ").\
            grid(row=1, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12),  fg="white",text=f"{self.date, start_time}")\
            .grid(row=1, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"),  fg="white",text="Duration: ")\
            .grid(row=2, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12), fg="white", text=f"{duration}")\
            .grid(row=2, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Distance covered: ")\
            .grid(row=3, column=0, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12),  fg="white",text=f"{distance}")\
            .grid(row=3, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"), fg="white", text="Average speed: ") \
            .grid(row=4, column=0, columnspan=2,  sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12),  fg="white",text=f"{avg_speed}")\
            .grid(row=4, column=2, columnspan=2, sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12, "bold"),  fg="white",text="Top speed: ") \
            .grid(row=5, column=0, columnspan=2,  sticky=tk.W, padx=30)
        tk.Label(self, bg="#2c2c2c", font=("cursive", 12),  fg="white",text=f"{max_speed}")\
            .grid(row=5, column=2, columnspan=2, sticky=tk.W, padx=30)

    def show_map(self):
        map_plot = tkintermapview.TkinterMapView(self, width=400, height=400, corner_radius=0)
        points = list(zip(*map(self.df.get, ['lat_d', 'long_d'])))
        map_plot.set_position(self.df['lat_d'].mean(), self.df['long_d'].mean())
        map_plot.set_zoom(12)
        map_plot.set_path(points)
        map_plot.grid(row=1, column=5, rowspan=20, columnspan=3, padx=20)


    def show_speed(self):
        figure=Figure(figsize=(5,2))
        figure.set_facecolor("#3c3c3c")
        ax=figure.add_subplot(111)
        ax.set_title("Speed")
        ax.set_facecolor("#3c3c3c")
        matplotlib.rcParams['text.color'] = 'white'
        plot=FigureCanvasTkAgg(figure,self)
        plot.get_tk_widget().grid(row=7, column=0, rowspan=15,columnspan=3, padx=30)
        self.df["speed_kmph"].plot(ax=ax)


if __name__ == '__main__':
    app = GPStracker()
    app.mainloop()
