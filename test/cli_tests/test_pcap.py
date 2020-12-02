import functools
import pathlib
import tempfile

from .base import CLITestCase


TEST_ROOT = pathlib.Path(__file__).parent.parent

TEST_DATA = TEST_ROOT / 'data'


def testdir(func):
    """Decorator to wrap given function such that a temporary directory
    is created and destroyed for each invocation.

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with tempfile.TemporaryDirectory(prefix=f'nprintml.{func.__module__}.') as tempdir:
            return func(*args, tempdir, **kwargs)

    return wrapper


class TestPcap(CLITestCase):

    @testdir
    def test_pcap_file(self, tempdir):
        temp_path = pathlib.Path(tempdir)

        self.try_execute(
            '--tcp',
            '--ipv4',
            '--aggregator', 'index',
            '--label-file', TEST_DATA / 'single-pcap' / 'labels.txt',
            '--pcap-file', TEST_DATA / 'single-pcap' / 'test.pcap',
            '--output', temp_path,
            '--quiet',  # autogluon's threading makes capturing/suppressing
                        # its stdout a little harder
        )

        npt_path = temp_path / 'nprint' / 'test.npt'
        self.assertTrue(npt_path.exists())

        graphs_path = temp_path / 'model' / 'graphs'
        self.assertTrue(any(graphs_path.glob('*.pdf')))

        models_path = temp_path / 'model' / 'models'
        self.assertTrue(any(models_path.rglob('*.pkl')))

    @testdir
    def test_pcap_directory(self, tempdir):
        temp_path = pathlib.Path(tempdir)

        self.try_execute(
            '--tcp',
            '--ipv4',
            '--aggregator', 'pcap',
            '--label-file', TEST_DATA / 'dir-pcap' / 'labels.txt',
            '--pcap-dir', TEST_DATA / 'dir-pcap' / 'pcaps',
            '--output', temp_path,
            '--quiet',  # autogluon's threading makes capturing/suppressing
                        # its stdout a little harder
        )

        npt_path_encrypted = temp_path / 'nprint' / 'encrypted'
        npt_path_unencrypted = temp_path / 'nprint' / 'unencrypted'
        self.assertTrue(any(npt_path_encrypted.glob('*.npt')))
        self.assertTrue(any(npt_path_unencrypted.glob('*.npt')))

        graphs_path = temp_path / 'model' / 'graphs'
        self.assertTrue(any(graphs_path.glob('*.pdf')))

        models_path = temp_path / 'model' / 'models'
        self.assertTrue(any(models_path.rglob('*.pkl')))
