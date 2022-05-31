# X-Ray-Diffraction (xrd)

## Description

Helper code to speed up X-Ray diffraction analysis and obtain information regularly required. 

## Usage

### Load data

XRAY(“Your data”) will instantiate the class.
It requires  data to be structured as:
* Lists of lists, like: [ [X data],[Y data] ]
* List of numpy arrays [ [X data], [Y data]]
* pandas dataframes: The first column is X and the second Y
* list of tuples [(X1,Y1), (X2.Y2),(X3,Y3)….(Xn,Yn)]

Once the class is instantiated, the data can be accessed by self.X and sef.Y as numpy arrays

