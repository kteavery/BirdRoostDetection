"""Read in csv and create train, test, and validation splits for ML.

Example command:
python create_ml_splits.py \
ml_labels.csv \
ml_splits.csv \
/home/carmen/PycharmProjects/BirdRoostDetection/MLData/

"""

import os
import sys
import pandas


def ml_splits_by_date(csv_input_path,
                      csv_output_path,
                      k=5):
    """Split labeled data for k-fold cross validation.

    For machine learning, you need a training, validation, and test set. This
    method will read in a csv from csv_input_path. This data should be formatted
    like the ml_labels_example file. It will then create k splits of the data.
    Each time the data is used for training, k - 2 splits will be used for
    training, 1 split will be used for testing, and 1 split will be used for
    validating. This method will split the data by date (to avoid cross
    contamination of the datasets) and then write out a csv used to look up
    which file belongs to which split.

    Args:
        csv_input_path: The input file location. Formated like
        example_labels.csv, a string.
        csv_output_path: The output csv location path, a string. The output csv
        will be saved to this location.
        k: The size of k for k fold cross validation.
    """
    pd = pandas.read_csv(csv_input_path)

    basenames = {}
    file_list = list(pd['AWS_file'])
    fold_images = [[] for split_index in range(k)]

    index = 0
    for file_name in file_list:
        basename = file_name[4:12]
        if basename not in basenames:
            basenames[basename] = index
            index = (index + 1) % 5

        hash = basenames[basename]

        for split_index in range(k):
            if hash == split_index:
                fold_images[split_index].append(file_name)

    output = []
    for split_index in range(k):
        for file_name in fold_images[split_index]:
            output.append({'split_index': split_index, 'AWS_file': file_name})
    output_pd = pandas.DataFrame.from_dict(output)
    output_pd.to_csv(csv_output_path, index=False)


def main():
    csv_input_path = sys.argv[1]
    csv_output_path = sys.argv[2]
    working_dir = sys.argv[3]
    os.chdir(working_dir)
    ml_splits_by_date(csv_input_path=csv_input_path,
                      csv_output_path=csv_output_path,
                      k=5)


if __name__ == "__main__":
    main()
