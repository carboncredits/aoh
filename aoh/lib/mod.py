from osgeo import gdal
import numpy
import pandas
import os

from .helpers import gdal_open


def rasterArrayWindow(template, mask):
    ''' return a template's window parameters according to a raster mask

    Given two rasters that are assumed to have aligned pixels but different
    extents, return parameters that describe the window of overlap between the
    mask and the template. The mask is assumed to be contained within the
    template.

    WARNING:
        If supplied, sid must describe contiguous areas. Otherwise, the output
        summary may contain multiple lines for the same spatial id.

    Parameters:
        template: the file address of a template raster
        mask: the file address of a mask raster

    Returns:
        dictionary: {
            xoff: int, the horizontal pixel offset, left to right
            yoff: int, the vertical pixel offset, top to bottom
            win_xsize: int, the number of horizontal pixels to read
            win_ysize: int, the number of vertical pixels to read
            }
    '''
    # open file GeoTransforms
    tGT = gdal_open(template, gdal.GA_ReadOnly).GetGeoTransform()
    mask_dataset = gdal_open(mask, gdal.GA_ReadOnly)
    mGT = mask_dataset.GetGeoTransform()
    # test resolutions
    if tGT[1] != mGT[1] or tGT[5] != mGT[5]:
        raise Exception('X and/or Y resolution mismatch')
    # test alignments TODO
    # calculate outputs
    output = {
        'xoff':  (mGT[0] - tGT[0]) / tGT[1],
        'yoff':  (mGT[3] - tGT[3]) / tGT[5],
        'xsize': mask_dataset.RasterXSize,
        'ysize': mask_dataset.RasterYSize
        }
    # return
    return output


def saveModel(path, landc, dem, mask, habs, dems, area = None, sid = None, return_sum = False):
    '''Writes a model output to file
    
        Parameters:
            path (str): path of the output map or summary file.
            landc (str): path to the land-cover map.
            dem (str): path to the dem map.
            mask (str): path to the mask map.
            habs (list or tuple): list of suitable land-cover codes.
            dems (list of tuple): list of suitable elevation bounds.
            area (str): path to the area map (optional). If supplied (and no sid
                is provided), the output map will have each suitable pixel's
                area written in. Otherwise, the map will be 1-bit encoded binary.
            sid (str): path to the spatial id file. Requires the area parameter.
                If supplied, a summary output file that matches id values to the
                total area per id will be returned.
            return_sum (bool): Optional. If true the function will return the
                output's sum, independently of where the output was written.
                Write to /dev/null to only obtain the sum. For sid runs, the AOH
                sum will be returned.
    '''
    # Tests
    if sid is not None and area is None:
        raise ValueError('The area file must be provided for summary outputs.')
    # Get overlap window
    window = rasterArrayWindow(landc, mask)
    # Open input layers
    landc = gdal_open(landc, gdal.GA_ReadOnly)
    landcBand = landc.GetRasterBand(1)
    dem   = gdal_open(dem,   gdal.GA_ReadOnly)
    demBand = dem.GetRasterBand(1)
    mask  = gdal_open(mask,  gdal.GA_ReadOnly)
    maskBand = mask.GetRasterBand(1)
    if area is not None:
        area  = gdal_open(area,  gdal.GA_ReadOnly)
        areaBand = area.GetRasterBand(1)
    if sid is not None:
        sid  = gdal_open(sid,  gdal.GA_ReadOnly)
        sidBand = sid.GetRasterBand(1)
    # Initialize the output sum if requested
    if return_sum:
        outputSum = 0
    # Initialize output raster
    if sid is None:
        if area is None:
            outputDataset = gdal.GetDriverByName('GTiff').Create(
                f'{path}.part',
                xsize = mask.RasterXSize,
                ysize = mask.RasterYSize,
                bands = 1,
                eType = gdal.GDT_Byte,
                options = ['NBITS=1', 'COMPRESS=LZW']
                )
        else:
            outputDataset = gdal.GetDriverByName('GTiff').Create(
                f'{path}.part',
                xsize = mask.RasterXSize,
                ysize = mask.RasterYSize,
                bands = 1,
                eType = gdal.GDT_Float32,
                options = ['COMPRESS=LZW']
                )
        outputDataset.SetGeoTransform(mask.GetGeoTransform())
        outputDataset.SetProjection(mask.GetProjection())
        outputBand = outputDataset.GetRasterBand(1)
        outputBand.SetNoDataValue(0)
    else:
        summaryKeys  = numpy.array([], dtype = int)
        summaryRange = numpy.array([], dtype = float)
        summaryAoh   = numpy.array([], dtype = float)
    # Row loop
    for subYOffset in range(mask.RasterYSize):
        subLandc = numpy.isin(
            landcBand.ReadAsArray(
                window['xoff'],
                window['yoff']+subYOffset,
                window['xsize'],
                1
                ),
            habs
            )
        subDem = demBand.ReadAsArray(
            window['xoff'],
            window['yoff']+subYOffset,
            window['xsize'],
            1
            )
        subDem = numpy.logical_and(subDem >= min(dems), subDem <= max(dems))
        subMask = maskBand.ReadAsArray(
            0,
            subYOffset,
            window['xsize'],
            1
            )
        if area is not None:
            subArea = areaBand.ReadAsArray(
                window['xoff'],
                window['yoff']+subYOffset,
                window['xsize'],
                1
                )
        if sid is not None:
            subSID = sidBand.ReadAsArray(
                window['xoff'],
                window['yoff']+subYOffset,
                window['xsize'],
                1
                ).astype(int) 

        # process map or summary subset output
        if sid is None:
            # map output
            if area is not None:
                outputArray = subLandc * subDem * subArea * subMask
            else:
                outputArray = subLandc * subDem * subMask
            outputBand.WriteArray(
                    outputArray,
                    xoff = 0,
                    yoff = subYOffset
                    )
            if return_sum:
                outputSum += numpy.sum(outputArray)
        else:
            # compact line

            #######################
            # Black Magic be here #
            #######################

            # Find the index of summaryKeys values that appear in subSID (not
            # yet completed), and those that can be written (completed and with
            # data).
            #
            # Values in summaryKeys are keys already scanned.
            # Values in subSID are new scanned keys.
            # Some ranges (masks) may be disjunct, meaning that if keys are
            # masked on the range, they may reappear down the line.
            # Two solutions:
            #     - do not mask inputs - This has been adopted
            #           mask the summaryRange summaryAoh appends by selecting
            #           where summaryRange>0.0
            #     - reconcile
            #           reconcile the tar.gz after creation.
            notDoneIndex = numpy.isin(summaryKeys, subSID, assume_unique = False)
            toWriteIndex = numpy.logical_and(numpy.invert(notDoneIndex), summaryRange>0.0)

            # these Keys, Ranges and Aoh will be assumed to be completely
            # summarized (and with data) and written to disk.
            pandas.DataFrame(
                list(zip(
                    summaryKeys[toWriteIndex],
                    summaryRange[toWriteIndex],
                    summaryAoh[toWriteIndex]
                    )),
                    columns = ['sid', 'range', 'aoh']
                    ).to_csv(
                        f'{path}.part',
                        mode = 'w' if subYOffset == 0 else 'a',
                        header = subYOffset == 0,
                        index = False,
                        compression='gzip'
                        )
            if return_sum:
                outputSum += numpy.sum(summaryAoh[toWriteIndex])
            
            # the others will be used to overwirte the summary arrays
            summaryKeys  = summaryKeys[notDoneIndex]
            summaryRange = summaryRange[notDoneIndex]
            summaryAoh   = summaryAoh[notDoneIndex]

            # extend summaryKeys with the arrays from the loop
            summaryKeys  = numpy.append(summaryKeys, subSID)
            summaryRange = numpy.append(summaryRange, (subArea * subMask))
            summaryAoh   = numpy.append(summaryAoh, (subArea * subLandc * subDem * subMask))

            # summarise Keys, Range and Aoh
            # summaryIndex keeps everything in order
            summaryKeys, summaryIndex = numpy.unique(summaryKeys, return_inverse=True)
            summaryRange = numpy.bincount(summaryIndex, summaryRange)
            summaryAoh   = numpy.bincount(summaryIndex, summaryAoh)

    # Cleanup
    if sid is None:
        # Close output database
        outputDataset = None
        os.rename(f'{path}.part', path)
        if return_sum:
            return outputSum
        else:
            return path
    else:
        # write final summarised output
        pandas.DataFrame(
            list(zip(
                summaryKeys[summaryRange>0.0],
                summaryRange[summaryRange>0.0],
                summaryAoh[summaryRange>0.0]
                )),
            columns = ['sid', 'range', 'aoh']
            ).to_csv(f'{path}.part', mode = 'a', header = False, index = False, compression='gzip')
        os.rename(f'{path}.part', path)
        if return_sum:
            outputSum += numpy.sum(summaryAoh[summaryAoh>0.0])
            return outputSum
        else:
            return path