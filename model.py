#!/usr/bin/python
# -*- coding:utf-8 -*-
from __future__ import division, print_function, unicode_literals

import math
import random
import time
import enum

import networkx as nx
import numpy as np


def function(cls, *args):
    return cls.spread_n_time(*args)

class Info(enum.Enum):
    INFO_S = enum.auto()
    INFO1 = enum.auto()
    INFO2 = enum.auto()
    INFO3 = enum.auto()
    INFO4 = enum.auto()
    INFO5 = enum.auto()


class Model:
    def __init__(self, graph: nx.Graph, conf):
        self.graph = graph
        self.nodes = graph.nodes()
        if len(self.nodes) == 0:
            print("The graph has no nodes!")
        # 设置超参数
        self.set_hyperparameter(conf)
        # 设置传播参数
        self.set_epidemic_parameter(conf)

    def update_graph(self, graph:nx.Graph):
        self.graph = graph
        self.nodes = graph.nodes()

    def set_hyperparameter(self, conf):
        """设置传播超参数"""
        # 传播迭代次数（表示传播了n个周期）
        self.t = conf.t
        # 实验次数（表示重复实验次数）
        self.n = conf.n
        # 设置随机种子
        self.seed = conf.seed
        # 是否使用多进程
        self.flags = False
        # 显示参数，不参于传播
        self.__t = 0
        self.__n = 0
        self.__N = self.t * self.n
        self.__st = 0

    def set_epidemic_parameter(self, conf):
        """设置传播参数"""
        # 三种情感人群 初始感染比例
        self.init_im = conf.init_im
        self.init_ip = conf.init_ip
        self.init_in = conf.init_in
        # 事件类型
        self.S_e = conf.S_e
        # 整个网络的总情绪值
        self.T_e = conf.T_e
        # 整个网络的平均情绪值
        self.E_m = conf.E_m
        # 感染速率
        self.infected_rate = conf.infected_rate
        # 定义五个信息片段的S_List
        self.S_List = conf.S_List
        # 定义五个信息片段的I_List
        self.I_List = conf.I_List
        # 信息片段个数
        self.frag_nums = conf.frag_nums

    # 初始的S_List包含五个列表，代表五个信息片段中未知某个片段的节点集合
    # 统计节点i的信息量--论文公式
    # 初步设定五个信息片段：权重分别为3，1，1，3.5，1.5
    def infomation_acount_math(self, graph, i):
        q = 0
        if graph.nodes[i]["mass_frag"][0][0].count(1) != 0:
            q += math.sqrt(3) / 10
        if graph.nodes[i]["mass_frag"][0][0].count(2) != 0:
            q += math.sqrt(1) / 10
        if graph.nodes[i]["mass_frag"][0][0].count(3) != 0:
            q += math.sqrt(1) / 10
        if graph.nodes[i]["mass_frag"][0][0].count(4) != 0:
            q += math.sqrt(3.5) / 10
        if graph.nodes[i]["mass_frag"][0][0].count(5) != 0:
            q += math.sqrt(1.5) / 10
        else:
            graph.nodes[i]["mass_count"] = 0
        graph.nodes[i]["mass_count"] = q
        # 保留四位小数
        q = round(q, 4)
        return q

    # 统计节点i的稀有性
    def infomation_rarity_math(self, i):
        r = 0
        if self.nodes[i]["mass_frag"][0][0].count(1) != 0:
            r += math.log((1 + (1 / 0.5)), math.e)
        if self.nodes[i]["mass_frag"][0][0].count(2) != 0:
            r += math.log((1 + (1 / 0.7)), math.e)
        if self.nodes[i]["mass_frag"][0][0].count(3) != 0:
            r += math.log((1 + (1 / 0.9)), math.e)
        if self.nodes[i]["mass_frag"][0][0].count(4) != 0:
            r += math.log((1 + (1 / 0.2)), math.e)
        if self.nodes[i]["mass_frag"][0][0].count(5) != 0:
            r += math.log((1 + (1 / 0.4)), math.e)
        else:
            self.nodes[i]["mass_rarity"] = 0
        self.nodes[i]["mass_rarity"] = r
        # 保留四位小数
        r = round(r, 4)
        return r

    def set_initial_condition(self):
        """初始化网络节点状态
        Returns:
            set -- 初始感染集合
        """
        # 生成5000个符合幂律分布(帕累托分布)的数据
        from scipy.stats import pareto

        np.random.seed(0)
        b = 4
        mean, var, skew, kurt = pareto.stats(b, moments="mvsk")
        x = np.linspace(pareto.ppf(0.01, b), pareto.ppf(0.99, b), 100)
        rv = pareto(b)
        vals = pareto.ppf([0.001, 0.5, 0.999], b)
        np.allclose([0.001, 0.5, 0.999], pareto.cdf(vals, b))
        A = pareto.rvs(b, size=5000)
        # 初始化节点的各个参数
        for i in self.nodes:
            node = self.nodes[i]
            node.node_state:Info = Info.INFO_S
            # 将符合幂律分布(帕累托分布)的数据赋给5000个节点'
            node.active = A[i]
            # 节点i已知的信息片段列表，初始为空
            node.mass_frag = []
            # 节点i的信息耦合值
            node.mass_count = 0
            #  节点i的信息稀有性
            node.mass_rarity = 0
            #  节点i的自我认知产生的情感值
            node.node_Es = 0
            #  周围邻居节点对节点i的情绪值的影响
            node.node_En = 0
            # 节点i的情感值
            node.emotion_value = 0
        self.number_nodes = len(self.nodes)
        a = []
        # 调用change_state函数将初始感染节点等比例分为三部分:中立I_M, 积极I_P, 消极IN
        infected_M = self.change_state(self.nodes, self.init_im, "I_M")
        infected_P = self.change_state(self.nodes, self.init_ip, "I_P")
        infected_N = self.change_state(self.nodes, self.init_in, "I_N")
        # infected_M类型为集合set()将集合set转换为列表list[]
        a = list(infected_M)
        print("a", len(a))
        b = list(infected_P)
        print("b", len(b))
        c = list(infected_N)
        print("c", len(c))
        infect_List = a + b + c
        print("初始Im+Ip+In", infect_List)
        print("初始Im+Ip+In长度", len(infect_List))
        # 中立情感的节点
        for i in infected_M:
            # 在节点i的信息片段列表中加入1，2
            b = [[1, 2], None, None]
            self.graph.nodes[i]["mass_frag"].append(b)
            # self.graph.nodes[i]['mass_frag'][0][0]-列表里面是存放的是该节点已知的信息片段1，2
            # print('frag',self.graph.nodes[i]['mass_frag'][0][0])
            # 用随机种子固定每次生成的情感值是一样的
            random.seed(0)
            # 赋值一个（-0.8，0.8）的情感值，保留四位小数
            self.graph.nodes[i]["emotion_value"] = round(random.uniform(-0.8, 0.8), 4)
            # 计算节点i的信息量
            self.graph.nodes[i]["mass_count"] = self.infomation_acount_math(
                self.graph, i
            )
            # print('count',self.graph.nodes[i]['mass_count'])
            # 计算节点i的稀有性
            self.graph.nodes[i]["mass_rarity"] = self.infomation_rarity_math(
                self.graph, i
            )
            # print('rarity', self.graph.nodes[i]['mass_rarity'])
        #  积极情感的节点
        for i in infected_P:
            # 在节点i的信息片段列表中加入1，2
            b = [[1, 2], None, None]
            self.graph.nodes[i]["mass_frag"].append(b)
            # self.graph.nodes[i]['mass_frag'][0][0]-列表里面是存放的是该节点已知的信息片段1，2
            # print('frag', self.graph.nodes[i]['mass_frag'][0][0])
            # 赋值一个（-0.8，0.8）的情感值，保留四位小数
            random.seed(0)
            self.graph.nodes[i]["emotion_value"] = round(random.uniform(0.8, 1), 4)
            # 计算节点i的信息量
            self.graph.nodes[i]["mass_count"] = self.infomation_acount_math(
                self.graph, i
            )
            # print('count', self.graph.nodes[i]['mass_count'])
            # 计算节点i的稀有性
            self.graph.nodes[i]["mass_rarity"] = self.infomation_rarity_math(
                self.graph, i
            )
            # print('rarity', self.graph.nodes[i]['mass_rarity'])
        # 消极情感的节点
        for i in infected_N:
            # 在节点i的信息片段列表中加入1，2
            b = [[1, 2], None, None]
            self.graph.nodes[i]["mass_frag"].append(b)
            # self.graph.nodes[i]['mass_frag'][0][0]-列表里面是存放的是该节点已知的信息片段1，2
            # print('frag', self.graph.nodes[i]['mass_frag'][0][0])
            # 赋值一个（-1,-0.8）的情感值，保留四位小数
            random.seed(0)
            self.graph.nodes[i]["emotion_value"] = round(random.uniform(-1, -0.8), 4)
            # 计算节点i的信息量
            self.graph.nodes[i]["mass_count"] = self.infomation_acount_math(
                self.graph, i
            )
            # print('count', self.graph.nodes[i]['mass_count'])
            # 计算节点i的稀有性
            self.graph.nodes[i]["mass_rarity"] = self.infomation_rarity_math(
                self.graph, i
            )
            # print('rarity', self.graph.nodes[i]['mass_rarity'])
        # 这个地方有问题--相加的 时候节点的属性没有加进去

        frag_nums = self.frag_nums
        print("frag_nums", frag_nums)
        t = self.t

        # S_list[x][y]   x 代表迭代次数   y中[0-5],0代表S状态的节点，1代表已知信息片段1的节点，2代表已知信息片段2的节点，
        # 3代表已知信息片段3的节点，.4代表已知信息片段4的节点，5代表已知信息片段5的节点
        # 网络中所有的节点编号的列表
        print("self.nodes", self.nodes)
        print(infect_List)
        # data_s一个存放数据的集合，
        data_s = []
        data_s.append(list(set(self.nodes) - set(infect_List)))  # 0
        data_s.append(infect_List)  # 1
        data_s.append(infect_List)
        data_s.append([])
        data_s.append([])
        data_s.append([])  # 5
        print("data_s", data_s)
        # [[1,...,5000]存放的s状态的节点,[infect_list],信息片段1的感染列表 [infect_list],信息片段2的感染列表，[],[],[]信息片段3、4、5的感染列表]
        self.S_List.append(data_s)
        # S_List是在data_s的外面再加一个大括号
        # [[[1,...,5000]存放的s状态的节点,[infect_list],信息片段1的感染列表 [infect_list],信息片段2的感染列表，[],[],[]信息片段3、4、5的感染列表]]
        """从信息片段1、2的S_List中移除这些节点"""
        """从信息片段1、2的I_List中添加这些节点"""
        print("infect_List长度", len(infect_List))
        # 现有的infect_List 内所有节点的总情绪值self.T_e
        T_e = self.T_e
        print("类型", type(T_e))
        E_m = self.E_m
        #
        for i in infect_List:
            T_e = T_e + self.graph.nodes[i]["emotion_value"]
        print("T_E", T_e)
        #
        print("初始总情感值", T_e)
        E_m = T_e / (len(infect_List))
        print("初始网络情感平均值", E_m)
        

        return infected_M, infected_N, infected_P, self.S_List

    # 想一下这里的返回值，应该传进epidemic的 是I_List,还是I_List[0],还是I_List[0][0],？？？其中I_List[0][0]代表信息片段1第一次迭代为I状态的集合
    def search_nearest_neighbor(self, source_set, state):
        """寻找邻居集合"""
        # 目标节点集合
        target = set()
        for node in source_set:
            target.update(
                [
                    v
                    for v in self.graph.neighbors(node)
                    if self.graph.nodes[v]["node state"] == state
                ]
            )
        else:
            if len(target) == 0:
                print("There isn't a {} node is found.".format(len(target)))
        # print(len(target))
        return target

    # 寻找信息片段1中未被感染的节点，，，，，寻找信息片段5中未被感染的节点
    def search_nearest_neighbor_1(self, source_set, state):
        """寻找邻居集合"""
        # 目标节点集合
        target = set()
        for node in source_set:
            v_set = []
            for v in self.graph.neighbors(node):
                if self.graph.nodes[v]["mass_frag"] == []:
                    v_set.append(v)
                else:
                    if state not in self.graph.nodes[v]["mass_frag"][0][0]:
                        v_set.append(v)
            target.update(v_set)
            # print('ta',target)
        else:
            if len(target) == 0:
                print("There isn't a {} node is found.".format(len(target)))
        # print(len(target))
        return target

    # zx
    # def search_state_nodes(self, state):
    #     """寻找全局网络中指定状态的所有节点
    #     return 指定状态的节点集合
    #     """
    #     target = set()
    #     target.update([v for v in self.nodes if self.node_state[v] == state])
    #     return target

    def change_state(self, nodes, scale, to_state):
        """转变状态
        return 转换后集合
            nodes {set} -- 节点集合
            scale {float64} -- 转化比例，注意获得列表大小是最接近len(nodes) * scale 的整数。
            to_state {string} -- 将变化成的状态
        """
        to_nodes = random.sample(
            nodes, int(len(nodes) * scale)
        )  # 从nodes中取int(len(nodes) * scale)个元素
        for node in to_nodes:
            self.graph.nodes[node]["node state"] = to_state

        return set(to_nodes)

    # 找到信息片段1未被感染的节点，按照一定的概率将其转变为已知信息片段1状态，，，，找到信息片段5未被感染的节点，按照一定的概率将其转变为已知信息片段5状态，
    def change_state_1(self, nodes, scale, to_state):
        """转变状态
        return 转换后集合
            nodes {set} -- 节点集合
            scale {float64} -- 转化比例，注意获得列表大小是最接近len(nodes) * scale 的整数。
            to_state {string} -- 将变化成的状态
        """
        to_nodes = random.sample(
            nodes, int(len(nodes) * scale)
        )  # 从nodes中取int(len(nodes) * scale)个元素
        for node in to_nodes:
            if self.graph.nodes[node]["mass_frag"] == []:
                a = [[to_state], None, None]
                self.graph.nodes[node]["mass_frag"].append(a)
            else:
                self.graph.nodes[node]["mass_frag"][0][0].append(to_state)

        return set(to_nodes)

    #  这里定义一个选取节点启示编号的函数？----这个地方要修改zx
    # 这个地方要改成 S_List[frag_num]把one_dim里面的节点放进去，因为上面描述了S_List[0]存放的是S状态的节点
    # S_List[1]代表信息片段1的感染列表（已知信息片段1的节点集合），，，，S_List[5]代表信息片段5的感染列表（已知信息片段5的节点集合），
    def random_infect(self, graph, frag_num, iterm, node_a):
        # 传进来信息片段编号，
        one_dim = [node_a]
        print(one_dim, "one_dim")
        # 这个地方写的对不对？意思是将该初始启示编号的列表one_dim添加到该片段的感染列表里面
        self.S_List[frag_num] = one_dim
        # 下面是遍历启示编号中的每一个节点，将其状态变为已知者，且在该节点的['mass_frag'][0][0]中添加进去该片段
        for i in one_dim:
            # graph.nodes[i]['node state'] = frag_num
            graph.nodes[i]["mass_frag"][0][0].append(frag_num)

    # zx 自己定义了一个信息片段的启示函数
    def info_star(self, graph, t):
        # print('S_List[1]', self.S_List[1])
        frag_num = 1
        for i in range(self.frag_nums):
            # 如果S_List[frag_num]里面没有节点，即代表该信息片段frag_num还未开始传播，infe_num = len(self.S_List[frag_num])
            # 这里报错，IndexError: list index out of range，原因1、index超出范围 2、list是空的，没有一个元素
            # 但是S_List[]
            # print("S_List[frag_num]", self.S_List[frag_num])
            infe_num = len(self.S_List[frag_num])
            if infe_num == 0 and frag_num == 3 and (40 - t) == 4:
                node_a = 25  # 信息片段3的启示节点编号
                self.random_infect(self.graph, frag_num, (40 - t), node_a)
            if infe_num == 0 and frag_num == 4 and t == 11:
                node_b = 10  # 信息片段4的启示节点编号
                self.random_infect(self.graph, frag_num, (40 - t), node_b)
            if infe_num == 0 and frag_num == 5 and (40 - t) == 17:
                node_c = 101  # 信息片段5的启示节点编号
                self.random_infect(self.graph, frag_num, (40 - t), node_c)
            frag_num += 1

    def spread_one_time(self, infected_M, infected_N, infected_P, S_List, seed=None):
        """实验一次"""
        if seed is not None:
            random.seed = seed
        infected_M_distance = [len(infected_M) / self.number_nodes]
        infected_N_distance = [len(infected_N) / self.number_nodes]
        infected_P_distance = [len(infected_P) / self.number_nodes]
        # 40
        t = self.t
        self.__t = 0
        while t:
            # 信息片段3在第5轮次传播，信息片段4在第12轮次传播，信息片段5在第18轮次传播，分别设定每个信息片段的传播启示编号。
            # zx 这个能这样写吗,下面这样写感觉不对，t=40开始,39,38,,,,5,4,3,2,1,感觉这里应该定义一个函数然后去调用
            # 现在这个
            self.info_star(self, t)
            # frag_num = 1
            # for i in range(self.frag_nums):
            #     # 如果S_List[frag_num]里面没有节点，即代表该信息片段frag_num还未开始传播，infe_num = len(self.S_List[frag_num])
            #     print('S_List[frag_num]',self.S_List[frag_num])
            #     infe_num = len(self.S_List[frag_num])
            #     if infe_num == 0 and frag_num == 3 and (40-t) == 5:
            #         node_a = 25  # 信息片段3的启示节点编号
            #         self.random_infect(self.graph, frag_num, (40-t), node_a)
            #     if infe_num == 0 and frag_num == 4 and t == 12:
            #         node_b = 10  # 信息片段4的启示节点编号
            #         self.random_infect(self.graph, frag_num, (40-t), node_b)
            #     if infe_num == 0 and frag_num == 5 and (40-t) == 18:
            #         node_c = 101  # 信息片段5的启示节点编号
            #         self.random_infect(self.graph, frag_num, (40-t), node_c)
            #     frag_num += 1
            # zx
            infected_M, infected_N, infected_P, one_S_List, = self.epidemic(
                infected_M, infected_N, infected_P, S_List[40 - t], self.nodes
            )
            self.S_List.append(one_S_List)
            infected_M_distance.append(len(infected_M) / self.number_nodes)
            infected_N_distance.append(len(infected_N) / self.number_nodes)
            infected_P_distance.append(len(infected_P) / self.number_nodes)
            print(
                "传播轮次",
                41 - t,
            )
            # print("该轮Im的感染密度",infected_M_distance)
            # print("该轮Ip的感染密度", infected_P_distance)
            # print("该轮In的感染密度", infected_N_distance)
            # # 每四轮保存一个图文件
            if (41 - t) % 10 == 0:
                print("记录文件的轮次", 41 - t)
                nx.write_gexf(self.graph, "BA_1第%d轮.gexf" % (41 - t))
            t -= 1
            self.__t += 1
        return (
            np.asarray(infected_M_distance),
            np.asarray(infected_P_distance),
            np.asarray(infected_N_distance),
        )

    def spread_n_time(self, n, seed):

        # """重复n次实验，每一次实验中的迭代次数为t

        n_infected_M_distance, n_infected_N_distance, n_infected_P_distance = (
            np.zeros(self.t + 1),
            np.zeros(self.t + 1),
            np.zeros(self.t + 1),
        )
        print("n", n)
        while n:

            infected_M, infected_N, infected_P, S_List = self.set_initial_condition()
            (
                n_infected__M_distance_temp,
                n_infected__N_distance_temp,
                n_infected__P_distance_temp,
            ) = self.spread_one_time(
                infected_M, infected_N, infected_P, S_List, seed=seed
            )
            n_infected_M_distance += n_infected__M_distance_temp
            n_infected_N_distance += n_infected__N_distance_temp
            n_infected_P_distance += n_infected__P_distance_temp
            print(
                "实验次数",
                2 - n,
            )
            # # 每五轮保存一个图文件
            #   if (21- n) % 1 == 0:
            #       nx.write_gexf(self.graph, "5000-3-0.2-0.0005第%d次实验.graph.gexf" % (21 - n))
            n -= 1
            self.__n += 1
        return n_infected_M_distance, n_infected_N_distance, n_infected_P_distance

    def spread(self, seed=None, flags=False):
        """一次完整的实验：
        重复n次实验，每次实验中迭代传播t次。
        """
        # start = time.clock()
        cores = 1
        self.flags = flags
        # 初始化数据
        infected_M_distance, infected_N_distance, infected_P_distance, = (
            np.zeros(self.t + 1),
            np.zeros(self.t + 1),
            np.zeros(self.t + 1),
        )
        if seed is None and self.seed is not None:
            seed = self.seed
        print("传播速度为{}时：".format(self.infected_rate))
        self.__st = time.perf_counter()

        number = self.n
        (
            infected_M_distance_temp,
            infected_N_distance_temp,
            infected_P_distance_temp,
        ) = self.spread_n_time(number, seed)
        infected_M_distance += infected_M_distance_temp
        infected_N_distance += infected_N_distance_temp
        infected_P_distance += infected_P_distance_temp
        infected_M_distance = infected_M_distance / float(self.n)
        infected_N_distance = infected_N_distance / float(self.n)
        infected_P_distance = infected_P_distance / float(self.n)
        print("使用核心数：{}".format(cores))
        return infected_M_distance, infected_N_distance, infected_P_distance
