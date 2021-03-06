# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for `astropy.vo.validator.inspect`."""
from __future__ import absolute_import, division, print_function, unicode_literals

# STDLIB
import os
import shutil
import tempfile

# LOCAL
from .. import inspect
from ...client.vos_catalog import BASEURL
from ....utils.data import _find_pkg_data_path, get_pkg_data_filename


__doctest_skip__ = ['*']


class TestConeSearchResults(object):
    """Inspection of `TestConeSearchValidation` results."""
    def setup_class(self):
        self.datadir = 'data'
        self.out_dir = tempfile.mkdtemp()
        BASEURL.set(_find_pkg_data_path(self.datadir) + os.sep)
        self.r = inspect.ConeSearchResults()

    def test_catkeys(self):
        assert (self.r.catkeys['good'] ==
                ['HST Guide Star Catalog 2.3 1',
                 'The USNO-A2.0 Catalogue (Monet+ 1998) 1'])
        assert self.r.catkeys['warn'] == []
        assert self.r.catkeys['exception'] == []
        assert self.r.catkeys['error'] == []

    def gen_cmp(self, func, oname, *args, **kwargs):
        dat_file = get_pkg_data_filename(os.path.join(self.datadir, oname))
        out_file = os.path.join(self.out_dir, oname)
        with open(out_file, 'w') as fout:
            func(fout=fout, *args, **kwargs)

        with open(dat_file) as f1:
            contents_1 = f1.readlines()
        with open(out_file) as f2:
            contents_2 = f2.readlines()

        assert len(contents_1) == len(contents_2)

        # json.dumps() might or might not add trailing whitespace
        # http://bugs.python.org/issue16333
        for line1, line2 in zip(contents_1, contents_2):
            assert line1.rstrip() == line2.rstrip()

    def test_tally(self):
        self.gen_cmp(self.r.tally, 'tally.out')

    def test_listcats(self):
        self.gen_cmp(self.r.list_cats, 'listcats1.out', 'good')
        self.gen_cmp(self.r.list_cats, 'listcats2.out', 'good',
                     ignore_noncrit=True)

    def test_printcat(self):
        self.gen_cmp(self.r.print_cat, 'printcat.out',
                     'The USNO-A2.0 Catalogue (Monet+ 1998) 1')

    def teardown_class(self):
        BASEURL.set(BASEURL.defaultvalue)
        shutil.rmtree(self.out_dir)
