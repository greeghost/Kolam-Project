import tkinter as tk
from tkinter.filedialog import asksaveasfile,  askopenfile
from math import sqrt, ceil, floor
from mercat import Grid, Point
from random import random
import matplotlib.pyplot as plt
import re

class KolamApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.pb = PulliBoard(self)
        self.pb.pack(side = "right", expand = True)

        self.cp = ControlPanel(self)
        self.cp.pack(side = "left", fill = "x", expand = True)

    def run(self):
        self.mainloop()

class ControlPanel(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        kwargs["highlightthickness"]  = 0


        self.b1 = tk.Button(self, text = "Add/remove pulli", command = self.mouse_preset_1)
        self.b1.grid(row=0, column=0)

        self.b2 = tk.Button(self, text = "Add/remove link", command = self.mouse_preset_2)
        self.b2.grid(row=1, column=0)

        self.b3 = tk.Button(self, text = "Clear Board", command = self.clean)
        self.b3.grid(row=2, column=0)

        self.b4 = tk.Button(self, text = "Apply Mercat Algorithm", command = self.mercatize)
        self.l1 = tk.Label(self, text="Method")
        self.e1 = tk.StringVar(self)
        self.e1.set("bezier")
        self.om1 = tk.OptionMenu(self, self.e1, *["bezier", "hermite"])
        self.b4.grid(row=3, column=0)
        self.l1.grid(row=3, column=1)
        self.om1.grid(row=3, column=2)

        self.b5 = tk.Button(self, text = "Gridify", command = self.gridify)
        self.l2 = tk.Label(self, text="spacing")
        self.e2 = tk.Entry(self)
        self.e2.insert(0, "80")
        self.e3 = tk.StringVar(self)
        self.e3.set("square")
        self.l3 = tk.Label(self, text="shape")
        self.om2 = tk.OptionMenu(self, self.e3, *["square", "triangular", "hexagonal"])
        self.b5.grid(row=4, column=0)
        self.l2.grid(row=4, column=1)
        self.e2.grid(row=4, column=2)
        self.l3.grid(row=5, column=1)
        self.om2.grid(row=5, column=2)

        self.b6 = tk.Button(self, text = "Save", command = self.save)
        self.b6.grid(row=6, column=0)

        self.b7 = tk.Button(self, text = "Load", command = self.load)
        self.b7.grid(row=7, column=0)

        self.b8 = tk.Button(self, text = "Generate", command = self.generate)
        self.l4 = tk.Label(self, text="edge density (0-1)")
        self.e4 = tk.Entry(self)
        self.e4.insert(0, "0.5")
        self.e5 = tk.StringVar(self)
        self.e5.set("None")
        self.l5 = tk.Label(self, text="Symmetry")
        self.om3 = tk.OptionMenu(self, self.e5, *["None", "Vertical", "Horizontal", "Radial"])
        self.b8.grid(row=8, column=0)
        self.l4.grid(row=8, column=1)
        self.e4.grid(row=8, column=2)
        self.l5.grid(row=9, column=1)
        self.om3.grid(row=9, column=2)

    def mouse_preset_1(self):
        self.master.pb.selected_pulli = None
        self.master.pb.bind("<ButtonPress-1>", self.master.pb.add_pulli)
        self.master.pb.bind("<ButtonPress-3>", self.master.pb.remove_pulli)

    def mouse_preset_2(self):
        self.master.pb.bind("<ButtonPress-1>", self.master.pb.add_link)
        self.master.pb.bind("<ButtonPress-3>", self.master.pb.remove_link)

    def clean(self):
        self.master.pb.clean()
    
    def mercatize(self):
        fun = self.e1.get()
        if fun != "":
            self.master.pb.mercatize(fun)
        else:
            self.master.pb.mercatize("bezier")

    def get_spacing(self):
        spacing = self.e2.get()
        if spacing != "":
            try:
                spacing = int(spacing)
                return spacing
            except ValueError:
                print("Invalid spacing")
        else:
            return 80        
    
    def gridify(self):
        spacing = self.get_spacing()
        shape = self.e3.get()
        self.master.pb.create_pulli_grid(shape, spacing)
    
    def save(self):
        self.master.pb.save()
    
    def load(self):
        self.master.pb.load()
    
    def generate(self):
        spacing = self.get_spacing()
        density = self.e4.get()
        symmetry = self.e5.get()
        if density != "":
            try:
                density = float(density)
                self.master.pb.generate(density, symmetry, spacing)
            except ValueError:
                print("Invalid density")
        else:
            self.master.pb.generate(0.5, symmetry, spacing)

class PulliBoard(tk.Canvas):
    PULLI_RADIUS = 10
    ADD_LINK = 1
    RM_LINK = 2
    WIDTH = 960
    HEIGHT = 540

    def __init__(self, *args, **kwargs):
        self.pullis = []
        self.links = []
        self.selected_pulli = None
        self.last_event = self.ADD_LINK
        kwargs["width"] = PulliBoard.WIDTH
        kwargs["height"] = PulliBoard.HEIGHT
        kwargs["bg"] = "white"
        kwargs["highlightthickness"]  = 10
        # kwargs["highlightbackground"] = 'black'
        super().__init__(*args, **kwargs)
        self.bind("<Button-1>", self.add_pulli)
        self.bind("<Button-3>", self.remove_pulli)


    def clean(self):
        for p in self.pullis:
            self.delete(p[2])
        for link in self.links:
            self.delete(link[2])
        self.pullis = []
        self.links = []
        self.selected_pulli = None
    
    def get_pulli(self, x, y):
        for pulli in self.pullis[::-1]:
            if sqrt((pulli[0] - x) ** 2 + (pulli[1] - y) ** 2) <= self.PULLI_RADIUS:
                return pulli
        return None

    def add_pulli(self, event):
        x = event.x
        y = event.y
        pulli = self.create_oval(x - self.PULLI_RADIUS, y - self.PULLI_RADIUS, x + self.PULLI_RADIUS, y + self.PULLI_RADIUS, fill="red")
        self.pullis.append((x, y, pulli))

    def remove_pulli(self, event):
        pulli = self.get_pulli(event.x, event.y)
        if pulli is None:
            return
        self.pullis.remove(pulli)
        self.delete(pulli[2])
        for link in self.links[:]: # [:] to iterate over a copy since we remove element of self.links on the fly.
            if pulli in link:
                self.delete(link[2])
                self.links.remove(link)

    def add_link(self, event):
        pulli = self.get_pulli(event.x, event.y)
        if pulli is None:
            return
        if (self.selected_pulli is not None) and (self.last_event == self.ADD_LINK):
            p1 = min(self.selected_pulli, pulli)
            p2 = max(self.selected_pulli, pulli)
            if p1 == p2:
                return
            for link in self.links:
                if link[0] == p1 and link[1] == p2:
                    break
            else:
                line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                self.links.append((p1, p2, line))
                self.selected_pulli = None
        else:
            self.selected_pulli = pulli
            self.last_event = self.ADD_LINK

    def remove_link(self, event):
        pulli = self.get_pulli(event.x, event.y)
        if pulli is None:
            return
        if (self.selected_pulli is not None) and (self.last_event == self.RM_LINK):
            p1 = min(self.selected_pulli, pulli)
            p2 = max(self.selected_pulli, pulli)
            for link in self.links:
                if link[0] == p1 and link[1] == p2:
                    self.delete(link[2])
                    self.links.remove(link)
                    self.selected_pulli = None
        else:
            self.selected_pulli = pulli
            self.last_event = self.RM_LINK
    
    def mercatize(self, fun):
        G = Grid([])
        for link in self.links:
            p1 = Point(link[0][0], -link[0][1])
            p2 = Point(link[1][0], -link[1][1])
            G.add_point(p1)
            G.add_point(p2)
            G.add_edge(p1, p2)
        G.plot_knotwork(0.75, 1.6, color_each_thread = True, interp=fun)
        # G.plot()
        plt.show()
    
    def create_pulli_grid(self, shape, spacing = 100):
        match = {
            "square": self.create_square_grid,
            "triangular": self.create_triangular_grid,
            "hexagonal": self.create_hexagonal_grid
        }
        match[shape](spacing)
    
    def create_square_grid(self, spacing, square=False):
        ret = []
        dist = max(self.WIDTH, self.HEIGHT)
        hd = int(((dist - self.WIDTH) // 2) * square)
        vd = int(((dist - self.HEIGHT) // 2) * square)
        for i in range(2 * self.PULLI_RADIUS + vd, self.WIDTH - vd, spacing):
            ret.append([])
            for j in range(2 * self.PULLI_RADIUS + hd, self.HEIGHT - hd, spacing):
                pulli = self.create_oval(i - self.PULLI_RADIUS, j - self.PULLI_RADIUS, i + self.PULLI_RADIUS, j + self.PULLI_RADIUS, fill="red")
                self.pullis.append((i, j, pulli))
                ret[-1].append((i, j, pulli))
        return ret

    def create_triangular_grid(self, spacing, hex=False):
        dbr = 2 * self.PULLI_RADIUS
        
        i0 = dbr - int(self.HEIGHT / sqrt(3))
        imax = self.WIDTH - dbr

        iind = 0
        for i in range(i0, imax, spacing):
            j0 = dbr
            jmax = 2 * int(self.HEIGHT / sqrt(3)) + dbr
            jind = 0
            for j in range(j0, jmax, spacing):
                x = i + j / 2
                y = j * sqrt(3) / 2
                if not hex or (jind % 3 != iind % 3):
                    pulli = self.create_oval(x - self.PULLI_RADIUS, y - self.PULLI_RADIUS, x + self.PULLI_RADIUS, y + self.PULLI_RADIUS, fill="red")
                    self.pullis.append((x, y, pulli))
                jind += 1

            iind += 1

    def create_hexagonal_grid(self, spacing):
        self.create_triangular_grid(spacing, hex=True)
                
    def save(self):
        G = Grid([])
        for link in self.links:
            p1 = Point(link[0][0], -link[0][1])
            p2 = Point(link[1][0], -link[1][1])
            G.add_point(p1)
            G.add_point(p2)
            G.add_edge(p1, p2)
        fh = asksaveasfile(initialdir="Kolam-Project/saves")
        fh.write(str(G))
        fh.close()

    def load(self):
        regexp = r"^((?:\([0-9e+\-.]+, [0-9e+\-.]+\) )*)-((?: (?:\([0-9e+\-.]+, [0-9e+\-.]+\)) (?:\([0-9e+\-.]+, [0-9e+\-.]+\)))*)$"
        fh = askopenfile(initialdir="Kolam-Project/saves")
        self.clean()
        content = fh.readline()
        match = re.search(regexp, content)
        if match is None:
            print("Invalid file")
            return

        pullis, links = content.split(" - ")
        for pulli in re.findall(r"\([0-9e+\-.]*, [0-9e+\-.]*\)", pullis):
            x, y = pulli[1:-1].split(", ")
            x = float(x)
            y = -float(y)
            pulli = self.create_oval(x - self.PULLI_RADIUS, y - self.PULLI_RADIUS, x + self.PULLI_RADIUS, y + self.PULLI_RADIUS, fill="red")
            self.pullis.append((x, y, pulli))

        for link in re.findall(r"\([0-9e+\-.]*, [0-9e+\-.]*\) \([0-9e+\-.]*, [0-9e+\-.]*\)", links):
            p1, p2 = re.findall(r"\([0-9e+\-.]*, [0-9e+\-.]*\)", link)
            p1 = p1[1:-1].split(", ")
            p2 = p2[1:-1].split(", ")
            p1 = self.get_pulli(float(p1[0]), -float(p1[1]))
            p2 = self.get_pulli(float(p2[0]), -float(p2[1]))
            line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
            self.links.append((p1, p2, line))
    
    def generate(self, density, symmetry, spacing):
        self.clean()
        pullis = self.create_square_grid(spacing, square=True)

        i_amount = len(pullis)
        j_amount = len(pullis[0])

        if symmetry == "None":
            imax = i_amount
            jmax = j_amount
        elif symmetry == "Vertical":
            imax = i_amount // 2 + i_amount % 2
            jmax = j_amount
        elif symmetry == "Horizontal":
            imax = i_amount
            jmax = j_amount // 2 + j_amount % 2
        elif symmetry == "Radial":
            imax = i_amount // 2 + i_amount % 2
            jmax = j_amount // 2
            
        for i in range(imax):
            for j in range(jmax):
                if i != len(pullis) - 1 and random() < density:
                    # Horizontal link
                    p1 = pullis[i][j]
                    p2 = pullis[i + 1][j]
                    line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                    self.links.append((p1, p2, line))
                    if symmetry == "Vertical":
                        p1 = pullis[-i - 1][j]
                        p2 = pullis[-i - 2][j]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                    elif symmetry == "Horizontal":
                        p1 = pullis[i][-j - 1]
                        p2 = pullis[i + 1][-j - 1]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                    elif symmetry == "Radial":
                        p1 = pullis[j][-i - 1]
                        p2 = pullis[j][-i - 2]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                        p1 = pullis[-j - 1][i]
                        p2 = pullis[-j - 1][i + 1]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                        p1 = pullis[-i - 1][-j - 1]
                        p2 = pullis[-i - 2][-j - 1]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))

                                                
                if j != len(pullis[i]) - 1 and random() < density:
                    p1 = pullis[i][j]
                    p2 = pullis[i][j + 1]
                    line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                    self.links.append((p1, p2, line))
                    if symmetry == "Vertical":
                        p1 = pullis[-i - 1][j]
                        p2 = pullis[-i - 1][j + 1]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                    elif symmetry == "Horizontal":
                        p1 = pullis[i][-j - 1]
                        p2 = pullis[i][-j - 2]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                    elif symmetry == "Radial":
                        p1 = pullis[j][-i - 1]
                        p2 = pullis[j + 1][-i - 1]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                        p1 = pullis[-j - 1][i]
                        p2 = pullis[-j - 2][i]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))
                        p1 = pullis[-i - 1][-j - 1]
                        p2 = pullis[-i - 1][-j - 2]
                        line = self.create_line(p1[0], p1[1], p2[0], p2[1], width=2)
                        self.links.append((p1, p2, line))


if __name__ == '__main__':
    KolamApp().run()
