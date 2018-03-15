import os
import datetime
from BirdRoostDetection.PrepareData import NexradUtils
import numpy as np
from PIL import Image
from BirdRoostDetection import utils


class ML_Label():
    """This class contains all the information needed for a single ML label.

    Class Variables:
        self.fileName: The filename, RRRRYYYYMMDD_HHMMSS_VO#
        self.is_roost: True is it the file contains a roost
        self.roost_id: The id of the roost, -1 if no roost
        self.latitude: The latitude of the roost in the radar file
        self.longitude: The longitude of the roost in the radar file
        self.timestamp: The radius of the roost in the radar file
        self.sunrise_time: The sunrise time at the lat, lon coordinates
        self.image_paths: A dictionary that contains path to the images with the
            following radar products : reflectivity, velocity, rho_hv, zdr
    """

    def __init__(self, pd_row, root_dir, high_memory_mode):
        """Initialize class using roost directory and pandas dataframe row.

        Args:
            pd_row: A pandas dataframe row read in from a csv with the format
            in ml_labels_example.csv
            root_dir: The directory where the images as stored.
            high_memory_mode: Boolean, if true then all of the data will be read
            in at the beginning and stored in memeory. Otherwise only one batch
            of data will be in memeory at a time. high_memory_mode is good
            for machines with slow IO and at least 8 GB of memeory available.

        """
        self.high_memory_mode = high_memory_mode
        self.fileName = pd_row['AWS_file']
        self.is_roost = pd_row['Roost']
        self.roost_id = pd_row['roost_id']
        self.latitude = pd_row['lat']
        self.longitude = pd_row['lon']
        self.radius = pd_row['radius']
        self.timestamp = datetime.datetime.strptime(pd_row['roost_time'],
                                                    '%Y-%m-%d %H:%M:%S')
        self.sunrise_time = datetime.datetime.strptime(pd_row['sunrise_time'],
                                                       '%Y-%m-%d %H:%M:%S')
        self.images = {}
        for radar_prodcut in utils.Radar_Products:
            image_path = self.__get_radar_product_path(
                root_dir, radar_prodcut.fullname)
            if self.high_memory_mode:
                self.images[radar_prodcut] = self.load_image(image_path)
            else:
                self.images[radar_prodcut] = image_path

    def get_image(self, radar_product):
        if self.high_memory_mode:
            return self.images[radar_product]
        return self.load_image(self.images[radar_product])

    def __get_radar_product_path(self, root_dir, radar_product):
        return os.path.join(root_dir, '{1}/',
                            NexradUtils.getBasePath(self.fileName),
                            '{0}_{1}.png').format(self.fileName, radar_product)

    def load_image(self, filename):
        """Load image from filepath.

        Args:
            filename: The path to the image file.

        Returns:
            Image as numpy array.
        """
        dim = 120
        if not os.path.exists(filename):
            return None
        img = np.array(Image.open(filename))
        shape = img.shape
        w_mid = shape[0] / 2
        h_mid = shape[1] / 2
        img = img[w_mid - dim:w_mid + dim, h_mid - dim:h_mid + dim]
        return img
