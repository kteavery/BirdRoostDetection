import os
import pandas
import datetime
from BirdRoostDetection.PrepareData import NexradUtils
import numpy as np
from enum import Enum
from PIL import Image

RADAR_FILE_DIR = 'radarfiles/'
RADAR_IMAGE_DIR = 'radarimages/'


class ML_Set(Enum):
    """Machine learning set enum, includes validation, train, and test."""
    validation = 1
    training = 2
    testing = 3


class Radar_Products(Enum):
    """Radar Product enum, includes reflectivity, velocity, rho_hv, and zdr."""
    reflectivity = 1
    velocity = 2
    rho_hv = 3
    zdr = 4


ZDR = 'Zdr'
RHO_HV = 'Rho_HV'
VELOCITY = 'Velocity'
REFLECTIVITY = 'Reflectivity'


def getListOfFilesInDirectory(dir, fileType):
    """Given a folder, recursively return the names of all files of given type.

    Args:
        dir: path to folder, string
        fileType: Example: ".txt" or ".png"

    Returns:
        list of fileNames
    """
    fileNames = []
    for root, dirs, files in os.walk(dir):
        for f in files:
            if os.path.splitext(f)[1].lower() == fileType:
                fullPath = os.path.join(root, f)
                fileNames.append(fullPath)
    return fileNames


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

    def __init__(self, pd_row, root_dir):
        """Initialize class using roost directory and pandas dataframe row.

        Args:
            pd_row: A pandas dataframe row read in from a csv with the format
            in ml_labels_example.csv
            root_dir: The directory where the images as stored.
        """
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
        self.image_paths = {}
        self.image_paths[
            Radar_Products.reflectivity] = self.__get_radar_product_path(
            root_dir, REFLECTIVITY)
        self.image_paths[
            Radar_Products.velocity] = self.__get_radar_product_path(
            root_dir, VELOCITY)
        self.image_paths[Radar_Products.rho_hv] = self.__get_radar_product_path(
            root_dir, RHO_HV)
        self.image_paths[Radar_Products.zdr] = self.__get_radar_product_path(
            root_dir, ZDR)

    def get_path(self, radar_product):
        return self.image_paths[radar_product]

    def __get_radar_product_path(self, root_dir, radar_product):
        return os.path.join(root_dir, '{1}/',
                            NexradUtils.getBasePath(self.fileName),
                            '{0}_{1}.png').format(self.fileName, radar_product)


class Batch_Generator():
    """This class organized the machine learning labels and creates ML batches.

    Class Variables:
        self.root_dir: The directory where the radar images are stored
        self.ml_sets: A dictionary containing a list of files that are part of
            the given ml set
        self.batch_size: the size of the minibatch learning batches
        self.label_dict: A dictionary of the labels, the key is the filename,
        and the value is a ML_Label object.
    """

    def __init__(self,
                 ml_label_csv,
                 ml_split_csv,
                 validate_k_index,
                 test_k_index,
                 default_batch_size=32,
                 root_dir=RADAR_IMAGE_DIR):
        self.label_dict = {}
        self.root_dir = root_dir
        self.__set_ml_sets(ml_split_csv,
                           validate_k_index,
                           test_k_index)

        ml_label_pd = pandas.read_csv(ml_label_csv)
        for index, row in ml_label_pd.iterrows():
            self.label_dict[row['AWS_file']] = ML_Label(row, self.root_dir)
        self.batch_size = default_batch_size

    def __set_ml_sets(self,
                      ml_split_csv,
                      validate_k_index,
                      test_k_index):
        """Create Train, test, and Validation set from k data folds.

        The k data folds are saved out to ml_split_csv. The fold at the given
        test and train indices as set to their corresponding set. The rest
        of the data is put into train. This method will initialize the following
        class variables: self.train, self.validation, and self.test. Each of
        these contains a list of filenames that correspond with the set.

        Args:
            ml_split_csv: A path to a csv file, where the csv has two columns,
            'AWS_file' and 'split_index'.
            validate_k_index: The index of the validation set.
            test_k_index: The index of the test set.
        """
        ml_split_pd = pandas.read_csv(ml_split_csv)
        # Remove files that weren't found
        all_files = getListOfFilesInDirectory(self.root_dir + '/All', '.png')
        all_files_dict = {}
        for i in range(len(all_files)):
            all_files_dict[
                os.path.basename(all_files[i]).replace('.png', '')] = True

        for index, row in ml_split_pd.iterrows():
            if all_files_dict.get(row['AWS_file']) is None:
                ml_split_pd.drop(index, inplace=True)

        # Sort into train, test, and validation sets
        self.no_roost_sets = {}
        self.__set_ml_sets_helper(self.no_roost_sets,
                                  ml_split_pd[ml_split_pd.Roost != True],
                                  validate_k_index, test_k_index)
        self.roost_sets = {}
        self.__set_ml_sets_helper(self.roost_sets,
                                  ml_split_pd[ml_split_pd.Roost],
                                  validate_k_index, test_k_index)

    def __set_ml_sets_helper(self, ml_sets, ml_split_pd, val_k, test_k):
        no_val_pd = ml_split_pd[ml_split_pd.split_index != val_k]
        ml_sets[ML_Set.training] = list(
            no_val_pd[no_val_pd.split_index != test_k]['AWS_file'])
        ml_sets[ML_Set.validation] = list(
            ml_split_pd[ml_split_pd.split_index == val_k][
                'AWS_file'])
        ml_sets[ML_Set.testing] = list(
            ml_split_pd[ml_split_pd.split_index == test_k]['AWS_file'])

        # Shuffle the data
        np.random.shuffle(ml_sets[ML_Set.training])
        np.random.shuffle(ml_sets[ML_Set.validation])
        np.random.shuffle(ml_sets[ML_Set.testing])

    def get_batch(self, ml_set, radar_product):
        """Get a batch of data for machine learning.

        Args:
            ml_set: ML_Set enum value, train, test, or validation.
            radar_product: Radar_Product enum value, reflectivity, velocity,
                zdr, or rho_hv.

        Returns:
            train_data, ground_truth:
                The ground truth is an array of batch size, where each item
                in the array contains a single ground truth label.
                The train_data is an array of images, corresponding to the
                ground truth values.
        """
        ground_truths = []
        train_data = []
        for ml_sets in [self.roost_sets, self.no_roost_sets]:
            indices = np.random.randint(low=0,
                                        high=len(ml_sets[ml_set]),
                                        size=self.batch_size / 2)
            for index in indices:
                filename = ml_sets[ml_set][index]
                is_roost = int(self.label_dict[filename].is_roost)
                image_path = self.label_dict[filename].get_path(radar_product)
                ground_truths.append([is_roost, 1 - is_roost])
                train_data.append(self.__load_image(image_path))
        return self.__format_image_data(train_data), np.array(ground_truths)

    def __format_image_data(self, train_data):
        """Ensure that the batch of train data is properly shaped"""
        return np.array(train_data)[:, 5:245, 5:245, 0:3]

    def __load_image(self, filename):
        """Load image from filepath.

        Args:
            filename: The path to the image file.

        Returns:
            Image as numpy array.
        """
        img = Image.open(filename)
        return np.array(img)


def main():
    os.chdir('/home/carmen/PycharmProjects/BirdRoostDetection/MLData')
    batch_generator = Batch_Generator(ml_label_csv='ml_labels.csv',
                                      ml_split_csv='ml_splits.csv',
                                      validate_k_index=3,
                                      test_k_index=4)
    x, y = batch_generator.get_batch(
        ml_set=ML_Set.training,
        radar_product=Radar_Products.reflectivity)
    print y


if __name__ == "__main__":
    main()
