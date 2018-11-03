# coding = utf-8
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import xlrd
import pandas as pd
import numpy as np


SHEET_NAME_MAP = {
    "dataDemad": "数据要求",
    "examInfo": "考试信息",
    "testPaperInfo": "试卷信息",
    "studentInfo": "学生信息",
    "studentAchiInfo": "学生成绩信息",
    "achievementDetail": "成绩详情"
}


class GenerateMatrix(object):

    def __init__(self, excelName: str):
        self._excelName = excelName
        self._sheetNames = self._getSheetNames()

    def _getSheetNames(self) -> list:
        """
        得到excel文件中的sheet names
        :return:
        """
        workbook = xlrd.open_workbook(self._excelName)
        sheet_names = workbook.sheet_names()
        return sheet_names

    def extraSubjectId(self, subjectName: str, questionType: str):
        """
        提取某个科目或者某个科目特定问题的id
        :param subjectName: 科目名称
        :param questionType: 题目类型
        :return:
        """
        if SHEET_NAME_MAP["testPaperInfo"] in self._sheetNames:
            df = pd.read_excel(self._excelName, sheet_name=SHEET_NAME_MAP['testPaperInfo'])
            # 取出某些列，然后根据科目选择某些行
            subjectDf = pd.DataFrame(df, columns=["试题ID", "题型", "分值"])[subjectName and df.科目 == subjectName]

            # 筛选出想要的题型
            if questionType:
                subjectDf = subjectDf[subjectDf.题型 == questionType]

            subjectDf["C"] = subjectDf["题型"]
            questionTypeMapToC = {"选择题": 0.25, "填空题": 0, "判断题": 0.5, "解答题": 0}
            subjectDf["C"] = subjectDf["C"].map(questionTypeMapToC)  # 添加预测参数的值
            subjectDf["分值"] = subjectDf["分值"]  # 将题目的分值除以2，用于后面的类别标签

            return subjectDf

        else:
            raise Exception("{} not exist".format(SHEET_NAME_MAP['testPaperInfo']))

    def getAchievementDetail(self, isSub: bool=False, subjectName: str=None,
                             questionType: str=None, studentID: int=None):
        """
        得到行为学生，列为题目的得分矩阵
        :param isSub: 是否要选取某个科目的某个题型
        :param subjectName:科目名称
        :param questionType:题目类型
        :param studentID:学生ID
        :return:
        """
        df = pd.read_excel(self._excelName, sheet_name="成绩详情")
        subjectDf = self.extraSubjectId(subjectName, questionType)

        subjectID = list(set(df.题目ID.tolist()))

        if not studentID:
            studentID = list(set(df.学生ID.tolist()))

        if isSub:
            subjectID = subjectDf.试题ID.tolist()

        subjectScores = []
        for subject in subjectID:
            subjectScore = []
            questionScore = subjectDf.分值[subjectDf.试题ID == subject].tolist()[0]

            for student in studentID:
                # subjectScore += [0 if i < subjectDf.分值[subjectDf.试题ID == subject].tolist()[0] else 1
                #                  for i in df.题目得分[(df.学生ID == student) & (df.题目ID == subject)].tolist()]
                subjectScore += (df.题目得分[(df.学生ID == student) & (df.题目ID == subject)] / questionScore).tolist()

            subjectScores.append(subjectScore)
        return np.array(subjectScores)


