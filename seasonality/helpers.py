from osgeo import gdal, ogr

def gdal_open(filename, permissions):
    dataset = gdal.Open(filename, permissions)
    if dataset is None:
        raise FileNotFoundError(filename)
    return dataset

def ogr_open(filename, permissions):
    data = ogr.Open(filename, permissions)
    if data is None:
        raise FileNotFoundError(filename)
    return data