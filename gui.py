import tkinter as tk
from math import sqrt
from mercat import Grid, Point
import matplotlib.pyplot as plt

class KolamApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        # self.configure(width = 1200)
        # self.configure(height = 600)
        super().__init__(*args, **kwargs)

        self.pb = PulliBoard(self)
        self.pb.pack(side = "right", expand = True)

        self.cp = ControlPanel(self)
        self.cp.pack(side = "left", fill = "x", expand = True)

    def run(self):
        self.mainloop()

class ControlPanel(tk.Canvas):
    def __init__(self, *args, **kwargs):
        kwargs["highlightthickness"] = 10
        super().__init__(*args, **kwargs)
        b1 = tk.Button(self, text = "Add/remove pulli", command = self.mouse_preset_1)
        b1.pack()
        b2 = tk.Button(self, text = "Add/remove link", command = self.mouse_preset_2)
        b2.pack()
        b3 = tk.Button(self, text = "Clear Board", command = self.clean)
        b3.pack()
        b4 = tk.Button(self, text = "Apply Mercat Algorithm", command = self.mercatize)
        b4.pack()
    
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
        self.master.pb.mercatize()

class PulliBoard(tk.Canvas):
    PULLI_RADIUS = 10
    ADD_LINK = 1
    RM_LINK = 2

    def __init__(self, *args, **kwargs):
        self.pullis = []
        self.links = []
        self.selected_pulli = None
        self.last_event = self.ADD_LINK
        kwargs["width"] = 960
        kwargs["height"] = 540
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

    def remove_pulli(self, event):
        pulli = self.get_pulli(event)
        if pulli is None:
            return
        self.pullis.remove(pulli)
        self.delete(pulli[2])
        for link in self.links[:]: # [:] to iterate over a copy since we remove element of self.links on the fly.
            print(pulli, link)
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
            for link in self.links:
                if link[0] == p1 and link[1] == p2:
                    break
            else:
                line = self.create_line(p1[0], p1[1], p2[0], p2[1])
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
    
    def mercatize(self):
        G = Grid([])
        for pulli in self.pullis:
            G.add_point(Point(pulli[0], -pulli[1]))
        for link in self.links:
            p1 = Point(link[0][0], -link[0][1])
            p2 = Point(link[1][0], -link[1][1])
            G.add_edge(p1, p2)
        G.plot_knotwork(.5, 1)
        G.plot()
        plt.show()



if __name__ == '__main__':
    KolamApp().run()
