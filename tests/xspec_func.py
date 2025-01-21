def run_xspec_analysis(pha, rmf, bkg, opath, model_str, params, plot_filename, model_filename):
    """
    Performs Xspec analysis for a given model, logs the fitting process, generates plots, and saves results.
    
    Args:
        pha (str): The path to the PHA file, which contains the spectrum data.
        rmf (str): The path to the RMF file used for spectral response calibration.
        bkg (str): The path to the BKG (Background File) used to model the background spectrum.
        opath (str): The directory where the output files will be saved.
        model_str (str): The Xspec model string to be used.
        params (dict): A dictionary containing the parameters to set for the model.
        plot_filename (str): The filename for saving the plot.
        model_filename (str): The filename for saving the model.

    Returns:
        bool: True if the function completes successfully, False otherwise.
    """
    try:
        # Xspec output logging setup
        ch = Xset.chatter
        Xset.chatter = 0
        lch = Xset.logChatter
        Xset.logChatter = 20
        logFile = Xset.openLog(f"{opath}/{plot_filename}_xspec.log")
        logFile = Xset.log

        # Loading spectrum, response, and background files
        s1 = Spectrum(pha)
        s1.response = rmf
        s1.background = bkg
        AllData.ignore("bad")
        s1.ignore("**-0.3,10.0-**")

        # Define model and its parameters
        model = Model(model_str)
        for param, value in params.items():
            getattr(model, param).value = value
            getattr(model, param).frozen = True  # Freeze the parameter if needed

        # Fitting process
        Fit.nIterations = 100
        Fit.statMethod = "chi"
        Fit.perform()
        Fit.show()

        # Plotting
        Plot.device = f"{opath}/{plot_filename}_plot.ps"
        Plot.xAxis = "keV"
        Plot.xLog = True
        Plot.yLog = True
        Plot("eeufspec", "ratio")

        # Save spectrum and ratio data
        Plot.device = "/null"
        Plot("eeufspec")
        xVals = Plot.x()
        yVals = Plot.y()
        modVals = Plot.model()
        yErrs = Plot.yErr()
        dataM = np.column_stack((xVals, yVals, yErrs, modVals))
        np.savetxt(f"{opath}/{plot_filename}_spec.csv", dataM, delimiter=",", header="xVals,yVals,yErrs,modVals", comments="")
        
        Plot("ratio")
        xVals = Plot.x()
        yVals = Plot.y()
        yErrs = Plot.yErr()
        dataR = np.column_stack((xVals, yVals, yErrs))
        np.savetxt(f"{opath}/{plot_filename}_ratio.csv", dataR, delimiter=",", header="xVals,yVals,yErrs", comments="")

        # Save the model
        Xset.save(f"{opath}/{model_filename}_model.xcm", info='m')

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
    return run_xspec_analysis(pha, rmf, bkg, opath, "tbabs*logpar", params, "logpar", "logpar")


def model_powerlaw(pha, rmf, bkg, opath):
    params = {
        "TBabs.nH": 0.0131,
        "powerlaw.PhoIndex": 1.0
    }
    return run_xspec_analysis(pha, rmf, bkg, opath, "tbabs*powerlaw", params, "plaw", "plaw")


def model_bknpowerlaw(pha, rmf, bkg, opath):
    params = {
        "TBabs.nH": 0.0131,
        "bknpower.PhoIndx1": 1.0,
        "bknpower.PhoIndx2": 1.0
    }
    return run_xspec_analysis(pha, rmf, bkg, opath, "tbabs*bknpower", params, "bknpl", "bknpl")
