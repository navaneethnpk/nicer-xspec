def run_xspec_analysis(pha, rmf, bkg, opath, model_name, model_params):
    """
    General XSPEC analysis function for any model.

    Args:
        pha (str): Path to the PHA file (spectrum data).
        rmf (str): Path to the RMF file (response matrix).
        bkg (str): Path to the BKG file (background).
        opath (str): Output directory for saving results.
        model_name (str): The name of the XSPEC model (e.g., 'logpar', 'powerlaw', 'bknpower').
        model_params (dict): The parameters for the model (e.g., alpha, beta for logpar).

    Returns:
        bool: True if the analysis completes successfully, False otherwise.
    """
    try:
        ch = Xset.chatter
        Xset.chatter = 0
        lch = Xset.logChatter
        Xset.logChatter = 20
        logFile = Xset.openLog(f"{opath}/{model_name}_xspec.log")
        logFile = Xset.log

        s1 = Spectrum(pha)
        s1.response = rmf
        s1.background = bkg
        AllData.ignore("bad")
        s1.ignore("**-0.3,10.0-**")

        # Set up model based on model_name and model_params
        if model_name == "logpar":
            m1 = Model("tbabs*logpar")
            m1.TBabs.nH = 0.0131
            m1.TBabs.nH.frozen = True
            m1.logpar.alpha = model_params['alpha']
            m1.logpar.beta = model_params['beta']
        elif model_name == "powerlaw":
            m1 = Model("tbabs*powerlaw")
            m1.TBabs.nH = 0.0131
            m1.TBabs.nH.frozen = True
            m1.powerlaw.PhoIndex = model_params['PhoIndex']
        elif model_name == "bknpower":
            m1 = Model("tbabs*bknpower")
            m1.TBabs.nH = 0.0131
            m1.TBabs.nH.frozen = True
            m1.bknpower.PhoIndx1 = model_params['PhoIndx1']
            m1.bknpower.PhoIndx2 = model_params['PhoIndx2']
            m1.bknpower.BreakE = model_params['BreakE']
        else:
            raise ValueError(f"Unknown model: {model_name}")

        # Perform fitting
        Fit.nIterations = 100
        Fit.statMethod = "chi"
        Fit.perform()
        Fit.show()

        # Plotting
        Plot.device = f"{opath}/{model_name}_plot.ps"
        Plot.xAxis = "keV"
        Plot.xLog = True
        Plot.yLog = True
        Plot("eeufspec", "ratio")

        # Save plots and data
        Plot.device = "/null"
        Plot("eeufspec")
        xVals = Plot.x()
        yVals = Plot.y()
        modVals = Plot.model()
        yErrs = Plot.yErr()
        dataM = np.column_stack((xVals, yVals, yErrs, modVals))
        np.savetxt(f"{opath}/{model_name}_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")

        Plot("ratio")
        xVals = Plot.x()
        yVals = Plot.y()
        yErrs = Plot.yErr()
        dataR = np.column_stack((xVals, yVals, yErrs))
        np.savetxt(f"{opath}/{model_name}_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

        Xset.save(f"{opath}/{model_name}_model.xcm", info='m')
        AllData.clear()
        Xset.closeLog()

        return True
    except Exception as e:
        print(f"> Error: An error in Xspec analysis: {e}")
        return False

# Example of how you can call the function for each model:

# For logpar model:
logpar_params = {'alpha': 1.0, 'beta': 1.0}
run_xspec_analysis(pha="spectrum.pha", rmf="response.rmf", bkg="background.bkg", opath="output", model_name="logpar", model_params=logpar_params)

# For powerlaw model:
plaw_params = {'PhoIndex': 1.0}
run_xspec_analysis(pha="spectrum.pha", rmf="response.rmf", bkg="background.bkg", opath="output", model_name="powerlaw", model_params=plaw_params)

# For bknpower model:
bknpl_params = {'PhoIndx1': 1.0, 'PhoIndx2': 1.0, 'BreakE': 1000}
run_xspec_analysis(pha="spectrum.pha", rmf="response.rmf", bkg="background.bkg", opath="output", model_name="bknpower", model_params=bknpl_params)
