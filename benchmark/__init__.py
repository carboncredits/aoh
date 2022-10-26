'''Basic benchmark implementation

The user must pass a `benchmark_parameters` parameter to the main benchmark
function. This is a dictionary with all modeller parameters with the exclusion
of `path`.
'''

import os
import tempfile
import timeit


from .benchmark_parameters import benchmark_parameters


def benchmark_run(parameters, tempdir, silent=False):
    import aoh
    if not silent:
        print('function start')
    aoh.modeller(
        path       = os.path.join(tempdir, 'output.tif'),
        landc      = parameters['landc'],
        dem        = parameters['dem'],
        habs       = parameters['habs'],
        dems       = parameters['dems'],
        maskRast   = parameters['maskRast'],
        maskVect   = parameters['maskVect'],
        maskWhere  = parameters['maskWhere'],
        area       = parameters['area'],
        sid        = parameters['sid'],
        return_sum = parameters['return_sum']
        )
    if not silent:
        print('function end')


def benchmark(parameters=benchmark_parameters, number=5):
    with tempfile.TemporaryDirectory() as tempdir:
        print()
        print('Pre-running modeller to normalize execution time')
        benchmark_run(parameters=parameters, tempdir=tempdir, silent=True)
        print(f'executing {number} times')
        mtpr = timeit.Timer(lambda: benchmark_main(parameters=parameters, tempdir=tempdir)).timeit(number=number)/number
        print(f'Modeller mean time per run: {mtpr}')        
        print()
