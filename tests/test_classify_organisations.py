"""Unit tests for the file /extract_pdf/classify_organisations."""
import os
import unittest
import pandas as pd
from nedextract.classify_organisation import file_to_pd
from nedextract.classify_organisation import train


infolder = os.path.join(os.getcwd(), 'tests')
inputfile = os.path.join(infolder, 'test_excel.xlsx')


class TestClassifyOrganisations(unittest.TestCase):
    """Unit tests for classify_organisations.

    This class contains the following functions:
    - test_file_to_pd: tests the file_to_pd function that reads an excel file into a pandas dataframe and
      performs some preprocssing steps
    - test_train: tests the train function which trains a Multinomial Naive Bayes
      classifier to classify texts into main sector categories.
    """

    def test_file_to_pd(self):
        """Unit test function for the 'file_to_pd' function.

        The 'file_to_pdf' function reads an excel file into a pandas dataframe and
        pefrforms some preprocssing steps.

        This test asserts for the inputfile 'test_excel.xslx' if the returned value is a pandas dataframe

        Raises:
            AssertionError: if the output iof the 'file_to_pd' function is not a pandas dataframe.
        """
        result = file_to_pd(inputfile)
        assert isinstance(result, pd.DataFrame)

    def test_train(self):
        """Unit test function for the 'train' function.

        This function tests the 'train' function, which trains a Multinomial Naive Bayes
        classifier to classify texts into main sector categories.

        The test function performs the following steps:
        1. Reads data from the test inputfile using the 'file_to_pd' function into a df.
        2. Calls the 'train' function with the 'df' DataFrame, train_size=0.99, alpha=0.99,
        and save=False. The function returns a tuple, and the second element of the tuple
        ('label') represents the label encoding for sectors.
        3. Asserts that the 'label' obtained from the 'train' function matches the expected
        sector label 'Natuur'.

        Raises:
            AssertionError: If the 'label' obtained from the 'train' function does not match
                            the expected sector label 'Natuur'.
        """
        df = file_to_pd(inputfile)
        label = train(df, 0.99, 0.99, False)[1]
        assert label == 'Natuur'
