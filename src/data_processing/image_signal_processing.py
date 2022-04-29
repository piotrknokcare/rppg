import cv2
from os import walk, path, makedirs
from scipy.fft import fft, fftfreq
from skimage import io
import directories
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
from scipy import signal


def convert_video_to_images(video_path, frame_rate):
    split_path = video_path.split('/')
    save_path = '/'.join(split_path[:-1]) + '/' + split_path[-1].replace('.mp4', '')
    if not path.exists(save_path):
        makedirs(save_path)
    clip = cv2.VideoCapture(video_path)
    success, image = clip.read()
    count = 0
    while success:
        cv2.imwrite(save_path + '/' + "frame{0}FR{1}.jpg".format(count, frame_rate), image)  # save frame as JPEG file
        success, image = clip.read()
        count += 1
    print('Images created.')


def process_finger_image(images_dir, frame_rate):
    filenames = next(walk(images_dir), (None, None, []))[2]
    period = 1/frame_rate

    averages = []
    for img_name in filenames:
        img = io.imread(images_dir + img_name, as_gray=False)
        mean_rgb = get_mean_rgb(img)

        averages.append([mean_rgb[0], mean_rgb[1], mean_rgb[2]])

    ts = pd.DataFrame(averages)  # time series
    ts.columns = ['red', 'green', 'blue']
    ts['red_ema'] = ts['red'].ewm(span=13).mean()  # Exponential moving average
    ts['green_ema'] = ts['green'].ewm(span=13).mean()
    ts['blue_ema'] = ts['green'].ewm(span=13).mean()
    ts.insert(0, 'time', ts.index * period)
    return ts


def get_mean_rgb(img):

    mean_red = img[:, :, 0].mean()
    mean_green = img[:, :, 1].mean()
    mean_blue = img[:, :, 2].mean()

    return  mean_red, mean_green, mean_blue


def plot_timeseries(ts, *cols):
    """ By default, prints all the colors, the cols is the bonus abbreviation"""

    for color in ['red', 'green', 'blue']:
        for column in cols:
            plt.grid(visible=True)
            plt.step(ts['time'], ts[color], 'r--')
            plt.step(ts['time'], ts[color + '_' + column], 'k--')
            plt.show()


def plot_fft(ts, frame_rate):
    # Number of sample points
    N = ts.shape[0]
    # sample spacing
    T = 1.0 / frame_rate
    xf = fftfreq(N, T)[:N // 2]

    y_red = ts['red_ema']
    yf_red = fft(np.array(y_red))
    plt.plot(xf, 2.0 / N * np.abs(yf_red[0:N // 2]))
    plt.grid()
    plt.show()

    y_green = ts['green_ema']
    yf_green = fft(np.array(y_green))
    plt.plot(xf, 2.0 / N * np.abs(yf_green[0:N // 2]))
    plt.grid()
    plt.show()

    y_blue = ts['blue_ema']
    yf_blue = fft(np.array(y_blue))
    plt.plot(xf, 2.0 / N * np.abs(yf_blue[0:N // 2]))
    plt.grid()
    plt.show()


def plot_ifft():
    pass


def plot_derivative(ts):
    ts['red_d'] = ts['red'].diff()/ts['time'].diff()
    ts['green_d'] = ts['green'].diff()/ts['time'].diff()
    ts['blue_d'] = ts['blue'].diff()/ts['time'].diff()
    plot_timeseries(ts, 'd')


def plot_periodogram(ts, frame_rate):
    f, Pxx_den = signal.periodogram(ts['red'], frame_rate, 'flattop', scaling='spectrum')
    plt.semilogy(f, Pxx_den)
    # plt.ylim([1e-7, 1e2])
    plt.xlabel('frequency [Hz]')
    plt.ylabel('PSD [V**2/Hz]')
    plt.show()


def find_peaks():
    from scipy.signal import find_peaks
    peaks, _ = find_peaks(x, height=0)


if __name__ == "__main__":
    directories.change_dir_to_main()
    frame_rate = 30
    convert_video_to_images("data/examples/BPM75OX97FR30.mp4", frame_rate)
    # ts = process_finger_images("data/examples/BPM68OX97FR30/", frame_rate)
    # plot_fft(ts, frame_rate)
    # plot_derivative(ts)
    # plot_periodogram(ts, frame_rate)