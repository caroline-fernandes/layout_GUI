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
    This project creates a GUI for a tool that will stack objects in a scene using
    a bit of randomization. It sets up buttons and line edits to choose objects that
    will be placed at the bottom, middle, and top of stack. Depending on user input it
    will create however many stacks of random selections from each group.

:applications:
    Maya

:see_also:
    stacker.py, gen_utils.py
"""

#----------------------------------------------------------------------------------------#
#----------------------------------------------------------------------------- IMPORTS --#

# Default Python Imports
from PySide2 import QtGui, QtWidgets
from maya import OpenMayaUI as omui
from shiboken2 import wrapInstance
import maya.cmds as cmds
import random

# Imports that you wrote
from td_maya_tools.stacker import stack_objs, get_center_point
from td_maya_tools.stacker import create_stack, offset_objs_in_x
from td_maya_tools.gen_utils import read_stack_xml

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- FUNCTIONS --#

def get_maya_window():
    """
    This gets a pointer to the Maya window.

    :return: A pointer to the Maya window.
    :type: pointer
    """
    maya_main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(maya_main_window_ptr), QtWidgets.QWidget)

#----------------------------------------------------------------------------------------#
#--------------------------------------------------------------------------- CLASSES ----#

class BuilderGUI(QtWidgets.QDialog):
    """
    This GUI will show buttons and line edits to create stacks of objects
    inside a Maya scene.
    """
    def __init__(self):
        QtWidgets.QDialog.__init__(self, parent=get_maya_window())
        self.num_stack = None
        self.max_height = None
        self.sep_value = None

        self.top_group = None
        self.mid_group = None
        self.bottom_group = None
        self.top_objects = None
        self.mid_objects = None
        self.bottom_objects = None

        self.btn_01 = None
        self.btn_02 = None
        self.btn_03 = None
        self.btn_04 = None
        self.btn_05 = None
        self.btn_06 = None

        self.tree_view = None

    def init_gui(self):
        """
        Displays the GUI to the user. This GUI consists of three buttons and line edits
        for selecting top, mid, and bottom objects. It also contains UI for inputting
        a set number of stacks to create, a max height for the stacks,
        a separation value for the groups, and then a button to make
        stacks and cancel the GUI.
        """
        # Make a layout, and call make options layout func.
        main_vb = QtWidgets.QVBoxLayout(self)
        sec_hb = QtWidgets.QHBoxLayout()
        sec_hb.addLayout(self.make_options_layout())

        # Make a tree view widget.
        self.tree_view = QtWidgets.QTreeWidget()
        self.tree_view.setHeaderLabels(['Object Stacks'])
        self.tree_view.currentItemChanged['QTreeWidgetItem*',
                                    'QTreeWidgetItem*'].connect(self.tree_item_clicked)
        sec_hb.addWidget(self.tree_view)

        # Make some buttons
        self.btn_04 = QtWidgets.QPushButton('Make Stack')
        self.btn_05 = QtWidgets.QPushButton('Cancel')
        self.btn_06 = QtWidgets.QPushButton('Load XML')

        # Add a clicked event.
        self.btn_01.clicked.connect(self.set_selection)
        self.btn_02.clicked.connect(self.set_selection)
        self.btn_03.clicked.connect(self.set_selection)
        self.btn_04.clicked.connect(self.make_stacks)
        self.btn_05.clicked.connect(self.close)
        self.btn_06.clicked.connect(self.apply_xml)

        # Add some color to the buttons.
        self.btn_06.setStyleSheet('background-color: dodgerblue')
        self.btn_04.setStyleSheet('background-color: forestgreen')
        self.btn_05.setStyleSheet('background-color: crimson')

        # Set up some rows.
        hb_01 = QtWidgets.QHBoxLayout()

        # Add stuff to the GUI
        hb_01.addWidget(self.btn_06)
        hb_01.addWidget(self.btn_04)
        hb_01.addWidget(self.btn_05)

        main_vb.addLayout(sec_hb)
        main_vb.addLayout(hb_01)

        # Display the window to the user.
        self.setWindowTitle('Stack Builder')
        self.setGeometry(300,300, 450, 300)
        self.show()

    def make_options_layout(self):
        """
        This function sets up the work for part of the GUI.

        :return: A part of the layout for the GUI.
        :type: QFormLayout
        """
        layout = QtWidgets.QFormLayout()

        # Add some buttons
        self.btn_01 = QtWidgets.QPushButton('Set Top Parts')
        self.btn_02 = QtWidgets.QPushButton('Set Mid Parts')
        self.btn_03 = QtWidgets.QPushButton('Set Bottom Parts')

        # Add a few line edits and a label and make them read-only.
        self.top_group = QtWidgets.QLineEdit('')
        self.mid_group = QtWidgets.QLineEdit('')
        self.bottom_group = QtWidgets.QLineEdit('')
        self.top_group.setReadOnly(True)
        self.mid_group.setReadOnly(True)
        self.bottom_group.setReadOnly(True)

        lbl_01 = QtWidgets.QLabel('Set Stack Count')
        lbl_02 = QtWidgets.QLabel('Set Max Height')
        lbl_03 = QtWidgets.QLabel('Set Separation')

        # Create some spin boxes
        self.num_stack = QtWidgets.QSpinBox()
        self.max_height = QtWidgets.QSpinBox()
        self.sep_value = QtWidgets.QDoubleSpinBox()

        # Set some default values
        self.num_stack.setValue(3)
        self.max_height.setValue(3)
        self.sep_value.setValue(0.1)
        self.sep_value.setSingleStep(0.1)

        # Create several hboxes for the btns
        hb_01 = QtWidgets.QHBoxLayout()
        hb_01.addWidget(self.btn_01)
        hb_01.addWidget(self.top_group)
        layout.addRow(hb_01)

        hb_02 = QtWidgets.QHBoxLayout()
        hb_02.addWidget(self.btn_02)
        hb_02.addWidget(self.mid_group)
        layout.addRow(hb_02)

        hb_03 = QtWidgets.QHBoxLayout()
        hb_03.addWidget(self.btn_03)
        hb_03.addWidget(self.bottom_group)
        layout.addRow(hb_03)

        hb_04 = QtWidgets.QHBoxLayout()
        hb_04.addWidget(lbl_01)
        hb_04.addWidget(self.num_stack)
        layout.addRow(hb_04)

        hb_05 = QtWidgets.QHBoxLayout()
        hb_05.addWidget(lbl_02)
        hb_05.addWidget(self.max_height)
        layout.addRow(hb_05)

        hb_06 = QtWidgets.QHBoxLayout()
        hb_06.addWidget(lbl_03)
        hb_06.addWidget(self.sep_value)
        layout.addRow(hb_06)

        return layout

    def set_selection(self):
        """
        Tells us which button was clicked, and completes the appropriate operation.
        """
        clicked = self.sender()

        sel = cmds.ls(selection=True)
        count = 0
        for i in range(len(sel)):
            count+=1

        amount = "%s objects" % str(count)

        if clicked == self.btn_01:
            # Select the top objects
            self.top_objects = sel
            self.top_group.setText(amount)
            self.top_group.setStyleSheet('background-color: seagreen')

        elif clicked == self.btn_02:
            # Select the mid objects
            self.mid_objects = sel
            self.mid_group.setText(amount)
            self.mid_group.setStyleSheet('background-color: seagreen')

        elif clicked == self.btn_03:
            # Select the bottom objects
            self.bottom_objects = sel
            self.bottom_group.setText(amount)
            self.bottom_group.setStyleSheet('background-color: seagreen')

    def make_stacks(self):
        """
        Call to verify_args to ensure arguments' validity. Run's a for loop
        for the number of stacks entered by the user. Picks random object from
        each of the groups to stack, duplicates them and makes a call to functions from
        stacker.py (get_center_point and create_stack). It then groups the stack
        and renames it.

        :return: Success of the operation
        :type: bool
        """

        status_new = self.verify_args()
        if status_new is None:
            return None

        stacks = int(self.num_stack.text())
        for i in range(stacks):
            # Randomly choose an obj from each list
            top_obj = random.choice(self.top_objects)
            bottom_obj = random.choice(self.bottom_objects)

            # Creating names for the duplicate objects
            top_name = 'second_top%s' % str(i+1)
            bottom_name = 'second_bottom%s' % str(i+1)

            # Duplicate the chosen objects
            dup_top = cmds.duplicate(top_obj, n = top_name)
            dup_bottom = cmds.duplicate(bottom_obj, n = bottom_name)

            # Create a group name and make a group of the duplicate objects
            grp_name = 'stack00%s' % str(i + 1)
            cmds.group(dup_top, dup_bottom, n=grp_name)

            # Select a random number of middle objects based on input.
            number_in_middle = random.randint(1,int(self.max_height.text()))

            list_of_objects = [dup_bottom]
            tree_list = [top_name]

            for j in range(number_in_middle):
                mid_obj = random.choice(self.mid_objects)
                mid_name = 'second_mid%s_%s' % (grp_name[-1], str(j + 1))
                dup_mid = cmds.duplicate(mid_obj, n=mid_name)
                cmds.parent(dup_mid, grp_name)
                list_of_objects.append(dup_mid)
                tree_list.append(mid_name)

            list_of_objects.append(dup_top)
            tree_list.append(bottom_name)

            # Move the base object to the origin
            bottom_center = get_center_point(dup_bottom,0,1)
            origin = [0,0,0]
            create_stack(dup_bottom, bottom_center, origin)

            stack_objs(list_of_objects)

            # Set the pivot point to the origin
            cmds.move(0, 0, 0, grp_name + '.scalePivot', grp_name + '.rotatePivot'
                      , absolute = True)

            self.add_stack_to_tree_view(grp_name,tree_list)

        for j in range(stacks-1):
            obj_static = 'stack00%s' % str(j+1)
            obj_move   = 'stack00%s' % str(j+2)
            offset_objs_in_x(obj_static, obj_move, self.sep_value.value())

        return True

    def verify_args(self):
        """
        Makes sure GUI has all info it needs by checking the three
        groups are not empty, requiring the number to stack box to be filled out,
        and only allowing integers to be entered into he number to stack box.

        :return: Validity of all of the arguments value's
        :type: bool
        """
        # Set up an int validator to prevent any other type being entered in
        bound = QtGui.QIntValidator()

        # Make sure only ints are allowed by setting a lower bound
        bound.setBottom(0)

        # Checks if any of the group line edits are empty
        if not self.top_group.text():
            message = 'You must set a selection for the top objects.'
            title = 'Not enough arguments'
            self.warn_user(title, message)
            return None
        elif not self.mid_group.text():
            message = 'You must set a selection for the middle objects.'
            title = 'Not enough arguments'
            self.warn_user(title, message)
            return None
        elif not self.bottom_group.text():
            message =  'You must set a selection for the bottom objects.'
            title = 'Not enough arguments'
            self.warn_user(title, message)
            return None

        # Checks if the num_stack line edit if filled with a value OR
        # Checks to make sure stack count is at least 1
        elif not self.num_stack.hasAcceptableInput() or int(self.num_stack.text()) < 1:
            message =  'The number of stacks needs to be an integer that is at least 1'
            title = 'Incorrect format'
            self.warn_user(title,message)
            return None

        # The max height is anything between 1 to 6
        elif int(self.max_height.text()) < 1 or int(self.max_height.text()) > 6:
                message = 'The max height should be a number from 1 to 6'
                title = 'Incorrect max height'
                self.warn_user(title,message)
                return None

        # The separation value must at least be 0.1
        elif float(self.sep_value.text()) < 0.1:
            message = 'The separation value must be at least 0.1'
            title = 'Incorrect separation value'
            self.warn_user(title,message)
            return None

        return True

    def add_stack_to_tree_view(self, grp_name = None, args_list = None):
        """
        Add group and its contents to the tree view.
        :param grp_name: Name of grouped objects in a single stack
        :type: str

        :param args_list: Names of objects belonging to a particular stack
        :type: list
        """
        group = QtWidgets.QTreeWidgetItem(self.tree_view,[grp_name])

        for obj in args_list:
            node = QtWidgets.QTreeWidgetItem(group)
            node.setText(0, str(obj))

    def apply_xml(self):
        """
        Allows the user to select a XML file and applies the values to the objects.
        :return: The success of the operation.
        :type: bool
        """
        # Prompt the user to select a file.
        filename, ffilter = QtWidgets.QFileDialog.getOpenFileName(caption = 'Open File',
                            dir = 'C:/Users/0cfer/code/td_maya_tools/',
                            filter = 'XML Files (*.xml)')

        if not filename:
            return None

        #xml_path = filename
        dict = read_stack_xml(filename)

        # Make sure the file is not empty.
        if not dict:
            message = 'The xml file provided was empty after reading.'
            title = 'Empty file'
            self.warn_user(title,message)
            return None

        for key in dict:
            #Key will access the first subroot maya_stacks
            for j in dict[key]:
                # I will access the sec. subroot stack00_
                #for i in dict[key][j]:
                    #obj_list.append(value)
                cmds.move(dict[key][j]['tx'], dict[key][j]['ty'],
                          dict[key][j]['tz'], j, absolute=True)

        return True

    def tree_item_clicked(self, arg_one = None):
        """
        Selects the obj in the Maya scene based on what is clicked in the tree view.

        :param arg_one: A QTreeWidgetItem
        :type: QTreeWidgetItem
        """
        #Check validity
        if arg_one:
            cmds.select(arg_one.text(0))

    def warn_user(self, title=None, message=None):
        """
        Displays a message to the user.

        :param title: The title of the window;
        :type: str

        :param message: The message the popup will say.
        :type: str
        """
        # Build a QMessageBox, and pass it the values provided, then show it.
        msg = QtWidgets.QMessageBox()
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.exec_()  # will freeze Maya until the user responds to the message.
