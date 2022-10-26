# aoh modeller
Package to develop and process AOH models.

## Name
aoh

## Description
A Pyhton package to automate the development Area Of Habitat (AOH) models.

IUCN defines AOH as suitable habitat within suitable elevation within a species' range. This package facilitates the development of these models in a highly efficient manner.

You may be interested to also install the iucn-modlib package to create automatic frameworks.

```https://gitlab.com/daniele.baisero/iucn-modlib```

## Installation

### From GitLab
```pip install git+https://gitlab.com/daniele.baisero/aoh```

If you want to use the optional apps, you will need to install additional requirements.  
```pip install -e git+https://gitlab.com/daniele.baisero/aoh#egg=aoh[apps]```

### From PIP
```pip install aoh```

## Requirements
This package will require the gdal python package to be installed in your system. This can be installed via the python ```gdal``` or ```osgeo``` packages. The ```gdal``` and ```osgeo``` packages will also require gdal binary libraries to be installed on your operating system. This unfortunately needs to be done outside of python.

On a Linux system, if you have ```libgdal-dev``` installed, you can install the python gdal package with
`` pip install gdal==`gdal-config --version` ``

## Usage

```
import aoh

# The modeller can be used to create binary models.
# The paths to the output file, the landcover file, and the elevation file are always needed.
# The species' mask is also always needed, but can come in two ways: a binary raster mask,
# or a vector file AND sql filters.

# All the raster files, where provided, are assumed to have the same extent and resolution,
# so that all pixels aligned. Future updates will remove the same extent requirement,
# but all raster maps will still be assumed to have the same resolutions and pixels aligned.

# Run a model with a species' raster mask
aoh.modeller(
    path       = '/path/to/output_file.tif',
    landc      = '/path/to/landcover_file.tif',
    dem        = '/path/to/elevation_file.tif',
    habs       = [170, 202, 210, 180], # list of suitable landcover pixel values
    dems       = (-500, 3),            # min and max elevation boundaries
    maskRast   = '/path/to/species_raster_mask.tif',
    maskVect   = None,
    maskWhere  = None,
    area       = None,
    sid        = None,
    return_sum = False
    )

# Run a model with a species' vector file and sql filters
aoh.modeller(
    path       = '/path/to/output_file.tif',
    landc      = '/path/to/landcover_file.tif',
    dem        = '/path/to/elevation_file.tif',
    habs       = [170, 202, 210, 180], # list of suitable landcover pixel values
    dems       = (-500, 3),            # min and max elevation boundaries
    maskRast   = None,
    maskVect   = '/path/to/species_vector_mask.tif',
    maskWhere  = "id_no = 39994 and (presence = 'resident' or presence = 'breeding')",
    area       = None,
    sid        = None,
    return_sum = False
    )


# If the additional area raster file is included, the output will not be binary,
# but each suitable pixel will contain the pixel area. This will allow you to
# simply add all pixel values in an area of interest to have the local AOH.
aoh.modeller(
    path       = '/path/to/output_file.tif',
    landc      = '/path/to/landcover_file.tif',
    dem        = '/path/to/elevation_file.tif',
    habs       = [170, 202, 210, 180], # list of suitable landcover pixel values
    dems       = (-500, 3),            # min and max elevation boundaries
    maskRast   = '/path/to/species_raster_mask.tif',
    maskVect   = None,
    maskWhere  = None,
    area       = '/path/to/pixel_area_file.tif',
    sid        = None,
    return_sum = False
    )


# The sid (spatial ID) parameter allows you to include a raster file that divides
# the whole region into study units with unique integer values. If this is provided,
# the written path file will not be a raster, but a csv file (gzipped) indexed
# by each unique value in the sid file. Two values will be included in the csv
# file: range and aoh. Range will be the sum of areas covered by the mask within
# each spatial id feature, while aoh will be the sum of AOH within each spatial
# id feature. The use of sid requires the area file to be provided.
aoh.modeller(                                                           
    path       = '/path/to/output_file.tif',
    landc      = '/path/to/landcover_file.tif',
    dem        = '/path/to/elevation_file.tif',
    habs       = [170, 202, 210, 180], # list of suitable landcover pixel values
    dems       = (-500, 3),            # min and max elevation boundaries
    maskRast   = 'path/to/species_raster_mask.tif',
    maskVect   = None,
    maskWhere  = None,
    area       = '/path/to/pixel_area_file.tif',
    sid        = '/path/to/spatial_id_file.tif',
    return_sum = False
    )


# Independently of which run-method is applied, the return_sum parameter can be
# set to True. This will make the function also return the total area identified
# as suitable (number of suitable pixels, or total AOH).
total_area = aoh.modeller(
    path       = '/path/to/output_file.tif',
    landc      = '/path/to/landcover_file.tif',
    dem        = '/path/to/elevation_file.tif',
    habs       = [170, 202, 210, 180], # list of suitable landcover pixel values
    dems       = (-500, 3),            # min and max elevation boundaries
    maskRast   = '/path/to/species_raster_mask.tif',
    maskVect   = None,
    maskWhere  = None,
    area       = '/path/to/pixel_area_file.tif',
    sid        = None,
    return_sum = True
    )
print(f'Total area is {total_area}')
```

## Support
For support please use the issue tracker at [https://gitlab.com/daniele.baisero/aoh](https://gitlab.com/daniele.baisero/aoh).

## Contributing
The project is open to contributions. Please contact Daniele Baisero.

## Authors and acknowledgment
This package was ideated, designed and coded by Daniele Baisero. Michael Dales provided invaluable feedback and improvements.

## License
ISC license. Please read the LICENSE file.

## Project status
This library is under active development.
