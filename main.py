#!/usr/bin/python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror

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

        self._R = np.array([0, 0, 0], dtype=float)
        self._E = np.array([0, 0, 0], dtype=float)
        self._H = np.array([0, 0, 0], dtype=float)

        master.title("Plane Wave Polarization Visualizer")
        master.columnconfigure(index=0, weight=1)
        master.rowconfigure(index=0, weight=1)

        image = ImageTk.PhotoImage(file="img/fields.png")

        self._eq = ttk.Label(master=self, image=image)
        self._eq.image = image
        self._eq.grid(row=0, column=0, columnspan=2, pady=10)

        self._a_label = ttk.Label(master=self, text="a", font="Times 18 bold")
        self._a_label.grid(row=1, column=0)

        self._a_entry = EntryWithPlaceholder(master=self, placeholder="0,0,1")
        self._a_entry.grid(row=1, column=1)

        self._Er_label = ttk.Label(master=self, text="E\u1d63", font="Times 18 bold")
        self._Er_label.grid(row=2, column=0)

        self._Er_entry = EntryWithPlaceholder(master=self, placeholder="0.5,0,0")
        self._Er_entry.grid(row=2, column=1)

        self._Ei_label = ttk.Label(master=self, text="E\u1d62", font="Times 18 bold")
        self._Ei_label.grid(row=3, column=0)

        self._Ei_entry = EntryWithPlaceholder(master=self, placeholder="0,0.5,0")
        self._Ei_entry.grid(row=3, column=1)

        self._eta_label = ttk.Label(master=self, text="\u03b7", font="Times 18")
        self._eta_label.grid(row=4, column=0)

        self._eta_scale = ttk.Scale(master=self, from_=1, to=10, value=2)
        self._eta_scale.grid(row=4, column=1)

        self._button = ttk.Button(
            master=self, text="Ok", width=10, command=self._visualize
        )
        self._button.grid(row=5, column=0, columnspan=2, pady=10)

        self._figure = Figure(figsize=(4, 4), dpi=100)
        self._figure.patch.set_facecolor("#ececec")

        figure_canvas = FigureCanvasTkAgg(master=self, figure=self._figure)

        self.ax = self._figure.subplots()
        self._canvas = figure_canvas.get_tk_widget()
        self._canvas.grid(row=6, column=0, columnspan=2)

        self.columnconfigure(index=0, weight=1)
        self.grid(row=0, column=0, sticky="nsew")

        self._anim = FuncAnimation(
            fig=self._figure, func=self._animate, frames=10, interval=100
        )

    def _visualize(self):
        self._a = np.array(self._a_entry.get().split(","), dtype=float)

        _Er = np.array(self._Er_entry.get().split(","), dtype=float)
        _Ei = np.array(self._Ei_entry.get().split(","), dtype=float)

        _E = _Er + 1j * _Ei

        if np.dot(_E, self._a):
            showerror(
                title="Error",
                message="The electric field and the propagation direction must be orthogonal.",
            )
            return

        self._E = _E
        self._H = np.cross(self._a, self._E) / self._eta_scale.get()

        z = np.array([0, 0, 1])  # Rotate to Z-axis.
        u = np.cross(self._a, z)
        norm = np.linalg.norm(u)

        if norm:
            u = u / norm  # Normalize axis rotation vector.
            ux, uy, uz = u
        else:
            ux, uy, uz = [0, 0, 0]

        theta = np.arctan2(norm, np.dot(self._a, z))

        A = np.array(
            [
                [
                    np.cos(theta) + ux ** 2 * (1 - np.cos(theta)),
                    ux * uy * (1 - np.cos(theta)) - uz * np.sin(theta),
                    ux * uz * (1 - np.cos(theta)) + uy * np.sin(theta),
                ],
                [
                    uy * ux * (1 - np.cos(theta)) + uz * np.sin(theta),
                    np.cos(theta) + uy ** 2 * (1 - np.cos(theta)),
                    uy * uz * (1 - np.cos(theta)) - ux * np.sin(theta),
                ],
                [
                    uz * ux * (1 - np.cos(theta)) - uy * np.sin(theta),
                    uz * uy * (1 - np.cos(theta)) + ux * np.sin(theta),
                    np.cos(theta) + uz ** 2 * (1 - np.cos(theta)),
                ],
            ]
        )  # Rotation Matrix.

        self._E = A @ self._E
        self._H = A @ self._H

    def _animate(self, i):
        Ex, Ey, _ = np.real(self._E * np.exp(2 * np.pi / 10 * i * 1j))
        Hx, Hy, _ = np.real(self._H * np.exp(2 * np.pi / 10 * i * 1j))
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
