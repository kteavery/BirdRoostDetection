"""Train the shallow CNN model on a single radar product.

Use command line arguments to select which radar product to train the model on.
Optionally input the location of the save file where the default is
model/radar_product/
Use an integer to select a radar_product from the following list:
    0 : Reflectivity
    1 : Velocity
    2 : Correlation Coefficient
    3 : Differential Reflectivity

Example command:
python train.py \
--radar_product=0 \
--log_path=model/Reflectivity/ \
--eval_increment=5 \
--num_iterations=2500 \
--checkpoint_frequency=100 \
--learning_rate=.001

"""
import BirdRoostDetection.LoadSettings as settings
from BirdRoostDetection import utils
from BirdRoostDetection.BuildModels import readMLData
from BirdRoostDetection.BuildModels import ml_utils
from keras.callbacks import TensorBoard
import os
import argparse
from BirdRoostDetection.BuildModels.ShallowCNN import model as keras_model



def train(log_path, radar_product, eval_increment=5,
          num_iterations=2500, checkpoint_frequency=100, lr=.0001):
    """"Train the shallow CNN model on a single radar product.

    Args:
        log_path: The location of the save directory. The model checkpoints,
            model weights, and the tensorboard events are all saved in this
            directory.
        radar_product: The radar product the model is training on. This should
            be a value of type utils.Radar_Products.
        eval_increment: How frequently the model prints checks validation result
        num_iterations: The number of training iterations the model will run.
        checkpoint_frequency: How many training iterations should the model
            perform before saving out a checkpoint of the model training.
        lr: The learning rate of the model, this value must be between 0 and 1.
            e.g. .1, .05, .001
    """
    batch_generator = readMLData.Batch_Generator(
        ml_label_csv=settings.LABEL_CSV,
        ml_split_csv=settings.ML_SPLITS_DATA)

    save_file = ml_utils.KERAS_SAVE_FILE.format(radar_product.fullname, '{}')

    checkpoint_path = log_path + ml_utils.CHECKPOINT_DIR
    if not os.path.exists(checkpoint_path):
        os.makedirs(os.path.dirname(checkpoint_path))
    model = keras_model.build_model(inputDimensions=(240, 240, 1), lr=lr)

    # Setup callbacks
    callback = TensorBoard(log_path)
    callback.set_model(model)
    train_names = ['train_loss', 'train_accuracy']
    val_names = ['val_loss', 'val_accuracy']

    progress_string = '{} Epoch: {} Loss: {} Accuracy {}'

    for batch_no in range(num_iterations):
        x, y, _ = batch_generator.get_batch(
            ml_set=utils.ML_Set.training,
            radar_product=radar_product)
        train_logs = model.train_on_batch(x, y)
        print progress_string.format(utils.ML_Set.training.fullname, batch_no,
                                     train_logs[0], train_logs[1])
        ml_utils.write_log(callback, train_names, train_logs, batch_no)
        if (batch_no % eval_increment == 0):
            model.save_weights(log_path + save_file.format(''))
            x_, y_, _ = batch_generator.get_batch(
                ml_set=utils.ML_Set.validation,
                radar_product=radar_product)
            val_logs = model.test_on_batch(x_, y_)
            ml_utils.write_log(callback, val_names, val_logs, batch_no)
            print progress_string.format(utils.ML_Set.validation.fullname,
                                         batch_no,
                                         val_logs[0], val_logs[1])

        if batch_no % checkpoint_frequency == 0 \
                or batch_no == num_iterations - 1:
            model.save_weights(
                os.path.join(checkpoint_path, save_file.format(batch_no)))

    model.save_weights(save_file)


def main(results):
    os.chdir(settings.WORKING_DIRECTORY)
    radar_product = utils.Radar_Products(results.radar_product)
    if results.log_path is None:
        log_path = ml_utils.LOG_PATH.format(radar_product.fullname)
    else:
        log_path = results.log_path

    train(log_path=log_path,
          radar_product=radar_product,
          eval_increment=results.eval_increment,
          num_iterations=results.num_iterations,
          checkpoint_frequency=results.checkpoint_frequency,
          lr=results.learning_rate)


if __name__ == "__main__":
    os.chdir(settings.WORKING_DIRECTORY)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-r',
        '--radar_product',
        type=int,
        default=0,
        help="""
            Use an integer to select a radar_product from the following list:
                0 : Reflectivity
                1 : Velocity
                2 : Correlation Coefficient
                3 : Differential Reflectivity
            """
    )

    parser.add_argument(
        '-l',
        '--log_path',
        type=str,
        default=None,
        help="""
            Optionally input the location of the save file where the default is
            model/radar_product
            """
    )

    parser.add_argument(
        '-e',
        '--eval_increment',
        type=int,
        default=5,
        help="""How frequently the model prints out the validation results."""
    )

    parser.add_argument(
        '-n',
        '--num_iterations',
        type=int,
        default=2500,
        help="""The number of training iterations the model will run"""
    )

    parser.add_argument(
        '-c',
        '--checkpoint_frequency',
        type=int,
        default=100,
        help="""
            How many training iterations should the model perform before saving 
            out a checkpoint of the model training.
            """
    )

    parser.add_argument(
        '-lr',
        '--learning_rate',
        type=float,
        default=.0001,
        help="""
            The learning rate of the model, this value must be between 0 and 1
            .e.g. .1, .05, .001
            """
    )
    results = parser.parse_args()
    main(results)
