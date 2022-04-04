from auto_extract.classify_organisation import file_to_pd, train, predict_main_sector
import os
import pandas as pd

infolder = os.path.join(os.getcwd(), 'tests')
inputfile = os.path.join(infolder, 'test_excel.xlsx')


def test_file_to_pd():
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
