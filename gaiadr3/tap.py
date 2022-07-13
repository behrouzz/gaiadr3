from urllib.request import urlopen
import pandas as pd
import json


BASE_GAI = """https://gea.esac.esa.int/tap-server/tap/sync?\
request=doQuery&lang=adql&format=json&query=""".replace(' ','')

BASE_VIZ = """http://tapvizier.u-strasbg.fr/TAPVizieR/tap/sync?\
request=doQuery&lang=adql&format=json&query=""".replace(' ','')

TABLE_VIZ = "'I/355/gaiadr3'"
TABLE_GAI = 'gaiadr3.gaia_source'

 
sel_cols_gai = [
    'source_id','ra','dec',
    'parallax','distance_gspphot','pm','pmra','pmdec',
    'radial_velocity','teff_gspphot','logg_gspphot',
    'phot_g_mean_mag','phot_bp_mean_mag','phot_rp_mean_mag',
    'phot_g_mean_flux','phot_bp_mean_flux','phot_rp_mean_flux',
    #'HIP', #'SDSS13',
    'has_epoch_photometry','has_epoch_rv','has_rvs','has_xp_continuous',
    'has_xp_sampled','has_mcmc_gspphot','has_mcmc_msc'
    ]

sel_cols_viz =[
    'Source','RAJ2000','DEJ2000', #'RandomI',
    'Plx','Dist','PM','pmRA','pmDE',
    'RV','Teff','logg',
    'Gmag','BPmag','RPmag',
    'FG','FBP','FRP',
    #'HIP','SDSS13',
    'EpochPh','EpochRV','RVS','XPcont','XPsamp',
    # has_mcmc_gspphot & has_mcmc_msc SHOULD BE ADDED
    ]


dc_vizier = {'BASE': BASE_VIZ, 'TABLE': TABLE_VIZ, 'COLS': sel_cols_viz}
dc_gaia = {'BASE': BASE_GAI, 'TABLE': TABLE_GAI, 'COLS': sel_cols_gai}



def shortcut(script, server='gaia'):
    dc_server = get_server_dc(server)
    
    if server.lower()=='gaia':
        s = script.replace('@MT', TABLE_GAI)
        s = s.replace('@LT', 'gaiadr3.gaia_source_lite')
    elif server.lower()=='vizier':
        s = script.replace('@MT', TABLE_VIZ)
    else:
        raise Exception('Invalide server!')
    
    cols = ','.join(dc_server['COLS'])
    s = s.replace('@COLS', cols)
    return s


def get_server_dc(server):
    if server.lower()=='gaia':
        dc_server = dc_gaia
    elif server.lower()=='vizier':
        dc_server = dc_vizier
    else:
        raise Exception('Server name not valide!')
    return dc_server


def get(script, server='gaia'):
    dc_server = get_server_dc(server)
    script = ' '.join(script.strip().split('\n'))
    url = dc_server['BASE'] + script.replace(' ', '%20')
    dc = json.loads(urlopen(url).read().decode('utf-8'))
    return dc


def columns(table=None, ucd=False, server='gaia'):
    dc_server = get_server_dc(server)
    if table is None:
        table = dc_server['TABLE']
    ucd = ', ucd' if ucd else ''
    cols = 'column_name, description, unit' + ucd
    script = f"SELECT {dc_server['COLS']} FROM tap_schema.columns WHERE table_name='{table}'"
    r = get(script)
    cols = [i['name'] for i in r['metadata']]
    df = pd.DataFrame(r['data'], columns=cols)
    return df.set_index('column_name')


def sql2df(script, server='gaia'):
    script = shortcut(script, server=server)
    r = get(script)
    cols = [i['name'] for i in r['metadata']]
    data = pd.DataFrame(r['data'], columns=cols)
    meta = pd.DataFrame(r['metadata'])
    meta = meta[['name', 'description', 'unit']].set_index('name')
    return data, meta


def get_source(source_id, full=False, server='gaia'):
    dc_server = get_server_dc(server)
    cols = '*' if full else ','.join(dc_server['COLS'])
    source_col = 'source_id' if server=='gaia' else 'source'
    script = f"SELECT {cols} FROM {dc_server['TABLE']} WHERE {source_col}={source_id}"
    data, meta = sql2df(script)
    dc = data.iloc[0].to_dict()
    return dc, meta

