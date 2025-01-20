from xspec import *
s1=Spectrum("data/ni6100110132mpu7_src.pha")
s1.response = "data/ni6100110132mpu7.rmf"
#s1.arf= "ni6100110111mpu7.arf"
s1.ignore("**-0.3,10.0-**") 
s1.background = "data/ni6100110132mpu7_bkg.xcm"
#grppha
#s1.group(20)
#ni6100110111mpu7_sr.pha
#chkey backfile ni6100110111mpu7_bg.pha
#chkey ancrfile ni6100110111mpu7.arf
#chkey respfile ni6100110111mpu7.rmf
m1 = Model ("tbabs*bknpower")
#Component objects are accessible-by-name as Model object attributes:
par1 = m1(1)
par2=m1(2)
par3=m1(3)
par4=m1(4)
par5=m1(5)
par1.values=0.0131
par2.values=1.0
par3.values=1.0
par1.frozen = True
Fit.nIterations = 100
Fit.statMethod = "chi"
Fit.perform()
Plot.device = "/xs"
#Xset.save("fitted_model2.xcm")
Plot.device = "spectrum_bkn.png"
#Plot("data")


Plot.xAxis = "keV"
Plot.yLog = True  # Correct
Plot.xLog = True
#Plot.xlim(0.2, 12)

#Plot("data")
#Plot("model")
Plot("eeufspec","ratio")
Plot.device = "/xs"


