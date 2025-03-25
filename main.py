import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QTime, QDate
from os import listdir
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
import numpy as np
# Добавление ui файлов
from Ui_files.MainWindow import Ui_MainWindow  # конвертированный файл дизайна
import Ui_files.WaterfallSettings as WFSets  # окно настроек
# Добавление своих файлов библиотек
from libs.Canvas import MplCanvas
from libs.Settings import SettingsGeneral as SetsGen
from libs.mngGraphs import Graph


class ExampleApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.setWindowTitle("UniReflView")

        self.window_water_sets = WaterSetsWindow()

        # Settings of graphics
        self.sc_refl_data = MplCanvas(self)
        self.sc_waterfall_data = MplCanvas(self)
        self.sc_fft_data = MplCanvas(self)

        self.toolbar_refl_data = NavigationToolbar2QT(self.sc_refl_data, None)
        self.toolbar_waterfall_data = NavigationToolbar2QT(self.sc_waterfall_data, None)
        self.toolbar_fft_data = NavigationToolbar2QT(self.sc_fft_data, None)

        self.layout_refl_data = QtWidgets.QVBoxLayout()
        self.layout_waterfall_data = QtWidgets.QVBoxLayout()
        self.layout_fft_data = QtWidgets.QVBoxLayout()

        self.layout_refl_data.addWidget(self.sc_refl_data)
        self.layout_refl_data.addWidget(self.toolbar_refl_data)
        self.layout_waterfall_data.addWidget(self.sc_waterfall_data)
        self.layout_waterfall_data.addWidget(self.toolbar_waterfall_data)
        self.layout_fft_data.addWidget(self.sc_fft_data)
        self.layout_fft_data.addWidget(self.toolbar_fft_data)

        self.ReflFrame.setLayout(self.layout_refl_data)
        self.WaterfallFrame.setLayout(self.layout_waterfall_data)
        self.FftFrame.setLayout(self.layout_fft_data)

        self.listWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Signals
        self.ChooseFile.triggered.connect(self.onChooseFileTriggered)
        self.ChooseFolder.triggered.connect(self.onChooseFolderTriggered)
        self.BuildAll.clicked.connect(self.onBuildAllClicked)
        self.checkAll.clicked.connect(self.onCheckAllClicked)
        self.uncheckAll.clicked.connect(self.onUncheckAllClicked)
        self.ClearAll.clicked.connect(self.onClearAllClicked)
        self.WaterfallSettings.triggered.connect(lambda x: self.window_water_sets.show())

        self.dct_graphs = dict()

    sets_gen = SetsGen()  # импорт настроек
    #TODO добавить выведение разницы поканально (пока до конца неясно как)
    @staticmethod
    def sorting_items_by_statusTip(items: list):
        """Сортировка списка из предметов. Нужно в силу некорректности обычной сортировки.
        :param items: Список предметов типа QListWidgetItem"""
        return sorted(items, key=lambda x: int(x.statusTip()[x.statusTip().rfind("/") + 1:].split("_")[1].rstrip(".csv")))

    @staticmethod
    def sorting_folder(lst: list):
        """Сортировка списка с файлами"""
        return sorted(lst, key=lambda x: int(x.split('_')[1].rstrip(".csv")))

    def onChooseFileTriggered(self):
        ''' Сигнал о выборе файла (файлов) '''
        print("Action 'onChooseFileTriggered' clicked...")
        files = QtWidgets.QFileDialog.getOpenFileNames(self)[0]
        if files:
            for file_path in files:
                folder_path, file_name = file_path[:file_path.rfind("/")], file_path[file_path.rfind("/") + 1:]
                self.listWidget.addItem(self.convert_to_item(file_name, folder_path))
        else:
            print("No files opened with 'OnChooseFileTriggered")

    def onChooseFolderTriggered(self):
        ''' Сигнал о выборе папки '''
        print("Action 'onChooseFolderTriggered' clicked.")
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Выбрать папку", ".")
        if folder_path:
            self.listWidget.clear()
            # print(folder_path)
            print("Opened folder '" + str(folder_path) + "'")
            self.sets_gen.chosen_dir = folder_path
            dir_list = listdir(folder_path)
            dir_list_filt = self.sorting_folder(list(filter(lambda x: x.endswith(self.sets_gen.format_files), dir_list)))
            # for i in range(1, len(dir_list_filt)):
            #     print(i, dir_list_filt[i].split('_')[1])
            # print('7' in list(map(lambda x: x.split("_")[1], dir_list_filt)))
            print("Placing folder to list...", end="")
            for file_name in dir_list_filt:
                self.listWidget.addItem(self.convert_to_item(file_name, folder_path))
            if self.sets_gen.save_all_refls:
                self.dct_graphs.clear()
                for file_name in dir_list_filt:
                    graph = Graph.convert_to_graph(folder_path + "/" + file_name,
                                                   self.sets_gen.date_format_file,
                                                   self.sets_gen.time_format_file)
                    self.dct_graphs[graph.name] = graph
            print(' complete.')
        else:
            print("No folder opened with 'OnChooseFolderTriggered'")

    def convert_to_item(self, file_name, folder_path):
        ''' Функция для конвертации файла с данными в Item в QListWidget '''
        item = QtWidgets.QListWidgetItem()
        # Название из имени файла
        info = file_name.split("_")
        # print(*info, sep="\n")
        item.setText(info[0] + info[1])
        if len(info) >= 4:
            item.setToolTip("Date: " + QDate.toString(QDate.fromString(info[2], self.sets_gen.date_format_file), self.sets_gen.date_format_list) + "\n" +
                            "Time: " + QTime.toString(QTime.fromString(info[3], self.sets_gen.time_format_file), self.sets_gen.time_format_list) + "\n" +
                            "ADC: " + info[4] + "\n" +
                            "Points: " + info[5])
        else:
            item.setToolTip("Date: -" + "\n" +
                            "Time: -" + "\n" +
                            "ADC: -" + "\n" +
                            "Points: -")
        try:
            suf = info[6]
        except:
            pass
        else:
            item.setToolTip(item.toolTip() + "\nSuf: " + suf)
        item.setCheckState(Qt.Checked)
        item.setStatusTip(folder_path + "/" + file_name)
        # Название из содержимого файла
        # with open(file_name, 'r') as inp:
        #     item.setText(inp.readline().strip())
        #     item.setToolTip(inp.readline().strip() + ' ' + inp.readline().strip())
        #     item.setCheckState(Qt.Checked)
        # self.lst_items.append(item)
        return item

    def add_refl(self, graph: Graph, count: int):
        '''
        Не используется
        Добавление рефлектограммы из файла в график
        :param graph : график типа данных mngGraps.Graph
        :param count : счётчик для сдвига графика вверх типа int'''
        dx = self.sets_gen.len_between_refls # Расстояние между графиками при отображении рефлектограмм
        # TODO доделать в нормальном виде, а то заколебало
        self.sc_refl_data.axes.plot(np.linspace(0.01, len(graph.yAxis) * 0.01, num=len(graph.yAxis)),
                                    graph.yAxis + count * dx, label=graph.name)
        # print(*graph.xAxis, sep="--")
        # print(*graph.yAxis, sep="--")

    def add_refl_by_item(self, item: QtWidgets.QListWidgetItem, count: int):
        ''' Добавление рефлектограммы из файла в график
        :param item : предмет типа QtWidgets.QListWidgetItem
        :param count : счётчик для сдвига графика вверх типа int'''

        graph = Graph.convert_to_graph(item.statusTip(), self.sets_gen.date_format_file, self.sets_gen.time_format_file, self.sets_gen.x_axis_in_file)
        dx = self.sets_gen.len_between_refls # Расстояние между графиками при отображении рефлектограмм
        t = len(graph.yAxis) * 0.01 * 10 ** (-6)  # время записи в с
        c = 2.99792458 * 10 ** 8  # Скорость света
        N_g = self.sets_gen.N_g  # Показатель преломления кабеля
        x = np.linspace(-self.sets_gen.delay, (t * c) / (2 * N_g) - self.sets_gen.delay, num=len(graph.yAxis))
        self.sc_refl_data.axes.plot(x, graph.yAxis + count * dx, label=graph.name)

    def calc_matrix_waterfall(self, graphs: list):
        '''
        Не используется
        Вычисление матрицы для построения водопада в GUI
        :param graphs — список (тип list) графиков типа Graph
        :return: np.matrix
        '''
        print("Calculating matrix for waterfall... ", end="")
        length = np.shape(graphs[0].xAxis)[0]
        # Check that all graphs has equal length
        min_len_index = 0
        flag = True
        for i in range(1, len(graphs)):
            if np.shape(graphs[i].xAxis)[0] != length:
                flag = False
                print("Length of Graph with number " + str(i) + " is not equal to length of Graph 0")
                if len(graphs[min_len_index].xAxis) > len(graphs[i].xAxis):
                    min_len_index = i

        # Cutting all to equal length
        if not flag:
            min_len = len(graphs[min_len_index].xAxis)
            length = min_len
            for i in range(len(graphs)):
                graphs[i].xAxis = graphs[i].xAxis[:min_len]
                graphs[i].yAxis = graphs[i].yAxis[:min_len]

        init_mat = np.zeros((len(graphs), length))
        for i in range(len(graphs)):
            for j in range(length):
                init_mat[i][j] = graphs[i].yAxis[j]
        # print(init_mat)
        # print(type(init_mat))
        if self.sets_gen.waterfall_mode == "Diff":
            for i in range(np.shape(init_mat)[0] - 1, 0, -1):
                for j in range(np.shape(init_mat)[1]):
                    init_mat[i][j] = init_mat[i][j] - init_mat[i - 1][j]
            # print(np.shape(init_mat))
            init_mat = init_mat[1:np.shape(init_mat)[0], 0:np.shape(init_mat)[1]]
            # print(np.shape(init_mat))
        elif self.sets_gen.waterfall_mode == "Average":
            aver_array = init_mat.mean(axis=0) # среднее значение по столбцам
            for i in range(np.shape(init_mat)[0]):
                for j in range(np.shape(init_mat)[1]):
                    init_mat[i][j] = init_mat[i][j] - aver_array[j]
        else:
            print("Invalid waterfall mode — '" + self.sets_gen.waterfall_mode + "'")
        return init_mat, graphs

    def calc_matrix_waterfall_by_items(self, items: list, only_init_mat=False):
        '''
        Вычисление матрицы для построения водопада в GUI (без сохранения в оперативную память)
        :param items — список (тип list) графиков типа QtWidgets.QListWidgetItem
        :return: np.matrix — матрица водопада в соответствии с выбранным методом waterfall_mode
        '''
        # Нахождение минимальной длины массива
        graph = Graph.convert_to_graph(items[0].statusTip(), self.sets_gen.date_format_file,
                                       self.sets_gen.time_format_file)
        # print(self.sets_gen.x_axis_in_file)
        min_len = np.shape(graph.yAxis)[0]
        if self.sets_gen.check_len_refls:
            print("Cutting reflectograms to equal length...")
            min_len_index = 0
            for i in range(1, len(items)): #TODO переделать в более оптимальную версию
                graph = Graph.convert_to_graph(items[i].statusTip(), self.sets_gen.date_format_file, self.sets_gen.time_format_file)
                if np.shape(graph.yAxis)[0] < min_len:
                    print(f'Length of Graph in file {str(items[i].statusTip()[items[i].statusTip().rfind("/"):])} with value {str(np.shape(graph.yAxis)[0])} is'
                          f' less then length of Graph in file {str(items[min_len_index].statusTip()[items[min_len_index].statusTip().rfind("/"):])} with value {str(min_len)}')
                    min_len = np.shape(graph.yAxis)[0]
                    min_len_index = i
        print("Creating initial matrix...")
        init_mat = np.zeros((len(items), min_len))
        try:
            for i in range(len(items)):
                array = np.array(Graph.convert_to_graph(items[i].statusTip(), self.sets_gen.date_format_file, self.sets_gen.time_format_file, x_axis=self.sets_gen.x_axis_in_file).yAxis[:min_len])
                for j in range(min_len):
                    init_mat[i][j] = array[j]
        except Exception as e:
            print(e)
        if only_init_mat:
            return init_mat, min_len
        else:

            print("Calculating matrix for waterfall... ")
            if self.sets_gen.waterfall_mode.lower() == "diff":
                for i in range(np.shape(init_mat)[0] - 1, 0, -1):
                    for j in range(np.shape(init_mat)[1]):
                        init_mat[i][j] = init_mat[i][j] - init_mat[i - 1][j]
                init_mat = init_mat[1:np.shape(init_mat)[0], 0:np.shape(init_mat)[1]]
            elif self.sets_gen.waterfall_mode.lower() == "average":
                aver_array = init_mat.mean(axis=0) # среднее значение по столбцам
                for i in range(np.shape(init_mat)[0]):
                    for j in range(np.shape(init_mat)[1]):
                        init_mat[i][j] = init_mat[i][j] - aver_array[j]


            elif self.sets_gen.waterfall_mode.lower() == "slopeaverage":
                num_aver = self.sets_gen.average_number
                aver_mat = np.zeros((np.shape(init_mat)[0], np.shape(init_mat)[1]))
                n = np.shape(init_mat)[0]
                for i in range(np.shape(init_mat)[0]):
                    aver_mat[i, :] = init_mat[max(0, i - num_aver): min(i + num_aver + 1, n), ].mean(axis=0)
                init_mat = init_mat - aver_mat
            else:
                print("Invalid waterfall mode — '" + self.sets_gen.waterfall_mode + "'")

            # Нормирование матрицы
            if self.sets_gen.mat_normalization: #TODO сделать настройку в GUI
                print("Proceed matrix normalization...")
                for i in range(np.shape(init_mat)[1]):
                    max_val = np.max(np.abs(init_mat[:, i]))
                    init_mat[:, i] /= max_val

            # Автоматическая регулировка усиления
            try:

                if self.sets_gen.auto_gain_contol:
                    print("Proceed automatic gain control...")  # TODO сделать настройку в GUI
                    num_gain = self.sets_gen.num_of_auto_gain_contol
                    gain_mat = np.zeros((np.shape(init_mat)[0], np.shape(init_mat)[1]))
                    n, m = np.shape(init_mat)
                    for i in range(n):
                        for j in range(m):
                            value = np.max(np.abs(init_mat[max(0, i - num_gain): min(i + num_gain, n), j]))
                            gain_mat[i, j] = value if value != 0 else 1
                    init_mat /= gain_mat
            except Exception as e:
                print(e)
            return init_mat, min_len

    def do_waterfall(self, graphs: list):
        '''
        Не используется
        Построение водопада. Если графиков не больше 2, то водопад не будет построен.
        :param graphs: список (тип list) графикиков типа Graph

        '''
        if len(graphs) > 2:
            wfm = self.sets_gen.waterfall_mode
            multiplier = 1
            if wfm.lower() == 'diff':
                multiplier = 35
            elif wfm.lower() == 'average':
                multiplier = 3
            elif wfm.lower() == "slopeaverage":
                multiplier = 5
            else:
                raise Exception('Incorrect waterfall mode:', wfm)
            mat, min_len = self.calc_matrix_waterfall(graphs)
            start_time = 0
            end_time = graphs[0].time.msecsTo(graphs[-1].time)
            # Перевод времени в метры (считается что частота дискретизации АЦП 100МГЦ!)
            t = np.shape(graphs[0].xAxis)[0] * 0.01 # время записи в мкс
            c = 2.99792458 * 10**8 # Скорость света
            N_g = self.sets_gen.N_g # Показатель преломления кабеля
            L_max = (t * 10**(-6) * c * 0.8) / N_g # для DVS от Метротек
            # L_max = (t * 10**(-6) * c) / N_g # для DAS от ПИШ
            self.sc_waterfall_data.axes.imshow(mat,
                                               aspect='auto',
                                               vmin=np.min(mat) / 4, vmax=np.max(mat) / 4,
                                               cmap='coolwarm',
                                               extent=[0, L_max, end_time, start_time])

            self.sc_waterfall_data.draw()
        else:
            print("No waterfall, because of small number of graphs (" + str(len(graphs)) + ")")

    def do_waterfall_by_items(self, items: list):
        '''
        Построение водопада без записи данных в оперативную память. Если графиков не больше 2, то водопад не будет построен.
        :param items: список (тип list) предметов типа QtWidgets.QListWidgetItem
        '''
        if len(items) > 2:
            wfm = self.sets_gen.waterfall_mode
            multiplier = 1
            if wfm.lower() == 'diff':
                multiplier = 20
            elif wfm.lower() == 'average':
                multiplier = 1
            elif wfm.lower() == "slopeaverage":
                multiplier = 5
            else:
                raise Exception('Incorrect waterfall mode:', wfm)
            mat, min_len = self.calc_matrix_waterfall_by_items(items)
            start_time = 0
            try:
                end_time = Graph.convert_to_graph(items[0].statusTip(),
                                                  self.sets_gen.date_format_file,
                                                  self.sets_gen.time_format_file).time.secsTo(Graph.convert_to_graph(items[-1].statusTip(), self.sets_gen.date_format_file, self.sets_gen.time_format_file).time)
            except Exception as e: # если время не указано
                print("Error:", e)
                print("Setting to 1 second.")
                end_time = 1
            # Перевод времени в метры (считается что частота дискретизации АЦП 100МГЦ!) #TODO сделать для любой частоты дискретизации
            if end_time == 0:
                print("Attempting to set identical low and high xlims (seconds << 1).\nSetting to 1 second.")
                end_time = 1

            t = min_len * 0.01 * 10**(-6) # время записи в с
            c = 2.99792458 * 10**8 # Скорость света
            N_g = self.sets_gen.N_g # Показатель преломления кабеля
            # L_max = ((t * c * 0.8)) / (2 * N_g) - self.sets_gen.delay # для DVS от Метротек
            L_max = ((t * c)) / (2 * N_g) - self.sets_gen.delay # для DAS от ПИШ
            v_min_max = min(abs(np.min(mat)), abs(np.max(mat)))
            self.sc_waterfall_data.axes.imshow(mat.T,
                                               aspect='auto',
                                               vmin=-v_min_max / multiplier, vmax=v_min_max / multiplier,
                                               cmap='bwr',
                                               extent=[start_time, end_time, -self.sets_gen.delay, L_max])

            self.sc_waterfall_data.draw()
        else:
            print("No waterfall, because of small number of graphs (" + str(len(items)) + ")")

    def phase_demodule(self, init_mat, shift_freq=80 * 10**6):
        ''' Демодуляция фазы '''
        print('Demodulation phase...')
        try:
            add_mat = np.zeros((np.shape(init_mat)[1], np.shape(init_mat)[1]))
            for i in range(np.shape(init_mat)[1]):
                add_mat[:, i] = np.sin(np.linspace(10**(-9), np.shape(init_mat)[0] * 10**(-9), num=np.shape(init_mat)[1]) * shift_freq) #TODO частота дискретизации 1ГГЦ
            sin_mat = np.dot(init_mat, add_mat)
            for i in range(np.shape(init_mat)[1]):
                add_mat[:, i] = np.cos(np.linspace(10**(-9), np.shape(init_mat)[0] * 10**(-9), num=np.shape(init_mat)[1]) * shift_freq)  # TODO частота дискретизации 1ГГЦ
            cos_mat = np.dot(init_mat, add_mat)
            #TODO по статье здесь(!) надо добавить LPF для матриц sin и cos
            phase_mat = np.arctan(np.divide(sin_mat, cos_mat))
        except Exception as e:
            print(e)
        return phase_mat

    def do_fft_by_items(self, items: list):
        ''' Вычисление результатов преобразования Фурье'''
        mat, min_len = self.calc_matrix_waterfall_by_items(items, only_init_mat=True)
        phase_mat = self.phase_demodule(mat, self.sets_gen.AOM_freq_shift)
        start_time = 0
        try:
            end_time = Graph.convert_to_graph(items[0].statusTip(),
                                              self.sets_gen.date_format_file,
                                              self.sets_gen.time_format_file).time.msecsTo(
                Graph.convert_to_graph(items[-1].statusTip(), self.sets_gen.date_format_file,
                                       self.sets_gen.time_format_file).time)
        except Exception as e:  # если время не указано
            print("Error:", e)
            end_time = 1000
            print('Total time was set to', end_time)
        multiplier = 1000
        v_min_max = min(abs(np.min(mat)), np.max(mat)) / multiplier
        # Перевод времени в метры (считается что частота дискретизации АЦП 1ГГЦ!) #TODO сделать для любой частоты дискретизации
        t = min_len * 0.001 * 10 ** (-6)  # быстрое время записи в с
        c = 2.99792458 * 10 ** 8  # Скорость света
        N_g = self.sets_gen.N_g  # Показатель преломления кабеля
        # L_max = ((t * c * 0.8)) / (2 * N_g) - self.sets_gen.delay  # для DVS от Метротек
        L_max = ((t * c)) / (2 * N_g) - self.sets_gen.delay # для DAS от ПИШ
        self.sc_fft_data.axes.imshow(phase_mat,
                                           aspect='auto',
                                           vmin=-v_min_max, vmax=v_min_max,
                                           cmap='coolwarm',
                                           extent=[-self.sets_gen.delay, L_max, end_time, start_time])
        self.sc_fft_data.draw()

    def onBuildAllClicked(self):
        '''
        Сигнал о нажатии на клавишу построить всё. Вызывает функции для построения графиков и водопада. Самостоятельно находит
        отмеченные графики для построения
        '''

        file_names = []
        items = []
        for i in range(self.listWidget.count()):
            if self.listWidget.item(i).checkState() == Qt.Checked:
                status_tip = self.listWidget.item(i).statusTip()
                file_names.append(status_tip[status_tip.rfind("/") + 1:])
                items.append(self.listWidget.item(i))
        if items:
            print("-" * 8 + " START CALCULATIONS " + 8 * "-")
            items = self.sorting_items_by_statusTip(items)

            # Построение рефлектограмм
            if self.sets_gen.show_refls:
                print("Distance between reflectograms:", self.sets_gen.len_between_refls)
                self.sc_refl_data.clear()
                count = len(file_names) - 1
                if self.sets_gen.save_all_refls:
                    for item in items:
                        self.add_refl(self.dct_graphs[item.name], count)
                        count -= 1
                else:
                    for item in items:
                        self.add_refl_by_item(item, count)
                        count -= 1
                if self.sets_gen.axes_settings_enabled_refl:
                    self.sc_refl_data.axes.set_xlabel("X, м")
                    self.sc_refl_data.axes.set_ylabel("Интенсивность, В")
                    self.sc_refl_data.axes.grid(True)
                    self.sc_refl_data.figure.legend()
                self.sc_refl_data.draw()
            # Построение водопада
            if self.sets_gen.show_waterfall:
                print("Waterfall Mode:", self.sets_gen.waterfall_mode)
                self.sc_waterfall_data.axes.cla()
                if self.sets_gen.axes_settings_enabled_waterfall:
                    self.sc_waterfall_data.axes.set_xlabel("Время, с")
                    self.sc_waterfall_data.axes.set_ylabel("X, м")
                    self.sc_waterfall_data.axes.grid(True)
                if self.sets_gen.save_all_refls:
                    self.do_waterfall([self.dct_graphs[item.text()] for item in items])
                else:
                    self.do_waterfall_by_items(items)
            if self.sets_gen.show_fft:
                self.sc_fft_data.axes.cla()
                if self.sets_gen.axes_settings_enabled_fft:  #TODO не настроено в GUI
                    self.sc_fft_data.axes.set_xlabel("X, м")
                    self.sc_fft_data.axes.set_ylabel("Время, с")
                    self.sc_fft_data.axes.grid(True)
                self.do_fft_by_items(items)
            print("All figures was calculated and shown.\n")
        else:
            print("No files chose to calculate.")


        # Старый вариант с сохранением всех файлов в памяти
        # graphs = []
        # for file_name in file_names:
        #     graph_name = file_name.split("_")[0] + file_name.split("_")[1]
        #     if Graph.find_graph_by_name(graph_name, self.lst_graphs):
        #         graph = Graph.find_graph_by_name(graph_name, self.lst_graphs)
        #         graphs.append(graph)
        # if graphs:
        #     self.sc_refl_data.clear()
        #     graphs.sort(key=lambda x: x.name) # сортировка для правильного отображения
        #     count = len(graphs) - 1
        #
        #     for graph in graphs:
        #         self.add_refl(graph, count)
        #         # legends_labels.append(graph.name)
        #         count -= 1
        #
        #     if self.axes_settings_enabled:
        #         self.sc_refl_data.axes.set_xlabel("X, м")
        #         self.sc_refl_data.axes.set_ylabel("Интенсивность, В")
        #         self.sc_refl_data.axes.grid(True)
        #         self.sc_refl_data.figure.legend()
        #     self.sc_refl_data.draw()
        #
        #     # Settings of graphics waterfall
        #     self.sc_waterfall_data.axes.cla()
        #     if self.axes_settings_enabled:
        #         self.sc_waterfall_data.axes.set_xlabel("X, м")
        #         self.sc_waterfall_data.axes.set_ylabel("Время, мс")
        #         self.sc_waterfall_data.axes.grid(True)
        #     self.do_waterfall(graphs)
        # else:
        #     print(" do not do anything.")

    def onCheckAllClicked(self):
        print("Button 'CheckAll' clicked...")
        self.checkAll.setCheckState(Qt.Checked)
        if self.listWidget.selectedItems():
            for item in self.listWidget.selectedItems():
                item.setCheckState(Qt.Checked)
        else:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Checked)

    def onUncheckAllClicked(self):
        print("Button 'UnCheckAll' clicked...")
        self.uncheckAll.setCheckState(Qt.Unchecked)
        if self.listWidget.selectedItems():
            for item in self.listWidget.selectedItems():
                item.setCheckState(Qt.Unchecked)
        else:
            for i in range(self.listWidget.count()):
                self.listWidget.item(i).setCheckState(Qt.Unchecked)

    def onClearAllClicked(self):
        self.listWidget.clear()
        self.lst_path_files = []
        self.lst_items = []
        self.lst_graphs = []
        self.chosen_dir = []


class WaterSetsWindow(QtWidgets.QWidget, WFSets.Ui_WaterfallSets):
    def __init__(self):
        super(WaterSetsWindow, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Settings")
        #Signals
        self.waterfall_mode_gui.currentIndexChanged.connect(self.onwaterfall_mode_guiCurrentIndexChanged)
        self.show_relfs_gui.stateChanged.connect(self.onshow_relfs_guiStateChanged)
        self.show_waterfall_gui.stateChanged.connect(self.onshow_waterfall_guiStateChanged)
        self.len_between_refls_gui.valueChanged.connect(self.onlen_between_refls_guiValueChanged)
        self.x_axis_in_file_gui.stateChanged.connect(self.on_x_axis_in_file_guiCurrentIndexChanged)
        self.format_files_gui.textChanged.connect(self.onformat_files_guiTextChanged)
        self.save_all_refls_gui.stateChanged.connect(self.onsave_all_refls_guiStateChanged)
        self.delay_gui.valueChanged.connect(self.onDelayLineDoubleSpinBoxChanged)
        self.N_g_gui.valueChanged.connect(self.onN_g_guiValueChanged)
        self.check_len_refls_gui.stateChanged.connect(self.oncheck_len_refls_guiStateChanged)
        self.average_number_gui.valueChanged.connect(self.onAverageNumberBoxChanged)

    def oncheck_len_refls_guiStateChanged(self):
        ExampleApp.sets_gen.check_len_refls = self.check_len_refls_gui.isChecked()

    def on_x_axis_in_file_guiCurrentIndexChanged(self):
        ExampleApp.sets_gen.x_axis_in_file = self.x_axis_in_file_gui.isChecked()
    def onN_g_guiValueChanged(self):
        ExampleApp.sets_gen.N_g = self.N_g_gui.value()
    def onshow_relfs_guiStateChanged(self):
        ExampleApp.sets_gen.show_refls = self.show_relfs_gui.isChecked()

    def onshow_waterfall_guiStateChanged(self):
        ExampleApp.sets_gen.show_waterfall = self.show_waterfall_gui.isChecked()

    def onwaterfall_mode_guiCurrentIndexChanged(self):
        ExampleApp.sets_gen.waterfall_mode = self.waterfall_mode_gui.itemText(self.waterfall_mode_gui.currentIndex())

    def onlen_between_refls_guiValueChanged(self):
        ExampleApp.sets_gen.len_between_refls = self.len_between_refls_gui.value()

    def ondata_type_in_files_guiCurrentIndexChanged(self):
        pass

    def onformat_files_guiTextChanged(self):
        ExampleApp.sets_gen.format_files = self.format_files_gui.text()

    def onAverageNumberBoxChanged(self):
        ExampleApp.sets_gen.average_number = int(self.average_number_gui.value())

    def onsave_all_refls_guiStateChanged(self):
        ExampleApp.sets_gen.save_all_refls = self.save_all_refls_gui.isChecked()
        print(self.save_all_refls_gui.isChecked())

    def onDelayLineDoubleSpinBoxChanged(self):
        ExampleApp.sets_gen.delay = float(self.delay_gui.value())


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    # print("dct1") #TODO доделать сохранение настроек в файл
    # for key, value in ExampleApp.sets_gen.get_all_settings()[0].items():
    #     print(f'{key} = {value}')
    # print("dct2")
    # for key, value in ExampleApp.sets_gen.get_all_settings()[1].items():
    #     print(f'{key} = {value}')


if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()
