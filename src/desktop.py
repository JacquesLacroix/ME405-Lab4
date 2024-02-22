"""!
@file desktop.py
Creates a GUI for user to start and visualize response of DC motor.
"""

import math
import time
import tkinter
from random import random
from serial import Serial
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import struct


def plot_response(plot_axes, plot_canvas, xlabel, ylabel):
    """!
    Starts the step response and plots experimental results.
    @param plot_axes matplotlib figure which response is plotted on
    @param plot_canvas canvas which the plot will appear
    @param xlabel label for x axis of plot
    @param ylabel label for y axis of plot
    @returns None
    """
    times = []
    result = []

    with Serial('COM5', 9600, timeout=1) as ser:
        kp = input("ENTER KP VALUE: ")
        try:
            kp = float(kp)
        except:
            print("KP MUST BE A NUMBER")
            return
        
        ser.write("Begin\n".encode())
        ser.write((str(kp) + "\n").encode())
        ser.write("\n".encode())
        ser.flush()

        while True:
            line = ser.readline().decode().strip()
            
            if line == "":
                continue
            
            print(line)
            if line == "End":
                break
            else:
                pass
                times.append(float(line.split(", ")[0]))
                result.append(float(line.split(", ")[1]))
    
    plot_axes.scatter(times, result)
    plot_axes.set_xlabel(xlabel)
    plot_axes.set_ylabel(ylabel)
    plot_axes.set_xticks([0, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500, 550])
    plot_axes.set_yticks([0, 1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000])
    plot_axes.grid(True)
    plot_canvas.draw()


def tk_matplot(plot_function, xlabel, ylabel, title):
    """!
    Create a TK window with one embedded Matplotlib plot.
    This function makes the window, displays it, and runs the user interface
    until the user closes the window. The plot function, which must have been
    supplied by the user, should draw the plot on the supplied plot axes and
    call the draw() function belonging to the plot canvas to show the plot.
    @param plot_function The function which, when run, creates a plot
    @param xlabel The label for the plot's horizontal axis
    @param ylabel The label for the plot's vertical axis
    @param title A title for the plot; it shows up in window title bar
    """
    tk_root = tkinter.Tk()
    tk_root.wm_title(title)

    fig = Figure()
    axes = fig.add_subplot()

    canvas = FigureCanvasTkAgg(fig, master=tk_root)
    toolbar = NavigationToolbar2Tk(canvas, tk_root, pack_toolbar=False)
    toolbar.update()

    button_quit = tkinter.Button(master=tk_root, text="Quit", command=tk_root.destroy)
    button_clear = tkinter.Button(master=tk_root, text="Clear", command=lambda: axes.clear())
    button_run = tkinter.Button(master=tk_root, text="Run", command=lambda: plot_function(axes, canvas, xlabel, ylabel))

    canvas.get_tk_widget().grid(row=0, column=0, columnspan=3)
    toolbar.grid(row=1, column=0, columnspan=3)
    button_run.grid(row=2, column=0)
    button_clear.grid(row=2, column=1)
    button_quit.grid(row=2, column=2)

    tkinter.mainloop()


if __name__ == "__main__":
    tk_matplot(plot_response, xlabel="Time (ms)", ylabel="Position (Encoder Ticks)", title="Step Response")