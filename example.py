#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division, print_function, unicode_literals
import argparse
import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from epidemic import SI
parser = argparse.ArgumentParser(description="SI spreading")
parser.add_argument('--t', type=int, default=40, help="time")
#重复n次实验，每一次实验中的迭代次数为t，重复20轮实验，每次实验中的迭代次数为120次
parser.add_argument('--n', type=int, default=1, help="run")
parser.add_argument('--seed', type=int, default=0)
# 感染速率0.2
parser.add_argument('--infected_rate', type=float, default=0.2)
# 实验参数
# 将初始感染节点等比例分为三部分I_M,I_P,I_N'''
#I_M最初始感染密度----.0.005--中立
parser.add_argument('--init_im', type=float, default=0.005, help=" ")
#I_P最初始感染密度----.0.005--积极
parser.add_argument('--init_ip', type=float, default=0.005, help=" ")
#I_N最初始感染密度----.0.005--消极
parser.add_argument('--init_in', type=float, default=0.005, help=" ")
# 不同类型的事件具有不同的事件敏感性，初始分为极端事件和中立事件。极端事件：积极情绪主导的事件和消极情绪引导的事件，分别赋值-1，0，1代表三类不同的事件
# 积极事件1,中立0，消极-1
parser.add_argument('--S_e', type=int, default=1)
# 整个网络中所有节点的总情绪值
parser.add_argument('--T_e', type=float, default=0.0)
# 整个网络的平均情绪值
parser.add_argument('--E_m', type=float, default=0.0)
# 定义五个信息片段的S_List=[[[1,2,3,...,n],[],[],,,,,,,,,,,,,[]],信息片段1，n次迭代每一次迭代的S状态的节点集合  [[1,2,3,...,n],[],[],,,,,,,,,,,,,[]],信息片段2，n次迭代后的S状态的节点集合，，，，[[1,2,3,...,n],[],[],,,,,,,,,,,,,[]],信息片段5，n次迭代后的S状态的节点集合]
# 这个地方明天再看看
parser.add_argument('--S_List', type=list, default=[])
# 定义五个信息片段的I_List=[[[],[1],[1,8,9],[1,8,9,20],,,,,,[1,2,3,4,5,....,n]],信息片段1，n次迭代每一次迭代的I状态的节点集合  [],[],[],[]]
parser.add_argument('--I_List', type=list, default=[])
# 信息片段数frag_nums = 5
parser.add_argument('--frag_nums', type=int, default=5)
conf = parser.parse_args()
graph= nx.generators.random_graphs.barabasi_albert_graph(5000, 3)
nx.write_gexf(graph, "BA-original-1.gexf")

#最后经过一系列连边之后

if __name__ == '__main__':
#
# si模型
    si = SI(graph, conf)
    infected_M, infected_N, infected_P,S_List,= si.spread(flags=True)
    nx.write_gexf(graph, "BA-final-1.gexf")
    plt.plot(infected_M, label="Im")
    plt.xlabel('t')
    plt.ylabel('p(t)')
    plt.legend()
    plt.show()

