# -*- coding: utf-8 -*-
"""Regression check for the `native`/`abstract` method prototype emit path.

Before the fix `Writer.write_method` rendered every code-less method as
`<ret> <name>();` because `DvMethod.lparams` is only populated when the
method has a Dalvik code item.  This test asserts the rendered prototype
keeps the real arguments coming from `params_type`.
"""

import os
import unittest

from androguard.misc import AnalyzeAPK, AnalyzeDex
from androguard.decompiler.decompile import DvMethod


FIXTURE_DIR = os.path.join(os.path.dirname(__file__), 'data', 'native-decl')


class NativeMethodPrototypeTest(unittest.TestCase):
    """Decompile a DEX with one native + one abstract method and check the
    rendered prototype lines carry the full argument list."""

    def setUp(self):
        # Compiled from tests/data/native-decl/NativeOnly.java; both
        # methods carry real argument types in their `proto_id`.
        #   public class NativeOnly {
        #       public static native long add(long p0, int p1);
        #       public abstract void touch(java.lang.String p0);
        #   }
        dex_path = os.path.join(FIXTURE_DIR, 'NativeOnly.dex')
        _sha, self.dex, self.dx = AnalyzeDex(dex_path)

    def _decompile_method(self, name):
        for ma in self.dx.get_methods():
            if ma.get_method().get_name() == name:
                dv = DvMethod(ma)
                dv.process()
                return str(dv.writer)
        self.fail('method %r not found in fixture' % name)

    def test_native_method_keeps_argument_list(self):
        src = self._decompile_method('add')
        # Before the fix this read 'native long add();'.  Indices come
        # from range(len(params_type)) because code-less methods have no
        # Dalvik register layout to anchor against.
        self.assertIn('native long add(long p0, int p1)', src,
                      msg='native prototype lost its arguments: %r' % src)

    def test_abstract_method_keeps_argument_list(self):
        src = self._decompile_method('touch')
        # Same path through Writer.write_method – `graph is None` for both.
        self.assertIn('abstract void touch(String p0)', src,
                      msg='abstract prototype lost its arguments: %r' % src)

    def test_synthetic_indices_start_at_zero(self):
        # Pin the synthetic-range numbering so a future refactor cannot
        # silently shift the labels.  This intentionally diverges from
        # the code-bearing path's register-based `p{start}` numbering
        # because native / abstract methods have no register layout to
        # anchor against; the AST writer in `dast.py` already does the
        # same thing via `params = list(range(len(m.params_type)))`.
        src = self._decompile_method('add')
        self.assertIn('p0', src)
        self.assertIn('p1', src)


if __name__ == '__main__':
    unittest.main()
