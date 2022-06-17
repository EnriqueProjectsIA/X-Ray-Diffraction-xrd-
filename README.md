# X-Ray-Diffraction (xrd)

## Description

Files are used to manage data from different sources.

## Files

* XRD.py - Class and methods used to manipulate data from X-Ray diffractometers and calculate different magnitudes. 
* PrepareDataToPush – Class to give consistent struct and types to the data before pushing the data to a mongoDb

## Usage

### Load data

XRAY(“Your data”) will instantiate the class.
It requires  data to be structured as:
* Lists of lists, like: [ [X data],[Y data] ]
* List of numpy arrays [ [X data], [Y data]]
* pandas dataframes: The first column is X and the second Y
* list of tuples [(X1,Y1), (X2.Y2),(X3,Y3)….(Xn,Yn)]

Once the class is instantiated, the data can be accessed by self.X and sef.Y as numpy arrays

