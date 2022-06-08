import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from scipy.optimize import differential_evolution
import warnings

class XRAY():
    def __init__(self, data):
        '''
        data: datasource 
        It can be given in several format; list of lists, list of numpy arrays, dataframe or list of pairs [(x1,y1),(x2,y2),…(xn,yn)].
        The firsts elements are considered X
        The second’s elements are considered Y

        '''
        self.data = data
        if type(self.data)==list:
            if type(self.data[0])==list:
                self.X = np.array(self.data[0])
                self.Y = np.array(self.data[1])
            elif type(self.data[0]) ==np.ndarray:
                self.X = self.data[0]
                self.Y = self.data[1]
            else:
                self.X = np.array([i[0] for i in self.data])
                self.Y = np.array([i[1] for i in self.data])               
        elif type(self.data)==pd.core.frame.DataFrame:
            self.X = self.data.values[:,0]
            self.Y = self.data.values[:,1]
        else:
            raise NameError('No valid data structure')
        self.interval = []
    
    def intervals(self,listOfLists:list)->list:
        '''
        Modifies self.interval
        Allows to calculates fits in difractogram with multiple peaks.
        Listoflist needs to contain pairs of 2Theta angles, the pairs of points indicate intervals of peaks positions
        
        Parameters
        ----------
        listOfLists: list of lists like [[38,41],[42,52]]
        '''
        listOfIndexIntervals = []
        for interval in listOfLists:
            indexPos1 = np.abs(self.X-interval[0]).argmin()
            indexPos2 = np.abs(self.X-interval[1]).argmin()
            listOfIndexIntervals.append((indexPos1,indexPos2))
        self.interval = listOfIndexIntervals

    def __private1Gaussian(self,x:float, H:float, A:float, x0:float, sigma:float)->float:
        '''
        Calculates the gauss function in a gived point

        Parameters
        ----------
        x : numeric, poinnt to be calculated
        H : numeric, base level
        A : numeric, Amplitude
        x0 : numeric, center position 
        sigma : numeric, standar desviation
        '''
        return H + A * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))
    
    def __privateexp(x, A, K, C):
        '''
        Calculates a exponential function in a gived point

        Parameters
        ----------
        x : numeric, poinnt to be calculated
        C : numeric, base level
        A : numeric, Amplitude
        C : numeric, center position 
        
        '''

        return A*np.exp(K*x) + C
    
    def __private3poly(self,x, A, B, C, D):
        '''
        Calculates 3 deg polinomic function

        Parameters
        ----------
        x : numeric, poinnt to be calculated
        A : numeric, Free parameter 1
        B : numeric, Free parameter 2
        C : numeric, Free parameter 3 
        D : numeric, Free parameter 4
        '''
        return A*x**3 + B*x**2 + C*x + D
    def __private4poly(self,x, A, B, C, D, E):
        '''
        Calculates 3 deg polinomic function

        Parameters
        ----------
        x : numeric, poinnt to be calculated
        A : numeric, Free parameter 1
        B : numeric, Free parameter 2
        C : numeric, Free parameter 3 
        D : numeric, Free parameter 4
        E : numeric, Free parameter 5
        '''
        return A*x**4 + B*x**3 + C*x**2 + D*x + E

    def gauss_fit(self,peakIndexNumber):
        '''
        Fits X, Y data to a gaussian function and returns popt and pcov.
        popt contains the parameters fitted H, A, x0 and sigma.
        pcov is the covariance matrix from the gaussian fit

        Parameters
        ----------
        peakIndexNumber: Integer, index of the peak in difractogram to fit. It needs method intervals
        '''
        pos1 = self.interval[peakIndexNumber][0]
        pos2 = self.interval[peakIndexNumber][1]
        x = self.X[pos1:pos2]
        y = self.Y[pos1:pos2]
        mean = sum(x * y) / sum(y)
        sigma = np.sqrt(sum(y * (x - mean) ** 2) / sum(y))
        popt, pcov = curve_fit(self.__private1Gaussian, x, y, p0=[min(y), max(y), mean, sigma])
        H, A, x0, sigma = popt
        EH, EA, E2Theta, ES = np.sqrt(np.abs(pcov.diagonal()))#Desviaciiones Standart
        
        dictfit = {
            'baseLevel':[H,EH],
            'amplitude':[A,EA],
            'center':[x0,E2Theta],
            'FWHM':[round(2.355*abs(sigma),4),round(2.355*ES,4)],
            'integratedIntensity':np.trapz(y,x)
        }
        return (popt,pcov,dictfit)
    
    def plotData(self,label='raw data'):
        '''
        Helper method to visualize the data

        Parameter
        ---------
        label : str The label for the data
        '''

        plt.plot(self.X,self.Y, label = label)
        plt.ylabel('Intensity (Counts)', size = 20)
        plt.yticks(size = 15)
        plt.xlabel('$\Theta$-2$\Theta$',size = 20)
        plt.xticks(size = 15)
    
    def plotintervals(self):
        for indexes in self.interval:
            plt.plot(self.X[indexes[0]:indexes[1]],self.Y[indexes[0]:indexes[1]])
    
    def removeNoise(self,how='poly',rangeOfData=[],rangePeaks=[]):
        '''
        Remove base lavel/Noise
        
        Parameters
        ----------
        rangeOfData: list of a pair of numbers, containing range of data to explore
        rangePeaks: list of pairs of numbers. Each pair of numbers corresponds to the X positions which contains a peak (2Theta, indexes are calculated)
        '''
        #########################################
        # Generates data without peaks
        ##########################################
        dataTodelete = []

        if rangePeaks!=[]:
            for r in rangePeaks:
                indexminfoo = np.abs(self.X-r[0]).argmin()
                indexmaxfoo = np.abs(self.X-r[1]).argmin()
                listfoo = list(range(indexminfoo,indexmaxfoo+1))
                dataTodelete += listfoo
        else: # This part of the code requires previous use of method intervals
            for r in self.interval:
                listfoo = list(range(r[0],r[1]))
                dataTodelete += listfoo
        
        XToNoiseDelete = np.delete(self.X,dataTodelete)
        YToNoiseDelete = np.delete(self.Y,dataTodelete)

        ##########################################
        # Generates window of data to be fitted without peaks
        ##########################################
        if rangeOfData !=[]:   
            rangeDataIndex = (np.abs(XToNoiseDelete-rangeOfData[0]).argmin(),np.abs(XToNoiseDelete-rangeOfData[1]).argmin())
            XSelected = XToNoiseDelete[rangeDataIndex[0]:rangeDataIndex[1]]
            YSelected = YToNoiseDelete[rangeDataIndex[0]:rangeDataIndex[1]]
        else:# if not range is specified then all the data is selected
            XSelected = XToNoiseDelete
            YSelected = YToNoiseDelete

        ##########################################
        # Generates window of data to be fitted with peaks to substract noise
        ##########################################

        if rangeOfData ==[]:
            XToSubstract = self.X
            YToSubstract = self.Y
        else:
            XToSubstract = self.X[np.abs(self.X-rangeOfData[0]).argmin():np.abs(self.X-rangeOfData[1]).argmin()]
            YToSubstract = self.Y[np.abs(self.X-rangeOfData[0]).argmin():np.abs(self.X-rangeOfData[1]).argmin()]



        ##########################################################################
        # Automatic search for initial guess by differentila evolution           #
        ########################################################################## 
        def sumOfSquaredError(parameterTuple):
            warnings.filterwarnings("ignore") 
            val = self.__private4poly(XToNoiseDelete, *parameterTuple)
            return np.sum((YToNoiseDelete - val) ** 2.0)
        def generate_Initial_Parameters():
            # min and max used for bounds
            maxX = max(XSelected)
            minX = min(XSelected)
            maxY = max(YSelected)
            minY = min(YSelected)
            maxXY = max(maxX, maxY)

            parameterBounds = []
            parameterBounds.append([-maxXY, maxXY]) # seach bounds for A
            parameterBounds.append([-maxXY, maxXY]) # seach bounds for B
            parameterBounds.append([-maxXY, maxXY]) # seach bounds for C
            parameterBounds.append([-maxXY, maxXY]) # seach bounds for D
            parameterBounds.append([-maxXY, maxXY]) # seach bounds for E

            # "seed" the numpy random number generator for repeatable results
            result = differential_evolution(sumOfSquaredError, parameterBounds, seed=42)
            return result.x
        ##############################################################################
        popt, pcov = curve_fit(self.__private4poly, XSelected, YSelected,generate_Initial_Parameters())
        Yfit = self.__private4poly(XSelected,*popt)
        YNoNoise = YToSubstract -self.__private4poly(XToSubstract,*popt)
        zero_array = np.zeros(YNoNoise.shape, dtype=YNoNoise.dtype)
        YNoNoise = np.maximum(YNoNoise, zero_array)

        allDataSelectedWithoutPeaks = [XSelected,YSelected]
        noiseFitting = [XSelected,Yfit]
        dataWithNoNoise = [XToSubstract,YNoNoise]

        return (allDataSelectedWithoutPeaks,noiseFitting,dataWithNoNoise)

if __name__ == "__main__":
    print('_ok_')