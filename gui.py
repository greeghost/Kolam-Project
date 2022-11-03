import tkinter as tk
from math import sqrt, ceil, floor
from mercat import Grid, Point
import matplotlib.pyplot as plt

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
        self.l1 = tk.Label(self, text="method")
        self.e1 = tk.StringVar(self)
        self.e1.set("bezier")
        self.om1 = tk.OptionMenu(self, self.e1, *["bezier", "hermite"])
        self.b4.grid(row=3, column=0)
        self.l1.grid(row=3, column=1)
        self.om1.grid(row=3, column=2)

        self.b5 = tk.Button(self, text = "Gridify", command = self.gridify)
        self.l2 = tk.Label(self, text="spacing")
        self.e2 = tk.Entry(self)
        self.e2.insert(0, "150")
        self.e3 = tk.StringVar(self)
        self.e3.set("square")
        self.l3 = tk.Label(self, text="shape")
        self.om2 = tk.OptionMenu(self, self.e3, *["square", "triangular"])
        self.b5.grid(row=4, column=0)
        self.l2.grid(row=4, column=1)
        self.e2.grid(row=4, column=2)
        self.l3.grid(row=5, column=1)
        self.om2.grid(row=5, column=2)

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

    def gridify(self):
        spacing = self.e2.get()
        shape = self.e3.get()
        if spacing != "":
            try:
                spacing = int(spacing)
                self.master.pb.create_pulli_grid(shape, spacing)
            except ValueError:
                print("Invalid spacing")
        else:
            self.master.pb.create_pulli_grid(shape)

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
    
    def get_pulli(self, event):
        for pulli in self.pullis[::-1]:
            if sqrt((pulli[0] - event.x) ** 2 + (pulli[1] - event.y) ** 2) <= self.PULLI_RADIUS:
                return pulli
        return None

    def add_pulli(self, event):
        x = event.x
        y = event.y
        pulli = self.create_oval(x - self.PULLI_RADIUS, y - self.PULLI_RADIUS, x + self.PULLI_RADIUS, y + self.PULLI_RADIUS, fill="red")
        self.pullis.append((x, y, pulli))

    def create_pulli_grid(self, shape, spacing = 100):
        match = {
            "square": self.create_square_grid,
            "triangular": self.create_triangular_grid
        }
        match[shape](spacing)
    
    def create_square_grid(self, spacing):
        print("square")
        for i in range(2 * self.PULLI_RADIUS, self.WIDTH, spacing):
            for j in range(2 * self.PULLI_RADIUS, self.HEIGHT, spacing):
                pulli = self.create_oval(i - self.PULLI_RADIUS, j - self.PULLI_RADIUS, i + self.PULLI_RADIUS, j + self.PULLI_RADIUS, fill="red")
                self.pullis.append((i, j, pulli))

    def create_triangular_grid(self, spacing):
        print("triangular")
        dbr = 2 * self.PULLI_RADIUS
        
        i0 = dbr - int(self.HEIGHT / sqrt(3))
        imax = self.WIDTH - dbr
        
        for i in range(i0, imax, spacing):
            if i < dbr:
                j0 = ceil(2 * (dbr - i) / spacing) * spacing + dbr
            else:
                j0 = dbr
            if i > imax + i0:
                jmax = 2 * (imax - i) + dbr
            else:
                jmax = 2 * int(self.HEIGHT / sqrt(3)) + dbr

            for j in range(j0, jmax, spacing):
                x = i + j / 2
                y = j * sqrt(3) / 2
                pulli = self.create_oval(x - self.PULLI_RADIUS, y - self.PULLI_RADIUS, x + self.PULLI_RADIUS, y + self.PULLI_RADIUS, fill="red")
                self.pullis.append((x, y, pulli))





    def remove_pulli(self, event):
        pulli = self.get_pulli(event)
        if pulli is None:
            return
        self.pullis.remove(pulli)
        self.delete(pulli[2])
        for link in self.links[:]: # [:] to iterate over a copy since we remove element of self.links on the fly.
            if pulli in link:
                self.delete(link[2])
                self.links.remove(link)

    def add_link(self, event):
        pulli = self.get_pulli(event)
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
        pulli = self.get_pulli(event)
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
        for pulli in self.pullis:
            G.add_point(Point(pulli[0], -pulli[1]))
        for link in self.links:
            p1 = Point(link[0][0], -link[0][1])
            p2 = Point(link[1][0], -link[1][1])
            G.add_edge(p1, p2)
        G.plot_knotwork(0.75, 1.25, interp=fun)
        G.plot()
        plt.show()



if __name__ == '__main__':
    KolamApp().run()
