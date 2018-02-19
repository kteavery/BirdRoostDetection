import os
import pandas
import datetime
from BirdRoostDetection.PrepareData import NexradUtils

RADAR_FILE_DIR = 'radarfiles/'
RADAR_IMAGE_DIR = 'radarimages/'
VALIDATION = 'validation'
TRAINING = 'training'
TESTING = 'testing'
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
        self.reflectivity_path: The path to the reflectivity radar image
        self.velocity_path: The path to the velocity radar image
        self.rho_hv_path: The path to the rho_hv radar image
        self.zdr_path: The path to the zdr radar image
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

        self.reflectivity_path = self._get_radar_product_path(root_dir,
                                                              REFLECTIVITY)
        self.velocity_path = self._get_radar_product_path(root_dir, VELOCITY)
        self.rho_hv_path = self._get_radar_product_path(root_dir, RHO_HV)
        self.zdr_path = self._get_radar_product_path(root_dir, ZDR)

    def _get_radar_product_path(self, root_dir, radar_product):
        return os.path.join(root_dir, '{1}/',
                            NexradUtils.getBasePath(self.fileName),
                            '{0}_{1}.png').format(self.fileName, radar_product)


class Batch_Generator():
    """This class organized the machine learning labels and creates ML batches.

    Class Variables:
        self.root_dir: The directory where the radar images are stored
        self.train: A list of files that are part of the train set
        self.validation: A list of files that are part of the validation set
        self.test: A list of files that are part of the test set
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
        self._setTrainTestValidation(ml_split_csv,
                                     validate_k_index,
                                     test_k_index)

        ml_label_pd = pandas.read_csv(ml_label_csv)
        for index, row in ml_label_pd.iterrows():
            self.label_dict[row['AWS_file']] = ML_Label(row, self.root_dir)
        self.batch_size = default_batch_size

    def _setTrainTestValidation(self,
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
        no_val_pd = ml_split_pd[ml_split_pd.split_index != validate_k_index]
        self.train = list(
            no_val_pd[no_val_pd.split_index != test_k_index]['AWS_file'])
        self.validation = list(
            ml_split_pd[ml_split_pd.split_index == validate_k_index][
                'AWS_file'])
        self.test = list(
            ml_split_pd[ml_split_pd.split_index == test_k_index]['AWS_file'])
        print len(self.train)
        print len(self.validation)
        print len(self.test)
