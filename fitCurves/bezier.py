from __future__ import print_function
import numpy as np


def _prepare_t(t):
    t = np.asarray(t, dtype=float)

    if t.ndim == 0:
        return t

    return t[:, None]


def q(ctrlPoly, t):
    t = _prepare_t(t)

    return (
        (1.0 - t)**3 * ctrlPoly[0]
        + 3.0 * (1.0 - t)**2 * t * ctrlPoly[1]
        + 3.0 * (1.0 - t) * t**2 * ctrlPoly[2]
        + t**3 * ctrlPoly[3]
    )


def qprime(ctrlPoly, t):
    t = _prepare_t(t)

    return (
        3.0 * (1.0 - t)**2 * (ctrlPoly[1] - ctrlPoly[0])
        + 6.0 * (1.0 - t) * t * (ctrlPoly[2] - ctrlPoly[1])
        + 3.0 * t**2 * (ctrlPoly[3] - ctrlPoly[2])
    )


def qprimeprime(ctrlPoly, t):
    t = _prepare_t(t)

    return (
        6.0 * (1.0 - t)
        * (ctrlPoly[2] - 2 * ctrlPoly[1] + ctrlPoly[0])
        + 6.0 * t
        * (ctrlPoly[3] - 2 * ctrlPoly[2] + ctrlPoly[1])
    )