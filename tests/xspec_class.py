class XspecAnalysis:
    def __init__(self, pha, rmf, bkg, opath, model_str, params, plot_filename, model_filename):
        """
        Initializes the Xspec analysis with necessary parameters.
        """
        self.pha = pha
        self.rmf = rmf
        self.bkg = bkg
        self.opath = opath
        self.model_str = model_str
        self.params = params
        self.plot_filename = plot_filename
        self.model_filename = model_filename

    def _setup_logging(self):
        """
        Set up logging for the Xspec analysis.
        """
        ch = Xset.chatter
        Xset.chatter = 0
        lch = Xset.logChatter
        Xset.logChatter = 20
        logFile = Xset.openLog(f"{self.opath}/{self.plot_filename}_xspec.log")
        logFile = Xset.log

    def _load_data(self):
        """
        Load spectrum, response, and background files.
        """
        s1 = Spectrum(self.pha)
        s1.response = self.rmf
        s1.background = self.bkg
        AllData.ignore("bad")
        s1.ignore("**-0.3,10.0-**")
        return s1

    def _define_model(self):
        """
        Define the model and set its parameters.
        """
        model = Model(self.model_str)
        for param, value in self.params.items():
            getattr(model, param).value = value
            getattr(model, param).frozen = True  # Freeze the parameter if needed
        return model

    def _fit_model(self):
        """
        Perform the fitting procedure.
        """
        Fit.nIterations = 100
        Fit.statMethod = "chi"
        Fit.perform()
        Fit.show()

    def _generate_plots(self):
        """
        Generate and save the plots.
        """
        Plot.device = f"{self.opath}/{self.plot_filename}_plot.ps"
        Plot.xAxis = "keV"
        Plot.xLog = True
        Plot.yLog = True
        Plot("eeufspec", "ratio")

        Plot.device = "/null"
        Plot("eeufspec")
        xVals = Plot.x()
        yVals = Plot.y()
        modVals = Plot.model()
        yErrs = Plot.yErr()
        dataM = np.column_stack((xVals, yVals, yErrs, modVals))
        np.savetxt(f"{self.opath}/{self.plot_filename}_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
        
        Plot("ratio")
        xVals = Plot.x()
        yVals = Plot.y()
        yErrs = Plot.yErr()
        dataR = np.column_stack((xVals, yVals, yErrs))
        np.savetxt(f"{self.opath}/{self.plot_filename}_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

    def _save_model(self):
        """
        Save the model configuration.
        """
        Xset.save(f"{self.opath}/{self.model_filename}_model.xcm", info='m')

    def analyze(self):
        """
        Run the entire Xspec analysis process: setup, fit, plot, and save.
        """
        try:
            # Logging setup
            self._setup_logging()

            # Load data
            s1 = self._load_data()

            # Define the model and fit it
            model = self._define_model()
            self._fit_model()

            # Generate and save plots
            self._generate_plots()

            # Save the model configuration
            self._save_model()

            # Clear data and close log
            AllData.clear()
            Xset.closeLog()

            return True

        except Exception as e:
            print(f"> Error: An error in Xspec analysis: {e}")
            return False

# Specific models
def model_logpar(pha, rmf, bkg, opath):
    params = {
        "TBabs.nH": 0.0131,
        "logpar.alpha": 1.0,
        "logpar.beta": 1.0
    }
    analysis = XspecAnalysis(pha, rmf, bkg, opath, "tbabs*logpar", params, "logpar", "logpar")
    return analysis.analyze()


def model_powerlaw(pha, rmf, bkg, opath):
    params = {
        "TBabs.nH": 0.0131,
        "powerlaw.PhoIndex": 1.0
    }
    analysis = XspecAnalysis(pha, rmf, bkg, opath, "tbabs*powerlaw", params, "plaw", "plaw")
    return analysis.analyze()


def model_bknpowerlaw(pha, rmf, bkg, opath):
    params = {
        "TBabs.nH": 0.0131,
        "bknpower.PhoIndx1": 1.0,
        "bknpower.PhoIndx2": 1.0
    }
    analysis = XspecAnalysis(pha, rmf, bkg, opath, "tbabs*bknpower", params, "bknpl", "bknpl")
    return analysis.analyze()
