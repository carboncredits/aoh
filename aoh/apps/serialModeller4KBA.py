import aoh
from .lib import seasonality
import os
import traceback
try:
    import iucn_modlib
except:
    import warnings
    warnings.warn("Package 'iucn_modlib' not found. Some apps may not work.")

def serialModeller4KBA(species, path, landc, dem, mask, token = None, batchPath = None, conKBA = None, area = None, sid = None, filename = None):
    """Automatically create a species model.

    Suitable for serial modelling using the IUCN API.

    The `species` will be modelled once if the species is resident, or twice if
    it has different breeding/nonbreeding ranges or habitat suitabilities.
    All appropriate models will be writen in the `path` folder using the
    `species` parameter as prefix and appripriate suitability as suffix.
    E.g.
        Canis_lupus_resident.gpkg
        3746_resident.gpkg
        Ursus_maritimus_breeding.gpkg
        Ursus_maritimus_nonbreeding.gpkg
        22823_breeding.gpkg
        22823_nonbreeding.gpkg
    
    If `sid` is provided, a species spatial summary output is returned

        parameters:
            species (int, str, iucn_modlib.Taxon): The species' binomial, SIS taxon id,
            or an iucn_modlib.Taxon object.
            path (str): The file path of the folder where to write the file.
            landc (str): The file path to the landcover file
            dem (str): The file path to the DEM file.
            mask (str): The file path to the mask vector file.
            token (str): A valid IUCN API token.
            area (str): Optional. The file path to the area file.
            sid (str): Optional. The file path to the spatial id file.
    """
    # Get and clean taxon object
    if isinstance(species, iucn_modlib.Taxon):
        taxon = species
        species = taxon.taxonid
    elif token is not None:
        taxon = iucn_modlib.TaxonFactoryRedListAPI(sp=species, token=token, fixElevation=True, fixHabitats=True)
    elif batchPath is not None:
        taxon = iucn_modlib.TaxonFactoryRedListBatch(sp=species, source=batchPath, fixElevation=True, fixHabitats=True)
    elif conKBA is not None:
        if type(conKBA) == dict:
            import psycopg2
            conKBA = psycopg2.connect(
                host = conKBA["host"],
                database = conKBA["database"],
                user = conKBA["user"],
                password = conKBA["password"]
                )
        taxon = iucn_modlib.TaxonFactoryKBA(species, conKBA, fixElevation=True, fixHabitats=True)
    else:
        raise Exception('at least one of token, batchPath or conKBA must be provided')
    # Find if species is resident or seasonal
    habitatSeasons = seasonality.habitatSeasonality(taxon)
    rangeSeasons = seasonality.rangeSeasonality(mask, taxon.taxonid)
    seasons = list(set(habitatSeasons + rangeSeasons))
    if len(seasons) == 3:
        seasons = ('breeding', 'nonbreeding')
    elif len(seasons) == 2 and 'resident' in seasons:
        seasons = ('breeding', 'nonbreeding')
    # Run modeller
    for season in seasons:
        if season == 'resident':
            HF = iucn_modlib.HabitatFilters(season=('Resident', 'Seasonal Occurrence Unknown'))
        elif season == 'breeding':
            HF = iucn_modlib.HabitatFilters(season=('Resident', 'Breeding Season', 'Seasonal Occurrence Unknown'))
        elif season == 'nonbreeding':
            HF = iucn_modlib.HabitatFilters(season=('Resident', 'Non-Breeding Season', 'Seasonal Occurrence Unknown'))
        else:
            raise ValueError('internally badly coded season')
        try:
            if filename is None:
                filename = f"{species}_{season}.{'tif' if sid is None else 'csv.gz'}"
            filepath = os.path.join(path, filename)
            if filename not in os.listdir(path):
                aoh.modeller(
                    path = filepath,
                    landc = landc,
                    dem = dem,
                    habs = iucn_modlib.translator.toESACCI(taxon.habitatCodes(HF)),
                    dems = (taxon.elevation_lower, taxon.elevation_upper),
                    maskRast = None,
                    maskVect = mask,
                    maskWhere = f"id_no = {taxon.taxonid} and season in ('{season}', 'resident')",
                    area = area,
                    sid = sid
                    )
        except Exception:
            traceback.print_exc()