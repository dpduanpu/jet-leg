# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 06:10:18 2018

@author: Romeo Orsolino
"""

from context import legsthrust

from legsthrust.hyq_kinematics import HyQKinematics
import numpy as np

import unittest

class TestStringMethods(unittest.TestCase):
    
    epsilon = 10e-03
    assertPrecision = 3
    
    def test_inverse_kinematics(self):
        
        hyqKin = HyQKinematics()
        
        hyqKin.init_jacobians()
        hyqKin.init_homogeneous()
        
        foot_vel = np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0],[0, 0, 0]])
        
        LF_foot = np.array([0.3, 0.2, -0.58])
        RF_foot = np.array([0.3, -0.2, -0.58])
        LH_foot = np.array([-0.3, 0.2, -0.58])
        RH_foot = np.array([-0.3, -0.2, -0.58])
        contacts = np.vstack((LF_foot,RF_foot,LH_foot,RH_foot))
        
        #print contacts
        
        q, q_dot, J_LF, J_RF, J_LH, J_RH = hyqKin.inverse_kin(np.transpose(contacts[:,0]),
                                                              np.transpose(foot_vel[:,0]),
                                                        np.transpose(contacts[:,2]),
                                                        np.transpose(foot_vel[:,2]))
                                                        
        #print q
        hyqKin.update_homogeneous(q)
        hyqKin.update_jacobians(q)
        new_contacts = hyqKin.forward_kin(q)
        #print new_contacts
        
        error = np.subtract(contacts,new_contacts)
        feet_pos_error =  np.sqrt(np.sum(error*error))
        #print "feet error: ", np.sqrt(np.sum(error*error))
        
        new_q, q_dot, J_LF, J_RF, J_LH, J_RH = hyqKin.inverse_kin(np.transpose(new_contacts[:,0]),
                                                                  np.transpose(foot_vel[:,0]),
                                                        np.transpose(new_contacts[:,2]),
                                                        np.transpose(foot_vel[:,2]))
                                                        
        #print new_q
        joints_error = np.sqrt(np.sum((q-new_q)*(q-new_q)))
        #print "joints error: ", joints_error
        self.assertTrue( np.abs(joints_error) < self.epsilon)
        
        
    def test_forward_kinematics(self):
        
        hyqKin = HyQKinematics()
        
        hyqKin.init_jacobians()
        hyqKin.init_homogeneous()
        
        foot_vel = np.array([[0, 0, 0],[0, 0, 0],[0, 0, 0],[0, 0, 0]])
        
        LF_foot = np.array([0.3, 0.2, -0.58])
        RF_foot = np.array([0.3, -0.2, -0.58])
        LH_foot = np.array([-0.3, 0.2, -0.58])
        RH_foot = np.array([-0.3, -0.2, -0.58])
        contacts = np.vstack((LF_foot,RF_foot,LH_foot,RH_foot))
        
        #print contacts
        
        q, q_dot, J_LF, J_RF, J_LH, J_RH = hyqKin.inverse_kin(np.transpose(contacts[:,0]),
                                                              np.transpose(foot_vel[:,0]),
                                                        np.transpose(contacts[:,2]),
                                                        np.transpose(foot_vel[:,2]))
                                                        
        #print q
        hyqKin.update_homogeneous(q)
        hyqKin.update_jacobians(q)
        new_contacts = hyqKin.forward_kin(q)
        #print new_contacts
        
        error = np.subtract(contacts,new_contacts)
        feet_pos_error =  np.sqrt(np.sum(error*error))
        #print "feet error: ", np.sqrt(np.sum(error*error))

        self.assertAlmostEqual(feet_pos_error, 0.0, places = self.assertPrecision)