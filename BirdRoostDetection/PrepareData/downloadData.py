import os
import shutil
import sys
import pandas
from BirdRoostDetection.PrepareData import AWSNexradData
from BirdRoostDetection.PrepareData import NexradUtils


def downloadRadarsFromList(fileNames, saveDir, error_file_name):
    """Download all AWS radar files in fileNames to the save directory.

    This method will download NEXRAD radar files from Amazon Web Services. All
    the files will be saved in the saveDir directory under
    YYYY/MM/DD/RRRR/filename.gz. If this method fails to download any of the
    files in fileNames, then the error will be printed in error_file_name.

    Args:
        fileNames: A list of NEXRAD radar files to download. Each string is
            formatted as follows :
            'RRRRYYYYMMDD_HHMMSS_V06.gz' or
            'RRRRYYYYMMDD_HHMMSS_V03.gz'
            (R=radar, Y=year, M=month, D=day, H=hour, M=min, S=sec)
        saveDir: The directory to save the radar files in.
        error_file_name: The text file where any errors messages will be saved.
            This should be a text file. (e.g. error.txt)
    """
    errors = []
    for index, f in enumerate(fileNames):
        file_date = NexradUtils.getTimeStampFromFilename(f)
        file_radar = NexradUtils.getRadarFromFilename(f)
        bucketName = AWSNexradData.getBucketName(year=file_date.year,
                                                 month=file_date.month,
                                                 day=file_date.day,
                                                 radar=file_radar)
        fileName = bucketName + f

        radardir = saveDir + bucketName[11:] + bucketName[:11]

        if not os.path.exists(radardir):
            os.makedirs(radardir)

        conn = AWSNexradData.ConnectToAWS()
        bucket = AWSNexradData.GetNexradBucket(conn)
        if not os.path.isfile(radardir + f):
            try:
                file = None
                for filename in AWSNexradData.getFileNamesFromBucket(bucket,
                                                                     bucketName):
                    # Ignore seconds when searching for file
                    if f[0:17] in filename:
                        file = AWSNexradData.downloadDataFromBucket(bucket,
                                                                    filename)
                shutil.copy(file.name, radardir + f)
            except Exception as e:
                errors.append('{}, {}'.format(fileName, str(e)))

        else:
            print 'skipping, file already exists: {}'.format(radardir, f)
        conn.close()

    if len(errors) > 0:
        outfile = open(error_file_name, 'w')
        outfile.write("\n".join(errors))


def main():
    """Formatted to run either locally or on schooner. Read in csv and get radar
     files listed in 'AWS_file' column"""
    savepath = 'radardata/'
    radar = sys.argv[1]
    csvpath = sys.argv[2]
    working_dir = sys.argv[3]
    os.chdir(working_dir)
    labels = pandas.read_csv(filepath_or_buffer=csvpath,
                             skip_blank_lines=True)
    radar_labels = labels[labels.radar == radar]
    fileNames = list(radar_labels['AWS_file'])
    downloadRadarsFromList(fileNames, savepath, 'error_{0}.txt'.format(radar))


if __name__ == "__main__":
    main()