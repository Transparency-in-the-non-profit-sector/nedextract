import os
from auto_extract.run_auto_extract import main


def test_main():
    indir = os.path.join(os.getcwd(), 'tests')
    infile = os.path.join(indir, 'test_report.pdf')
    testarg = ['-f', infile]
    returnargs = main(testarg)
    assert(returnargs.file == infile)
    testarg = ['-d', indir]
    returnargs = main(testarg)
    assert(returnargs.directory == indir)
