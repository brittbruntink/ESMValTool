# ESMValTool
[![Documentation Status](https://readthedocs.org/projects/esmvaltool/badge/?version=version2_development)](https://esmvaltool.readthedocs.io/en/version2_development/?badge=version2_development)
[![DOIBadge](https://img.shields.io/badge/DOI-10.17874%2Fac8548f0315-blue.svg)](https://doi.org/10.17874/ac8548f0315)
[![Gitter](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/ESMValGroup?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![CircleCI](https://circleci.com/gh/ESMValGroup/ESMValTool.svg?style=svg)](https://circleci.com/gh/ESMValGroup/ESMValTool)
[![Codacy Coverage Badge](https://api.codacy.com/project/badge/Coverage/79bf6932c2e844eea15d0fb1ed7e415c)](https://www.codacy.com/app/ESMValGroup/ESMValTool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ESMValGroup/ESMValTool&amp;utm_campaign=Badge_Coverage)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/79bf6932c2e844eea15d0fb1ed7e415c)](https://www.codacy.com/app/ESMValGroup/ESMValTool?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=ESMValGroup/ESMValTool&amp;utm_campaign=Badge_Grade)
[![Docker Build Status](https://img.shields.io/docker/build/esmvalgroup/esmvaltool.svg)](https://hub.docker.com/r/esmvalgroup/esmvaltool/)
[![Anaconda-Server Badge](https://anaconda.org/esmvalgroup/esmvaltool/badges/installer/conda.svg)](https://conda.anaconda.org/esmvalgroup)


ESMValTool: A community diagnostic and performance metrics tool for routine evaluation of Earth system models in CMIP

## Developing
This is the development branch for version 2 of ESMValTool. To get started developing esmvaltool or developing/porting diagnostics, follow the instructions below. More detailed instructions can be found in the [manual](https://esmvaltool.readthedocs.io/en/version2_development/).

### Getting started
To install in development mode, follow these instructions.
- Install gcc, g++ and gfortran if these are not available on your system. On Debian based systems, this can be done by
running `apt install build-essential gfortran`.
- [Download and install conda](https://conda.io/projects/conda/en/latest/user-guide/install/linux.html) (this should be done even if the system in use already has a preinstalled version of conda, as problems have been reported with NCL when using such a version)
- If using (t)csh shell, do not prepend the installation path (`<prefix>`) to the environment variable PATH (as recommended by the installation procedure), but add `source <prefix>/etc/profile.d/conda.csh` to the `.cshrc`/`.tcshrc` file instead
- Update conda: `conda update -y conda`
- Create a conda environment: `conda create -y -n esmvaltool python=3`
- Activate the esmvaltool environment: `source activate esmvaltool` (or `conda activate esmvaltool` if using (t)csh shell)
- Clone the ESMValTool github repository: `git clone git@github.com:ESMValGroup/ESMValTool.git`
- Go to the esmvaltool directory: `cd ESMValTool`
- Check out the version 2 development branch: `git checkout version2_development`
- Update the esmvaltool conda environment `conda env update`
- Install in development mode: `pip install -e .[develop]` (or `pip install -e '.[develop]'` if using (t)csh shell). If you are installing behind a proxy that does not trust the usual pip-urls you can declare them with the option `--trusted-host`, e.g. `pip install --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org -e .[develop]`
- Test that your installation was succesful by running `esmvaltool -h`.
- Review `config-user.yml`. To customize for your system, create a copy, edit and use the command line option `-c` to instruct `esmvaltool` to use your custom configuration.
- Available recipes are located in the directory `esmvaltool/recipes`.

### Anaconda Package
The Anaconda packages can be found on [ESMValGroup Anaconda Channel.](https://anaconda.org/ESMValGroup)

First install gcc, g++ and gfortran if these are not available on your system. On Debian based systems, this can be done by
running `apt install build-essential gfortran`.

If you already installed Anaconda, you can install ESMValTool by running:
```
conda install -c esmvalgroup esmvaltool -c conda-forge -c birdhouse
```

### R support
If you haven't installed ESMValTool via Anaconda, one more step is required for R language support. You should run the command below to install R dependencies:
```
Rscript esmvaltool/install/R/setup.R
```
**This step is not needed if you install esmvaltool using anaconda.**

The dependencies of R diagostics should be added to `esmvaltool/install/R/r_requirements.txt` file.


### Julia support
If you haven't installed ESMValTool via Anaconda, you will also need to run the following to
the Julia dependencies: `./esmvaltool/install/Julia/setup.jl`.
The dependencies for Julia diagnostics should be added to `esmvaltool/install/Julia/julia_requirements.txt` file.


### Docker
ESMValTool Docker images automatically generated by Docker Hub. Run the command below to pull the most recent ESMValTool image.
```
docker pull esmvalgroup/esmvaltool
```
Example use:
```
[sudo] docker run -ti esmvalgroup/esmvaltool 
```


### Running tests
Go to the directory where the repository is cloned and run `./setup.py test`. Tests will also be run automatically by CircleCI.

### Code style
First go to the directory where the repository is cloned, e.g. `cd ESMValTool`.
- To review if your own code follows our coding standards, run `prospector esmvaltool/diag_scripts/your_diagnostic/your_script.py`.
- Run `./setup.py lint` to see the warnings about the code style of the entire project.

We use Codacy for monitoring (Python) code quality. However, running prospector locally will generally give you quicker and sometimes more accurate results. Note that Codacy does not install dependencies, so getting a warning "Unable to import 'external_library'" is probably not a real issue.   

### Building documentation
Go to the directory where the repository is cloned and run `./setup.py build_sphinx`
