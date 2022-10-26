from osgeo import gdal
from math import floor, ceil

from .helpers import gdal_open, ogr_open

def layerExtents(layer):
    layer.ResetReading()
    nFeatures = layer.GetFeatureCount()
    if nFeatures == 0:
        raise Exception("Layer has no features")
    extents = None
    for i in range(nFeatures):
        f = layer.GetNextFeature()
        if i == 0:
            extents = {
                'xMin':f.GetGeometryRef().GetEnvelope()[0],
                'xMax':f.GetGeometryRef().GetEnvelope()[1],
                'yMin':f.GetGeometryRef().GetEnvelope()[2],
                'yMax':f.GetGeometryRef().GetEnvelope()[3]
                }
        else:
            extents = {
                'xMin':min(extents['xMin'],f.GetGeometryRef().GetEnvelope()[0]),
                'xMax':max(extents['xMax'],f.GetGeometryRef().GetEnvelope()[1]),
                'yMin':min(extents['yMin'],f.GetGeometryRef().GetEnvelope()[2]),
                'yMax':max(extents['yMax'],f.GetGeometryRef().GetEnvelope()[3])
                }
        del f
    return extents


def getXYcellPar(raster, vectorExtents, xy):
    '''Gets the x or y offset, resolution and size of a vector layer's overlap with a raster

        Parameters:
        raster: a gdal raster object
        vectorExtents: a Vector extent list [Xmin, Xmax, Ymin, Ymax]
        xy: a string; either 'x' or 'y'

        Returns:
            dictionary: {
                cell-rounded start coordinate, of overlap,
                cell resolution,
                cell offset to read from template,
                number of cells to read in (x, y) coordinate axis
                }

        X offset is counted from left to right. The first column is at offset 0.
        Y offset is counted from top to bottom. The first row is at offset 0.
    '''
    if xy in ('x', 'X'):
        rStart = raster.GetGeoTransform()[0] # left of raster
        vStart = vectorExtents['xMin']       # left of vector
        vEnd   = vectorExtents['xMax']       # right of vector
        rStep  = raster.GetGeoTransform()[1] # x resolution
    elif xy in ('y', 'Y'):
        rStart = -raster.GetGeoTransform()[3] # top of raster (inverted)
        vStart = -vectorExtents['yMax']       # top of vector (inverted)
        vEnd   = -vectorExtents['yMin']       # bottom of the vector (inverted)
        rStep  = -raster.GetGeoTransform()[5] # y resolution (inverted)
    # calculations
    cellStart = rStart + (rStep * floor((vStart - rStart) / rStep))
    cellEnd   = rStart + (rStep *  ceil((vEnd   - rStart) / rStep))
    cellReadSize   = floor((cellEnd - cellStart) / rStep)
    cellReadOffset = floor((cellStart - rStart) / rStep)
    # return
    if xy in ('x', 'X'):
        return {
            'offsetCoord':cellStart,         # cell-rounded start coordinates of overlap
            'resolution':rStep,              # cell resolution
            'cellReadOffset':cellReadOffset, # template read offset in cells,
            'cellReadSize':cellReadSize      # template read size in cells
            }
    elif xy in ('y', 'Y'):
        return {
            'offsetCoord':-cellStart,         # cell-rounded start coordinates of overlap
            'resolution':-rStep,              # cell resolution
            'cellReadOffset':-cellReadOffset, # template read offset in cells,
            'cellReadSize':cellReadSize      # template read size in cells
            }
    else:
        raise ValueError('xy must be one of x y X Y')


def makeMask(rangeFile, template, maskWhere, maskFile, compress = False):
    '''Make a raster mask file that aligns with the raster template

    This script is about 10x faster than
    gdal.Warp(
        maskFile,
        template,
        cutlineDSName = rangeFile,
        cutlineWhere = maskWhere,
        cropToCutline = True,
        options=["ALL_TOUCHED=TRUE","NBITS=1"]
        )
    '''
    # open raster layer for reading
    template = gdal_open(template, gdal.GA_ReadOnly)
    # open vector layer and set layer filter
    src = ogr_open(rangeFile, 0)
    maskLayer = src.GetLayer()
    maskLayer.SetAttributeFilter(maskWhere)
    # extents and offsets
    vExtents = layerExtents(maskLayer) # [Xmin, Xmax, Ymin, Ymax]
    xCellPars = getXYcellPar(template, vExtents, xy='X')
    yCellPars = getXYcellPar(template, vExtents, xy='Y')
    # Initialize output raster
    opts = ['NBITS=1', 'COMPRESS=LZW'] if compress else ['NBITS=1']
    outputDataset = gdal.GetDriverByName('GTiff').Create(
                       maskFile,
                       xCellPars['cellReadSize'],
                       yCellPars['cellReadSize'],
                       1,
                       gdal.GDT_Byte, opts)
    outputDataset.SetGeoTransform((
        xCellPars['offsetCoord'], xCellPars['resolution'], 0.0,
        yCellPars['offsetCoord'], 0.0, yCellPars['resolution']
        ))
    outputDataset.SetProjection(template.GetProjection())
    ## Rasterize filtered layer
    gdal.RasterizeLayer(outputDataset, [1], maskLayer, burn_values=[1],
        options=["ALL_TOUCHED=TRUE"])
