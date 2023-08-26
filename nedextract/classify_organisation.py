"""Classify the sector in which the organisation is active.

- Read the required input data into a dataframe
- train a classifier model
- predict the sector using input text and a pretrained classifier model.

Copyright 2022 Netherlands eScience Center
Licensed under the Apache License, version 2.0. See LICENSE for details.
"""


import argparse
import os
from argparse import RawTextHelpFormatter
from datetime import datetime
import pandas as pd
from joblib import dump
from joblib import load
from sklearn import metrics
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from nedextract.preprocessing import preprocess_pdf


def file_to_pd(inputfile: str):
    """Read data from an Excel file and preprocess the text data.

    1. Read data from the specified Excel file ('inputfile') using pandas.
    2. Drop rows with missing values in the 'Sector' and 'Problem' columns.
    3. Assign the content of the 'Bestand' column to a new 'text' column in the DataFrame.
    4. Preprocess the text column using the 'preprocess_pdf' function.

    Args:
        inputfile (str): The path to the Excel file to be read.

    Returns:
        pandas.DataFrame: A pandas DataFrame containing the processed data.
    """
    df = pd.read_excel(inputfile)
    df.dropna(subset=["Sector"], inplace=True)
    df.dropna(subset=["Problem"], inplace=True)
    df = df.assign(text=df["Bestand"])
    df["text"] = df["text"].apply(preprocess_pdf)
    return df


def train(data: pd.DataFrame, train_size: float, alpha: float, save: bool = False):
    """Train a MultinomialNB classifier to classify texts into the main sector categories.

    This function trains a Multinomial Naive Bayes classifier to classify text data into
    main sector categories. It uses the given dataset ('data') containing 'text' and 'Sector'
    columns. The 'text' column contains the textual data, and the 'Sector' column represents
    the main sector categories that the texts belong to.

    The function performs the following steps:
    1. Factorizes the 'Sector' column, which contains the labels, to convert categories into numerical labels.
    2. Splits the data into training and testing sets based on the specified 'train_size'.
    3. Applies Term Frequency-Inverse Document Frequency (TF-IDF) vectorization to the
       training data to transform text features into numerical vectors.
    4. Trains a Multinomial Naive Bayes classifier using the training data.
    5. Predicts the sectors of the test data using the trained classifier.
    6. Calculates and prints the total accuracy classification score and the confusion matrix
       for the predicted labels.
    7. Save the trained model to joblib files if the 'save' argument is True

    Args:
        data (pandas.DataFrame): The dataset containing the 'text' and 'Sector' columns.
        train_size (float): The proportion of the dataset to be used for training (0.0 to 1.0).
        alpha (float): The additive (Laplace/Lidstone) smoothing parameter for the Naive Bayes model.
        save (bool, optional): Whether to save the trained classifier, labels, and TF-IDF vectorizer
                               to files in the 'Pretrained' directory. Defaults to False.

    Returns:
        tuple: A tuple containing the trained classifier, the label encoding for sectors, and the TF-IDF vectorizer.
    """
    # Factorize the categories
    sector_f, label = data['Sector'].factorize()

    # Split data in train and test set
    x_train, x_test, y_train, y_test = train_test_split(data['text'],
                                                        sector_f,
                                                        train_size=train_size, random_state=1)
    # Term frequency, normalized for total terms in document
    tf_idf = TfidfVectorizer()

    # Apply tf idf to training data
    x_train_tf = tf_idf.fit_transform(x_train)

    # Transform test data tinto tf-vectorized matrix
    x_test_tf = tf_idf.transform(x_test)

    # Train a Naive Bayes classifier on the training data
    clf = MultinomialNB(alpha=alpha)
    clf.fit(x_train_tf, y_train)

    # Predict sector of test data
    predicted = clf.predict(x_test_tf)

    # calculate accuracy of predictions
    print(f'Total accuracy classification score: {metrics.accuracy_score(y_test, predicted)}')
    print('Confusion matrix for the following labels:')
    print(label)
    print(metrics.confusion_matrix(y_test, predicted))

    # save the model
    if save:
        dump(clf, os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                               'trained_sector_classifier.joblib'))
        dump(label, os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                                 'labels_sector_classifier.joblib'))
        dump(tf_idf, os.path.join(os.path.join(os.getcwd(), 'Pretrained'),
                                  'tf_idf_vectorizer.joblib'))
    return clf, label


def predict_main_sector(saved_clf: str, saved_labels: str, saved_vector: str, text: str):
    """Predict the main sector category for a given text using a trained classifier.

    This function predicts the main sector category for a given text using a pre-trained
    Multinomial Naive Bayes classifier (which can be created using the function 'train').
    It loads the classifier, label encoding for sectors, and the TF-IDF vectorizer from the saved files
    ('saved_clf', 'saved_labels', and 'saved_vector') and then processes the input 'text' to predict its main sector.

    Args:
        saved_clf (str): The file path to the saved pre-trained classifier (joblib file).
        saved_labels (str): The file path to the saved label encoding for sectors (joblib file).
        saved_vector (str): The file path to the saved TF-IDF vectorizer (joblib file).
        text (str): The text for which the main sector category needs to be predicted.

    Returns:
        str: The predicted main sector category for the input text.
    """
    clf = load(saved_clf)
    labels = load(saved_labels)
    tf_idf = load(saved_vector)
    text_tf = tf_idf.transform([text])
    predicted = clf.predict(text_tf)
    predicted_class = labels[predicted]
    return predicted_class[0]


if __name__ == "__main__":
    desc = """ This script can train a classifier to determine the sector in which an organization is
    active based on the annual report. Use the -f argument to supply a training file. This file
    should contain: file names referencing the files on which to train (column "Bestand"),
    classification label (column "Sector"), and problem indicator (column "Problem"). Rows with
    empty classification or with empty problem column are omitted from the training data. I.E. if
    a file has a problem and you do not want it to be included, make sure the problem column is
    empty. Otherwise, make sure this column has a value.

    Training is performed with the sklearn naive_bayes MultinomialNB classifier, using
    tfidf_transformer. The alpha (smoothing) value of the classifier is set to 0.0001, because many
    words have a low frequency.

    The trained classifier is saved using joblib."""

    # start time
    start_time = f"{datetime.now():%Y-%m-%d %H:%M:%S}"
    print(start_time, 'Starting to preprocess the input data.')

    # Parse command line arguments
    parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
    parser.add_argument('-f', '--inputfile', help='Training file.')
    parser.add_argument('-a', '--alpha', default=0.0001,
                        help='smoothing parameter used by MultinomialNB.')
    parser.add_argument('-t', '--train_size', default=0.8,
                        help='fraction of data to be used as training data.')
    parser.add_argument('-s', '--save', default=False, help='save the trained model')
    args = parser.parse_args()

    if not args.inputfile:
        raise FileExistsError('No inputfile provided. Run with -h for help on arguments to be provided.')

    data = file_to_pd(args.inputfile)
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}",
          'Finished preprocssing the input data. Starting training.')
    clf, label = train(data, args.train_size, args.alpha, args.save)
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished training and saved the trained model.')
