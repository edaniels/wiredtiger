#!/usr/bin/env python
#
# Public Domain 2014-2018 MongoDB, Inc.
# Public Domain 2008-2014 WiredTiger, Inc.
#
# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# test_prepare02.py
#   Prepare : check post conditions to prepare operation
#

from suite_subprocess import suite_subprocess
import wiredtiger, wttest

def timestamp_str(t):
    return '%x' % t

class test_prepare02(wttest.WiredTigerTestCase, suite_subprocess):
    def test_timestamp_range(self):
        if not wiredtiger.timestamp_build():
            self.skipTest('requires a timestamp build')

        self.session.create("table:mytable", "key_format=S,value_format=S")
        # Commit after prepare is permitted
        self.session.begin_transaction()
        self.session.prepare_transaction()
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                lambda: self.session.reconfigure())
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                lambda: self.session.reset())
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                lambda: self.session.begin_transaction())
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                lambda: self.session.transaction_sync())
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                lambda: self.session.checkpoint())
        with self.expectedStderrPattern(''):
            self.assertRaises(wiredtiger.WiredTigerError,
                    lambda: self.session.compact("table:mytable"))

        self.session.alter("table:mytable","access_pattern_hint=random")
        self.session.open_cursor("table:mytable", None)
        self.session.create("table:mytable1", "key_format=S,value_format=S")
        self.session.rollback_transaction()

        # Commit after prepare is permitted
        self.session.begin_transaction()
        self.session.prepare_transaction()
        self.session.commit_transaction()

        # Rollback after prepare is permitted
        self.session.begin_transaction()
        self.session.prepare_transaction()
        self.session.rollback_transaction()

        # Close after prepare is permitted
        self.session.begin_transaction()
        self.session.prepare_transaction()
        self.session.close()

if __name__ == '__main__':
    wttest.run()
