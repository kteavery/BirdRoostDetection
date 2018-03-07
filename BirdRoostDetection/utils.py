from enum import Enum

RADAR_FILE_DIR = 'radarfiles/'
RADAR_IMAGE_DIR = 'radarimages/'



class ML_Set(Enum):
    """Machine learning set enum, includes validation, train, and test."""
    validation = 0, 'Validation'
    training = 1, 'Training'
    testing = 2, 'Testing'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value


class Radar_Products(Enum):
    """Radar Product enum, includes reflectivity, velocity, rho_hv, and zdr."""
    reflectivity = 0, 'Reflectivity'
    velocity = 1, 'Velocity'
    cc = 2, 'Correlation_Coefficient'
    diff_reflectivity = 3, 'Differential_Reflectivity'

    def __new__(cls, value, name):
        member = object.__new__(cls)
        member._value_ = value
        member.fullname = name
        return member

    def __int__(self):
        return self.value

pyart_key_dict = {
    Radar_Products.reflectivity: 'reflectivity',
    Radar_Products.velocity: 'velocity',
    Radar_Products.diff_reflectivity: 'differential_reflectivity',
    Radar_Products.cc: 'cross_correlation_ratio'
}
