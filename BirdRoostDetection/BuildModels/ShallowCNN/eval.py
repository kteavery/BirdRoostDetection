import os
import BirdRoostDetection.BuildModels.ShallowCNN.model as ml_model
from BirdRoostDetection.BuildModels import readMLData
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt


def main():
    os.chdir('/home/carmen/PycharmProjects/BirdRoostDetection/MLData')
    model = ml_model.build_model((240, 240, 4))
    model.load_weights('model/reflectivity/checkpoint/reflectivity400.h5')

    test_image = 'radarimages/Reflectivity/KMOB/2014/06/30' \
                 '/KMOB20140630_110631_V06_Reflectivity.png'
    img = Image.open(test_image)
    img = np.array(img)[5:245, 5:245, 0:3]
    img = img.reshape((1, 240, 240, 3))
    plt.imshow(img[0])
    plt.show()

    return

    print model.predict(x=img)

    x = np.copy(img)
    x[:, 0:145, 0:145, :].fill(255)
    print model.predict(x=x)
    plt.imshow(x[0])
    plt.show()

    x = np.copy(img)
    x[:, 0:145, 145:250, :].fill(255)
    print model.predict(x=x)
    plt.imshow(x[0])
    plt.show()

    x = np.copy(img)
    x[:, 145:250, 145:250, :].fill(255)
    print model.predict(x=x)
    plt.imshow(x[0])
    plt.show()

    x = np.copy(img)
    x[:, 145:250, 0:145, :].fill(255)
    print model.predict(x=x)
    plt.imshow(x[0])
    plt.show()


if __name__ == "__main__":
    main()
