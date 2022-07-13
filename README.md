**Author:** [Behrouz Safari](https://behrouzz.github.io/)<br/>
**Website:** [AstroDataScience.Net](http://astrodatascience.net/)<br/>

# gaiadr3
*Retrieve data and analysis package for Gaia Data Release 3*


## Installation

Install the latest version of *gaiadr3* from [PyPI](https://pypi.org/project/gaiadr3/):

    pip install gaiadr3

The only requirement is *pandas*.


## Background

Gaia Data Release 3 presents two main types of data: *tabular* and *ancillary*.
The tabular data can be retrieved using ADQL Tap queries and are described in the [Data Model](https://gea.esac.esa.int/archive/documentation/GDR3/Gaia_archive/chap_datamodel/)
The ancillary data are those that can not be accessed via ADQL Tap queries. Epoch photomerty and spectroscopic data are of this type.
You need to use DataLink to retrieve this type of data. 


## Tap queries

The standard way to retrieve tabular data is by using tap queries. Pass your script to the *sql2df* function. It will return two pandas dataframes: data and meta.

```python
>>> from gaiadr3 import sql2df
>>> data, meta = sql2df('SELECT TOP 5 source_id, ra, dec FROM gaiadr3.gaia_source')
>>> print(meta)
                                                 description  unit
name                                                              
source_id  Unique source identifier (unique within a part...  None
ra                                           Right ascension   deg
dec                                              Declination   deg
>>> print(data)
             source_id          ra        dec
0  4116903625596296576  266.323047 -22.651077
1  4116903625596299136  266.321568 -22.651833
2  4116903625596302976  266.320308 -22.652672
3  4116903625596305408  266.321332 -22.651379
4  4116903625596305536  266.321399 -22.651430
```

For ease of use, I have created some shortcut keywords which begin with '@'. Currently, they are:

* @MT : Main Table (gaiadr3.gaia_source)
* @LT : Lite Table (gaiadr3.gaia_source_lite)
* @COLS : A selection of the most important columns

```python
>>> data, meta = sql2df('SELECT TOP 3 @COLS FROM @MT')
>>> data
             source_id          ra  ...  has_mcmc_gspphot  has_mcmc_msc
0  4116903625596296576  266.323047  ...             False         False
1  4116903625596299136  266.321568  ...             False         False
2  4116903625596302976  266.320308  ...             False         False

[3 rows x 24 columns]
```


## Get single source

The simplest way to get data for a single source, is using *GaiaObject* class. You can create an instance of this class by passing a *source_id*:

```python
>>> from gaiadr3 import GaiaObject
>>> source_id = 30343944744320
>>> obj = GaiaObject(source_id=source_id)
```

Now you can use the *download* method to retrieve both tabular and ancillary. This method accepts two boolean arguments: *key_param* and *ancillary*.
Both are True by default. After using this method, some important key parameter will be downloaded as a python dictionary in the *key_param* attribute.

```python
>>> obj.download()
>>> print(obj.key_param['data'])
{'solution_id': 1636148068921376768,
 'ra': 45.09499151004629,
 'dec': 0.4768361311353548,
 'parallax': 1.120139133994462,
 'distance_gspphot': 913.4706,
 'pm': 19.76517,
 'pmra': 19.35330019571839,
 'pmdec': 4.013937591116442,
 'radial_velocity': 40.224552,
 'teff_gspphot': 12291.837,
 'logg_gspphot': 4.0962,
 'phot_g_mean_mag': 9.899,
 'phot_bp_mean_mag': 9.873377,
 'phot_rp_mean_mag': 9.918395,
 'phot_g_mean_flux': 2067028.6966188122,
 'phot_bp_mean_flux': 1534850.5584509764,
 'phot_rp_mean_flux': 854673.6713712276,
 'has_epoch_photometry': True,
 'has_epoch_rv': False,
 'has_rvs': True,
 'has_xp_continuous': True,
 'has_xp_sampled': True,
 'has_mcmc_gspphot': True,
 'has_mcmc_msc': True}
```

If you don't know what are these parameters, look at *obj.key_param['meta']*. <br/>

The ancillary data will be downloaded as csv files in the 'data' folder in the working directory. These data, if exist, can be accessed as attributes:<br/>

```python
>>> print(obj.xp_samp)
     wavelength          flux    flux_error
0         336.0  7.519030e-15  8.592673e-16
1         338.0  6.699424e-15  7.309379e-16
2         340.0  5.937778e-15  6.685453e-16
3         342.0  5.614390e-15  6.325656e-16
4         344.0  5.726218e-15  6.402061e-16
..          ...           ...           ...
338      1012.0  5.449369e-16  6.181877e-17
339      1014.0  5.333555e-16  6.771072e-17
340      1016.0  5.501445e-16  7.086527e-17
341      1018.0  5.647527e-16  6.731273e-17
342      1020.0  6.096352e-16  6.407823e-17

[343 rows x 3 columns]
```

Attributes corresponding to the ancillary data are: *ep_phot*, *rvs*, *xp_samp*, *xp_cont*. Use the *has* attribute to see which of these are available.

```python
>>> print(obj.has)
{'EPOCH_PHOTOMETRY': True,
 'RVS': True,
 'XP_CONTINUOUS': True,
 'XP_SAMPLED': True,
 'MCMC_GSPPHOT': True,
 'MCMC_MSC': True}
```

## Get multiple sources

If you want to get ancillary data for multiple sources you should use DataLink class. 

```python
>>> from gaiadr3 import DataLink
>>> sources = [30343944744320, 6196457933368101888]
>>> dl = DataLink(source_id=sources, retrieval_type='ALL')
>>> dl.download()
```

By default, the data will be downloaded in 'data' folder in the working directory. For each object a folder will be created.
Using the *get_objects* method, you can access each source as a GaiaObject as explained above.
Let's get the epoch photometry for green, blue and red bands for the first source:

```python
>>> objects = dl.get_objects()
>>> g, b, r = objects[0].ep_phot
>>> print(g)
                                 mag          flux   flux_error
TCB                                                            
2014-09-06 08:55:04.077123  9.910611  2.045042e+06  3983.560844
2014-09-06 10:41:40.701409  9.909272  2.047565e+06  3652.792295
2014-12-27 00:49:44.365184  9.890911  2.082487e+06  3175.264209
2014-12-27 02:36:15.656166  9.874771  2.113675e+06  4644.732420
2015-01-16 06:49:25.778803  9.883712  2.096341e+06  1828.438678
2015-01-16 08:35:59.407773  9.888541  2.087037e+06  2039.618901
2015-02-15 00:23:35.148389  9.864696  2.133381e+06  2924.895816
2015-07-07 19:46:09.417232  9.886747  2.090489e+06  2817.581457
2015-08-01 03:31:05.147557  9.922456  2.022854e+06  3171.964369
2015-08-30 03:21:11.667936  9.880055  2.103414e+06   977.945250
2016-01-05 13:57:07.739350  9.880296  2.102947e+06  1754.446362
2016-01-05 15:43:39.101625  9.878165  2.107079e+06  1487.112158
2016-01-31 01:44:44.422883  9.919168  2.028988e+06  1516.905039
2016-02-25 03:16:43.072088  9.923205  2.021458e+06  2363.931131
2016-07-17 08:55:16.873392  9.905461  2.054766e+06  3400.421158
2016-07-17 10:41:51.854195  9.909443  2.047244e+06  1766.953020
2016-08-15 14:44:12.432337  9.904904  2.055821e+06  1543.565592
2016-09-08 14:45:34.479689  9.897831  2.069257e+06  2292.732039
2016-09-08 16:32:08.406143  9.886640  2.090695e+06  4654.839112
2017-01-14 21:05:28.352674  9.926262  2.015774e+06  1613.007848
2017-01-14 22:52:01.924915  9.909325  2.047467e+06  3051.287780
2017-02-13 10:01:27.449079  9.920222  2.027019e+06  1790.127633
2017-02-13 11:48:01.024177  9.926633  2.015085e+06  3115.379630
2017-03-05 21:57:47.804485  9.886628  2.090718e+06  1692.944591
2017-03-05 23:44:23.399045  9.877953  2.107490e+06  4360.998681
```

See more at [astrodatascience.net](https://astrodatascience.net/)
