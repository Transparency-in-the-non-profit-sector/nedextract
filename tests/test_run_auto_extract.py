import os
from auto_extract.run_auto_extract import main


def test_main():
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    testarg = infile
    returnargs = main(testarg)
    assert(returnargs.file == infile)
