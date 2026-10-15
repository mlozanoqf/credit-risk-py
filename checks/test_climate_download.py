"""Request/schema tests without internet access or refreshed source files."""
from io import BytesIO
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.error import URLError

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'chapters/06-climate-credit-risk/helpers'))
import download_data


class DownloadTests(unittest.TestCase):
    def test_query_filters_and_response(self):
        payload = [{'scenario':'HWTP','region':'World','variable':'pd_adjustment|Coal','year':2030,'value':2.5}]
        with patch.object(download_data,'urlopen',side_effect=[BytesIO(b'"test-token"'),BytesIO(json.dumps(payload).encode())]) as mocked:
            result = download_data.query([75],['World'],['pd_adjustment|Coal'],[2030])
        request = mocked.call_args_list[1].args[0]
        filters = json.loads(request.data)['filters']
        self.assertEqual(filters,dict(runs=[75],regions=['World'],variables=['pd_adjustment|Coal'],years=[2030],units=[],timeslices=['Year']))
        self.assertEqual(request.get_header('Authorization'),'Bearer test-token')
        self.assertEqual(result.value.iloc[0],2.5)
    def test_empty_response(self):
        with patch.object(download_data,'guest_token',return_value='token'),patch.object(download_data,'urlopen',return_value=BytesIO(b'[]')):
            with self.assertRaises(ValueError): download_data.query([75],['World'],['pd_adjustment|Coal'],[2030])
    def test_bounded_token_retries(self):
        with patch.object(download_data,'urlopen',side_effect=URLError('offline')) as mocked,patch.object(download_data.time,'sleep'):
            with self.assertRaises(RuntimeError): download_data.guest_token()
            self.assertEqual(mocked.call_count,5)
    def test_existing_destination_is_protected(self):
        with tempfile.TemporaryDirectory() as directory,patch.object(sys,'argv',['download_data.py','--destination',directory]),patch.object(download_data,'query') as mocked:
            with self.assertRaises(SystemExit): download_data.main()
            mocked.assert_not_called()


if __name__=='__main__': unittest.main()
