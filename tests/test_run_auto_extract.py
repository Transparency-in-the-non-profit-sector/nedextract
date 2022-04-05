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
    url = ("https://github.com/Transparency-in-the-non-profit-sector/" +
           "np-transparency/blob/main/tests/test_report.pdf")
    testarg = ['-u', url]
    returnargs = main(testarg)
    assert(returnargs.url == url)
