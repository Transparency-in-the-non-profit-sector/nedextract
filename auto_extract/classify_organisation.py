# Copyright 2022 Netherlands eScience Center and Vrije Universiteit Amsterdam
# Licensed under the Apache License, version 2.0. See LICENSE for details.

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
from auto_extract.preprocessing import preprocess_pdf


def file_to_pd(inputfile):
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


def train(data, train_size, alpha, save=False):
    """Train a MultinomialNB classifier to classify texts into the main sector categories"""
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


def predict_main_sector(saved_clf, saved_labels, saved_vector, text):
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

    if not (args.inputfile):
        raise Exception('No inputfile provided. Run with -h for help on arguments to be provided.')

    data = file_to_pd(args.inputfile)
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}",
          'Finished preprocssing the input data. Starting training.')
    clf, label = train(data, args.train_size, args.alpha, args.save)
    print(f"{datetime.now():%Y-%m-%d %H:%M:%S}", 'Finished training and saved the trained model.')
