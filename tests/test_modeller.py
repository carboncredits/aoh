import aoh
import os

def test_modeller_dummy():
    try:
        aoh.modeller(
            path     = 'tests/data/output_0.tif',
            landc    = 'tests/data/landcover_0.tif',
            dem      = 'tests/data/dem_0.tif',
            maskRast = 'tests/data/mask_0.tif',
            habs  = (0),
            dems  = (0, 0)
            )
        os.remove('tests/data/output_0.tif')
    except Exception as e:
        assert False, f"'test_modeller_dummy' raised an exception {e}"


def test_modeller_x10():
    assert aoh.modeller(
        path     = 'tests/data/output_x10.tif',
        landc    = 'tests/data/landcover_tile_x10.tif',
        dem      = 'tests/data/dem_tile_x10.tif',
        maskRast = 'tests/data/mask_tile_x10.tif',
        area     = 'tests/data/area_tile_x10.tif',
        habs  = (1,2,3,4,5,6,7,8,9,10),
        dems  = (250, 750),
        return_sum = True
        ) == 161
    os.remove('tests/data/output_x10.tif')
