import os
import pyart.io
import pandas
from BirdRoostDetection import utils
import matplotlib
matplotlib.use('agg')  # Required for running on schooner
import matplotlib.pyplot as plt
import sys
from BirdRoostDetection.PrepareData import NexradUtils
import BirdRoostDetection.LoadSettings as settings
from PIL import Image

REFLECTIVITY = 'reflectivity'
VELOCITY = 'velocity'
DIFFERENTIAL_REFLECTIVITY = 'differential_reflectivity'
CROSS_CORRELATION_RATIO = 'cross_correlation_ratio'

plot_dict = {
    REFLECTIVITY: [-20, 30],
    VELOCITY: [-20, 20],
    DIFFERENTIAL_REFLECTIVITY: [-4, 8],
    CROSS_CORRELATION_RATIO: [.3, .95]
}


def plot_radar_files(file_path):
    img_path = file_path.replace(utils.RADAR_FILE_DIR,
                                 utils.RADAR_IMAGE_DIR + '{0}/') + '_{0}.png'
    if (not os.path.exists(img_path.format(REFLECTIVITY))):
        file = open(file_path, 'r')
        rad = pyart.io.read_nexrad_archive(file.name)
        if (6 <= int(file_path[-1])):
            keys = ['velocity', 'differential_reflectivity', 'reflectivity',
                    'cross_correlation_ratio']
        else:
            keys = ['velocity', 'reflectivity']
        for key in keys:
            fig, ax = plt.subplots(figsize=(3, 3))
            for i in range(3):
                plot_ppi(radar=rad, field=key, ax=ax,
                         sweep=i)
            plt.axis('off')
            full_img_path = img_path.format(key)
            img_folder = os.path.dirname(full_img_path)
            if not os.path.isdir(img_folder):
                os.makedirs(img_folder)
            plt.savefig(full_img_path)
            Image.open(full_img_path).convert('L').save(full_img_path)


def plot_ppi(
        radar,
        field,
        ax,
        sweep=0):
    # get data for the plot
    sweep_slice = radar.get_slice(sweep)
    data = radar.fields[field]['data'][sweep_slice]

    x, y, _ = radar.get_gate_x_y_z(
        sweep, edges=False, filter_transitions=True)
    x = x / 1000.0
    y = y / 1000.0

    cutoff = 1400
    x = x[:, 0:cutoff]
    y = y[:, 0:cutoff]
    data = data[:, 0:cutoff]

    ax.pcolormesh(
        x, y, data, vmin=plot_dict[field][0], vmax=plot_dict[field][1],
        cmap='binary')


def main():
    """Formatted to run either locally or on schooner. Read in csv and get radar
     files listed in 'AWS_file' column. Save these files out as png images."""
    radar = sys.argv[1]
    os.chdir(settings.WORKING_DIRECTORY)
    labels = pandas.read_csv(filepath_or_buffer=settings.LABEL_CSV,
                             skip_blank_lines=True)

    radar_labels = labels[labels.radar == radar]
    file_names = list(radar_labels['AWS_file'])
    # np.random.shuffle(file_names)
    for file_name in file_names:
        print file_name
        full_path = os.path.join(utils.RADAR_FILE_DIR,
                                 NexradUtils.getBasePath(file_name), file_name)
        plot_radar_files(full_path)


if __name__ == "__main__":
    os.chdir(settings.WORKING_DIRECTORY)
    main()
