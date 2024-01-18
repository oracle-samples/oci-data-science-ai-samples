import datetime
import sys
import os

import pytest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from pre_commit_scripts.check_copyright import main

class TestCopyrightCheck:

    CURRENT_YEAR = datetime.date.today().year

    def test_exit(self):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_copyright_check_empty(self, tmp_path, capsys):
        p = tmp_path / "empty.py"
        s = '''\
        This is an empty file.
        '''
        p.write_text(s)
        assert p.read_text() == s
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([p])
        assert pytest_wrapped_e.value.code == 1
        captured = capsys.readouterr()
        assert "or year last edited not correct" in captured.out

    def test_copyright_check_only_current_year(self, tmp_path):
        p = tmp_path / "only_current_year.py"
        s = f'''\
        Copyright (c) {self.CURRENT_YEAR} Oracle and/or its affiliates
        Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/
        
        This is a sentence.
        '''
        p.write_text(s)
        assert p.read_text() == s
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([p])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_copyright_check_2022_and_current_year(self, tmp_path):
        p = tmp_path / "2022_and_current_year.py"
        s = f'''\
        Copyright (c) 2022, {self.CURRENT_YEAR} Oracle and/or its affiliates
        Licensed under the Universal Permissive License v 1.0 as shown at https://oss.oracle.com/licenses/upl/

        This is a sentence.
        '''
        p.write_text(s)
        assert p.read_text() == s
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([p])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

    def test_copyright_incorrect_statement(self, tmp_path, capsys):
        p = tmp_path / "incorrect_statement.py"
        s = f'''\
        Copyright (c) {self.CURRENT_YEAR} Oracle and/or its affiliates
        Licensed under ---error in statement----- 1.0 as shown at https://oss.oracle.com/licenses/upl/

        This is a sentence.
        '''
        p.write_text(s)
        assert p.read_text() == s
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([p])
        assert pytest_wrapped_e.value.code == 1
        captured = capsys.readouterr()
        assert "missing or incomplete" in captured.out

    def test_copyright_non_copyright(self, tmp_path, capsys):
        p = tmp_path / "incorrect_statement.py"
        s = '''\
        This is a sentence.

        This is another sentence.
        '''
        p.write_text(s)
        assert p.read_text() == s
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            main([p])
        assert pytest_wrapped_e.value.code == 1
        captured = capsys.readouterr()
        assert "not correct" in captured.out
