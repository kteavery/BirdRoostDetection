from BirdRoostDetection.BuildModels import readMLData
from BirdRoostDetection.BuildModels.ShallowCNN import model as keras_model
from BirdRoostDetection.BuildModels import ml_utils
from keras.callbacks import TensorBoard
import BirdRoostDetection.LoadSettings as settings
import os


def train(log_path, radar_field, save_file, batch_generator):
    checkpoint_path = log_path + '/checkpoint/'
    if not os.path.exists(checkpoint_path):
        os.makedirs(os.path.dirname(checkpoint_path))
    model = keras_model.build_model(inputDimensions=(240, 240, 3), lr=.0001)

    # Setup callbacks
    callback = TensorBoard(log_path)
    callback.set_model(model)
    train_names = ['train_loss', 'train_accuracy']
    val_names = ['val_loss', 'val_accuracy']

    eval_increment = 5
    num_iterations = 2500

    progress_string = '{} Epoch: {} Loss: {} Accuracy {}'

    for batch_no in range(num_iterations):
        x, y = batch_generator.get_batch(
            ml_set=readMLData.ML_Set.training,
            radar_product=radar_field)
        train_logs = model.train_on_batch(x, y)
        print progress_string.format('Train', batch_no,
                                     train_logs[0], train_logs[1])
        ml_utils.write_log(callback, train_names, train_logs, batch_no)
        if (batch_no % eval_increment == 0):
            model.save_weights(save_file)
            x_, y_ = batch_generator.get_batch(
                ml_set=readMLData.ML_Set.validation,
                radar_product=radar_field)
            val_logs = model.test_on_batch(x_, y_)
            ml_utils.write_log(callback, val_names, val_logs, batch_no)
            print progress_string.format('Validation', batch_no,
                                         val_logs[0], val_logs[1])

        if (batch_no % 100 == 0 or batch_no == num_iterations - 1):
            model.save_weights(
                os.path.join(checkpoint_path, save_file.format(batch_no)))

    model.save_weights(save_file)


def main():
    os.chdir(settings.WORKING_DIRECTORY)
    batch_generator = readMLData.Batch_Generator(
        ml_label_csv=settings.LABEL_CSV,
        ml_split_csv=settings.ML_SPLITS_DATA,
        validate_k_index=3,
        test_k_index=4)

    train(log_path='model/reflectivity/',
          radar_field=readMLData.Radar_Products.reflectivity,
          save_file='reflectivity{}.h5',
          batch_generator=batch_generator)


if __name__ == "__main__":
    main()
