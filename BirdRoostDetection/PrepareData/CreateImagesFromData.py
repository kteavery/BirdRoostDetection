"""Once all NEXRAD radar images have been downloaded, convert them to images.

In order to parallelize the process of making images of the data, we run files
from each radar separately. For our research we had 81 radars and ran this file
81 times in parallel on schooner (OU super computer)

Example command:
python /home/cchilson/gitRepositories/BirdRoostDetection/BirdRoostDetection\
/PrepareData/CreateImagesFromData.py \
KLIX \
ml_labels_example.csv \
/home/cchilson/OBS_research/Data
"""
from BirdRoostDetection.PrepareData import VisualizeNexradData
import os
import sys
import pyart.io
from PIL import Image
import pandas


def getBasePath(radarFileName):
    """Given a single Nexrad radar file, create a path to save file at.

    In order to avoid saving too many files in a single folder, we save radar
    files and image in a path order using radar/year/month/day.

    Args:
        radarFileName: The name of the NEXRAD radar file.

    Returns:
        string path, RRRR/YYYY/MM/DD
    """
    radarFileName = os.path.basename(radarFileName)
    return os.path.join(radarFileName[0:4], radarFileName[4:8],
                        radarFileName[8:10], radarFileName[10:12])


def createLabelForFiles(fileNames, saveDir):
    """Given a Level 2 NEXRAD radar file, create images.

    This is a slightly fast and lazy was of creating these images. There is
    probably a better way to do this but this functions for my purposes
    I use the PyArt library to save out the radar products, and then read in the
    images and save out the 4 individual radar products.

    Args:
        fileNames: A list of filename paths, the location of the NEXRAD radar
            files.
        saveDir: The directory where the images will be saved in.
    """
    radarFilePath = 'radarfiles/'
    for f in fileNames:
        try:
            root = os.path.join(radarFilePath, getBasePath(f))
            name = f.replace('.gz', '')
            imgDir = os.path.join(saveDir, getBasePath(f)) + '/'
            imgPath = os.path.join(
                imgDir.replace(saveDir, os.path.join(saveDir, 'All/')),
                name + '.png')
            print imgPath

            if not os.path.isfile(imgPath):
                file = open(os.path.join(root, name), 'r')
                if not os.path.exists(os.path.dirname(imgPath)):
                    os.makedirs(os.path.dirname(imgPath))

                rad = pyart.io.read_nexrad_archive(file.name)

                dualPol = int(name[-1:]) >= 6
                VisualizeNexradData.visualizeLDMdata(rad, imgPath, dualPol)
                file.close()

                d1 = imgDir.replace(saveDir, os.path.join(saveDir, 'Reflectivity/'))
                d2 = imgDir.replace(saveDir, os.path.join(saveDir, 'Velocity/'))
                if dualPol:
                    d3 = imgDir.replace(saveDir, os.path.join(saveDir, 'Zdr/'))
                    d4 = imgDir.replace(saveDir, os.path.join(saveDir, 'Rho_HV/'))

                if not os.path.exists(d1):
                    os.makedirs(d1)
                if not os.path.exists(d2):
                    os.makedirs(d2)
                if dualPol:
                    if not os.path.exists(d3):
                        os.makedirs(d3)
                    if not os.path.exists(d4):
                        os.makedirs(d4)

                img = Image.open(imgPath)
                save_extension = '.png'
                if (not dualPol):
                    img1 = img.crop((115, 100, 365, 350))
                    img1.save(d1 + name + '_Reflectivity' + save_extension)

                    img2 = img.crop((495, 100, 740, 350))
                    img2.save(d2 + name + '_Velocity' + save_extension)

                if (dualPol):
                    img1 = img.crop((115, 140, 365, 390))
                    img1.save(d1 + name + '_Reflectivity' + save_extension)

                    img2 = img.crop((495, 140, 740, 390))
                    img2.save(d2 + name + '_Velocity' + save_extension)

                    img3 = img.crop((115, 520, 365, 770))
                    img3.save(d3 + name + '_Zdr' + save_extension)

                    img4 = img.crop((495, 520, 740, 770))
                    img4.save(d4 + name + '_Rho_HV' + save_extension)

                    # print root + '/' + name
        except Exception as e:
            print '{}, {}'.format(imgPath, str(e))


def main():
    """Formatted to run either locally or on schooner. Read in csv and get radar
     files listed in 'AWS_file' column. Save these files out as png images."""
    savepath = 'radarimages/'
    radar = sys.argv[1]
    working_dir = sys.argv[3]
    csvpath = sys.argv[2]
    os.chdir(working_dir)
    labels = pandas.read_csv(filepath_or_buffer=csvpath,
                             skip_blank_lines=True)

    radar_labels = labels[labels.radar == radar]
    # roost_labels = radar_labels[radar_labels.Roost == True]
    # noroost_labels = radar_labels[radar_labels.Roost == False]

    createLabelForFiles(fileNames=list(radar_labels['AWS_file']),
                        saveDir=savepath)


if __name__ == "__main__":
    main()
