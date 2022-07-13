"""
Module core
===========
This module provides two main classes: GaiaObject and DataLink

Ref: https://www.cosmos.esa.int/web/gaia-users/archive/programmatic-access#CommandLine_DataLink
"""

from urllib.request import urlopen, urlretrieve
import json, os, shutil
from zipfile import ZipFile
from glob import glob
from .tap import get_source
from .phot_spec import ep_phot, xp_samp, rvs, xp_cont
from .utils import get_filename



BASE = 'https://gea.esac.esa.int/data-server/data?RETRIEVAL_TYPE='

VALID_FT = ['VOTABLE', 'VOTABLE_PLAIN', 'FITS', 'CSV', 'ECSV']

VALID_RT = ['EPOCH_PHOTOMETRY', 'XP_SAMPLED', 'XP_CONTINUOUS',
             'MCMC_GSPPHOT', 'MCMC_MSC',  'RVS', 'ALL']

VALID_DS = ['INDIVIDUAL','COMBINED','RAW']

ancils = ['has_epoch_photometry', 'has_epoch_rv', 'has_rvs',
          'has_xp_continuous', 'has_xp_sampled',
          'has_mcmc_gspphot', 'has_mcmc_msc']



class GaiaObject:
    def __init__(self, source_id, adr_csv=None):
        
        self.source_id = str(source_id)
        self.adr = None
        self.files = None
        self.key_param = None

        self.has = {
            'EPOCH_PHOTOMETRY': False,
            #'EPOCH_RV': False,
            'RVS': False,
            'XP_CONTINUOUS': False,
            'XP_SAMPLED': False,
            'MCMC_GSPPHOT': False,
            'MCMC_MSC': False
            }
        
        if adr_csv is not None:
            self.files = [i for i in glob(adr_csv + '/*.csv') if self.source_id in i]
            self.adr = adr_csv
            self.__update_has()

        

    def __update_has(self):
        if self.files is not None:
            for f in self.files:
                for k in self.has.keys():
                    if k in f:
                        self.has[k] = True


    def download(self, key_param=True, ancillary=True):
        """
        key_param (bool): If True, the key parameters from gaia_source table
                          will be downloaded.
        ancillary (bool): If True, all the ancillary data will be downloaded.
        """
        if key_param:
            
            dc, meta = get_source(self.source_id)
            self.key_param = {'data':dc, 'meta':meta}

        if ancillary:
            
            folder = f'data/{self.source_id}'
            
            if os.path.isdir(folder):
                shutil.rmtree(folder)
            os.makedirs(folder)
            
            url = BASE + f'ALL&ID={self.source_id}&' + \
                  'DATA_STRUCTURE=INDIVIDUAL&RELEASE=Gaia+DR3&FORMAT=csv'
            
            filename = folder + '/' + get_filename(url)
            urlretrieve(url, filename)
            
            if filename[-3:]=='zip':
                with ZipFile(filename, 'r') as zip:
                    zip.extractall(folder)
                self.read_ancillary(adr=folder)
                os.remove(filename)


    def read_ancillary(self, adr=None):

        if adr is not None:
            self.files = [i for i in glob(adr + '/*.csv') if self.source_id in i]
            self.adr = adr
            self.__update_has()
        elif self.adr is not None:
            adr = self.adr
        else:
            raise Exception('No address provided!')

        if self.has['EPOCH_PHOTOMETRY']:
            self.ep_phot = ep_phot(
                file=adr+f'/EPOCH_PHOTOMETRY-Gaia DR3 {self.source_id}.csv',
                to_datetime=True)
            
        if self.has['RVS']:
            self.rvs = rvs(adr+f'/RVS-Gaia DR3 {self.source_id}.csv')

        if self.has['XP_CONTINUOUS']:
            self.xp_cont = xp_cont(adr+f'/XP_CONTINUOUS-Gaia DR3 {self.source_id}.csv')

        if self.has['XP_SAMPLED']:
            self.xp_samp = xp_samp(adr+f'/XP_SAMPLED-Gaia DR3 {self.source_id}.csv')

        # MCMC_GSPPHOT and MCMC_MSC will be added in the future




class DataLink:
    """
    Gaia DataLink class

    

    ARGUMENTS:
    ----------
    source_id (int or list): object or objects source_id(s)
    retrieval_type (str): 'EPOCH_PHOTOMETRY', 'XP_SAMPLED', 'XP_CONTINUOUS',
                          'MCMC_GSPPHOT', 'MCMC_MSC',  'RVS', 'ALL'
                          (Default: 'ALL')
    data_structure (str): 'INDIVIDUAL','COMBINED','RAW'
                          (Default: 'INDIVIDUAL')
    
    ATTRIBUTES:
    -----------
    multi (bool) : if the request is for multiple souces
    url (str) : the url of the file to download
    sources (lis): list of souce IDs
    files (list): list of downloaded files

    METHODS:
    --------
    datalink_url : return url of the file to download
    download : download the requested file
    get_objects : Create list of 'GaiaObject's

    Ref: https://www.cosmos.esa.int/web/gaia-users/archive/programmatic-access
    """
    def __init__(self, source_id, format='csv', retrieval_type=None, data_structure=None):
        self.multi = False
        
        self.source_id = self.__check_source_id(source_id)
        self.format = self.__check_format(format)
        self.retrieval_type = self.__check_retrieval_type(retrieval_type)
        self.data_structure = self.__check_data_structure(data_structure)
            
        self.url = self.datalink_url()
        
        
    def __check_source_id(self, source_id):
        if isinstance(source_id, list):
            self.multi = True
            self.sources = [str(i) for i in source_id]
            source_id = ','.join(self.sources).replace(' ', '')
        else:
            self.sources = [str(source_id)]
        return source_id

    def __check_format(self, format):
        format = format.upper()
        if format not in VALID_FT:
            raise Exception(f'format not valid! Options::\n{VALID_FT}')
        return format

    def __check_retrieval_type(self, retrieval_type):
        if retrieval_type is None:
            retrieval_type = 'ALL'
        else:
            retrieval_type = retrieval_type.upper()
            if retrieval_type not in VALID_RT:
                raise Exception(f'retrieval_type not valid! Options::\n{VALID_RT}')
        return retrieval_type

    def __check_data_structure(self, data_structure):
        if data_structure is None:
            data_structure = 'INDIVIDUAL'
        else:
            data_structure = data_structure.upper()
            if data_structure not in VALID_DS:
                raise Exception(f'data_structure not valid! Options::\n{VALID_DS}')
        return data_structure


    def datalink_url(self):
        #format='fits' to be added
        url = BASE + f'{self.retrieval_type}&ID={self.source_id}&' + \
              f'DATA_STRUCTURE={self.data_structure}&RELEASE=Gaia+DR3&FORMAT={self.format}'
        return url


    def download(self):

        folder = f'data/{self.source_id}'
            
        if os.path.isdir(folder):
            shutil.rmtree(folder)
        os.makedirs(folder)

        filename = folder + '/' + get_filename(self.url)
        urlretrieve(self.url, filename)

        if filename[-3:]=='zip':
            with ZipFile(filename, 'r') as zip:
                zip.extractall(folder)
            os.remove(filename)

        self.files = glob(folder+'/*')
        
        if self.multi:
            for s in self.sources:
                s_fol = 'data/' + s
                if os.path.isdir(s_fol):
                    shutil.rmtree(s_fol)
                os.makedirs(s_fol)
                for f in self.files:
                    end_file = os.path.basename(os.path.normpath(f))
                    if s in end_file:
                        shutil.copyfile(f, s_fol+'/'+end_file)
            shutil.rmtree(folder)
            self.files = []
            for s in self.sources:
                for f in glob(f'data/{s}/*'):
                    self.files.append(f)


    def get_objects(self):
        """
        Create list of 'GaiaObject's
        """
        objects = []
        if self.files is not None:
            if len(self.files)>0:
                for s in self.sources:
                    obj = GaiaObject(source_id=s)
                    obj.read_ancillary(f'data/{s}')
                    objects.append(obj)
        return objects

                


