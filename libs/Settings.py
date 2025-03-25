class SettingsWaterfall():

    _axes_settings_enabled_waterfall = True
    _waterfall_mode = "Diff"  # Режим водопада
    _show_waterfall = True
    _average_number = 51
    _check_len_refls = True

    @property
    def axes_settings_enabled_waterfall(self):
        return self._axes_settings_enabled_waterfall
    @axes_settings_enabled_waterfall.setter
    def axes_settings_enabled_waterfall(self, mode: bool):
        self._axes_settings_enabled_waterfall = mode

    @property
    def waterfall_mode(self):
        return self._waterfall_mode
    @waterfall_mode.setter
    def waterfall_mode(self, mode: str):
        self._waterfall_mode = mode

    @property
    def show_waterfall(self):
        return self._show_waterfall
    @show_waterfall.setter
    def show_waterfall (self, show_waterfall: bool):
        self._show_waterfall = show_waterfall

    @property
    def average_number(self):
        return self._average_number
    @average_number.setter
    def average_number(self, average_number: int):
        self._average_number = average_number

    @property
    def check_len_refls(self):
        return self._check_len_refls
    @check_len_refls.setter
    def check_len_refls(self, check_refl_len: float):
        self._check_len_refls = check_refl_len

class SettingsFFT():
    _AOM_freq_shift = 80 * 10**6 #Взято из мануала DAS Integrated Module

    @property
    def AOM_freq_shift(self):
        return self._AOM_freq_shift

    @AOM_freq_shift.setter
    def AOM_freq_shift(self, AOM_freq_shift):
        self._AOM_freq_shift = AOM_freq_shift

    _show_fft = False #TODO сделать нормальную настройку

    @property
    def show_fft(self):
        return self._show_fft

    @show_fft.setter
    def show_fft(self, show_fft):
        self._show_fft = show_fft

    _axes_settings_enabled_fft = True

    @property
    def axes_settings_enabled_fft(self):
        return self._axes_settings_enabled_fft

    @axes_settings_enabled_fft.setter
    def axes_settings_enabled_fft(self, axes_settings_enabled_fft):
        self._axes_settings_enabled_fft = axes_settings_enabled_fft

class SettingsRefl():
    _axes_settings_enabled_refl = True
    _show_refls = False
    _len_between_refls = 0.1

    @property
    def axes_settings_enabled_refl(self):
        return self._axes_settings_enabled_refl
    @axes_settings_enabled_refl.setter
    def axes_settings_enabled_refl(self, mode: bool):
        self._axes_settings_enabled_refl = mode

    @property
    def show_refls(self):
        return self._show_refls
    @show_refls.setter
    def show_refls(self, show_refls: bool):
        self._show_refls = show_refls

    @property
    def len_between_refls(self):
        return self._len_between_refls
    @len_between_refls.setter
    def len_between_refls(self, len_between_refls: float):
        self._len_between_refls = len_between_refls

class SettingsFiles():
    _date_format_file = 'yyyy-MM-dd'  # Формат даты названий файлов
    _time_format_file = 'hh-mm-ss.zzz'  # Формат времени названий файлов
    _format_files = ".csv"  # Формат файлов, который ищется в папке
    _chosen_dir = ''  # Выбранная папка

    @property
    def date_format_file(self):
        return self._date_format_file
    @date_format_file.setter
    def date_format_file(self, date_format: str):
        self._date_format_file = date_format

    @property
    def time_format_file(self):
        return self._time_format_file
    @time_format_file.setter
    def time_format_file(self, time_format: str):
        self._time_format_file = time_format

    @property
    def format_files(self):
        return self._format_files
    @format_files.setter
    def format_files(self, format_files: str):
        self._format_files = format_files

    @property
    def chosen_dir(self):
        return self._chosen_dir
    @chosen_dir.setter
    def chosen_dir(self, chosen_dir: str):
        self._chosen_dir = chosen_dir

class SettingsGeneral(SettingsWaterfall, SettingsRefl, SettingsFiles, SettingsFFT):
    def __init__(self, lst_graphs=None, len_between_refls=0.1, date_format_gui="dd MMMM yyyy", time_format_gui='hh:mm:ss.zzz',
                 save_all_refl=False, delay_len=23.0, N_g=1.4688):
        SettingsWaterfall.__init__(self)
        if lst_graphs is None:
            self.lst_graphs = []
        self._date_format_list = date_format_gui  # Формат даты для вывода в GUI
        self._time_format_list = time_format_gui  # Формат времени для вывода в GUI
        self._save_all_refls = save_all_refl
        self._delay = delay_len
        self._N_g = N_g
        self._x_axis_in_file = False
        self._auto_gain_control = False
        self._num_of_auto_gain_control = 1000
        self._mat_normalization = False


    def set_save_settings(self):
        pass #TODO сделать в нормальном виде сохранение и автоматический импорт настроек

    def get_all_settings(self):
        dct1 = dict()
        dct2 = dict()
        for item in dir(self):
            if not item.startswith('get') and not (item.startswith("__") and item.endswith("__")) and not item.startswith("set"):
                dct1[item] = getattr(self, item)
            if item.startswith('get'):
                dct2[item] = getattr(self, item)
            pass
        return dct1, dct2

    @property
    def auto_gain_contol(self):
        return self._auto_gain_control
    @auto_gain_contol.setter
    def auto_gain_contol(self, value: bool):
        self._auto_gain_control = value

    @property
    def mat_normalization(self):
        return self._mat_normalization
    @mat_normalization.setter
    def mat_normalization(self, value: bool):
        self._mat_normalization = value

    @property
    def num_of_auto_gain_contol(self):
        return self._num_of_auto_gain_control
    @num_of_auto_gain_contol.setter
    def num_of_auto_gain_contol(self, value: int):
        self._num_of_auto_gain_control = value

    @property
    def x_axis_in_file(self):
        return self._x_axis_in_file
    @x_axis_in_file.setter
    def x_axis_in_file(self, state: bool):
        self._x_axis_in_file = state
    @property
    def date_format_list(self):
        return self._date_format_list
    @date_format_list.setter
    def date_format_list(self, date_format_gui: str):
        self._date_format_list = date_format_gui

    @property
    def time_format_list(self):
        return self._time_format_list
    @time_format_list.setter
    def time_format_list(self, time_format_gui: str):
        self._time_format_list = time_format_gui

    @property
    def save_all_refls(self):
        return self._save_all_refls
    @save_all_refls.setter
    def save_all_refls(self, save_all_refl: bool):
        self._save_all_refls = save_all_refl

    @property
    def delay(self):
        return self._delay
    @delay.setter
    def delay(self, delay_len: float):
        self._delay = delay_len

    @property
    def N_g(self):
        return self._N_g
    @N_g.setter
    def N_g(self, N_g: float):
        self._N_g = N_g

if __name__ == '__main__':
    setsgen = SettingsGeneral()
    print(*dir(setsgen), sep="\n")

