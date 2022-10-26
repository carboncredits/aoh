
import tempfile
import os
from . import lib


def modeller(
    path,
    landc,
    dem,
    habs,
    dems,
    maskRast = None,
    maskVect = None,
    maskWhere = None,
    area = None,
    sid = None,
    return_sum = False):
    """Model a single species

    if sid is provided, a summary csv file is provided. This is mainly for KBA use.

        parameters:
            path (str): The output file path.
            landc (str): The path to the landcover file.
            dem (str): The path to the DEM file.
            habs (list or tuples): A list of suitable habitat values in landc.
            dems (list or tuple): A list of suitable elevation bounds in dem.
            mask (str): The path to the mask file. Raster or vector.
            maskWhere (str): Optional. A query to apply to the mask file
                if this is a vector file.
            area (str): Optional. The path to the area file.
            sid (str): Optional. The path to the spatial id file.
            return_sum (bool): Optional. If true the function will return the
                output's sum, independently of where the output was written.
                Write to /dev/null to only obtain the sum. For sid runs, the AOH
                sum will be returned.
    """
    # mask test
    if maskRast is None and maskVect is None:
        raise ValueError('at least one of maskRast or maskVect must be supplied')

    # In Windows we can't use NamedTemporaryFile, as you can't rewrite
    # a file which is already open. Instead we create a temp dir to use
    with tempfile.TemporaryDirectory() as tempdir:

        if maskRast is not None:
            mask = maskRast
        else:
            # get tmp maskfile address
            mask = os.path.join(tempdir, 'mask.tif')
            # write tmp maskfile
            lib.mask.makeMask(
                rangeFile = maskVect,
                template = landc,
                maskWhere = maskWhere,
                maskFile = mask,
                compress = False)

        # run model
        output = lib.mod.saveModel(
            path = path,
            landc = landc,
            dem = dem,
            mask = mask,
            habs = habs,
            dems = dems,
            area = area,
            sid = sid,
            return_sum = return_sum
            )
        
    if return_sum:
        return output



# HIC SVNT DRACONES