import matplotlib

# matplotlib.use('agg')  # Required for running on schooner
import matplotlib.pyplot as plt
import pyart.graph
import pyart.io
from BirdRoostDetection.PrepareData import AWSNexradData


# This method takes code from the following website, originally written by Lak,
# modified by Carmen
# https://eng.climate.com/2015/10/27/how-to-read-and-display-nexrad-on-aws
# -using-python/
#
# visualize the LDM2 radar data
# If image is from before 2012, make sure dualPolarization is set to false,
# seince images before this time have fewer fields
def visualizeLDMdata(radar, save, dualPolarization=False):
    display = pyart.graph.RadarDisplay(radar)
    if (dualPolarization):
        fig = plt.figure(figsize=(9, 9))
    else:
        fig = plt.figure(figsize=(9, 4.5))
    # display the lowest elevation scan data
    plots = []
    plots.append(['reflectivity', 'Reflectivity (dBZ)', 0])
    plots.append(['velocity', 'Velocity (m/s)', 1])
    if (dualPolarization):
        plots.append(['differential_reflectivity',
                      r'Differential Reflectivity $Z_{DR}$ (dB)', 0])
        plots.append(['cross_correlation_ratio',
                      r'Correlation Coefficient $\rho_{HV}$', 0])
    ncols = 2
    nrows = len(plots) / 2
    for plotno, plot in enumerate(plots, start=1):
        vmin = None
        vmax = None
        if (plot[0] == 'velocity'):
            vmin = -25
            vmax = 25
        if (plot[0] == 'reflectivity'):
            vmin = -25
            vmax = 35
        if (plot[0] == 'differential_reflectivity'):
            vmin = -4
            vmax = 6
        if (plot[0] == 'cross_correlation_ratio'):
            vmin = .3
            vmax = .95

        ax = fig.add_subplot(nrows, ncols, plotno)
        display.plot(plot[0], plot[2], ax=ax, title=plot[1],
                     colorbar_label='',
                     vmin=vmin,
                     vmax=vmax,
                     mask_outside=True,
                     axislabels=(
                         'East-West distance from radar (km)' if plotno == 6
                         else
                         '',
                         'North-South distance from radar (km)' if plotno == 1
                         else ''))
        display.set_limits((-300, 300), (-300, 300), ax=ax)

        display.set_aspect_ratio('equal', ax=ax)
        display.plot_range_rings(range(100, 350, 100), lw=0.5, col='black',
                                 ax=ax)
    if save:
        plt.savefig(save)
        # Image.open(save).save(save[0:len(save) - 4] + '.jpg', 'JPEG')
        plt.close()
    else:
        plt.show()


def main():
    """Example of how to use methods of this class."""
    conn = AWSNexradData.ConnectToAWS()
    bucket = AWSNexradData.GetNexradBucket(conn)

    #bucketName = AWSNexradData.getBucketName(2017, 10, 21, 'KTLX')

    # Get list of all files from bucket
    #fileNames = AWSNexradData.getFileNamesFromBucket(bucket, bucketName)
    #print fileNames

    fullname = '2015/07/04/KMOB/KMOB20150704_111944_V06.gz'
    file = AWSNexradData.downloadDataFromBucket(bucket, fullname)
    radar = pyart.io.read_nexrad_archive(file.name)

    visualizeLDMdata(radar, False, True)

    """
    for i, file in enumerate(fileNames):
        if os.path.basename(fullname)[0:17] in file:
            print i, fullname
            file_index = i

    for i in range(file_index - 3, file_index + 4):
        file = downloadDataFromBucket(bucket, fileNames[i])
        radar = pyart.io.read_nexrad_archive(file.name)
        visualizeLDMdata(radar, 'TestImg_{}.png'.format(i), True)
    """

    conn.close()


if __name__ == "__main__":
    main()
