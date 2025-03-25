import numpy as np
from PyQt5.QtCore import QTime, QDate
# from PyQt5 import QtWidgets


class Graph:
    def __init__(self):
        self.num = 0
        self.name = ''
        self.date = ''
        self.time = ''
        self.freq = 100 * 10**(9)
        self.xAxis = np.linspace(0.01, 8192 * 0.01, endpoint=True, num=8192) #TODO по умолчанию для размера буффера 8192
        self.yAxis = []
        self.delimiter = ';'

    # DASdata_103809879_2024 - 10 - 10_15 - 27 - 52.090_100000000Hz_8192_.csv
    info_lines_in_file = 3  # Нужно, чтобы отсекать информацию о графике и сам график

    @staticmethod
    def get_num_cols(file_path):
        with open(file_path, 'r', encoding='utf-8-sig') as inp:
            line = inp.readline()
        return line.count(';')

    @staticmethod
    def convert_to_graph(file_path, date_format, time_format, x_axis=False):
        file_name = file_path[file_path.rfind("/") + 1:]
        # print("Converting " + file_name + " to graph... ")
        graph = Graph()
        info = file_name.split("_")
        if len(info) >= 4:
            graph.name = info[0] + info[1]
            graph.freq = info[4][:-2]
            graph.date = QDate.fromString(info[2], date_format)
            graph.time = QTime.fromString(info[3], time_format)
        else: #TODO сделать в более подходящем виде
            graph.name = info[0] + info[1]
            graph.freq = '-'
            graph.date = '-'
            graph.time = '-'
        num_cols = 1 #Graph.get_num_cols(file_path)
        if not x_axis:
            mat = np.loadtxt(file_path, delimiter=";",
                             encoding="utf-8-sig", usecols=tuple([i for i in range(num_cols)]),
                             converters=dict.fromkeys([i for i in range(num_cols)], lambda x: str(x).replace(',', '.')))
            if num_cols > 1:
                graph.yAxis = mat.mean(axis=1)  # среднее значение по строкам
            else:
                graph.yAxis = mat
        else:
            mat = np.loadtxt(file_path, delimiter=";",
                             encoding="utf-8-sig", usecols=tuple([i for i in range(num_cols)]),
                             converters=dict.fromkeys([i for i in range(num_cols)], lambda x: str(x).replace(',', '.')))
            if num_cols > 2:
                graph.xAxis = mat[:, 0]
                graph.yAxis = mat[:, 1:].mean(axis=1)  # среднее значение по строкам
            else:
                graph.xAxis = mat[:, 0]
                graph.yAxis = mat[:, 1]
        if len(info) >= 4: # TODO сейчас здесь кривое разделение на DVS и DAS
            graph.xAxis = np.linspace(0.01, len(graph.yAxis) * 0.01, endpoint=True, num=len(graph.yAxis))
        else:
            graph.xAxis = np.linspace(0.008, len(graph.yAxis) * 0.008, endpoint=True, num=len(graph.yAxis))
        return graph

    @staticmethod
    def find_graph_by_name(name, graphs: list):
        for item in graphs:
            if item.name == name:
                return item
        return False

    @staticmethod
    def create_matrix_with(items: list):
        pass #TODO возможно стоит придумать как это реализовать...
