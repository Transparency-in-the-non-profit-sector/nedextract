import os
from auto_extract.read_pdf import download_stanza_NL


def test_stanza_NL():
    assert(True) is os.path.exists(download_stanza_NL())
