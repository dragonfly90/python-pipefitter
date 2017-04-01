#!/usr/bin/env python
# encoding: utf-8
#
# Copyright SAS Institute
#
#  Licensed under the Apache License, Version 2.0 (the License);
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

'''
Tests for CAS Imputers

'''

from __future__ import print_function, division, absolute_import, unicode_literals

import os
import numpy as np
import pandas as pd
import saspy
import swat.utils.testing as tm
import unittest
from pipefitter.transformer import Imputer, ImputerMethod

from swat.utils.compat import patch_pandas_sort

patch_pandas_sort()

SASPY_CONFIG = os.environ.get('SASPY_CONFIG', 'tdi')


class TestImputerMethod(tm.TestCase):

    def test_str(self):
        self.assertEqual(str(Imputer.MAX), 'max') 
        self.assertEqual(str(Imputer.MEAN), 'mean') 
        self.assertEqual(str(Imputer.MEDIAN), 'median') 
        self.assertEqual(str(Imputer.MIDRANGE), 'midrange') 
        self.assertEqual(str(Imputer.MIN), 'min') 
        self.assertEqual(str(Imputer.MODE), 'mode') 
        self.assertEqual(str(Imputer.RANDOM), 'random') 

    def test_repr(self):
        self.assertEqual(repr(Imputer.MAX), 'max') 
        self.assertEqual(repr(Imputer.MEAN), 'mean') 
        self.assertEqual(repr(Imputer.MEDIAN), 'median') 
        self.assertEqual(repr(Imputer.MIDRANGE), 'midrange') 
        self.assertEqual(repr(Imputer.MIN), 'min') 
        self.assertEqual(repr(Imputer.MODE), 'mode') 
        self.assertEqual(repr(Imputer.RANDOM), 'random') 


class TestImputer(tm.TestCase):

    def setUp(self):
        self.s = saspy.SASsession(cfgname=SASPY_CONFIG)

        self.df = pd.DataFrame([[1,      2,      3,   4,      5,      'a',    'b',    'c'],
                                [6,      np.nan, 8,   9,      np.nan, 'd',    'e',    'f'],
                                [11,     np.nan, 13,  14,     np.nan, np.nan, 'h',    'i'],
                                [16,     17,     18,  np.nan, 20,     'j',    np.nan, 'l'],
                                [np.nan, 22,     23,  24,     np.nan, np.nan, 'n',    'o']],
                        columns=['A',    'B',    'C', 'D',    'E',    'F',    'G',    'H'])

        self.table = self.s.dataframe2sasdata(self.df)

    def tearDown(self):
        # tear down tests
        del self.s

    def test_str(self):
        imp = Imputer()
        self.assertEqual(str(imp), 'Imputer(MEAN)')

        imp = Imputer(1.2345)
        self.assertEqual(str(imp), 'Imputer(1.2345)')

        imp = Imputer('foo')
        self.assertEqual(str(imp), 'Imputer(\'foo\')')

        imp = Imputer({'a': 1, 'b': 'foo'})
        self.assertIn(str(imp), ["Imputer({'a': 1, 'b': 'foo'})",
                                 "Imputer({'b': 'foo', 'a': 1})"])

    def test_repr(self):
        imp = Imputer()
        self.assertEqual(repr(imp), 'Imputer(MEAN)')

        imp = Imputer(1.2345)
        self.assertEqual(repr(imp), 'Imputer(1.2345)')

        imp = Imputer('foo')
        self.assertEqual(repr(imp), 'Imputer(\'foo\')')

        imp = Imputer({'a': 1, 'b': 'foo'})
        self.assertIn(repr(imp), ["Imputer({'a': 1, 'b': 'foo'})",
                                  "Imputer({'b': 'foo', 'a': 1})"])

    @unittest.skip('Need columns implementation')
    def test_basic_imputer(self):
        df = self.df
        tbl = self.table

        num_cols = ['A', 'B', 'C', 'D', 'E']
        char_cols = ['F', 'G', 'H']

        imp = Imputer()
        imp.transform(tbl)

        # Constant value
        self.assertTablesEqual(df.fillna(1000)[num_cols],
                               imp.transform(tbl, 1000)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, 1000)[char_cols])
        self.assertTablesEqual(df.fillna(23.4)[num_cols],
                               imp.transform(tbl, 23.4)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, 23.4)[char_cols])
        self.assertTablesEqual(df.fillna('x')[char_cols],
                               imp.transform(tbl, 'x')[char_cols])
        self.assertTablesEqual(df[num_cols],
                               imp.transform(tbl, 'x')[num_cols])

        # ImputerMethod value
        self.assertTablesEqual(df.fillna(tbl.mean())[num_cols],
                               imp.transform(tbl, imp.MEAN)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, imp.MEAN)[char_cols])
        self.assertTablesEqual(df.fillna(tbl.min())[num_cols],
                               imp.transform(tbl, imp.MIN)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, imp.MIN)[char_cols])
        self.assertTablesEqual(df.fillna(tbl.max())[num_cols],
                               imp.transform(tbl, imp.MAX)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, imp.MAX)[char_cols])
        self.assertTablesEqual(df.fillna(tbl.median())[num_cols],
                               imp.transform(tbl, imp.MEDIAN)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, imp.MEDIAN)[char_cols])
        self.assertTablesEqual(df.fillna((tbl[num_cols].min() + tbl[num_cols].max()) / 2)[num_cols],
                               imp.transform(tbl, imp.MIDRANGE)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, imp.MIDRANGE)[char_cols])
        self.assertTablesEqual(df[num_cols],
                               imp.transform(tbl, imp.MODE)[num_cols])
        self.assertTablesEqual(df.fillna({'F': 'a', 'G': 'b', 'H': 'c'})[char_cols],
                               imp.transform(tbl, imp.MODE)[char_cols])
        out = imp.transform(tbl, imp.RANDOM)
        self.assertTablesEqual(out.head().fillna(1000), out)

        # Dict value
        repl = {'A': 100, 'B': 200, 'C': 300}
        self.assertTablesEqual(df.fillna(repl)[num_cols],
                               imp.transform(tbl, repl)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, repl)[char_cols])

        repl = {'A': 100, 'C': 300, 'G': 'foo'}
        self.assertTablesEqual(df.fillna(repl)[num_cols],
                               imp.transform(tbl, repl)[num_cols])
        dfrepl = dict(repl)
        dfrepl['F'] = ''
        dfrepl['H'] = ''
        self.assertTablesEqual(df.fillna(dfrepl)[char_cols],
                               imp.transform(tbl, repl)[char_cols])
          
        repl = {'G': 'foo'}
        self.assertTablesEqual(df.fillna(repl)[num_cols],
                               imp.transform(tbl, repl)[num_cols])
        dfrepl = dict(repl)
        dfrepl['F'] = ''
        dfrepl['H'] = ''
        self.assertTablesEqual(df.fillna(dfrepl)[char_cols],
                               imp.transform(tbl, repl)[char_cols])
          
        # Series value
        repl = pd.Series([100, 200, 300], index=['A', 'B', 'C'])
        self.assertTablesEqual(df.fillna(repl)[num_cols],
                               imp.transform(tbl, repl)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, repl)[char_cols])

# TODO: This doesn't work yet.  In this case, missing values are replaced
#       by the value in the same position as the replacement DataFrame.
        # DataFrame value
        repl = pd.DataFrame([[100, 200, 300], [400, 500, 600]],
                             columns=['A', 'B', 'C'])
        with self.assertRaises(TypeError):
            imp.transform(tbl, repl)

    @unittest.skip('Need columns implementation')
    def test_bad_colname(self):
        df = self.df
        tbl = self.table

        num_cols = ['A', 'B', 'C', 'D', 'E']
        char_cols = ['F', 'G', 'H']

        imp = Imputer()

        repl = {'X': imp.MEAN}
        self.assertTablesEqual(df[num_cols],
                               imp.transform(tbl, repl)[num_cols])
        self.assertTablesEqual(df.fillna('')[char_cols],
                               imp.transform(tbl, repl)[char_cols])

#   def test_call_impute_action(self):
#       from pipefitter.backends.sas.transformer.imputer import Imputer as SASImputer
#       imp = SASImputer()
#       with self.assertRaises(RuntimeError):
#           imp._call_impute_action(self.table, dict(foo='bar'))


if __name__ == '__main__':
    tm.runtests()
