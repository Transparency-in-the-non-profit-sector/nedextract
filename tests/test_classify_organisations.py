import os
import pandas as pd
from auto_extract.classify_organisation import file_to_pd
from auto_extract.classify_organisation import predict_main_sector
from auto_extract.classify_organisation import train


infolder = os.path.join(os.getcwd(), 'tests')
inputfile = os.path.join(infolder, 'test_excel.xlsx')


def test_file_to_pd():
    """Unit test function for the 'file_to_pd' function.

    The 'file_to_pdf' function reads an excel file into a pandas dataframe and 
    pefrforms some preprocssing steps.

    This test asserts for the inputfile 'test_excel.xslx' if the returned value is a pandas dataframe

    Raises:
        AssertionError: if the output iof the 'file_to_pd' function is not a pandas dataframe.
    """
    result = file_to_pd(inputfile)
    assert(isinstance(result, pd.DataFrame))


def test_train():
    df = file_to_pd(inputfile)
    label = train(df, 0.99, 0.99, False)[1]
    assert(label == 'Natuur')


def test_predict_main_sector():
    saved_clf = os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                             'trained_sector_classifier.joblib')
    saved_labels = os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                                'labels_sector_classifier.joblib')
    saved_vector = os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                                'tf_idf_vectorizer.joblib')
    df = file_to_pd(inputfile)
    result = predict_main_sector(saved_clf, saved_labels, saved_vector, df.text[0])
    expected = 'Natuur en milieu'
    assert(result == expected)
