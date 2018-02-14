from BirdRoostDetection.PrepareData import VisualizeNexradData
import os
import sys
import pyart.io
from PIL import Image
import pandas


def getBasePath(radarFileName):
    """Given an AWS radar file, return radar/year/month/day.
    TODO: finish docstring
    """
    return os.path.join(radarFileName[0:4], radarFileName[4:8],
                        radarFileName[8:10], radarFileName[10:12])


def createLabelForFiles(fileNames, saveDir):
    #TODO write doc string
    radarFilePath = 'radarfiles/'
    for f in fileNames:
        root = os.path.join(radarFilePath, getBasePath(f))
        name = f.replace('.gz', '')
        print root, name

        file = open(os.path.join(root, name), 'r')
        imgDir = os.path.join(saveDir, getBasePath(f))
        imgPath = os.path.join(saveDir, getBasePath(f), name + '.png')
        if not os.path.exists(imgDir):
            os.makedirs(imgDir)

        rad = pyart.io.read_nexrad_archive(file.name)

        dualPol = int(name[-1:]) >= 6
        VisualizeNexradData.visualizeLDMdata(rad, imgPath, dualPol)
        file.close()

        d1 = imgDir.replace('Roost', 'Roost_Reflectivity')
        d2 = imgDir.replace('Roost', 'Roost_Velocity')
        if dualPol:
            d3 = imgDir.replace('Roost', 'Roost_Zdr')
            d4 = imgDir.replace('Roost', 'Roost_Rho_HV')

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

        print root + '/' + name


def main():
    """Formatted to run either locally or on schooner. Read in csv and get radar
     files listed in 'AWS_file' column"""
    savepath = 'radarimages/'
    radar = sys.argv[1]
    working_dir = sys.argv[3]
    csvpath = sys.argv[2]
    os.chdir(working_dir)
    labels = pandas.read_csv(filepath_or_buffer=csvpath,
                             skip_blank_lines=True)

    radar_labels = labels[labels.radar == radar]
    roost_labels = radar_labels[radar_labels.Roost == True]
    noroost_labels = radar_labels[radar_labels.Roost == False]

    createLabelForFiles(fileNames=list(roost_labels['AWS_file']),
                        saveDir=os.path.join(savepath, 'Roost'))
    createLabelForFiles(fileNames=list(noroost_labels['AWS_file']),
                        saveDir=os.path.join(savepath, 'NoRoost'))


if __name__ == "__main__":
    main()
