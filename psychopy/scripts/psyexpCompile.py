#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2018 Jonathan Peirce
# Distributed under the terms of the GNU General Public License (GPL).

import argparse
import codecs

# parse args for subprocess
parser = argparse.ArgumentParser(description='Compile your python file from here')
parser.add_argument('infile', help='The input (psyexp) file to be compiled')
parser.add_argument('--version', '-v', help='The PsychoPy version to use for compiling the script. e.g. 1.84.1')
parser.add_argument('--outfile', '-o', help='The output (py) file to be generated (defaults to the ')


def compileScript(infile=None, version=None, outfile=None):
    """
    This function will compile either Python or JS PsychoPy script from .psyexp file.

    Paramaters
    ----------

    infile: string, experiment.Experiment object
        The input (psyexp) file to be compiled
    version: str
        The PsychoPy version to use for compiling the script. e.g. 1.84.1.
        Warning: Cannot set version if module imported. Set version from
        command line interface only.
    outfile: string
        The output file to be generated (defaults to Python script.
    """

    def _setVersion(version):
        """
        Sets the version to be used for compiling using the useVersion function

        Parameters
        ----------
        version: string
            The version requested
        """

        # Set version
        if version:
            from psychopy import useVersion
            useVersion(version)

        from psychopy import logging

        if __name__ != '__main__' and version not in [None, 'None', 'none', '']:
            version = None
            msg = "You cannot set version by calling compileScript() manually. Setting 'version' to None."
            logging.warning(msg)

        return version

    def _getExperiment(infile, version):
        """

        Parameters
        ----------
        infile: string, experiment.Experiment object
            The input (psyexp) file to be compiled
        version: string
            The version requested
        Returns
        -------
        experiment.Experiment
            The experiment object used for generating the experiment script

        """

        # import PsychoPy experiment and write script with useVersion active
        from psychopy.app.builder import experiment
        # Check infile type
        if isinstance(infile, experiment.Experiment):
            thisExp = infile
        else:
            thisExp = experiment.Experiment()
            thisExp.loadFromXML(infile)
            thisExp.psychopyVersion = version

        return thisExp

    def _setTarget(outfile):
        """

        Parameters
        ----------
        outfile : string
             The output file to be generated (defaults to Python script).
        Returns
        -------
        string
            The Python or JavaScript target type
        """

        # Set output type, either JS or Python
        if outfile.endswith(".js"):
            targetOutput = "PsychoJS"
        else:
            targetOutput = "PsychoPy"

        return targetOutput

    def _makeTarget(thisExp, outfile, targetOutput):
        """
        This function generates the actual scripts for Python and/or JS
        Parameters
        ----------
        thisExp : experiment.Experiment object
            The current experiment created under requested version
        outfile : string
             The output file to be generated (defaults to Python script).
        targetOutput : string
            The Python or JavaScript target type
        """

        # Write script
        if targetOutput == "PsychoJS":
            try:
                # Write module JS code
                script = thisExp.writeScript(outfile, target=targetOutput, modular=True)
                # Write no module JS code
                outfileNoModule = outfile.replace('.js', 'NoModule.js')  # For no JS module script
                scriptNoModule = thisExp.writeScript(outfileNoModule, target=targetOutput, modular=False)
                # Store scripts in list
                scriptDict = {'outfile': script, 'outfileNoModule': scriptNoModule}
            except TypeError as err:
                msg = ("You cannot compile JavaScript experiments with this version of PsychoPy.\n"
                       "Please use version 3.0.0 or higher")
                raise Exception("{}: {}".format(err, msg))
        else:
            script = thisExp.writeScript(outfile, target=targetOutput)
            scriptDict = {'outfile': script}

        # Output script to file
        for scripts in scriptDict:
            if not type(scriptDict[scripts]) in (str, type(u'')):  # Compile buffer object called using subprocess
                with codecs.open(eval(scripts), 'w', 'utf-8') as f:
                    f.write(scriptDict[scripts].getvalue())
                f.close()
            else:  # Compile using string object called from script, where version is None
                with codecs.open(eval(scripts), 'w', 'utf-8') as f:
                    f.write(scriptDict[scripts])
                f.close()

    ###### Write script #####
    version = _setVersion(version)
    thisExp = _getExperiment(infile, version)
    targetOutput = _setTarget(outfile)
    _makeTarget(thisExp, outfile, targetOutput)

if __name__ == "__main__":
    # define args
    args = parser.parse_args()
    if args.outfile is None:
        args.outfile = args.infile.replace(".psyexp", ".py")
    compileScript(args.infile, args.version, args.outfile)
