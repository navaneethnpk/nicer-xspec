from xspec import *
s1=Spectrum("data/ni6100110132mpu7_src.pha")
s1.response = "data/ni6100110132mpu7.rmf"
#s1.arf= "ni6100110111mpu7.arf"
s1.ignore("**-0.3,10.0-**") 
s1.background = "data/ni6100110132mpu7_bkg.xcm"
m1 = Model("tbabs*po")
# Component objects are accessible-by-name as Model object attributes:
par1 = m1(1)
par2=m1(2)
par3=m1(3)
par1.values=0.0131
par2.values=1.0
par3.values=1.0
par1.frozen = True
Fit.nIterations = 100
Fit.statMethod = "chi"
Fit.perform()
Plot.device = "/xs"
#Xset.save("fitted_model1.xcm")
Plot.device = "spectrum_po.png"


#Plot("data")

Plot.xAxis = "keV"
Plot.yLog = True  # Correct
Plot.xLog = True


#Plot("data")
#Plot("model")
Plot("eeufspec","ratio")
#Plot("data","model","resid")
Plot.device = "/xs"

