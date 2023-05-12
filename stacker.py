#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Caroline Fernandes

:synopsis:
    Stacks three objects on top of one another.

:description:
    This module is passed a number of transform nodes in Maya, if it receives three
    parameters it will make a function call to get_center_point() either the top center
    or bottom center of an object based on what is passed and sends that info
    to create_stack() to solve for where to move the object to so that it is on top of
    the previous object.

:applications:
    Maya

:see_also:
    n/a
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import maya.cmds as cmds
# Imports That You Wrote

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def offset_objs_in_x(obj_static = None, obj_move = None, offset_val = None):
    """
    Moves an object so that the two input geos are at a certain distance apart.
    :param obj_static: Transform node of obj not to be moved.
    :type: str

    :param obj_move: Transform node of obj to be moved.
    :type: str

    :param offset_val: Amount to offset in x (between the bounding boxes of objects).
    :type: int
    """
    static_center_prev = get_center_point(obj_static)
    move_center_prev = get_center_point(obj_move)
    cmds.move(static_center_prev[0] - move_center_prev[0],
              0, 0, obj_move, relative = True)

    static_bounds = []
    static_bounds = cmds.xform(obj_static, query = True, boundingBox = True)
    static_center_new = get_center_point(obj_static)
    static_dist = static_bounds[3] - static_center_new[0]

    move_bounds = []
    move_bounds = cmds.xform(obj_move, query=True, boundingBox=True)
    move_center_new = get_center_point(obj_move)
    move_dist = move_center_new[0] - move_bounds[0]

    #last_char = int(obj_move[-1])
    offset_to = offset_val + static_dist + move_dist
    cmds.move(offset_to, 0, 0, obj_move, relative = True)

def stack_objs(arg_list = None):
    """
    This function stacks objects through the use of helper functions.

    :param arg_list: List of objects to stack.
    :type: list of str

    :return: Describes the success (or failure) of the operation.
    :type: bool
    """
    # call verify_args() to see if any parameters were passed as empty
    if verify_args(arg_list) is None:
        print('Given incorrect arguments, exiting now')
        return None

    for i in range(len(arg_list) - 1):
        # get the top center of the base object
        top_center = get_center_point(arg_list[i], 1, 0)

        # get the bottom center of the object to be placed directly above
        bottom_center = get_center_point(arg_list[i + 1], 0, 1)

        # move the above object so it's resting on the lower object
        create_stack(arg_list[i + 1], bottom_center, top_center)

    return True

def create_stack(object_name=None,bottom_center=None,new_point=None):
    """
    Finds out how much to move the object and moves it so that its bottom center point
    is sitting at the same location as the new point.

    :param object_name: The name of an object to move (transform node)
    :type: str

    :param bottom_center: The bottom center of an object to move (x,y,z values)
    :type: list

    :param new_point: The point in space to place this object (x,y,z values)
    :type: list
    """
    # Solve for the distance inbetween the bottomCenter and newPoint
    dist = [new_point[0] - bottom_center[0],
            new_point[1] - bottom_center[1],
            new_point[2] - bottom_center[2]]

    # Call the move command to place the object
    cmds.move(dist[0], dist[1], dist[2], object_name, relative = True)


def get_center_point(object_name=None,top_flag=0,bottom_flag=0):
    """
    Uses the 'xform' command to get the bounding box of the object passed in.

    :param object_name: The name of an object to move
    :type: str

    :param top_flag: A flag that indicates if it is getting the top center.
    0 for false, 1 for true
    :type: int

    :param bottom_flag: A flag that indicates if it is getting the bottom center.
    0 for false, 1 for true
    :type: int

    :return: Returns a list with the top center coordinates (x,y,z) if the top center
    flag is set to true.
	Returns a list with the bottom center coordinates (x, y, z) if the bottom center
	flag is set to true.
    :type: list
    """
    
    bound_coord = []
    # Get the bounding box coordinates using the xform command, it will return a list
    # in the form [xmin,ymin,zmin,xmax,ymax,zmax]
    bound_coord = cmds.xform(object_name, query = True, boundingBox = True)
    center_coord = []

    '''
    center_coord x and z positions are an average of the bounding box info from
    the bound_coord list so it finds the middle position of the object.
    The y is left blank at 0 for now, because this info depends on whether the function
    call set the topFlag or bottomFlag to true.
    '''
    center_coord = [(bound_coord[0] + bound_coord[3])/2,
                   (bound_coord[1] + bound_coord[4])/2,
                   (bound_coord[2] + bound_coord[5])/2]

    if top_flag == 1 and bottom_flag == 0:
        # return the top center
        center_coord[1] = bound_coord[4]
        return center_coord
    elif top_flag == 0 and bottom_flag == 1:
        # return the bottom center
        center_coord[1]= bound_coord[1]
        return center_coord
    else:
        return center_coord

def verify_args(arg_list = None):
    """
    Checks if any of the arguments does not have a value.
    
    :param arg_list: List of objects to stack
    :type: list

    :return: Presence of a value in all arguments, returns True.
    Otherwise, returns False.
    :type: bool
    """
    # Search through parameters to see if a value is equal to None
    for e in arg_list:
        if e is None:
            return None
        else:
            continue

    return True
