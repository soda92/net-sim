#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division, print_function, unicode_literals
import networkx as nx
import numpy as np
from model import Model
class SI(Model):
    def __init__(self,graph, conf):
        # 对于super(B, self).__init__()是这样理解的：super(B, self)
        # 首先找到B的父类（就是类A），然后把类B的对象self转换为类A的对象（通过某种方式，一直没有考究是什么方式，惭愧），然后“被转换”的类A对象调用自己的__init__函数。
        super(SI, self).__init__(graph, conf)
    def epidemic(self,infected_M,infected_N,infected_P,S_List,all_nodes):
    #     """思路：
    #     1.找到当前感染者的健康邻居列表L（只有这些节点才能被感染者感染）
    #     2.按照感染率随机选取L中的部分节点感染
    #     3.刷新感染节点集合

        '''这里不对，到时候再改'''
    #  S_List = [6*[]] 0-5
        # 【1，2，3，4，5】  `1 ，周围 没有1 的节点
        # 1 :
        # print('epidemic_SList',S_List)
        # 这个代表什么？输出
        # epidemic_SList [[], [0,,,,4999], [0,,,,4999], [], [], []]
        next_S_List = []
        print('epidemic_SList[0]', S_List[0])
        print('epidemic_SList[1]', S_List[1])
        print('Len_epidemic_SList[0]', len(S_List[0]))
        print('Len_epidemic_SList[1]', len(S_List[1]))
        # print('epidemic_SList[2]', S_List[2])
        # print('epidemic_SList[3]', S_List[3])
        # print('epidemic_SList[4]', S_List[4])
        # print('epidemic_SList[5]', S_List[5])

        # 这个函数是 S_List[1]代表已知信息片段1的列表，寻找未知信息片段1的节点，按照一定的概率将其感染为已知信息片段1
        next_S_set_1 = self.change_state_1(self.search_nearest_neighbor_1(set(S_List[1]),1) ,self.infected_rate,1)
        print('epidemic_next_S_set_1 ',  next_S_set_1 )
        # 这个函数是 S_List[2]代表已知信息片段2的列表，寻找未知信息片段2的节点，按照一定的概率将其感染为已知信息片段2
        next_S_set_2 = self.change_state_1(self.search_nearest_neighbor_1(set(S_List[2]),2),self.infected_rate,2)
        next_S_set_3 = self.change_state_1(self.search_nearest_neighbor_1(set(S_List[3]), 3), self.infected_rate, 3)
        next_S_set_4 = self.change_state_1(self.search_nearest_neighbor_1(set(S_List[4]), 4), self.infected_rate, 4)
        next_S_set_5 = self.change_state_1(self.search_nearest_neighbor_1(set(S_List[5]), 5), self.infected_rate, 5)
        # 最新一轮已知信息片段1的节点+最新一轮已知信息片段2的节点+最新一轮已知信息片段3的节点+最新一轮已知信息片段4的节点+最新一轮已知信息片段5的节点
        new_change_set =(next_S_set_1|next_S_set_2|next_S_set_3|next_S_set_4|next_S_set_5)
        print('epidemic_new_change_set  ', new_change_set )
        # 从S列表里面去除这些节点
        next_set_s = set(S_List[0])-new_change_set
        print('epidemic_next_set_s',list(next_set_s))
        # 下面这一系列是更新S_List即将更新后的0-6[[],[],[],[],[],[]]存放在next_S_List中
        # 首先next_S_List[0]中存放的是更新后的S状态的节点
        next_S_List.append(list(next_set_s))  # 更新 s
        # 这个地方是把新感染的加入到原先的列表中
        next_set_1 = set(S_List[1]) | next_S_set_1
        # 将新一轮已知信息片段1的节点与之前已知信息片段1的节点放在一起，将其存放在next_S_List[1]中
        next_S_List.append(list(next_set_1))
        next_set_2 = set(S_List[2])|next_S_set_2
        next_S_List.append(list(next_set_2))
        next_set_3 = set(S_List[3]) | next_S_set_3
        next_S_List.append(list(next_set_3))
        next_set_4 = set(S_List[4]) | next_S_set_4
        next_S_List.append(list(next_set_4))
        next_set_5 = set(S_List[5]) | next_S_set_5
        # print('epidemic_next_set_5',list(next_set_5 ) )
        next_S_List.append(list(next_set_5))
        print('epidemic_next_S_List', next_S_List)
        # next_S_List.append(list(set(S_List[2]).update(next_S_set_2)))
        # next_S_List.append(list(set(S_List[3]).update(next_S_set_3)))
        # next_S_List.append(list(set(S_List[4]).update(next_S_set_4)))
        # next_S_List.append(list(set(S_List[5]).update(next_S_set_5)))
        # next_set_s 里面存放的是没有感染任何信息片段的节点，即cal_set 里面存放是是知道1，2，3，4，5任意一个片段或者任意n个片段的节点，即知道该事件的节点
        # 这个集合是S_List里面除去已知信息片段的节点集合，（即已知一个信息片段或n个信息片段的集合）
        cal_set = set(all_nodes) - next_set_s
        # 遍历cal_set这个集合 计算情感值,把其划分为什么状态Im,In,Ip
        new_infected_1 = self.change_state(self.search_nearest_neighbor(infected_M, "S"),
                                         scale = self.infected_rate,
                                         to_state = "Im")

        new_infected_M = self.change_state(self.search_nearest_neighbor(infected_M, "S"),
                                         scale = self.infected_rate,
                                         to_state = "Im")

        self.update_graph(self.graph)
        infected_M.update(new_infected_M)
        # infected_N.update(new_infected_N)
    #         # infected_P.update(new_infected_P)
    #     suspected = set(self.graph.nodes()) - infected_M-infected_N-infected_P
        indesity =len(infected_M)/ len(set(self.graph.nodes()))
        return infected_M,infected_N,infected_P ,next_S_List,

