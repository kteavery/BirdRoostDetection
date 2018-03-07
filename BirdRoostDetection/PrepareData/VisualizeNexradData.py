import matplotlib.pyplot as plt
import pyart.graph
import pyart.io


def visualizeLDMdata(radar, save, dualPolarization=False, displayCircles=False):
    """Visualize the LDM2 radar data. Either display or save resulting image.

    This method was modified from code found at the following website :
    https://eng.climate.com/2015/10/27/how-to-read-and-display-nexrad-on-aws
    -using-python/. If the image is dual polarization it will save out
    reflectivity and velocity, otherwise it will also save differential
    reflectivity and correlation coefficient. These later radar products
    are only available in the dual polarization radar upgrades from 2012-2013.

    Args:
        radar:
        save:
        dualPolarization:
        displayCircles:
    """
    display = pyart.graph.RadarDisplay(radar)
    if (dualPolarization):
        fig = plt.figure(figsize=(9, 9))
    else:
        fig = plt.figure(figsize=(9, 4.5))
    # display the lowest elevation scan data
    plots = []
    plots.append(['reflectivity', 'Reflectivity_0 (dBZ)', 0])
    plots.append(['velocity', 'Velocity (m/s)', 1])
    if (dualPolarization):
        plots.append(['differential_reflectivity',
                      r'Differential Reflectivity $Z_{DR}$ (dB)', 0])
        plots.append(['cross_correlation_ratio',
                      r'Correlation Coefficient $\rho_{HV}$', 0])
    ncols = 2
    nrows = len(plots) / 2
    for plotno, plot in enumerate(plots, start=1):
        if (dualPolarization):
            mask_tuple = ['cross_correlation_ratio', .975]

        cmap = None
        vmin = None
        vmax = None

        if (plot[0] == 'reflectivity'):
            vmin = -20
            vmax = 30
        if (plot[0] == 'velocity'):
            vmin = -20
            vmax = 20
            cmap = 'coolwarm'
        if (plot[0] == 'differential_reflectivity'):
            vmin = -4
            vmax = 8
            cmap = 'coolwarm'
        if (plot[0] == 'cross_correlation_ratio'):
            vmin = .3
            vmax = .95
            cmap = 'jet'

        ax = fig.add_subplot(nrows, ncols, plotno)
        display.plot(plot[0], plot[2], ax=ax, title=plot[1],
                     vmin=vmin,
                     vmax=vmax,
                     cmap=cmap,
                     colorbar_label='',
                     mask_outside=True,
                     axislabels=(
                         'East-West distance from radar (km)' if plotno == 6
                         else
                         '',
                         'North-South distance from radar (km)' if plotno == 1
                         else ''))
        radius = 300
        display.set_limits((-radius, radius), (-radius, radius), ax=ax)

        display.set_aspect_ratio('equal', ax=ax)
        if (displayCircles):
            display.plot_range_rings(range(100, 350, 100), lw=0.5, col='black',
                                     ax=ax)
    if save:
        plt.savefig(save)
        plt.close()
    else:
        plt.show()
