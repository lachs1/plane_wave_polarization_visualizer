#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

import matplotlib
import numpy as np
from PIL import ImageTk

matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class EntryWithPlaceholder(ttk.Entry):
    def __init__(self, master, placeholder):
        super().__init__(master)

        self._placeholder = placeholder
        self._placeholder_color = "grey"
        self._default_fg_color = self["foreground"]

        self.bind(sequence="<FocusIn>", func=self.focus_in)
        self.bind(sequence="<FocusOut>", func=self.focus_out)

        self._set_placeholder()

    def _set_placeholder(self):
        self.insert(index=0, string=self._placeholder)
        self["foreground"] = self._placeholder_color

    def focus_in(self, _):
        if str(self["foreground"]) == self._placeholder_color:
            self.delete(first="0", last="end")
            self["foreground"] = self._default_fg_color

    def focus_out(self, _):
        if not self.get():
            self._set_placeholder()


class App(ttk.Frame):
    def __init__(self, master):
        super().__init__(master=master)

        master.title("Plane Wave Polarization Visualizer")
        master.columnconfigure(index=0, weight=1)
        master.rowconfigure(index=0, weight=1)

        image = ImageTk.PhotoImage(file="equation.png")

        self._eq = ttk.Label(master=self, image=image)
        self._eq.image = image  # Keep a reference
        self._eq.grid(row=0, column=0, columnspan=2, pady=10)

        self._R_label = ttk.Label(master=self, text="R", font="Times 18 bold")
        self._R_label.grid(row=1, column=0)

        self._R_entry = EntryWithPlaceholder(master=self, placeholder="0,0,1")
        self._R_entry.grid(row=1, column=1)

        self._Er_label = ttk.Label(master=self, text="E\u1d63", font="Times 18 bold")
        self._Er_label.grid(row=2, column=0)

        self._Er_label = EntryWithPlaceholder(master=self, placeholder="0.5,0,0")
        self._Er_label.grid(row=2, column=1)

        self._Ei_label = ttk.Label(master=self, text="E\u1d62", font="Times 18 bold")
        self._Ei_label.grid(row=3, column=0)

        self._Ei_label = EntryWithPlaceholder(master=self, placeholder="0,0.5,0")
        self._Ei_label.grid(row=3, column=1)

        self._button = ttk.Button(master=self, text="Ok", width=10)
        self._button.grid(row=4, column=0, columnspan=2, pady=10)

        figure = Figure(figsize=(4, 4), dpi=100)
        figure.patch.set_facecolor("#ececec")

        figure_canvas = FigureCanvasTkAgg(master=self, figure=figure)

        self.ax = figure.subplots()
        self._canvas = figure_canvas.get_tk_widget()
        self._canvas.grid(row=5, column=0, columnspan=2)

        self.columnconfigure(index=0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

        self._anim = FuncAnimation(
            fig=figure, func=self._animate, frames=10, interval=100
        )

    def _animate(self, i):
        my0 = 4 * np.pi * 10 ** -7
        eps0 = 8.854 * 10 ** -12
        R = np.array([0, 0, 1])  # Propagation direction of the plane wave
        ref = np.array([0, 0, 1])  # Reference axis
        n = np.sqrt(my0 / eps0)  # Intrinsic impedance of the medium
        E0 = 1  # Magnitude of the electric field
        Ere = np.array([0.5, 0, 0])  # Real part of the electric field
        Eim = np.array([0, 0.5, 0])  # Imaginary part of the electric field
        E = (Ere + 1j * Eim) * E0
        H = np.cross(R, E) / 2
        Ex, Ey, _ = np.real(E * np.exp(2 * np.pi / 10 * i * 1j))
        Hx, Hy, _ = np.real(H * np.exp(2 * np.pi / 10 * i * 1j))
        self.ax.clear()
        self.ax.grid(True)
        self.ax.set_xlim(-1, 1)
        self.ax.set_ylim(-1, 1)
        self.ax.quiver(
            [0],
            [0],
            [Ex],
            [Ey],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="b",
            label=r"$\bf{E}$",
        )
        self.ax.quiver(
            [0],
            [0],
            [Hx],
            [Hy],
            angles="xy",
            scale_units="xy",
            scale=1,
            color="r",
            label=r"$\bf{H}$",
        )
        self.ax.legend()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(master=root)
    app.mainloop()
