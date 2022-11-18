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
    
    def __le__(self, other):
        if isinstance(other, Point):
            return (self.x, self.y) <= (other.x, other.y)
        raise TypeError(f"Comparing Point with object of incompatible type : {other}")

    def __lt__(self, other):
        if isinstance(other, Point):
            return (self.x, self.y) < (other.x, other.y)
        raise TypeError(f"Comparing Point with object of incompatible type : {other}")

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
        if u in self.points:
            return
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

    def path(self, u, v, side):
        done = []
        starting_edge = (u, v)
        edge = starting_edge
        direction = side
        iter = 0
        while edge != starting_edge or iter % 2 == 1 or iter == 0:
            done.append(edge)
            next = self.next_vertex(edge[0], edge[1], direction)
            edge = edge[1], next
            direction = 1 - direction
            iter += 1

        return [edge[0] for edge in done]

    def plot_knotwork(self, spread, loop_size, color_each_arc = False, color_each_thread = True, interp = "bezier"):
        if interp == "hermite":
            fun = cubic_hermite
        else:
            fun = cubic_bezier
        plt.scatter([u.x for u in self.points], [u.y for u in self.points])
        plt.axis("equal")
        plt.axis('off')
        todo = {(init, dir, side) for init in self.edges for dir in self.edges[init] for side in (RIGHT, )}
        # simples = [(init) for init in self.edges if self.edges[init] == []]
        # simple_rad = 1
        colors = [mcolors.XKCD_COLORS["xkcd:" + col] for col in ["purple", "green", "blue", "pink", "brown", "red", "teal", "orange", "magenta", "yellow"]]
        # colors = list(mcolors.XKCD_COLORS.values()) # 954 common RGB colors, including some very pale shades
        shuffle(colors)
        color = 0
        vals_01 = np.linspace(0, 1, 100)

        while todo != set():
            (init, dir, side) = todo.pop()
            todo.add((init, dir, side))
            done = self.path(init, dir, side)
            done.append(done[0])
            done.append(done[1])

            clock = False
            starting_side = side
            current_side = starting_side
            for i in range(len(done) - 2):
                u, v, w = done[i], done[i + 1], done[i + 2]
                if ((u, v, current_side)) in todo: # needs to be made better
                    todo.remove((u, v, current_side))
                else:
                    # print(f"problem: {(u, v, current_side)} not in todo")
                    pass
                current_side = 1 - current_side
                mid1 = 0.5 * (u + v)
                mid2 = 0.5 * (v + w)
                dist = (mid1 - mid2).norm()
                if dist <= 1e-14:
                    dist = loop_size / spread * (v - u).norm()
                n1 = rotate_45(Point.normed(v - u), clockwise = clock)
                p1 = spread * dist * n1
                n2 = rotate_45(Point.normed(v - w), clockwise = not clock)
                p2 = spread * dist * n2
                cos = n1.x * n2.x + n1.y * n2.y
                arc = lambda t: fun(mid1, mid1 + p1, mid2 + p2, mid2, t, cos=cos)
                xs, ys = zip(*[arc(t) for t in vals_01])
                plt.plot(xs, ys, color=colors[color % len(colors)], label = f"{mid1} - {mid2}")
                clock = not clock
                color += color_each_arc
            color += color_each_thread

        # while simples != []:
        #     u = simples.pop()
        #     v, w = Point(u.x + simple_rad / 2, u.y), Point(u.x - simple_rad / 2, u.y)
        #     top = Point(0, 4/3 * simple_rad / 2)
        #     bottom = Point(0, -4/3 * simple_rad / 2)
        #     arctop = lambda t: fun(v, v + top, w + top, w, t)
        #     arcbottom = lambda t: fun(v, v + bottom, w + bottom, w, t)
        #     xs, ys = zip(*[arctop(t) for t in vals_01])
        #     plt.plot(xs, ys, color=colors[color % len(colors)])
        #     color += color_each_arc
        #     xs, ys = zip(*[arcbottom(t) for t in vals_01])
        #     plt.plot(xs, ys, color=colors[color % len(colors)])
        #     color += 1

    def plot(self):
        plt.axis("equal")
        plt.axis('off')
        plt.scatter([u.x for u in self.points], [u.y for u in self.points])
        done = []
        for u in self.edges:
            for v in self.edges[u]:
                if v not in done:
                    plt.plot((u.x, v.x), (u.y, v.y), color="grey")
            done.append(u)
    
    def __str__(self):
        """Convert a Grid object to a string representation."""
        points = " ".join([str(p) for p in self.points])
        edges = " ".join([f"{str(u)} {str(v)}" for u in self.edges for v in self.edges[u] if u < v])
        print (f"{points} - {edges}")
        return f"{points} - {edges}"


def cubic_bezier(u, v, w, p, t, **kwargs):
    # u, v, w, p : control points
    # t : [0-1], point on which to evaluate the function
    cos = kwargs.get("cos", 1)
    val1 = (1 - t) ** 3 * u
    val2 = 3 * t * (1 - t) ** 2 * (u + (1 + cos) * (v - u))
    val3 = 3 * (1 - t) * t ** 2 * (p + (1 + cos) * (w - p))
    val4 = t ** 3 * p
    res = val1 + val2 + val3 + val4
    return res.x, res.y

def cubic_hermite(u, v, w, p, t, **kwargs):
    # u, v, w, p : control points
    # t : [0-1], point on which to evaluate the function
    cos = kwargs.get("cos", 1)
    val1 = (2 * t ** 3 - 3 * t ** 2 + 1) * u
    val2 = 4 * (t ** 3 - 2 * t ** 2 + t) * ((1 + cos) * (v - u))
    val3 = 4 * (t ** 3 - t ** 2) * ((1 + cos) * (p - w))
    val4 = (-2 * t ** 3 + 3 * t ** 2) * p
    res = val1 + val2 + val3 + val4
    return res.x, res.y

def rotate_45(p, clockwise=True):
    b = sqrt(2) / 2
    if clockwise:
        return Point(b * (p.x - p.y), b * (p.x + p.y))
    else:
        return Point(b * (p.x + p.y), b * (p.y - p.x))

if __name__ == "__main__":
    l_classic = [Point(0, 1), Point(0, -1), Point(1, 0), Point(-1, 0), Point(0, 0), Point(0, 2), Point(1, 1), Point(-1, 1)]
    G_classic = Grid(l_classic)
    for i in range(4):
        G_classic.add_edge(l_classic[i], l_classic[4])
        G_classic.add_edge(l_classic[0], l_classic[4 + i])

    # G_classic.plot_knotwork(1, 2, color_each_arc=True, interp="bezier")
    # plt.show()

    l_problem1 = [Point(0, 1), Point(0, 0), Point(1, 0), Point(1, 1)]
    l_problem2 = [Point(1, 5), Point(1, 4), Point(2, 4), Point(2, 5)]
    G_problem = Grid(l_problem1 + l_problem2 + [Point(1, 2), Point(1, 3)])
    for i in range(4):
        G_problem.add_edge(l_problem1[i], l_problem1[(i + 1) % 4])
        G_problem.add_edge(l_problem2[i], l_problem2[(i + 1) % 4])
    G_problem.add_edge(Point(1, 1), Point(1, 2))
    G_problem.add_edge(Point(1, 2), Point(1, 3))
    G_problem.add_edge(Point(1, 3), Point(1, 4))

    G_problem.plot_knotwork(1, 2, color_each_arc=False, interp="bezier")
    plt.show()