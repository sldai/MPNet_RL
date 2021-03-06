from crl_kino.policy.rl_policy import load_policy, policy_forward
from crl_kino.utils import obs_generate
import os.path
#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@author: daishilong
@contact: daishilong1236@gmail.com
'''

from crl_kino.env import DifferentialDriveEnv, DifferentialDriveGym
from crl_kino.policy.dwa import DWA
from crl_kino.utils.draw import *
from crl_kino.planner.rrt import RRT
from crl_kino.planner.rrt_rl import RRT_RL
from crl_kino.planner.rrt_rl_estimator import RRT_RL_Estimator
from crl_kino.estimator.load_estimator import load_estimator
try:
    from crl_kino.planner.sst import SST
except ImportError:
    print('ompl not installed, cannot use SST')
import argparse
import pickle

import numpy as np
import matplotlib.pyplot as plt




def main(test_env, positions, fname):
    env = DifferentialDriveEnv(1.0, -0.1, np.pi, 1.0, np.pi)

    env.set_obs(test_env)

    model_path =os.path.dirname(__file__)+'/../data/net/end2end/ddpg/policy.pth'
    # policy = load_policy(DifferentialDriveGym(), [1024,512,512,512], model_path)
    # rl_rrt = RRT_RL(env, policy)

    data = {
        'runtime': [],
        'path_len': []
    }

    estimator_path = os.path.dirname(__file__)+"/../data/net/estimator/dist_est_statedict.pth"
    classifier_path = os.path.dirname(__file__)+"/../data/net/estimator/classifier_statedict.pth"

    estimator_model, classifier_model = load_estimator(estimator_path, classifier_path)

    policy = load_policy(DifferentialDriveGym(), [1024,512,512,512], model_path)
    rl_rrt_estimator = RRT_RL_Estimator(env, policy, estimator_model, classifier_model)


    # sst = SST(env)

    for i, start in enumerate(positions):
        for j, goal in enumerate(positions):
            if j == i: continue
            print('Start and goal', start, goal)
            # rl_rrt.set_start_and_goal(start, goal)
            # path = rl_rrt.planning()
            # if rl_rrt.reach_exactly:
            #     data['path_len'].append(0.2*(len(path)-1))
            #     data['runtime'].append(rl_rrt.planning_time)
            # else:
            #     data['runtime'].append(-1)


            rl_rrt_estimator.set_start_and_goal(start, goal)
            path = rl_rrt_estimator.planning()
            if rl_rrt_estimator.reach_exactly:
                data['path_len'].append(0.2*(len(path)-1))
                data['runtime'].append(rl_rrt_estimator.planning_time)
            else:
                data['runtime'].append(-1)

            # collect data of sst
            # sst.set_start_and_goal(start, goal)
            # sst.planning()
            # if sst.reach_exactly:
            #     data['path_len'].append(sst.get_path_len())
            #     data['runtime'].append(sst.planning_time)
            # else:
            #     data['runtime'].append(-1)
            
    for k,v in enumerate(data):
        data[v] = np.array(data[v])
    pickle.dump(data, open(fname+'.pkl', 'wb'))


if __name__ == "__main__":
    test_env1 = pickle.load(open(os.path.dirname(__file__)+'/../data/obstacles/test_env1.pkl', 'rb'))
    test_env2 = pickle.load(open(os.path.dirname(__file__)+'/../data/obstacles/test_env2.pkl', 'rb'))
    positions_test_env1 = pickle.load(open(os.path.dirname(__file__)+'/benchmark_position_test_env1.pkl', 'rb'))
    positions_test_env2 = pickle.load(open(os.path.dirname(__file__)+'/benchmark_position_test_env2.pkl', 'rb'))

    main(test_env1, positions_test_env1, 'planning_results_rrt_env1')
    main(test_env2, positions_test_env2, 'planning_results_rrt_env2')
