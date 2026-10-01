""" Python implementation of
    Algorithm for Automatically Fitting Digitized Curves
    by Philip J. Schneider
    "Graphics Gems", Academic Press, 1990
"""
from __future__ import print_function
#from numpy import *
import numpy as np
from . import bezier


# Fit one (ore more) Bezier curves to a set of points
def fitCurve(points, maxError):
    leftTangent = normalize(points[1] - points[0])
    rightTangent = normalize(points[-2] - points[-1])
    return fitCubic(points, leftTangent, rightTangent, maxError)


def fitCubic(points, leftTangent, rightTangent, error):
    # Use heuristic if region only has two points in it
    if (len(points) == 2):
        dist = np.linalg.norm(points[0] - points[1]) / 3.0
        bezCurve = [points[0], points[0] + leftTangent * dist, points[1] + rightTangent * dist, points[1]]
        return [bezCurve]

    # Parameterize points, and attempt to fit curve
    u = chordLengthParameterize(points)
    bezCurve = generateBezier(points, u, leftTangent, rightTangent)
    # Find max deviation of points to fitted curve
    maxError, splitPoint = computeMaxError(points, bezCurve, u)
    if maxError < error:
        return [bezCurve]

    # If error not too large, try some reparameterization and iteration
    if maxError < error**2:
        for i in range(20):
            uPrime = reparameterize(bezCurve, points, u)
            bezCurve = generateBezier(points, uPrime, leftTangent, rightTangent)
            maxError, splitPoint = computeMaxError(points, bezCurve, uPrime)
            if maxError < error:
                return [bezCurve]
            u = uPrime

    # Fitting failed -- split at max error point and fit recursively
    beziers = []
    centerTangent = normalize(points[splitPoint-1] - points[splitPoint+1])
    beziers += fitCubic(points[:splitPoint+1], leftTangent, centerTangent, error)
    beziers += fitCubic(points[splitPoint:], -centerTangent, rightTangent, error)

    return beziers

def generateBezier(points, parameters, leftTangent, rightTangent):
    parameters = np.asarray(parameters)

    p0 = points[0]
    p3 = points[-1]

    one_minus_u = 1.0 - parameters

    a0_scale = 3.0 * one_minus_u**2 * parameters
    a1_scale = 3.0 * one_minus_u * parameters**2

    A0 = a0_scale[:, None] * leftTangent
    A1 = a1_scale[:, None] * rightTangent

    C00 = np.sum(A0 * A0)
    C01 = np.sum(A0 * A1)
    C11 = np.sum(A1 * A1)

    base_curve = bezier.q(
        np.array([p0, p0, p3, p3]),
        parameters
    )

    tmp = points - base_curve

    X0 = np.sum(A0 * tmp)
    X1 = np.sum(A1 * tmp)

    det = C00 * C11 - C01 * C01

    if det == 0:
        alpha_l = 0.0
        alpha_r = 0.0
    else:
        alpha_l = (X0 * C11 - X1 * C01) / det
        alpha_r = (C00 * X1 - C01 * X0) / det

    segLength = np.linalg.norm(p0 - p3)
    epsilon = 1.0e-6 * segLength

    if alpha_l < epsilon or alpha_r < epsilon:
        alpha_l = segLength / 3.0
        alpha_r = segLength / 3.0

    return np.array([
        p0,
        p0 + leftTangent * alpha_l,
        p3 + rightTangent * alpha_r,
        p3
    ])

def reparameterize(bez, points, parameters):
    parameters = np.asarray(parameters)

    q = bezier.q(bez, parameters)
    qprime = bezier.qprime(bez, parameters)
    qprimeprime = bezier.qprimeprime(bez, parameters)

    d = q - points

    numerator = np.sum(
        d * qprime,
        axis=1
    )

    denominator = np.sum(
        qprime * qprime + d * qprimeprime,
        axis=1
    )

    new_parameters = parameters.copy()

    valid = denominator != 0.0

    new_parameters[valid] = (
        parameters[valid]
        - numerator[valid] / denominator[valid]
    )

    return new_parameters

'''
def newtonRaphsonRootFind(bez, point, u):
    """
       Newton's root finding algorithm calculates f(x)=0 by reiterating
       x_n+1 = x_n - f(x_n)/f'(x_n)

       We are trying to find curve parameter u for some point p that minimizes
       the distance from that point to the curve. Distance point to curve is d=q(u)-p.
       At minimum distance the point is perpendicular to the curve.
       We are solving
       f = q(u)-p * q'(u) = 0
       with
       f' = q'(u) * q'(u) + q(u)-p * q''(u)

       gives
       u_n+1 = u_n - |q(u_n)-p * q'(u_n)| / |q'(u_n)**2 + q(u_n)-p * q''(u_n)|
    """
    d = bezier.q(bez, u)-point
    numerator = (d * bezier.qprime(bez, u)).sum()
    denominator = (bezier.qprime(bez, u)**2 + d * bezier.qprimeprime(bez, u)).sum()

    if denominator == 0.0:
        return u
    else:
        return u - numerator/denominator
'''

def chordLengthParameterize(points):
    delta = np.diff(points, axis=0)

    distances = np.linalg.norm(delta, axis=1)

    u = np.concatenate((
        [0.0],
        np.cumsum(distances)
    ))

    if u[-1] != 0:
        u /= u[-1]

    return u


def computeMaxError(points, bez, parameters):
    curve_points = bezier.q(bez, parameters)

    diff = curve_points - points

    distances = np.sum(diff * diff, axis=1)

    splitPoint = np.argmax(distances)
    maxDist = distances[splitPoint]

    return maxDist, splitPoint


def normalize(v):
    return v / np.linalg.norm(v)

