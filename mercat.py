import matplotlib.pyplot as plt
import numpy as np
from math import sqrt

LEFT = 0
RIGHT = 1

class Point(object):
    """Basically a glorified 2D vector."""

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2)
    
    def normed(self):
        return Point(self.x / self.norm(), self.y / self.norm())

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, other):
        if isinstance(other, Point):
            return (self.x == other.x) and (self.y == other.y)
        return False
    
    def __str__(self):
        return f"({self.x:.2g}, {self.y:.2g})"
    
    def __repr__(self):
        return f"Point({self.x:.2g}, {self.y:.2g})"

    def __add__(self, other):
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        raise TypeError(f"Adding Point with object of incompatible type : {other}")

    def __sub__(self, other):
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        raise TypeError(f"Adding Point with object of incompatible type : {other}")

    def __mul__(self, other):
        if isinstance(other, float) or isinstance(other, int):
            return Point(self.x * other, self.y * other)
        raise TypeError(f"Multiplying Point with object of incompatible type : {other}")        

    def __rmul__(self, other):
        return self.__mul__(other)


class Grid(object):
    def __init__(self, point_list):
        self.points = point_list
        self.edges = {p : [] for p in point_list}

    def add_point(self, u):
        self.points.append(u)
        self.edges[u] = []

    def has_edge(self, u, v):
        return v in self.edges[u]

    def add_edge(self, u, v):
        self.edges[u].append(v)
        self.edges[v].append(u)

    def next_vertex(self, u, v, direction = RIGHT):
        assert self.has_edge(u, v)
        if len(self.edges[v]) == 1:
            return u

        vu = Point.normed(Point(u.x - v.x, u.y - v.y))
        min_angle = None
        vert = None

        for w in self.edges[v]:
            if w == u:
                continue
            vw = Point.normed(Point(w.x - v.x, w.y - v.y))
            det = (vu.x * vw.y - vu.y * vw.x)
            dot = (vu.x * vw.x + vu.y * vw.y)
            angle = np.arccos(dot)
            if det < 0:
                angle = 2 * np.pi - angle

            if min_angle is None:
                min_angle = angle
                vert = w

            elif direction == RIGHT and angle <= min_angle:
                min_angle = angle
                vert = w
            
            elif direction == LEFT and angle >= min_angle:
                min_angle = angle
                vert = w

        return vert

    def path(self, u, v):
        done = []
        starting_edge = (u, v)
        edge = starting_edge
        direction = RIGHT
        while (edge != starting_edge) or done == []:
            done.append(edge)
            next = g.next_vertex(edge[0], edge[1], direction)
            edge = edge[1], next
            direction = 1 - direction

        return [edge[0] for edge in done]

    def plot_knotwork(self, spread):
        spread = spread
        plt.axis("equal")
        todo = [(init, dir) for init in self.edges for dir in self.edges[init]]
        colors = ["red", "green", "blue", "yellow", "orange", "lime", "purple", "pink"]
        vals_01 = np.linspace(0, 1, 100)

        while todo != []:
            (init, dir) = todo[0]
            done = g.path(init, dir)
            done.append(done[0])
            done.append(done[1])

            color = 0
            clock = False
            for i in range(len(done) - 2):
                u, v, w = done[i], done[i + 1], done[i + 2]
                if ((u, v)) in todo: # needs to be made better
                    todo.remove((u, v))
                mid1 = 0.5 * (u + v)
                mid2 = 0.5 * (v + w)
                dist = (mid1 - mid2).norm()
                if dist <= 1e-14:
                    dist = spread / 2
                p1 = spread * dist * rotate_45(Point.normed(v - u), clockwise = clock)
                p2 = spread * dist * rotate_45(Point.normed(v - w), clockwise = not clock)
                path = lambda t: cubic_bezier(mid1, mid1 + p1, mid2 + p2, mid2, t)
                xs, ys = zip(*[path(t) for t in vals_01])
                plt.plot(xs, ys, color=colors[color % len(colors)], label = f"{mid1} - {mid2}")
                clock = not clock
            color += 1

    def plot(self):
        plt.axis("equal")
        plt.scatter([u.x for u in self.points], [u.y for u in self.points])
        done = []
        for u in self.edges:
            for v in self.edges[u]:
                if v not in done:
                    plt.plot((u.x, v.x), (u.y, v.y), color="grey")
            done.append(u)


def cubic_bezier(u, v, w, p, t):
    # u, v, w, p : control points
    # t : [0-1], point on which to evaluate the function
    val1 = (1 - t) ** 3 * u
    val2 = 3 * t * (1 - t) ** 2 * v
    val3 = 3 * (1 - t) * t ** 2 * w
    val4 = t ** 3 * p
    res = val1 + val2 + val3 + val4
    return res.x, res.y

def rotate_45(p, clockwise=True):
    b = sqrt(2) / 2
    if clockwise:
        return Point(b * (p.x - p.y), b * (p.x + p.y))
    else:
        return Point(b * (p.x + p.y), b * (p.y - p.x))

if __name__ == "__main__":
    # # test with a n-branch triangular star idk what to call that
    n = 5

    l = [Point(np.cos(2 * i * np.pi / n), np.sin(2 * i * np.pi / n))
        for i in range(n)]
    l.append(Point(0, 0))
    g = Grid(l)
    for i in range(n):
        g.add_edge(l[i], l[n])
        g.add_edge(l[i], l[(i + 1) % n])


    plt.subplot(121)
    g.plot_knotwork(.5)

    plt.subplot(122)
    g.plot()
    plt.show()


    # bezier curve illustration
    # ts = np.linspace(0, 1, 100)
    # init, dir = Point(-1, 0), Point(1, 0)
    # c1, c2 = Point(1, 1), Point(-1, 1) # medium
    # c3, c4 = 5 * c1, 5 * c2 # big
    # c5, c6 = .3 * c1, .3 * c2 # small

    # f3 = lambda t: cubic_bezier(init, c5, c6, dir, t)
    # f1 = lambda t: cubic_bezier(init, c1, c2, dir, t)
    # f2 = lambda t: cubic_bezier(init, c3, c4, dir, t)

    # x3s, y3s = zip(*[f3(t) for t in ts])
    # x1s, y1s = zip(*[f1(t) for t in ts])
    # x2s, y2s = zip(*[f2(t) for t in ts])

    # fig, axs = plt.subplots(3)
    
    # axs[0].plot(x3s, y3s)
    # axs[1].plot(x1s, y1s)
    # axs[2].plot(x2s, y2s)

    # plt.axis("equal")
    # plt.show()



    # # classic kolam illustration 
    # n = 4

    # l = [Point(0, 1), Point(0, -1), Point(1, 0), Point(-1, 0)]
    # l.append(Point(0, 0))
    # l.append(Point(0, 2))
    # l.append(Point(1, 1))
    # l.append(Point(-1, 1))

    # g = Grid(l)
    # g.add_edge(Point(0, 1), Point(0, 2))
    # g.add_edge(Point(1, 1), Point(0, 1))
    # g.add_edge(Point(-1, 1), Point(0, 1))
    # for i in range(n):
    #     g.add_edge(l[i], l[n])
    #     # g.add_edge(l[i], l[(i + 1) % n])


    # # g.plot()
    # plt.subplot(121)
    # g.plot_knotwork(2)

    # plt.subplot(122)
    # g.plot()
    # plt.show()
