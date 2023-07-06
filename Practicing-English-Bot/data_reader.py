import pandas
from pathlib import Path


def get_words(file_name):
    """
    reads the document for the words and extracts the words
    :param file_name: the file which has the words
    :return: list of the words
    """
    data_path = Path('./').joinpath('data', file_name)
    data = pandas.read_csv(data_path)
    data_refined = data.loc[data['word'].str.len() > 3, ['word']]
    return data_refined['word'].values.tolist()
