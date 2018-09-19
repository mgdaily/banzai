from banzai.images import Image, regenerate_data_table_from_fits_hdu_list
from banzai.tests.utils import FakeContext, FakeImage
import numpy as np
import pytest
from astropy.table import Table
from astropy.io import fits


@pytest.fixture(scope='module')
def set_random_seed():
    np.random.seed(10031312)


def test_null_filename():
    test_image = Image(FakeContext, filename=None)
    assert test_image.data is None


def test_3d_is_3d():
    test_image = FakeImage(n_amps=4)
    assert test_image.data_is_3d()


def test_2d_is_not_3d():
    test_image = FakeImage()
    assert not test_image.data_is_3d()


def test_get_n_amps_3d():
    test_image = FakeImage()
    assert test_image.get_n_amps() == 1


def test_get_n_amps_2d():
    n_amps = 4
    test_image = FakeImage(n_amps=n_amps)
    assert test_image.get_n_amps() == n_amps


def test_get_inner_quarter_default():
    test_image = FakeImage()
    test_image.data = np.random.randint(0, 1000, size=test_image.data.shape)
    # get inner quarter manually
    inner_nx = round(test_image.nx * 0.25)
    inner_ny = round(test_image.ny * 0.25)
    inner_quarter = test_image.data[inner_ny:-inner_ny, inner_nx:-inner_nx]
    np.testing.assert_array_equal(test_image.get_inner_image_section(), inner_quarter)


def test_get_inner_image_section_3d():
    test_image = FakeImage(n_amps=4)
    with pytest.raises(ValueError):
        test_image.get_inner_image_section()


def test_image_creates_and_loads_tables_correctly():
    test_image = Image(FakeContext, filename=None)
    table_name = 'test'
    a = np.arange(3)
    test_table = Table([a, a], names=('1', '2'), meta={'name': table_name})
    test_image.data_tables[table_name] = test_table
    test_table['1'].description = 'test_description'
    test_table['1'].unit = 'pixel'
    hdu_list = []
    hdu_list = test_image.add_data_tables_to_hdu_list(hdu_list)
    fits_hdu_list = fits.HDUList(hdu_list)
    test_table_dict = regenerate_data_table_from_fits_hdu_list(fits_hdu_list, table_extension_name=table_name)
    test_table_recreated = test_table_dict[table_name]
    assert (test_table_recreated == test_table).all()
