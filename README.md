[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Naereen/StrapDown.js/graphs/commit-activity)
[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Documentation Status](https://readthedocs.org/projects/esmvaltool/badge/?version=latest)](https://esmvaltool.readthedocs.io/en/latest/?badge=latest)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3401363.svg)](https://doi.org/10.5281/zenodo.3401363)
[![Chat on Matrix](https://matrix.to/img/matrix-badge.svg)](https://matrix.to/#/#ESMValGroup_Lobby:gitter.im)
[![CircleCI](https://circleci.com/gh/ESMValGroup/ESMValTool/tree/main.svg?style=svg)](https://circleci.com/gh/ESMValGroup/ESMValTool/tree/main)
[![Test in Full Development Mode](https://github.com/ESMValGroup/ESMValTool/actions/workflows/test-development.yml/badge.svg)](https://github.com/ESMValGroup/ESMValTool/actions/workflows/test-development.yml)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/79bf6932c2e844eea15d0fb1ed7e415c)](https://app.codacy.com/gh/ESMValGroup/ESMValTool/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![Docker Build Status](https://img.shields.io/docker/automated/esmvalgroup/esmvaltool)](https://hub.docker.com/r/esmvalgroup/esmvaltool/)
[![Anaconda-Server Badge](https://img.shields.io/conda/vn/conda-forge/ESMValTool?color=blue&label=conda-forge&logo=conda-forge&logoColor=white)](https://anaconda.org/conda-forge/esmvaltool)
![stand with Ukraine](https://badgen.net/badge/stand%20with/UKRAINE/?color=0057B8&labelColor=FFD700)

![esmvaltoollogo](https://raw.githubusercontent.com/ESMValGroup/ESMValTool/main/doc/sphinx/source/figures/ESMValTool-logo-2-glow.png)

- [**Documentation**](https://docs.esmvaltool.org/en/latest/)
- [**ESMValTool Website**](https://www.esmvaltool.org/)
- [**ESMValTool Tutorial**](https://tutorial.esmvaltool.org/index.html)
- [**ESMValGroup Project on GitHub**](https://github.com/ESMValGroup)
- [**Gallery**](https://docs.esmvaltool.org/en/latest/gallery.html)
- [**`conda-forge` package feedstock**](https://github.com/conda-forge/esmvaltool-suite-feedstock)

# Introduction

ESMValTool is a community-developed climate model diagnostics and evaluation software package, driven
both by computational performance and scientific accuracy and reproducibility. ESMValTool is open to both
users and developers, encouraging open exchange of diagnostic source code and evaluation results from the
Coupled Model Intercomparison Project [CMIP](https://www.wcrp-climate.org/wgcm-cmip) ensemble. For a
comprehensive introduction to ESMValTool please visit our
[documentation](https://docs.esmvaltool.org/en/latest/introduction.html) page.

# Running esmvaltool

Diagnostics from ESMValTool are run using [recipe](https://docs.esmvaltool.org/en/latest/recipes/index.html)
files that contain pointers to the requested data types, directives for the preprocessing steps that data
will be subject to, and directives for the actual diagnostics that will be run with the now preprocessed data.
Data preprocessing is done via the [ESMValCore](https://docs.esmvaltool.org/projects/ESMValCore/en/latest/quickstart/index.html) package, a pure Python, highly-optimized scientific library, developed by the ESMValTool core developers,
and that performs a number of common analysis tasks
such as regridding, masking, levels extraction etc. [Diagnostics](https://docs.esmvaltool.org/en/latest/develop/diagnostic.html) are written in a variety of programming languages (Python, NCL, R, Julia) and are developed by the wider
scientific community, and included after a scientific and technical review process.

# Input data

ESMValTool can run with the following types of [data as input](https://docs.esmvaltool.org/en/latest/input.html):

- CMIP6
- CMIP5
- CMIP3
- [observational and re-analysis datasets](https://docs.esmvaltool.org/en/latest/input.html#supported-datasets-for-which-a-cmorizer-script-is-available)
- obs4MIPs
- ana4mips
- CORDEX ([work in progress](https://docs.esmvaltool.org/en/latest/input.html#cordex-note))

# Getting started

Please see [getting started](https://docs.esmvaltool.org/en/latest/quickstart/index.html) on our instance of Read the Docs as well as [ESMValTool tutorial](https://tutorial.esmvaltool.org/index.html). The tutorial is a set of lessons that together teach skills needed to work with ESMValTool in climate-related domains.

## Getting help

The easiest way to get help, if you cannot find the answer in the documentation in our [docs](https://docs.esmvaltool.org), is to open an [issue on GitHub](https://github.com/ESMValGroup/ESMValTool/issues).

## Contributing

If you would like to contribute a new diagnostic or feature, please have a look at our [contribution guidelines](https://docs.esmvaltool.org/en/latest/community/index.html).
