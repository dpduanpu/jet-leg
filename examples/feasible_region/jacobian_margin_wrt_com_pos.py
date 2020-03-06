# -*- coding: utf-8 -*-
"""
Created on Tue Jun 12 10:54:31 2018

@author: Romeo Orsolino
"""

import numpy as np

from numpy import array
from copy import deepcopy
import random
from jet_leg.computational_geometry.math_tools import Math
from jet_leg.dynamics.computational_dynamics import ComputationalDynamics
from jet_leg.computational_geometry.computational_geometry import ComputationalGeometry
from jet_leg.computational_geometry.iterative_projection_parameters import IterativeProjectionParameters
from jet_leg.optimization.jacobians import Jacobians
from jet_leg.variables.com import CoM
import time

import matplotlib.pyplot as plt
from jet_leg.plotting.arrow3D import Arrow3D

plt.close('all')
math = Math()

''' Set the robot's name (either 'hyq', 'hyqreal' or 'anymal')'''
robot_name = 'anymal'

'''
possible constraints for each foot:
 ONLY_ACTUATION = only joint-torque limits are enforces
 ONLY_FRICTION = only friction cone constraints are enforced
 FRICTION_AND_ACTUATION = both friction cone constraints and joint-torque limits
'''
constraint_mode_IP = ['ONLY_FRICTION',
                      'ONLY_FRICTION',
                      'ONLY_FRICTION',
                      'ONLY_FRICTION']

# number of decision variables of the problem
# n = nc*6
comWF = np.array([.0, 0.0, 0.0])
comWF_lin_acc = np.array([.0, .0, .0])
comWF_ang_acc = np.array([.0, .0, .0])

''' extForceW is an optional external pure force (no external torque for now) applied on the CoM of the robot.'''
extForce = np.array([0., .0, 0.0 * 9.81])  # units are N
extCentroidalTorque = np.array([.0, .0, .0])  # units are Nm
extCentroidalWrench = np.hstack([extForce, extCentroidalTorque])

''' parameters to be tuned'''
mu = 0.5

''' stanceFeet vector contains 1 is the foot is on the ground and 0 if it is in the air'''
stanceFeet = [1, 1, 1, 1]

randomSwingLeg = random.randint(0, 3)
tripleStance = False  # if you want you can define a swing leg using this variable
if tripleStance:
    print 'Swing leg', randomSwingLeg
    stanceFeet[randomSwingLeg] = 0
print 'stanceLegs ', stanceFeet

''' now I define the normals to the surface of the contact points. By default they are all vertical now'''
axisZ = array([[0.0], [0.0], [1.0]])

n1 = np.transpose(np.transpose(math.rpyToRot(0.0, 0.0, 0.0)).dot(axisZ))  # LF
n2 = np.transpose(np.transpose(math.rpyToRot(0.0, 0.0, 0.0)).dot(axisZ))  # RF
n3 = np.transpose(np.transpose(math.rpyToRot(0.0, 0.0, 0.0)).dot(axisZ))  # LH
n4 = np.transpose(np.transpose(math.rpyToRot(0.0, 0.0, 0.0)).dot(axisZ))  # RH
normals = np.vstack([n1, n2, n3, n4])

''' extForceW is an optional external pure force (no external torque for now) applied on the CoM of the robot.'''
extForceW = np.array([0.0, 0.0, 0.0])  # units are Nm

comp_dyn = ComputationalDynamics(robot_name)

'''You now need to fill the 'params' object with all the relevant 
    informations needed for the computation of the IP'''
params = IterativeProjectionParameters(robot_name)
""" contact points in the World Frame"""
LF_foot = np.array([0.3, 0.2, -0.4])
RF_foot = np.array([0.3, -0.2, -0.4])
LH_foot = np.array([-0.3, 0.2, -0.4])
RH_foot = np.array([-0.3, -0.2, -0.4])

contactsWF = np.vstack((LF_foot, RF_foot, LH_foot, RH_foot))
params.setContactsPosWF(contactsWF)


start = time.time()

params.useContactTorque = True
params.useInstantaneousCapturePoint = True
params.externalCentroidalWrench = extCentroidalWrench
params.setCoMPosWF(comWF)
params.comLinVel = [0., 0.0, 0.0]
params.setCoMLinAcc(comWF_lin_acc)
params.setTorqueLims(comp_dyn.robotModel.robotModel.joint_torque_limits)
params.setActiveContacts(stanceFeet)
params.setConstraintModes(constraint_mode_IP)
params.setContactNormals(normals)
params.setFrictionCoefficient(mu)
params.setTotalMass(comp_dyn.robotModel.robotModel.trunkMass)
params.externalForceWF = extForceW  # params.externalForceWF is actually used anywhere at the moment

params_com_y = deepcopy(params)
params_com_vel_y = deepcopy(params)
params_com_acc_y = deepcopy(params)

jac = Jacobians("anymal")
comp_geom = ComputationalGeometry()
com = CoM(params)

delta_y_range = 0.9
num_of_tests = 20
delta_y_range_vec = np.linspace(-delta_y_range/2.0, delta_y_range/2.0, num_of_tests)
print "number of tests", num_of_tests

pos_margin_x, jac_com_pos_x = jac.plotMarginAndJacobianWrtComPosition(params_com_y, delta_y_range_vec, 0)
pos_margin_y, jac_com_pos_y = jac.plotMarginAndJacobianWrtComPosition(params_com_y, delta_y_range_vec, 1)
pos_margin_z, jac_com_pos_z = jac.plotMarginAndJacobianWrtComPosition(params_com_y, delta_y_range_vec, 2)

delta_vel_range = 3.0
delta_vel_range_vec = np.linspace(-delta_vel_range/2.0, delta_vel_range/2.0, num_of_tests)
print num_of_tests, np.shape(delta_vel_range_vec)

""" contact points in the World Frame"""
LF_foot = np.array([0.3, 0.2, -0.4])
RF_foot = np.array([0.3, -0.2, -0.4])
LH_foot = np.array([-0.3, 0.2, -0.4])
RH_foot = np.array([-0.3, -0.2, -0.4])

contactsWF = np.vstack((LF_foot, RF_foot, LH_foot, RH_foot))
params.setContactsPosWF(contactsWF)

vel_margin, jac_com_lin_vel = jac.plotMarginAndJacobianOfMarginWrtComVelocity(params_com_vel_y, delta_vel_range_vec)

delta_vel_range = 8.0
delta_acc_range_vec = np.linspace(-delta_vel_range/2.0, delta_vel_range/2.0, num_of_tests)
acc_margin, jac_com_lin_acc = jac.plotMarginAndJacobianOfMarginWrtComLinAcceleration(params_com_acc_y, delta_acc_range_vec)

### Plotting

### X axis
plt.figure(1)
plt.subplot(231)
plt.plot(delta_y_range_vec, pos_margin_x, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel("m [m]")
plt.title("CoM Y pos margin")

plt.subplot(234)
plt.plot(delta_y_range_vec, jac_com_pos_x[0,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel(" $ \delta m/  \delta c_y$")
plt.title("CoM Y pos jacobian")

plt.subplot(232)
plt.plot(delta_vel_range_vec, vel_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y vel margin")

plt.subplot(235)
plt.plot(delta_vel_range_vec, jac_com_lin_vel[0,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \dot{c}_y$")
plt.title("CoM Y vel jacobian")

plt.subplot(233)
plt.plot(delta_acc_range_vec, acc_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y acc margin")

plt.subplot(236)
plt.plot(delta_acc_range_vec, jac_com_lin_acc[0,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \ddot{c}_y$")
plt.title("CoM Y acc jacobian")

### Y axis
plt.figure(2)
plt.subplot(231)
plt.plot(delta_y_range_vec, pos_margin_y, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel("m [m]")
plt.title("CoM Y pos margin")

plt.subplot(234)
plt.plot(delta_y_range_vec, jac_com_pos_y[1,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel(" $ \delta m/  \delta c_y$")
plt.title("CoM Y pos jacobian")

plt.subplot(232)
plt.plot(delta_vel_range_vec, vel_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y vel margin")

plt.subplot(235)
plt.plot(delta_vel_range_vec, jac_com_lin_vel[1,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \dot{c}_y$")
plt.title("CoM Y vel jacobian")

plt.subplot(233)
plt.plot(delta_acc_range_vec, acc_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y acc margin")

plt.subplot(236)
plt.plot(delta_acc_range_vec, jac_com_lin_acc[1,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \ddot{c}_y$")
plt.title("CoM Y acc jacobian")


### Z axis
plt.figure(3)
plt.subplot(231)
plt.plot(delta_y_range_vec, pos_margin_z, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel("m [m]")
plt.title("CoM Y pos margin")

plt.subplot(234)
plt.plot(delta_y_range_vec, jac_com_pos_z[2,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$c_y$ [m]")
plt.ylabel(" $ \delta m/  \delta c_y$")
plt.title("CoM Y pos jacobian")

plt.subplot(232)
plt.plot(delta_vel_range_vec, vel_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y vel margin")

plt.subplot(235)
plt.plot(delta_vel_range_vec, jac_com_lin_vel[2,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\dot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \dot{c}_y$")
plt.title("CoM Y vel jacobian")

plt.subplot(233)
plt.plot(delta_acc_range_vec, acc_margin, 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("m [m]")
plt.title("CoM Y acc margin")

plt.subplot(236)
plt.plot(delta_acc_range_vec, jac_com_lin_acc[2,:], 'g', markersize=15, label='CoM')
plt.grid()
plt.xlabel("$\ddot{c}_y$ [m/s]")
plt.ylabel("$ \delta m/  \delta \ddot{c}_y$")
plt.title("CoM Y acc jacobian")

plt.show()