from os.path import expanduser


benchmark_parameters = {
    'landc'      : expanduser('~/python/benchmark_aoh/data/esacci_2020.tif'),
    'dem'        : expanduser('~/python/benchmark_aoh/data/esacci_dem.tif'),
    'habs'       : [170, 202, 210, 180],
    'dems'       : (-500, 3),
    'maskRast'   : expanduser('~/python/benchmark_aoh/data/8010_breeding_mask.tif'),
    'maskVect'   : None,
    'maskWhere'  : None,
    'area'       : expanduser('~/python/benchmark_aoh/data/esacci_area.tif'),
    'sid'        : None,
    'return_sum' : False
    }