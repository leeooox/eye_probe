import numpy as np
cimport numpy as np
cimport cython


@cython.boundscheck(False)
cdef int bres_segment_count(unsigned x0, unsigned y0,
                            unsigned x1, unsigned y1,
                            np.ndarray[np.int32_t, ndim=2] grid):
    """Bresenham's algorithm.

    See http://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm
    """

    cdef unsigned nrows, ncols
    cdef int e2, sx, sy, err
    cdef int dx, dy

    nrows = grid.shape[0]
    ncols = grid.shape[1]

    if x1 > x0:
        dx = x1 - x0
    else:
        dx = x0 - x1
    if y1 > y0:
        dy = y1 - y0
    else:
        dy = y0 - y1

    sx = 0
    if x0 < x1:
        sx = 1
    else:
        sx = -1
    sy = 0
    if y0 < y1:
        sy = 1
    else:
        sy = -1

    err = dx - dy

    while True:
        # Note: this test occurs before increment the
        # grid value, so we don't count the last point.
        if x0 == x1 and y0 == y1:
            break

        if (x0 < nrows) and (y0 < ncols):
            grid[x0, y0] += 1

        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

    return 0


def bres_curve_count(np.ndarray[np.int32_t, ndim=1] x,
                     np.ndarray[np.int32_t, ndim=1] y,
                     np.ndarray[np.int32_t, ndim=2] grid):
    cdef unsigned k
    cdef int x0, y0, x1, y1

    for k in range(len(x)-1):
        x0 = x[k]
        y0 = y[k]
        x1 = x[k+1]
        y1 = y[k+1]
        bres_segment_count(x0, y0, x1, y1, grid)
    if 0 <= x1 < grid.shape[0] and 0 <= y1 < grid.shape[1]:
        grid[x1, y1] += 1