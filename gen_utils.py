#!/usr/bin/env python
#SETMODE 777

#----------------------------------------------------------------------------------------#
#------------------------------------------------------------------------------ HEADER --#

"""
:author:
    Caroline Fernandes

:synopsis:
    GUI for stacker tool.

:description:
    File containing ability to read XML files, it does this
    with the Perl method of creating dictionaries.

:applications:
    Maya

:see_also:

"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
import xml.etree.ElementTree as et
import os

# Imports that you wrote

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def read_stack_xml(file_path = None):
    """
    Reading an xml file for the stack information.

    :param file_path: A path to a file in the computer's directory
    :type: str

    :return: Contents of the file stored in a dictionary
    :type: dict
    """
    if not os.path.isfile(file_path):
        return None

    xml_fh = et.parse(file_path)
    root = xml_fh.getroot()

    contents = Autovivification()
    groups = root.getchildren()
    for stack in groups:
        vector = stack.getchildren()
        for i in vector:
            point = i.getchildren()
            for comp in point:
                value = comp.attrib['value']
                contents[stack.tag][i.tag][comp.tag] = value
    return contents

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- CLASSES --#

class Autovivification(dict):
    """
    This is a Python implementation of Perl's autovivification feature.
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value