import numpy as np
from datetime import date, datetime, time, timedelta
from pydantic import BaseModel, validator, root_validator, constr
from typing import Optional, List, Dict
import re


########################################################################
## Errors
########################################################################

class NameError(Exception):
    '''Exception raised when validation string is invalid'''

    def __init__(self, value:str, message:str) ->None:
        self.value = value
        self.message = message
        super().__init__(message)

class UnitMissingError(Exception):
    '''Exception raised when a vulue is given but not the units'''

    def __init__(self, values:dict, message:str) ->None:
        self.values = values
        self.message = message
        super().__init__(message)

class DlimiterNumberError(Exception):
    '''Exception raised when incorrect number of delimiter'''

    def __init__(self, value:int, message:str) ->None:
        self.value = value
        self.message = message
        super().__init__(message)
class WrongDateFormat(Exception):
    '''Exception raised when incorrect number of delimiter'''

    def __init__(self, value:int, message:str) ->None:
        self.value = value
        self.message = message
        super().__init__(message)

class MissingDataError(Exception):
    '''Exception raised when the X data and Y data dimensions are different'''

    def __init__(self, values:dict, message:str) ->None:
        self.values = values
        self.message = message
        super().__init__(message)

################################################################
## classes for multiple uses
################################################################

class PairValueUnit(BaseModel):
    quantity:   Optional[float] = None
    units:      Optional[str] = None

    @root_validator(pre = True)
    @classmethod
    def checkForUnits(cls, values:Dict)->Dict:
        valueToCheck = values.get('quantity')
        unitToCheck = values.get('units')
        if valueToCheck!=None and unitToCheck==None:
            raise UnitMissingError(values = values, message="A measure has to have units")
        return values

class PairListValueUnit(BaseModel):
    quantity:   Optional[List[float]] = []
    units:      Optional[str] = None

    @root_validator(pre = True)
    @classmethod
    def checkForUnits(cls, values:Dict)->Dict:
        valueToCheck = values.get('quantity')
        unitToCheck = values.get('units')
        if valueToCheck!=[] and unitToCheck==None:
            raise UnitMissingError(values = values, message="A measure has to have units")
        return values

class AnnealingProfile(BaseModel):
    steps:          Optional[int] = None
    temperature:    Optional[PairValueUnit]
    time:           Optional[PairValueUnit]

class Annealing(BaseModel):
    type:       Optional[str] = 'NA'
    ramp:       Optional[str] = 'NA'
    profile:    Optional[List[AnnealingProfile]]


class FabricationPresure(BaseModel):
    atmosphere: Optional[str] = 'ar'
    type:       Optional[str] = "pressure"
    quantity:   Optional[float] = None
    units:      Optional[str] = None

    @root_validator()
    @classmethod
    def checkForUnits(cls, values:Dict) -> Dict:
        valueToCheck = values.get('quantity')
        unitToCheck = values.get('units')
        if valueToCheck!=None and unitToCheck==None:
            raise UnitMissingError(values = values, message="A measure has to have units")
        return values

class Substrate(BaseModel):
    type:           str
    orientation:    str

class degreeIntensity(BaseModel):
    degrees: List[float]
    intensity: List[int]
    @root_validator()
    @classmethod
    def checkForUnits(cls, values:Dict) -> Dict:
        listToCheck1 = values.get('degrees')
        listToCheck2 = values.get('intensity')
        if len(listToCheck1)!=len(listToCheck2):
            raise MissingDataError(values = values, message="X data dimensions doesn’t match with Y data dimensions")
        return values

class TransportXY(BaseModel):
    X: Optional[PairListValueUnit]=[]
    Y: Optional[PairListValueUnit]=[]

################################################################
## Data structures for different measurements
################################################################
class MeasurementsXRAY(BaseModel):
    '''class to detail the XRAY measurements of a thin film sample'''

    nameInBox:  str
    type:       str = 'theta-2theta'
    mode:       str = ''
    machine:    str = 'SIEMENS'
    fileName:   List[str]
    location:   str
    date:       datetime
    Step_size:  float = 0.02
    Step_Time:  float = 1
    measures:   degreeIntensity

    @validator('date', pre = True)
    @classmethod
    def dateFormated(cls,value:str)->datetime:
        delimiter = re.findall(r'\D', value)
        vd = delimiter[0]
        if len(delimiter)!=2:
            raise DlimiterNumberError(value, 'Error in date delimiter')
        else:
            dateFormat=f'%Y{vd}%m{vd}%d'
        if int(value.split(vd)[0])<2000:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if int(value.split(vd)[1])>12:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if len(delimiter)==2:
            if delimiter[0]!=delimiter[1]:
                raise DlimiterNumberError(value, 'Error in date delimiter')
        value = datetime.combine(datetime.strptime(value, dateFormat),datetime.min.time())
        return value

class MeasurementsTransportM(BaseModel):
    '''class to detail the XRAY measurements of a thin film sample'''

    nameInBox:      str
    type:           str = 'transport'
    mode:           str = '4-points'
    machine:        str = 'dilution cryostat'
    fileName:       str
    location:       str
    measurementDay: datetime
    measures:       Optional[TransportXY]
    place:          str

    @validator('measurementDay', pre = True)
    @classmethod
    def dateFormated(cls,value:str)->datetime:
        delimiter = re.findall(r'\D', value)
        vd = delimiter[0]
        if len(delimiter)!=2:
            raise DlimiterNumberError(value, 'Error in date delimiter')
        else:
            dateFormat=f'%Y{vd}%m{vd}%d'
        if int(value.split(vd)[0])<2000:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if int(value.split(vd)[1])>12:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if len(delimiter)==2:
            if delimiter[0]!=delimiter[1]:
                raise DlimiterNumberError(value, 'Error in date delimiter')
        value = datetime.combine(datetime.strptime(value, dateFormat),datetime.min.time())
        return value

################################################################
## Data structures for calculated data from different sources
################################################################
class CalculatedDataTransport(BaseModel):
    '''
    Class to add data extracted from transpor measurements
    '''
    calculatedFrom: str
    nameInBox: str
    R300K:  Optional[PairValueUnit]
    R4K:    Optional[PairValueUnit]
    RN:     Optional[PairValueUnit]
    RRR:    Optional[PairValueUnit]
    TC:     Optional[PairValueUnit]


################################################################
## classes for data structures in files to be pushed
################################################################
class Sample(BaseModel):
    '''
    Base classs to create sample before pushing the data to a MongoDB.
    It contains the general data structure
    '''
    
    sampleName:     str
    tags:           Optional[List[str]]
    fabrication:    Optional[List]#Each sample layer is an element in the list
    measurements:   Optional[List]
    calculatedData: Optional[List]
    comments:       Optional[List]


    @validator('sampleName')
    @classmethod
    def validate_SampleName(cls, value):
        if ' ' in value or value=='':
            raise NameError(value=value, message="A sample has to have a name and no blank spaces are allowed")
        return value

class Fabrication(BaseModel):
    '''class to detail the fabrication steps for each layer of the thin film sample'''
    class Config:
        anystr_lower: True

    layer:                  int #from bottom to top the number of the layer
    material:               str
    method:                 str
    annealing:              Optional[Annealing]
    chamberName:            Optional[str]
    chamberConfiguration:   Optional[str]
    basePresure:            Optional[PairValueUnit]
    fabricationPresure:     Optional[FabricationPresure]
    fabricationPower:       Optional[PairValueUnit]
    substrate:              Optional[Substrate]
    depositionRate:         Optional[PairValueUnit]
    expectedThickness:      Optional[PairValueUnit]
    place:                  str
    fabricationDate:        datetime

    @validator('fabricationDate', pre = True)
    @classmethod
    def dateFormated(cls,value:str)->datetime:
        delimiter = re.findall(r'\D', value)
        vd = delimiter[0]
        if len(delimiter)!=2:
            raise DlimiterNumberError(value, 'Error in date delimiter')
        else:
            dateFormat=f'%Y{vd}%m{vd}%d'
        if int(value.split(vd)[0])<2000:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if int(value.split(vd)[1])>12:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if len(delimiter)==2:
            if delimiter[0]!=delimiter[1]:
                raise DlimiterNumberError(value, 'Error in date delimiter')
        value = datetime.combine(datetime.strptime(value, dateFormat),datetime.min.time())
        return value



class CalculatedData(BaseModel):
    '''
    Base class to add data calculated from different sources
    '''
    transport: Optional[List[CalculatedDataTransport]]
    xrd:       Optional[List]
    sem:       Optional[List]



################################################################
## classes for keepin track of sample location.
## In collection: sendSample
################################################################



class SendSample(BaseModel):
    '''
    Base classs to keep track of the sample location
    '''
    sampleName:         str
    fabricationMethod:  str
    substrate:          str
    origin:             str
    destination:        str
    sendDate:           datetime
    more:               Optional[List]
    @validator('sendDate', pre = True)
    @classmethod
    def dateFormated(cls,value:str)->datetime:
        delimiter = re.findall(r'\D', value)
        vd = delimiter[0]
        if len(delimiter)!=2:
            raise DlimiterNumberError(value, 'Error in date delimiter')
        else:
            dateFormat=f'%Y{vd}%m{vd}%d'
        if int(value.split(vd)[0])<2000:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if int(value.split(vd)[1])>12:
            raise WrongDateFormat(value,'Appropiate date format YYYY-MM-DD')
        if len(delimiter)==2:
            if delimiter[0]!=delimiter[1]:
                raise DlimiterNumberError(value, 'Error in date delimiter')
        value = datetime.combine(datetime.strptime(value, dateFormat),datetime.min.time())
        return value


if __name__ == '__main__':
    #Example of use
    print(Sample(sampleName='Test',
        fabrication = [Fabrication(
            layer = 1,
            material = 'Aluminum',
            method = 'dc-sputtering',
            depositionRate = {'quantity':11.2, 'units':'nm/min'},
            expectedThickness = {'quantity':50,'units':'nm'},
            place = 'IMB',
            fabricationDate =  "2023 7 06"
        )]
        ).dict())

    print('ok')