import tkinter as tk
from tkinter import filedialog
import pandas as pd

df=""
def open_file():
    path=filedialog.askopenfilename()
    df=pd.read_csv(path, names=range(13), on_bad_lines="skip")
    label=tk.Label(root, text=df.shape)
    label.pack()

root = tk.Tk()
root.geometry("500x500")
root.title("GPS tracker")
file_button=tk.Button(text="choose gps log", command=open_file)
file_button.pack()
root.mainloop()

