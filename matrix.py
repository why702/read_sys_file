import math

import numpy as np


def rotate_shift_matrix(angle, dx, dy):
    return np.array([[math.cos(angle), -math.sin(angle), dx], [math.sin(angle), math.cos(angle), dy], [0, 0, 1]])


if __name__ == '__main__':
    angle = 90
    dx = 1
    dy = 2
    angle = math.pi * angle / 180
    print(rotate_shift_matrix(angle, dx, dy))
    A = np.array([3, 2, 1])
    print(A)
    print(rotate_shift_matrix(angle, 0, 0).dot(A))
    B = rotate_shift_matrix(angle, dx, dy).dot(A)
    print(B)
    C = rotate_shift_matrix(0, -dx, -dy).dot(B)
    print(C)
    print(rotate_shift_matrix(-angle, 0, 0))
    D = rotate_shift_matrix(-angle, 0, 0).dot(C)
    print(D)
    E = rotate_shift_matrix(-angle, -dx, -dy).dot(rotate_shift_matrix(angle, dx, dy))
    print(E)
    F = E.dot(A)
    print(F)
    G = np.linalg.inv(rotate_shift_matrix(angle, dx, dy))
    print(G)
    H = G.dot(rotate_shift_matrix(angle, dx, dy).dot(A))
    print(H)
    I = rotate_shift_matrix(-angle, 0, 0).dot(rotate_shift_matrix(0, -dx, -dy).dot(rotate_shift_matrix(angle, dx, dy).dot(A)))
    print(H)