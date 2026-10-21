import csv
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import pandas as pd

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shared.output import show_table


class OutputTitleTests(unittest.TestCase):
    def test_index_title_is_visible_without_changing_values(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            out=root/'output'/'test'
            (out/'tables').mkdir(parents=True)
            (root/'results-index.csv').write_text('kind,number,title\nTable,3.1,Value in MU.\n')
            frame=pd.DataFrame({'Value':[1.25]})
            with patch('shared.output.display') as display:
                show_table(out,'3.1',frame)
                self.assertIn('Table 3.1. Value in MU.',display.call_args_list[0].args[0].data)
                self.assertEqual(display.call_count,2)
            self.assertEqual(pd.read_csv(out/'tables/table-3-1.csv').iloc[0,0],1.25)
            self.assertEqual(frame.iloc[0,0],1.25)

    def test_missing_title_fails_clearly(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);out=root/'output'/'test'
            (out/'tables').mkdir(parents=True)
            (root/'results-index.csv').write_text('kind,number,title\n')
            with self.assertRaisesRegex(ValueError,'indexed title'):
                show_table(out,'3.1',pd.DataFrame({'Value':[1.25]}))


if __name__=='__main__':unittest.main()
