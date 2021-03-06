# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""Tests for `astropy.vo.validator.validate`.

.. note::

    This test will fail if external URL query status
    changes. This is beyond the control of AstroPy.
    When this happens, rerun or update the test.

"""
from __future__ import absolute_import, division, print_function, unicode_literals

# STDLIB
import os
import shutil
import sys
import tempfile

# LOCAL
from .. import validate
from ..exceptions import ValidationMultiprocessingError
from ...client.vos_catalog import VOSDatabase
from ....tests.helper import pytest, remote_data
from ....utils.data import get_pkg_data_filename
from ....utils.data import REMOTE_TIMEOUT


__doctest_skip__ = ['*']


@remote_data
class TestConeSearchValidation(object):
    """Validation on a small subset of Cone Search sites."""
    def setup_class(self):
        self.datadir = 'data'
        self.out_dir = tempfile.mkdtemp()
        self.filenames = {
            'good': 'conesearch_good.json',
            'warn': 'conesearch_warn.json',
            'excp': 'conesearch_exception.json',
            'nerr': 'conesearch_error.json'}

        validate.CS_MSTR_LIST.set(get_pkg_data_filename(os.path.join(
            self.datadir, 'vao_conesearch_sites_121107_subset.xml')))

        REMOTE_TIMEOUT.set(30)

    @staticmethod
    def _compare_catnames(fname1, fname2):
        db1 = VOSDatabase.from_json(fname1)
        db2 = VOSDatabase.from_json(fname2)
        assert db1.list_catalogs() == db2.list_catalogs()

    @pytest.mark.parametrize(('parallel'), [True, False])
    def test_validation(self, parallel):
        if os.path.exists(self.out_dir):
            shutil.rmtree(self.out_dir)

        # For some reason, Python 3.3 does not work
        # using multiprocessing.Pool and callback function.
        # See http://bugs.python.org/issue16307
        try:
            validate.check_conesearch_sites(
                destdir=self.out_dir, parallel=parallel, url_list=None)
        except ValidationMultiprocessingError as e:
            if parallel and sys.version_info >= (3, 3):
                pytest.xfail('See http://bugs.python.org/issue16307')
            else:
                raise

        for val in self.filenames.values():
            self._compare_catnames(get_pkg_data_filename(
                os.path.join(self.datadir, val)),
                os.path.join(self.out_dir, val))

    def test_url_list(self):
        local_outdir = os.path.join(self.out_dir, 'subtmp1')
        local_list = [
            'http://www.google.com/foo&',
            'http://vizier.u-strasbg.fr/viz-bin/votable/-A?-source=I/252/out&']
        # Same multiprocessing problem in Python 3.3 as above
        validate.check_conesearch_sites(destdir=local_outdir, parallel=False,
                                        url_list=local_list)
        self._compare_catnames(get_pkg_data_filename(
            os.path.join(self.datadir, 'conesearch_good_subset.json')),
            os.path.join(local_outdir, 'conesearch_good.json'))

    def teardown_class(self):
        validate.CS_MSTR_LIST.set(validate.CS_MSTR_LIST.defaultvalue)
        REMOTE_TIMEOUT.set(REMOTE_TIMEOUT.defaultvalue)
        shutil.rmtree(self.out_dir)
