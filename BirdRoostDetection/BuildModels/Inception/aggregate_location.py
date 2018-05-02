import os.path
from BirdRoostDetection import utils
import BirdRoostDetection.LoadSettings as settings
from BirdRoostDetection.BuildModels.Inception import aggregate_train
import os
from BirdRoostDetection import utils
import os.path
import numpy as np
import tensorflow as tf
from tensorflow.python.platform import gfile
from BirdRoostDetection.BuildModels.Inception import retrain

WHITE_COLOR = 0.9921875

def run_bottleneck_on_image(sess, image_path, image_data_tensor,
                            decoded_image_tensor, resized_input_tensor,
                            bottleneck_tensor):
    image_data = gfile.FastGFile(image_path, 'rb').read()
    resized_input_values = sess.run(decoded_image_tensor,
                                    {image_data_tensor: image_data})

    print resized_input_values.shape

    bottleneck_values = sess.run(bottleneck_tensor,
                                 {resized_input_tensor: resized_input_values})
    bottleneck_values = np.squeeze(bottleneck_values)
    return bottleneck_values


def test(model, bottleneck_list, radar_fields):
    x, y, _ = aggregate_train.get_random_cached_bottlenecks(
        image_lists=bottleneck_list,
        how_many=512,
        category='training',
        radar_fields=radar_fields)
    result = model.evaluate(x, y, 32)
    print result


def get_bottleneck():
    # Gather information about the model architecture we'll be using.
    model_dir = 'tf_files/models/'
    model_info = retrain.create_model_info('inception_v3')
    retrain.maybe_download_and_extract(model_info['data_url'], model_dir)
    graph, bottleneck_tensor, resized_image_tensor = (
        retrain.create_model_graph(model_info, model_dir))

    with tf.Session(graph=graph) as sess:
        # Set up the image decoding sub-graph.
        jpeg_data_tensor, decoded_image_tensor = retrain.add_jpeg_decoding(
            model_info['input_width'], model_info['input_height'],
            model_info['input_depth'], model_info['input_mean'],
            model_info['input_std'])

        image_path = '/home/carmen/PycharmProjects/BirdRoostDetection/MLData' \
                     '/radarimages/{0}_Color/KABR/2012/08/05' \
                     '/KABR20120805_092139_V06_{0}.png'.format(
            'Correlation_Coefficient')


        bottleneck_values = run_bottleneck_on_image(
            sess, image_path, jpeg_data_tensor, decoded_image_tensor,
            resized_image_tensor, bottleneck_tensor)
        print len(bottleneck_values)


def main():
    os.chdir(settings.WORKING_DIRECTORY)
    dual_pol = True

    get_bottleneck()
    return

    if dual_pol:
        radar_field = utils.Radar_Products.cc
        radar_fields = aggregate_train.dual_pol_fields
        save = 'dual_pol.h5'
        model = aggregate_train.create_model(8192, save)
    else:
        radar_field = utils.Radar_Products.reflectivity
        radar_fields = aggregate_train.legacy_fields
        save = 'legacy.h5'
        model = aggregate_train.create_model(4096, save)

    image_lists = aggregate_train.create_image_lists(radar_field)
    bottleneck_list = aggregate_train.get_bottleneck_list(image_lists,
                                                          radar_field)
    test(model, bottleneck_list, radar_fields)


if __name__ == '__main__':
    main()
