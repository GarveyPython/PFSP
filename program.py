import random
import math
import copy
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文
color = ['blue', 'purple', 'green', 'red', 'lawngreen', 'yellow', 'pink', 'brown', 'orange', 'cyan', 'magenta', 'teal', 'coral']


# 计算完工时间的函数
def cal_makespan(data, dispatch_lst, render=False):
    if render:
        plt.figure(figsize=(20, 8), dpi=300)
        x_tricks = []
        x_tricks.append(0)
        y_tricks = [f"M{j}" for j in range(1, len(data[0]) + 1)]
        y_tricks.insert(0, "")
        plt.yticks([j for j in range(len(data[0]) + 1)], y_tricks)
    # 工件的开始加工时间列表
    start_time_lst = [0 for _ in range(len(dispatch_lst))]
    # 工件的结束加工时间列表
    end_time_lst = [0 for _ in range(len(dispatch_lst))]
    for j in range(len(data[0])):
        for i in range(len(dispatch_lst)):
            if j == 0:
                start_time_lst[dispatch_lst[i]] = end_time_lst[dispatch_lst[i - 1]] if i > 0 else 0
                end_time_lst[dispatch_lst[i]] = start_time_lst[dispatch_lst[i]] + data[dispatch_lst[i]][j]
                if render:
                    plt.barh(j + 1, data[dispatch_lst[i]][j], height=1, left=start_time_lst[dispatch_lst[i]],
                             align='center', color=color[dispatch_lst[i]], edgecolor='grey')
            else:
                tmp_start_point = max(end_time_lst[dispatch_lst[i]], end_time_lst[dispatch_lst[i - 1]]) if i > 0 else \
                end_time_lst[dispatch_lst[i]]
                end_time_lst[dispatch_lst[i]] = tmp_start_point + data[dispatch_lst[i]][j]
                if render:
                    plt.barh(j + 1, data[dispatch_lst[i]][j], height=1, left=tmp_start_point, align='center',
                             color=color[dispatch_lst[i]], edgecolor='grey')
                    if j==len(data[0])-1:
                        plt.text(tmp_start_point+5, j + 1, f"J{dispatch_lst[i] + 1}")
    cmax = max(end_time_lst)
    if render:
        plt.title('调度甘特图')
        x_tricks.append(cmax)
        plt.xticks(x_tricks)
        plt.axvline(cmax, color='r', linestyle='--')
        plt.show()
        print(start_time_lst)
        print(end_time_lst)
    return cmax


# 随机生成一个初始解
def preDispatch(data):
    pre_dispatch_lst = [i for i in range(len(data))]
    random.shuffle(pre_dispatch_lst)
    return pre_dispatch_lst, cal_makespan(data, pre_dispatch_lst)


# 交换函数
def swap(a, b):
    temp = a
    a = b
    b = temp
    return a, b


# 局部搜索函数(两位置交换排序法)
def localSearch(data, dispatch_lst):
    for t in range(len(dispatch_lst) - 1):
        for i in range(t + 1, len(dispatch_lst)):
            tmp_dispatch_lst = copy.deepcopy(dispatch_lst)
            tmp_dispatch_lst[t], tmp_dispatch_lst[i] = swap(tmp_dispatch_lst[t], tmp_dispatch_lst[i])
            if cal_makespan(data, tmp_dispatch_lst) < cal_makespan(data, dispatch_lst):
                dispatch_lst = tmp_dispatch_lst
    return dispatch_lst, cal_makespan(data, dispatch_lst)


# 更新温度的函数
def update_temperature(base_T, anneal_F, set_iteration, iteration):
    return base_T * math.exp(-anneal_F * (set_iteration - iteration))


# 邻域搜索函数
def reverseSubsequence(data, dispatch_lst):
    i, j = sorted(random.sample(range(len(dispatch_lst)), 2))
    new_dispatch_lst = dispatch_lst[:i] + dispatch_lst[i:j + 1][::-1] + dispatch_lst[j + 1:]
    new_makespan = cal_makespan(data, new_dispatch_lst)
    return new_dispatch_lst, new_makespan


# 全局搜索函数(模拟退火法)
def globalSearch(data, dispatch_lst, makespan, base_T, anneal_F, iteration):
    x_lst = [i for i in range(1, iteration + 1)]
    y_lst = []
    set_base_T = base_T
    set_iteration = iteration
    while iteration > 0:
        get_dispatch_lst, get_makespan = reverseSubsequence(data, dispatch_lst)
        if get_makespan <= makespan:
            # 局部搜索
            up_dispatch_lst, up_makespan = localSearch(data, get_dispatch_lst)
            # 更新最优调度方案
            dispatch_lst, makespan = up_dispatch_lst, up_makespan
        else:
            delta_f = makespan - get_makespan
            temperature = update_temperature(set_base_T, anneal_F, set_iteration, iteration)
            cal_p = math.exp(delta_f / temperature)
            rand_number = random.random()
            # 以一定概率选择劣解
            if cal_p > rand_number:
                # 局部搜索
                up_dispatch_lst, up_makespan = localSearch(data, get_dispatch_lst)
                if up_makespan < makespan:
                    # 更新最优调度方案
                    dispatch_lst, makespan = up_dispatch_lst, up_makespan
        y_lst.append(makespan)
        iteration -= 1
    plt.plot(x_lst, y_lst, linewidth=1, linestyle="solid")
    plt.text(set_iteration - 1, makespan + 10, str(makespan), fontsize=10, color='black')
    plt.title('算法迭代图')
    plt.xlabel('迭代次数')
    plt.ylabel('最大完工时间')
    plt.show()
    return dispatch_lst, makespan


if __name__ == '__main__':
    # Car2 13x2 7166
    data = [[654, 147, 345, 447],
            [321, 520, 789, 702],
            [12, 147, 630, 255],
            [345, 586, 214, 866],
            [678, 532, 275, 332],
            [963, 145, 302, 225],
            [25, 24, 142, 589],
            [874, 517, 24, 996],
            [114, 896, 520, 541],
            [785, 543, 336, 234],
            [203, 210, 699, 784],
            [696, 784, 855, 512],
            [302, 512, 221, 345]]
    preDispatchList, makespan = preDispatch(data)
    res_DispatchList, res_makespan = globalSearch(data, preDispatchList, makespan, 100, 0.02, 40)
    print(res_DispatchList, res_makespan)
    cal_makespan(data, res_DispatchList, render=True)
