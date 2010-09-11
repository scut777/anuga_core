#!/usr/bin/env python

import unittest
import sys
from math import sqrt


from anuga import Domain
from anuga import rectangular_cross

from anuga_parallel.distribute_mesh import pmesh_divide_metis
from anuga_parallel.distribute_mesh import build_submesh
from anuga_parallel.distribute_mesh import submesh_full, submesh_ghost, submesh_quantities
from anuga_parallel.distribute_mesh import extract_hostmesh, rec_submesh, send_submesh

import numpy as num


def topography(x,y): 
    return -x/2


def xcoord(x,y):
    return x

def ycoord(x,y):
    return y



class Test_Distribute_Mesh(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass



    def test_pmesh_1(self):
        """
        test distributing with just one processor
        """
        
        points, vertices, boundary = rectangular_cross(2,2)


        true_points = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0], [0.5, 0.0], [0.5, 0.5], [0.5, 1.0], [1.0, 0.0], [1.0, 0.5], [1.0, 1.0], [0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]

        true_vertices = [[0, 9, 1], [3, 9, 0], [4, 9, 3], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]]


        assert num.allclose(points,true_points)
        assert num.allclose(vertices,true_vertices)

        domain = Domain(points, vertices, boundary)


        domain.set_quantity('elevation', topography) # Use function for elevation
        domain.set_quantity('friction', 0.0)         # Constant friction 
        domain.set_quantity('stage', expression='elevation') # Dry initial stage
        domain.set_quantity('xmomentum', expression='friction + 2.0') # 
        domain.set_quantity('ymomentum', ycoord) #


        #print domain.quantities['ymomentum'].centroid_values
 
        nodes, triangles, boundary, triangles_per_proc, quantities = pmesh_divide_metis(domain,1)


        true_nodes = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0], [0.5, 0.0], [0.5, 0.5], [0.5, 1.0], [1.0, 0.0], [1.0, 0.5], [1.0, 1.0], [0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]

        true_triangles = [[0, 9, 1], [3, 9, 0], [4, 9, 3], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]]


        assert num.allclose(nodes,true_nodes)
        assert num.allclose(triangles,true_triangles)


        assert num.allclose(triangles_per_proc,[16])
        
        

    def test_pmesh_2(self):
        """
        Test 2 way pmesh
        """
        points, vertices, boundary = rectangular_cross(2,2)


        true_points = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0], [0.5, 0.0], [0.5, 0.5], [0.5, 1.0], [1.0, 0.0], [1.0, 0.5], [1.0, 1.0], [0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]

        true_vertices = [[0, 9, 1], [3, 9, 0], [4, 9, 3], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]]


        assert num.allclose(points,true_points)
        assert num.allclose(vertices,true_vertices)

        domain = Domain(points, vertices, boundary)


        domain.set_quantity('elevation', topography) # Use function for elevation
        domain.set_quantity('friction', 0.0)         # Constant friction 
        domain.set_quantity('stage', expression='elevation') # Dry initial stage
        domain.set_quantity('xmomentum', expression='friction + 2.0') # 
        domain.set_quantity('ymomentum', ycoord) #


        #print domain.quantities['ymomentum'].centroid_values
 
        nodes, triangles, boundary, triangles_per_proc, quantities = pmesh_divide_metis(domain,2)


        true_nodes = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0], [0.5, 0.0], [0.5, 0.5], [0.5, 1.0], [1.0, 0.0], [1.0, 0.5], [1.0, 1.0], [0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]


        true_triangles = [[0, 9, 1], [3, 9, 0], [4, 9, 3], [1, 9, 4], [4, 10, 1], [3, 11, 4], [4, 11, 7], [4, 12, 5], [1, 10, 2], [5, 10, 4], [2, 10, 5], [6, 11, 3], [7, 11, 6], [7, 12, 4], [8, 12, 7], [5, 12, 8]]


        assert num.allclose(nodes,true_nodes)
        assert num.allclose(triangles,true_triangles)


        assert num.allclose(triangles_per_proc,[8,8])


            
    def test_build_submesh_3(self):
        """
        Test 3 way build_submesh
        """

        nodes = [[0.0, 0.0], [0.0, 0.5], [0.0, 1.0], [0.5, 0.0], [0.5, 0.5], [0.5, 1.0], [1.0, 0.0], [1.0, 0.5], [1.0, 1.0], [0.25, 0.25], [0.25, 0.75], [0.75, 0.25], [0.75, 0.75]]


        triangles = [[4, 9, 3], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8], [0, 9, 1], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5], [3, 9, 0], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7]]


        edges = {(13, 1): 'bottom', (7, 1): 'left', (3, 1): 'right', (14, 1): 'right', (11, 1): 'bottom', (10, 1): 'top', (5, 1): 'left', (4, 1): 'top'}

        triangles_per_proc = [5, 6, 5]


        quantities = {'stage': num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ],
       [-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.   , -0.125, -0.   ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]),  'elevation': num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ],
       [-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.   , -0.125, -0.   ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]),  'ymomentum': num.array([[ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ],
       [ 0.  ,  0.25,  0.5 ],
       [ 0.5 ,  0.25,  0.5 ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.  ,  0.25,  0.5 ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.5 ]]),  'friction': num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]]),  'xmomentum': num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]])}


        
        true_submesh = {'full_boundary': [{(3, 1): 'right', (4, 1): 'top'}, {(5, 1): 'left', (10, 1): 'top', (7, 1): 'left'}, {(13, 1): 'bottom', (14, 1): 'right', (11, 1): 'bottom'}],
                        'ghost_nodes': [num.array([[  0.  ,   0.  ,   0.  ],
       [  1.  ,   0.  ,   0.5 ],
       [  2.  ,   0.  ,   1.  ],
       [  6.  ,   1.  ,   0.  ],
       [ 10.  ,   0.25,   0.75],
       [ 11.  ,   0.75,   0.25]]), num.array([[  3.  ,   0.5 ,   0.  ],
       [  7.  ,   1.  ,   0.5 ],
       [  8.  ,   1.  ,   1.  ],
       [ 11.  ,   0.75,   0.25],
       [ 12.  ,   0.75,   0.75]]), num.array([[  1.  ,   0.  ,   0.5 ],
       [  5.  ,   0.5 ,   1.  ],
       [  8.  ,   1.  ,   1.  ],
       [ 12.  ,   0.75,   0.75]])],
                        'full_nodes': [num.array([[  3.  ,   0.5 ,   0.  ],
       [  4.  ,   0.5 ,   0.5 ],
       [  5.  ,   0.5 ,   1.  ],
       [  7.  ,   1.  ,   0.5 ],
       [  8.  ,   1.  ,   1.  ],
       [  9.  ,   0.25,   0.25],
       [ 12.  ,   0.75,   0.75]]), num.array([[  0.  ,   0.  ,   0.  ],
       [  1.  ,   0.  ,   0.5 ],
       [  2.  ,   0.  ,   1.  ],
       [  4.  ,   0.5 ,   0.5 ],
       [  5.  ,   0.5 ,   1.  ],
       [  9.  ,   0.25,   0.25],
       [ 10.  ,   0.25,   0.75]]), num.array([[  0.  ,   0.  ,   0.  ],
       [  3.  ,   0.5 ,   0.  ],
       [  4.  ,   0.5 ,   0.5 ],
       [  6.  ,   1.  ,   0.  ],
       [  7.  ,   1.  ,   0.5 ],
       [  9.  ,   0.25,   0.25],
       [ 11.  ,   0.75,   0.25]])],
                        'ghost_triangles': [num.array([[ 5,  0,  9,  1],
       [ 6,  1,  9,  4],
       [ 8,  4, 10,  1],
       [ 9,  5, 10,  4],
       [10,  2, 10,  5],
       [11,  3,  9,  0],
       [12,  3, 11,  4],
       [13,  6, 11,  3],
       [14,  7, 11,  6],
       [15,  4, 11,  7]]), num.array([[ 0,  4,  9,  3],
       [ 1,  4, 12,  5],
       [ 2,  7, 12,  4],
       [ 4,  5, 12,  8],
       [11,  3,  9,  0],
       [12,  3, 11,  4]]), num.array([[ 0,  4,  9,  3],
       [ 1,  4, 12,  5],
       [ 2,  7, 12,  4],
       [ 3,  8, 12,  7],
       [ 5,  0,  9,  1],
       [ 6,  1,  9,  4]])],
                        'ghost_boundary': [{(13, 1): 'ghost', (8, 0): 'ghost', (14, 1): 'ghost', (11, 1): 'ghost', (10, 1): 'ghost', (5, 1): 'ghost', (10, 2): 'ghost'}, {(12, 2): 'ghost', (12, 0): 'ghost', (2, 1): 'ghost', (11, 1): 'ghost', (2, 2): 'ghost', (4, 1): 'ghost', (4, 0): 'ghost'}, {(3, 2): 'ghost', (6, 1): 'ghost', (3, 1): 'ghost', (5, 1): 'ghost', (1, 0): 'ghost', (1, 1): 'ghost'}],
                        'full_triangles': [[[4, 9, 3], [4, 12, 5], [7, 12, 4], [8, 12, 7], [5, 12, 8]], [[0, 9, 1], [1, 9, 4], [1, 10, 2], [4, 10, 1], [5, 10, 4], [2, 10, 5]], [[3, 9, 0], [3, 11, 4], [6, 11, 3], [7, 11, 6], [4, 11, 7]]],
                        'full_commun': [{0: [1, 2], 1: [1, 2], 2: [1, 2], 3: [2], 4: [1]}, {5: [0, 2], 6: [0, 2], 7: [], 8: [0], 9: [0], 10: [0]}, {11: [0, 1], 12: [0, 1], 13: [0], 14: [0], 15: [0]}],
                        'ghost_commun': [num.array([[ 5,  1],
       [ 6,  1],
       [ 8,  1],
       [ 9,  1],
       [10,  1],
       [11,  2],
       [12,  2],
       [13,  2],
       [14,  2],
       [15,  2]]), num.array([[ 0,  0],
       [ 1,  0],
       [ 2,  0],
       [ 4,  0],
       [11,  2],
       [12,  2]]), num.array([[0, 0],
       [1, 0],
       [2, 0],
       [3, 0],
       [5, 1],
       [6, 1]])],  'ghost_quan': {'stage': [num.array([[-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]), num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.25 , -0.375, -0.5  ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ]]), num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ]])],  'elevation': [num.array([[-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]), num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.25 , -0.375, -0.5  ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ]]), num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ]])],  'ymomentum': [num.array([[ 0.  ,  0.25,  0.5 ],
       [ 0.5 ,  0.25,  0.5 ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.  ,  0.25,  0.5 ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.5 ]]), num.array([[ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.  ,  0.25,  0.5 ]]), num.array([[ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 0.  ,  0.25,  0.5 ],
       [ 0.5 ,  0.25,  0.5 ]])],  'friction': [num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]]), num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]]), num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]])], 'xmomentum': [num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]]), num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]]), num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]])]},  'full_quan': {'stage': [num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]), num.array([[-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.   , -0.125, -0.   ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ]]), num.array([[-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]])],  'elevation': [num.array([[-0.25 , -0.125, -0.25 ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]]), num.array([[-0.   , -0.125, -0.   ],
       [-0.   , -0.125, -0.25 ],
       [-0.   , -0.125, -0.   ],
       [-0.25 , -0.125, -0.   ],
       [-0.25 , -0.125, -0.25 ],
       [-0.   , -0.125, -0.25 ]]), num.array([[-0.25 , -0.125, -0.   ],
       [-0.25 , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.25 ],
       [-0.5  , -0.375, -0.5  ],
       [-0.25 , -0.375, -0.5  ]])],  'ymomentum': [num.array([[ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ]]), num.array([[ 0.  ,  0.25,  0.5 ],
       [ 0.5 ,  0.25,  0.5 ],
       [ 0.5 ,  0.75,  1.  ],
       [ 0.5 ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  0.5 ],
       [ 1.  ,  0.75,  1.  ]]), num.array([[ 0.  ,  0.25,  0.  ],
       [ 0.  ,  0.25,  0.5 ],
       [ 0.  ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.  ],
       [ 0.5 ,  0.25,  0.5 ]])],  'friction': [num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]]), num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]]), num.array([[ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.],
       [ 0.,  0.,  0.]])],  'xmomentum': [num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]]), num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]]), num.array([[ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.],
       [ 2.,  2.,  2.]])]}}
                                  

        from anuga.abstract_2d_finite_volumes.neighbour_mesh import Mesh
        
        mesh = Mesh(nodes, triangles)
        boundary_polygon = mesh.get_boundary_polygon()


        # Subdivide into non-overlapping partitions

        submesh = submesh_full(nodes, triangles, edges, \
                            triangles_per_proc)

        #print submesh


        for i in range(3):
            assert num.allclose(true_submesh['full_triangles'][i],submesh['full_triangles'][i])
            assert num.allclose(true_submesh['full_nodes'][i],submesh['full_nodes'][i])
        assert true_submesh['full_boundary'] == submesh['full_boundary']

        # Add any extra ghost boundary layer information

        submesh = submesh_ghost(submesh, mesh, triangles_per_proc)

        for i in range(3):
            assert num.allclose(true_submesh['ghost_triangles'][i],submesh['ghost_triangles'][i])
            assert num.allclose(true_submesh['ghost_nodes'][i],submesh['ghost_nodes'][i])
            assert num.allclose(true_submesh['ghost_commun'][i],submesh['ghost_commun'][i])

        assert true_submesh['full_commun'] == submesh['full_commun']


        # Order the quantities information to be the same as the triangle
        # information


        submesh = submesh_quantities(submesh, quantities, \
                                 triangles_per_proc)



        for key, value in true_submesh['ghost_quan'].iteritems():
            for i in range(3):
                assert num.allclose(true_submesh['ghost_quan'][key][i],submesh['ghost_quan'][key][i])
                assert num.allclose(true_submesh['full_quan'][key][i],submesh['full_quan'][key][i])
        

        submesh["boundary_polygon"] = boundary_polygon


        #print submesh

#-------------------------------------------------------------

if __name__ == "__main__":
    suite = unittest.makeSuite(Test_Distribute_Mesh,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
