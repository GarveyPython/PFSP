import random  
import math  
import copy  
import time  
random.seed(1)  
import matplotlib.pyplot as plt  
from get_data import get_data  
from solution import Solution  
from fuzzy_operators import rank, value  
  
plt.rcParams['font.sans-serif'] = ['SimHei']  # 显示中文  
  
  
# 交换函数  
def swap(a, b):  
    temp = a  
    a = b  
    b = temp  
    return a, b  
  
  
# 局部搜索函数(两位置交换排序法)  
def localSearch(solution, dispatch_lst, makespan):  
    first_dispatch_lst = dispatch_lst[0][0][0]  
    for t in range(len(first_dispatch_lst) - 1):  
        for i in range(t + 1, len(first_dispatch_lst)):  
            tmp_first_dispatch_lst = copy.deepcopy(first_dispatch_lst)  
            tmp_first_dispatch_lst[t], tmp_first_dispatch_lst[i] = swap(tmp_first_dispatch_lst[t],  
                                                                        tmp_first_dispatch_lst[i])  
            tmp_encoder, tmp_obj = solution.decode(tmp_first_dispatch_lst)  
            if rank(tmp_obj, makespan) == makespan:  
                dispatch_lst = tmp_encoder  
                makespan = tmp_obj  
    return dispatch_lst, makespan  
  
  
# 更新温度的函数  
def update_temperature(base_T, anneal_F, set_iteration, iteration):  
    return base_T * math.exp(-anneal_F * (set_iteration - iteration))  
  
  
# 邻域搜索函数  
def reverseSubsequence(solution, dispatch_lst):  
    first_dispatch_lst = dispatch_lst[0][0][0]  
    i, j = sorted(random.sample(range(len(first_dispatch_lst)), 2))  
    new_first_dispatch_lst = first_dispatch_lst[:i] + first_dispatch_lst[i:j + 1][::-1] + first_dispatch_lst[j + 1:]  
    new_dispatch_lst, new_makespan = solution.decode(new_first_dispatch_lst)  
    return new_dispatch_lst, new_makespan  
  
  
# 全局搜索函数(模拟退火法)  
def globalSearch(solution, base_T, anneal_F, iteration,begin):  
    dispatch_lst = solution.encoder  
    makespan = solution.obj  
    x_lst = [i for i in range(1, iteration + 1)]  
    y_lst = []  
    set_base_T = base_T  
    set_iteration = iteration  
    flag = 1  
    while iteration > 0:  
        get_dispatch_lst, get_makespan = reverseSubsequence(solution, dispatch_lst)  
        if rank(get_makespan, makespan) == makespan:  
            # 局部搜索  
            up_dispatch_lst, up_makespan = localSearch(solution, dispatch_lst, makespan)  
            # 更新最优调度方案  
            dispatch_lst, makespan = up_dispatch_lst, up_makespan  
        else:  
            delta_f = value(makespan) - value(get_makespan)  
            temperature = update_temperature(set_base_T, anneal_F, set_iteration, iteration)  
            cal_p = math.exp(delta_f / temperature)  
            rand_number = random.random()  
            # 以一定概率选择劣解  
            if cal_p > rand_number:  
                # 局部搜索  
                up_dispatch_lst, up_makespan = localSearch(solution, dispatch_lst, makespan)  
                if rank(up_makespan, makespan) == makespan:  
                    # 更新最优调度方案  
                    dispatch_lst, makespan = up_dispatch_lst, up_makespan  
        y_lst.append(value(makespan))  
        iteration -= 1  
        print(f"iteration{flag} fuzzy makespan{makespan}")  
        flag += 1  
    print(f"算法共运行{time.time() - begin}s")  
    plt.plot(x_lst, y_lst, linewidth=1, linestyle="solid")  
    plt.text(set_iteration - 1, value(makespan) + 10, str(int(value(makespan))), fontsize=10, color='black')  
    plt.title('算法迭代图')  
    plt.xlabel('迭代次数')  
    plt.ylabel('最大模糊完工时间')  
    plt.show()  
    solution.encoder = dispatch_lst  
    solution.obj = makespan  
    solution.draw_fuzzy_gantt()  
    return dispatch_lst, makespan  
  
  
if __name__ == '__main__':  
    inst = 'data/k6_l6_C_t5.json'  # Extract from Taillard50x20_5  
    job_num, machine_num, stage_num, layer_num, layer_stage_list, machines, layer_ava_machines, new_release_list = get_data(  
        inst)  
    release_code = 'interval100_q5'  
    release_dict = new_release_list[release_code]  
    begin = time.time()  
    solution = Solution(job_num, stage_num, machine_num, layer_stage_list, layer_ava_machines, machines, release_dict)  
    res_DispatchList, res_makespan = globalSearch(solution, 100, 0.02, 100, begin)  
