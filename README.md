# BirdRoostDetection
This code was developed for the Oklahoma Biological Survey for a research project. We use machine learning to automate the detection of pre migratory purple martin roosts, their location, and the radius of the roost in NEXRAD radar data.

## Requires Software
- tensorflow https://www.tensorflow.org/install/
- Keras https://keras.io/
- PyArt http://arm-doe.github.io/pyart/
- Numpy http://www.numpy.org/
- Matplotlib https://matplotlib.org/

## Setting up Amazon Web Services
- In order to access radar files stored on Amazon Web Services you will first need to setup the .boto file with your user credentials.
- See instructions here: https://aws.amazon.com/developers/getting-started/python/