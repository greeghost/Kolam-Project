import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from random import shuffle
import numpy as np # trigonometric functions and pi, linspace for plotting with matplotlib
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

    def __neg__(self):
        return Point(-self.x, -self.y)

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
            next = self.next_vertex(edge[0], edge[1], direction)
            edge = edge[1], next
            direction = 1 - direction

        return [edge[0] for edge in done]

    def plot_knotwork(self, spread, color_each_arc = False):
        plt.scatter([u.x for u in self.points], [u.y for u in self.points])
        spread = spread
        plt.axis("equal")
        todo = [(init, dir) for init in self.edges for dir in self.edges[init]]
        simples = [(init) for init in self.edges if self.edges[init] == []]
        simple_rad = 1
        # colors = [mcolors.XKCD_COLORS["xkcd:" + col] for col in ["purple", "green", "blue", "pink", "brown", "red", "teal", "orange", "magenta", "yellow"]]
        colors = list(mcolors.XKCD_COLORS.values()) # 954 common RGB colors, including some very pale shades
        # shuffle(colors)
        color = 0
        vals_01 = np.linspace(0, 1, 100)

        while todo != []:
            (init, dir) = todo[0]
            done = self.path(init, dir)
            done.append(done[0])
            done.append(done[1])

            clock = False
            for i in range(len(done) - 2):
                u, v, w = done[i], done[i + 1], done[i + 2]
                if ((u, v)) in todo: # needs to be made better
                    todo.remove((u, v))
                mid1 = 0.5 * (u + v)
                mid2 = 0.5 * (v + w)
                dist = (mid1 - mid2).norm()
                if dist <= 1e-14:
                    dist = spread * 3
                p1 = spread * dist * rotate_45(Point.normed(v - u), clockwise = clock)
                p2 = spread * dist * rotate_45(Point.normed(v - w), clockwise = not clock)
                path = lambda t: cubic_bezier(mid1, mid1 + p1, mid2 + p2, mid2, t)
                xs, ys = zip(*[path(t) for t in vals_01])
                plt.plot(xs, ys, color=colors[color % len(colors)], label = f"{mid1} - {mid2}")
                clock = not clock
                color += color_each_arc
            color += 1

        while simples != []:
            u = simples.pop()
            v, w = Point(u.x + simple_rad / 2, u.y), Point(u.x - simple_rad / 2, u.y)
            top = Point(0, 4/3 * simple_rad / 2)
            bottom = Point(0, -4/3 * simple_rad / 2)
            pathtop = lambda t: cubic_bezier(v, v + top, w + top, w, t)
            pathbottom = lambda t: cubic_bezier(v, v + bottom, w + bottom, w, t)
            xs, ys = zip(*[pathtop(t) for t in vals_01])
            plt.plot(xs, ys, color=colors[color % len(colors)])
            color += color_each_arc
            xs, ys = zip(*[pathbottom(t) for t in vals_01])
            plt.plot(xs, ys, color=colors[color % len(colors)])
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
    # Square-ish pattern
    G_squares = Grid([Point(0, 2), Point(0, -2), Point(-2, 0), Point(2, 0), Point(1, 1), Point(1, -1), Point(-1, 1), Point(-1, -1), Point(0, 0)])
    G_squares.add_edge(Point(0, 2), Point(1, 1))
    G_squares.add_edge(Point(0, 2), Point(-1, 1))
    G_squares.add_edge(Point(0, -2), Point(1, -1))
    G_squares.add_edge(Point(0, -2), Point(-1, -1))
    G_squares.add_edge(Point(2, 0), Point(1, 1))
    G_squares.add_edge(Point(2, 0), Point(1, -1))
    G_squares.add_edge(Point(-2, 0), Point(-1, 1))
    G_squares.add_edge(Point(-2, 0), Point(-1, -1))

    # n-branch star
    n = 3
    l_star = [Point(np.cos(2 * i * np.pi / n), np.sin(2 * i * np.pi / n))
        for i in range(n)]
    l_star.append(Point(0, 0))
    G_star = Grid(l_star)
    for i in range(n):
        G_star.add_edge(l_star[i], l_star[n])
        G_star.add_edge(l_star[i], l_star[(i + 1) % n])

    # classic kolam 
    l_classic = [Point(0, 1), Point(0, -1), Point(1, 0), Point(-1, 0)]
    l_classic.append(Point(0, 0))
    l_classic.append(Point(0, 2))
    l_classic.append(Point(1, 1))
    l_classic.append(Point(-1, 1))
    G_classic = Grid(l_classic)
    G_classic.add_edge(Point(0, 1), Point(0, 2))
    G_classic.add_edge(Point(1, 1), Point(0, 1))
    G_classic.add_edge(Point(-1, 1), Point(0, 1))
    for i in range(4):
        G_classic.add_edge(l_classic[i], l_classic[4])
    

    # G_squares.plot_knotwork(0.75)
    # plt.show()
    # G_star.plot_knotwork(1)
    # plt.show()
    # G_classic.plot_knotwork(2)
    # plt.show()

    # Non-classic test pattern
    u1 = Point(1, 0)
    u2 = Point(np.sin(np.pi / 6), np.cos(np.pi / 6))

    l_hex1 = [u1, u2, u2 - u1, -u1, -u2, u1 - u2, Point(0, 0)]
    G_hex1 = Grid(l_hex1 + [2 * u1, -2 * u2, 2 * (u2 - u1)])
    G_hex1.add_edge(u1, u2)
    G_hex1.add_edge(u2, u2 - u1)
    G_hex1.add_edge(u2 - u1, -u1)
    G_hex1.add_edge(-u1, -u2)
    G_hex1.add_edge(-u2, u1 - u2)
    G_hex1.add_edge(u1 - u2, u1)

    G_hex1.add_edge(u1, 2 * u1)
    G_hex1.add_edge(-u2, -2 * u2)
    G_hex1.add_edge(u2 - u1, 2 * (u2 - u1))

    G_hex1.plot_knotwork(2/3)
    G_hex1.plot()
    plt.show()