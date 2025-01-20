"""
[] Ignoring bad channel only working in AllData
[] Only spectrum plot data is able to save. The ratio plot data is not able to save
"""

import os
import glob
import numpy as np
from xspec import *
import matplotlib.pyplot as plt

def model_logpar(pha, rmf, bkg, opath):
	"""
	
	"""
	# Xpsec output logging
	lch = Xset.logChatter
	Xset.logChatter = 20
	logFile = Xset.openLog(f"{opath}/logpar.log")
	logFile = Xset.log

	# Loading data
	s1 = Spectrum(pha)
	s1.response = rmf
	s1.background = bkg
	# s1.ignore("bad")
	s1.ignore("**-0.3,10.0-**")

	# Define model and its parameters
	m1 = Model("tbabs*logpar")
	m1.TBabs.nH = 0.0131
	m1.TBabs.nH.frozen = True
	m1.logpar.alpha = 1.0
	m1.logpar.beta = 1.0
	Fit.nIterations = 100
	Fit.statMethod = "chi"
	Fit.perform()
	Fit.show()

	# Plotting
	Plot.device = f"{opath}/logpar_plot.ps"
	Plot.xAxis = "keV"
	Plot.xLog = True
	Plot.yLog = True
	Plot("eeufspec","ratio")

	# Saving the spectrum data
	xVals = Plot.x()
	yVals = Plot.y()
	modVals = Plot.model()
	yErrs = Plot.yErr()
	dataM = np.column_stack((xVals, yVals, yErrs, modVals))
	np.savetxt(f"{opath}/logpar_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
	
	Xset.save(f"{opath}/logpar_model.xcm", info='m')
	Xset.closeLog()

	return





if __name__ == "__main__":

	file_path = "/home/student/GitHome/nicer-xspec/data"
	src_file = glob.glob(os.path.join(file_path, "*src.pha"))
	rmf_file = glob.glob(os.path.join(file_path, "*.rmf"))
	bkg_file = glob.glob(os.path.join(file_path, "*bkg.xcm"))
	out_path = file_path

	if src_file:
		src_file = src_file[0]
	else:
		print("The PHA file is not present in the given path. Check!")
	if rmf_file:
		rmf_file = rmf_file[0]
	else:
		print("The RMF file is not present in the given path. Check!")
	if bkg_file:
		bkg_file = bkg_file[0]
	else:
		print("The BKG file is not present in the given path. Check!")


	model_logpar(src_file, rmf_file, bkg_file, out_path)