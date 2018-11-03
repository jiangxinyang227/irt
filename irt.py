from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
from functools import reduce

import pymc as pm
import numpy as np

from generateMatrix import GenerateMatrix


D = 1.7
NUM_THETAS = 1  # 学生能力参数theta的个数

if os.path.exists("npData/labelMatrix.npy"):
    print('enter')
    labelMatrix = np.load("npData/labelMatrix.npy")
else:
    # 实例化生成数据对象
    generateMatrix = GenerateMatrix("data/rawData.xlsx")
    # 得到二分矩阵
    labelMatrix = generateMatrix.getAchievementDetail(isSub=True, subjectName="数学")
    np.save("labelMatrix", labelMatrix)


# 得到二分矩阵的行数和列数（分别表示题目数量和学生数量）

numQuestion, numPeople = labelMatrix.shape
print(numQuestion, numPeople)
# 初始化theta，logA，b的值
theta_initial = np.zeros((NUM_THETAS, numPeople))
a_initial = np.ones((numQuestion, NUM_THETAS))
b_initial = np.zeros((numQuestion, NUM_THETAS))

# 构建参数theta，logA，b的建议分布采样, value是采样前的初始值
theta = pm.Normal("theta", mu=0, tau=1.1 ** 2, value=theta_initial)
a = pm.Lognormal("a", mu=0, tau=0.3 ** 2, value= a_initial)
b = pm.Normal("b", mu=0, tau=0.3 ** 2, value=b_initial)


@pm.deterministic  # 将先验标为一个定值
def irtModel(theta=theta, a=a, b=b):
    bs = np.repeat(b, numPeople, 1)
    prob = 1.0 / (1.0 + np.exp(D * (bs - np.dot(a, theta))))

    return prob


# 得到预测的结果，在这里irtModel代表了先验，value代表了观测值，labels是后验分布
labels = pm.Bernoulli("labels", p=irtModel, value=labelMatrix, observed=True)

mcmc = pm.MCMC([a, b, theta, labels])
aArrays = []
bArrays = []
thetaArrays = []
for i in range(1):
    print("chain: {}".format(i))
    mcmc.sample(40000)
    aArray_ = mcmc.trace("a")[:]
    bArray_ = mcmc.trace("b")[:]
    thetaArray_ = mcmc.trace("theta")[:]
    aArrays.append(aArray_)
    bArrays.append(bArray_)
    thetaArrays.append(thetaArray_)
aArray = reduce(lambda x, y: x+y, aArrays) / 1.
bArray = reduce(lambda x, y: x+y, bArrays) / 1.
thetaArray = reduce(lambda x, y: x+y, thetaArrays) / 1.
print(type(aArray))






