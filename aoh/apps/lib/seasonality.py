from aoh.lib.helpers import ogr_open

def habitatSeasonality(taxon):
    # setup
    seasons = []
    if len([
        'breeding' for h in taxon.habitats
        if h['season'] in ('Breeding Season')
        and h['suitability'] in ('Suitable', 'Unknown')
        ]) > 0:
        seasons.append('breeding')
    if len([
        'nonbreeding' for h in taxon.habitats
        if h['season'] in ('Non-Breeding Season')
        and h['suitability'] in ('Suitable', 'Unknown')
        ]) > 0:
        seasons.append('nonbreeding')
    if len([
        'resident' for h in taxon.habitats
        if h['season'] in ('Resident', 'Seasonal Occurrence Unknown')
        and h['suitability'] in ('Suitable', 'Unknown')
        ]) > 0:
        seasons.append('resident')
    # format output
    seasons = list(set(seasons))
    if len(seasons) == 3:
        seasons = ['breeding', 'nonbreeding']
    elif len(seasons) == 2 and 'resident' in seasons:
        seasons = ['breeding', 'nonbreeding']
    # return output
    return seasons


def rangeSeasonality(rangeFile, taxonid):
    # setup
    src = ogr_open(rangeFile, 0)
    lyr = src.GetLayer()
    lyr.SetAttributeFilter(f'id_no = {taxonid}')
    rSeasons = [
        lyr.GetNextFeature().GetField('season')
        for _ in range(lyr.GetFeatureCount())
        ]
    seasons = []
    if 'breeding' in rSeasons:
        seasons.append('breeding')
    if 'nonbreeding' in rSeasons:
        seasons.append('nonbreeding')
    if 'resident' in rSeasons:
        seasons.append('resident')
    # format output
    seasons = list(set(seasons))
    if len(seasons) == 3:
        seasons = ['breeding', 'nonbreeding']
    elif len(seasons) == 2 and 'resident' in seasons:
        seasons = ['breeding', 'nonbreeding']
    # return
    return seasons