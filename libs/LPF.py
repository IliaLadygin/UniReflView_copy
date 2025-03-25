import numpy as np
import scipy.signal
import scipy.io.wavfile
import matplotlib.pyplot as plt

def lowpass(data: np.ndarray, cutoff: float, sample_rate: float, poles: int = 5):
    sos = scipy.signal.butter(poles, cutoff, 'lowpass', fs=sample_rate, output='sos')
    filtered_data = scipy.signal.sosfiltfilt(sos, data)
    return filtered_data

def bandpass(data: np.ndarray, sample_rate: float, cutoff_low=0.5, cutoff_high=35, poles: int = 6):
    sos = scipy.signal.butter(poles, [cutoff_low, cutoff_high], 'bandpass', fs=sample_rate, output='sos')
    filtered_data = scipy.signal.sosfiltfilt(sos, data)
    return filtered_data

# if __name__ == '__main__':
#     # Load sample data from a WAV file
#     sample_rate, data = scipy.io.wavfile.read('ecg.wav')
#     times = np.arange(len(data))/sample_rate
#
#     # Apply a 50 Hz low-pass filter to the original data
#     filtered = lowpass(data, 50, sample_rate)

def create_mat(list_of_files, path, num_cols=4):
    cutoff_low_ADC = 2
    cutoff_high_ADC = 49.9 * 10**6
    freq_ADC = 100 * 10**6
    list_of_files = sorted(list_of_files, key=lambda x: int(x.split('_')[1].rstrip(".csv")))
    mat = np.loadtxt(path + '/' + list_of_files[0], delimiter=";",
                             encoding="utf-8-sig", usecols=tuple([i for i in range(num_cols)]),
                             converters=dict.fromkeys([i for i in range(num_cols)], lambda x: str(x).replace(',', '.')))
    # print(np.shape(mat))
    m_mat = np.zeros((len(list_of_files), np.shape(mat)[0]))
    for i in range(len(list_of_files)):
        mat = np.loadtxt(path + '/' + list_of_files[i], delimiter=";",
                             encoding="utf-8-sig", usecols=tuple([i for i in range(num_cols)]),
                             converters=dict.fromkeys([i for i in range(num_cols)], lambda x: str(x).replace(',', '.')))
        for j in range(np.shape(mat)[1]):
            mat[:, j] = bandpass(mat[:, j], cutoff_low=cutoff_low_ADC, cutoff_high=cutoff_high_ADC, sample_rate=freq_ADC)
        m_mat[i, :] = mat.mean(axis=1)
    return m_mat

def ch_to_meters(t, c, n_g, delay):
    return (t  * 0.01 * 10 ** (-6) * c) / (2 * n_g) - delay

def calc_SNR(array, start_point, end_point, indent=50, method="std"):
    if method.lower() == "std":
        return 10 * np.log10(array[start_point + indent:end_point - indent].std(ddof=1) / array[:start_point - indent].std(ddof=1))
    if method.lower() == "rms":
        return 10 * np.log10(np.sqrt(np.mean(np.square(array[start_point + indent:end_point - indent]))) / np.sqrt(np.mean(np.square(array[:start_point - indent]))))