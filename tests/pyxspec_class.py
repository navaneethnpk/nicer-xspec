from xspec import *

class XspecAnalysis:
	def __init__(self, pha, rmf, bkg, path, model, params):
		self.pha = pha
		self.rmf = rmf
		self.bkg = bkg
		self.path = path
		self.model = model
		self.params = params
		self.mname = self.model.replace('*', '_')

	def _setup_logging(self):
		"""
		Set up logging for the Xspec analysis.
		"""
		ch = Xset.chatter
		Xset.chatter = 20
		lch = Xset.logChatter
		Xset.logChatter = 20
		logFile = Xset.openLog(f"{self.path}/{self.mname}_xspec.log")
		logFile = Xset.log

	def _load_data(self):
		"""
		Load spectrum, response, and background files.
		"""
		spec = Spectrum(self.pha)
		spec.response = self.rmf
		spec.background = self.bkg
		spec.ignore("**-0.3,10.0-**")
		AllData.ignore("bad")

	def _load_model(self):
		"""
		Define the model and set its parameters.
		"""
		model = Model(self.model)
		for comp, comp_params in self.params.items():
			print(comp, comp_params)


	def run_xspec(self):
		self._setup_logging()
		self._load_data()
		# self._load_model()


		AllData.clear()
		Xset.closeLog()

from src.xspec import XspecAnalysis

src_file = "/home/student/GitHome/nicer-xspec/data/6100110132/ni6100110132mpu7_sr.pha"
rmf_file = "/home/student/GitHome/nicer-xspec/data/6100110132/ni6100110132mpu7.rmf"
bkg_file = "/home/student/GitHome/nicer-xspec/data/6100110132/ni6100110132mpu7_bg.xcm"

out_path = "/home/student/Testarea/2503_nicer_test"

model_params = {
	"TBabs": {
		"nH": {"value": 0.0131, "frozen": True},
	},
	"logpar": {
		"alpha": {"value": 1.0, "frozen": False},
		"beta": {"value": 1.0, "frozen": False},
	}
}


analysis = XspecAnalysis(pha=src_file, rmf=rmf_file, bkg=bkg_file, path=out_path, model="TBabs*logpar", params=model_params)
analysis.run_xspec()

