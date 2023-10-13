# xenon-gas-exchange-python

Gas exchange pipeline, developed at the [Driehuyslab](https://sites.duke.edu/driehuyslab/), processes raw MRI data and produce summary report to analyze the functionality of the human lung. The details of the workflow can be seen in the Wiki(see left menu bar)-- work in progress. This ReadMe presents the installation procedure of the pipeline. Before moving to the installation process, download or clone this repository in your computer.

## Table of contents:

1. [Setup](#setup)

2. [Installation](#installation)

3. [Execution](#execution)

4. [Acknowledgments](#acknowledgements)

## Setup

Gas exchange pipeline is a cross platform program that works on Windows, Mac and Linux system. At least 8GB of RAM is required to run this pipeline. Windows users can install Windows Subsystem for Linux (WSL) or install Ubuntu as dual boot/in the virtual box. The details of WSL installation can be seen in Section 1.1. Warning: run time in WSL can be slower compare to Linux or Mac system.

### 1.1. Windows Subsystem for Linux

Windows Subsystem for Linux installation process can seem overwhelming, espcially following the procedure in the microsoft [documentation](https://docs.microsoft.com/en-us/windows/wsl/install-win10). However a short Youtube video can make the install process much easier. One good example YouTube instruction can be seen [here](https://www.youtube.com/watch?v=X-DHaQLrBi8&t=385s&ab_channel=ProgrammingKnowledge2ProgrammingKnowledge2). Note: If the YouTube link is broken, please search in YouTube.

### 1.2. Xcode and Homebrew for Mac

First, open the terminal and install Xcode Command Line Tools using this command:

```bash
xcode-select --install
```

If homebrew is not already installed, it can be installed using this command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Don't forget to add homebrew to your path. Check if homebrew installed correctly, writing `which brew`. The details of homebrew can be seen [here](https://brew.sh/).

## Installation

This program is written in Python. Some of the code is written in C language. We will begin with Python installation.

### 2.1. Python Installation

First step of the installation process is to install python. This gas exchange pipeline works with Python 3.8.8 in its current version. In order to install necessary Python Libraries, Python 3.8.8 version is required. To create a virtual environment, a 'conda' distribution is required. If you don't have conda distribution installed into your machine, you can install one downloading 'Anaconda' or 'Miniconda'. You can download the 'Anaconda Distribution' from this [link](https://www.anaconda.com/products/individual), or 'Miniconda' from this [link](https://docs.conda.io/en/latest/miniconda.html). Here, command line installation procedure has been presented. So, Mac user can download the Command Line Installer.

#### 2.1.1. Conda Installation on Intel Based Mac or Linux systems:

Now, open the terminal. You need to write a command to install Anaconda/Miniconda. Command to install the Anaconda or Miniconda is:

```bash
bash ~/path/filename
```

Example: If your downloaded Anaconda file is in the "Downloads" folder and the file name is "Anaconda3-2020.11-Linux-x86_64.sh", write the following in the terminal:

```bash
bash ~/Downloads/Anaconda3-2020.11-Linux-x86_64.sh
```

Here, path = Downloads and filename = Anaconda3-2020.11-Linux-x86_64.sh

Press "enter" and reply "yes" to agree to the license agreements. After completing the installation process, close and reopen the terminal. You can verify if you have `conda` now by typing `which conda` in your terminal.

If you don't see 'conda' directory after verifing, you can review the details of [Anconda](https://docs.anaconda.com/anaconda/install/linux/) or [Miniconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/linux.html) installation.

#### 2.1.2. Conda Installation on Apple Silicon Based Mac systems:

For full use of this pipeline with Apple silicon based Mac systems, Conda should be installed with miniforge. Install miniforge using Homebrew using the following command:

```bash
brew install miniforge
```

More information on miniforge and alternative installation methods can be found at the [miniforge GitHub](https://github.com/conda-forge/miniforge).

#### 2.1.3. Conda Installtion on Windows Subsystem for Linux(WSL):

WSL users need to install `Anaconda` or 'Miniconda' for Linux inside the WSL shell. Change your current directory to where you have downloaded your Anaconda or Miniconda installation file (.sh file). Then run the:

```bash
bash filename
```

You can verify if you have `conda` now by typing `which conda` in your terminal.

### 2.2. Virtual Environment Creation and Python Package Installation

#### 2.2.1. Create Virtual Environment

To create a virtual environment using `conda` execute the command in the terminal:

```bash
conda create --name XeGas python=3.8.8
```

Here, XeGas is the the given name, but any name can be given.

To activate the environment, execute the command

```bash
conda activate XeGas
```

#### 2.2.2. Install Required Packages

We will be using pip to install the required packages. First update the pip using: pip install --upgrade pip

Now install a c compiler. Here we will install gcc compiler.

##### Linux and WSL users:

Get updates: sudo apt-get update

Install gcc executing this command: sudo apt install gcc

##### Mac Users:

If homebrew is not already installed, it can be installed using this command:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Don't forget to add homebrew to your path. Check if homebrew installed correctly, writing `which brew`. The details of homebrew can be seen [here](https://brew.sh/).

Now install gcc:

```bash
brew install gcc
```

##### Installing Packages in the Virtual Environment:

Now we are ready to install necessary packages. Packages must be installed inside the virtual conda environment. The list of packages are in the requirements.txt or requirements_ubuntu.txt file. These two files can be found in the setup folder of the main program directory. If in the terminal you are not in the main program directory, change the directory using cd command. To install the required packages, execute the command:

```bash
pip install -r setup/requirements.txt
```

To confirm that correct packages are installed, execute the command

```
pip list
```

and verify that the packages in the virtual environment agree with that in the `requirements.txt` file.

##### Install Packages in your Native Computer:

For Linux and WSL:

```
sudo apt install wkhtmltopdf
sudo apt install poppler-utils
```

For Mac:

```
brew install wkhtmltopdf
brew install poppler
```

### 2.3. Compilation and Download Necessary tools

#### 2.3.1. For Segmentation: Downloading the h5 models for machine learning

Check the `models/weights` folder if two `.h5` files are not available there, download `model_ANATOMY_UTE.h5` and `model_ANATOMY_VEN.h5` from this [link](https://drive.google.com/drive/folders/1gcwT14_6Tl_2zkLZ_MHsm-pAYHXWtVOA?usp=sharing) and place it in the `models/weights` folder in your main program directory.

#### 2.3.2. For Registration: Compiling ANTs

Compiling ANTs require to install git, cmake, g++, zlib. Following commands will install these packages.

#### Linux and Windows Subsystem For Linux(WSL) user: execute following commands on your terminal:

```bash
sudo apt-get -y install git
sudo apt-get -y install cmake
sudo apt install g++
sudo apt-get -y install zlib1g-dev
```

#### Mac User: check you have git, cmake, g++ writing, e.g. which git, which cmake

If you don't have any of these, you have to install in the command line.Now you can install packages writing following commands:

```bash
brew install git
brew install cmake
brew install g++
```

Now we are ready to perform SuperBuild. Execute the following commands on your terminal.

```bash
workingDir=${PWD}
git clone https://github.com/ANTsX/ANTs.git
mkdir build install
cd build
cmake \
    -DCMAKE_INSTALL_PREFIX=${workingDir}/install \
    ../ANTs 2>&1 | tee cmake.log
make -j 4 2>&1 | tee build.log
cd ANTS-build
make install 2>&1 | tee install.log
```

Warning: This might take a while.

After sucessful ANTs SuperBuild, you will have to copy 'antApplyTransforms', 'antsRegistration' and 'N4BisaFieldCorrection' files from the `install/bin`, and paste it to the main program directory. Now we are ready to process MRI scan of human lung.

Note: If necesary, the details of ANTs Compilation can be seen [here](https://github.com/ANTsX/ANTs/wiki/Compiling-ANTs-on-Linux-and-Mac-OS)

## Execution

To process raw MRI data, you can follow the Team Xenon workflow outlined below. Note: Wiki presents the code structure and workflow of this pipeline -- work-in-progress.

### 3.1. General usage

#### 3.1.1 Config files
All subject information and processing parameters are specified in a subject-specific configuration file. Default configuration settings are defined in `config/base_config.py`. The defaults are inhereted by subject-specific config files, unless overriden.
<br />
<br />`config/demo_config_basic.py` shows examples of basic config settings that you will usually want to change for each subject scan.

- `data_dir`: Directory containing dixon, ute, and (optionally) calibration scan files or .mat file. This is where output files will be saved.
- `subject_id`: Subject ID number that will be used to label output files
- `site`: Site of data acquisition
- `rbc_m_ratio`: RBC to membrane signal ratio for Dixon decomposition. If not set in config file, a calibartion scan file is required from which the ratio will be calculated.
- `segmentation_key`: Defines what kind of segmentation to use. Typically set to CNN_VENT for automatic segmentation of the gas image or MANUAL_VENT for manual segmentation of the gas image.
- `manual_seg_filepath`: Path of manual segmentation file, if MANUAL_VENT is chosen.

`config/demo_config_advanced.py` shows examples of advanced config settings that may commonly be modified for more specific cases. See `config/base_config.py` for all config settings that can be modified.

#### 3.1.2 Processing a subject

First, copy one of the demo config files or the base_config file, rename it, and modify configuration settings. In terminal, navigate to the main pipeline directory and activate the virtual environment you set up earlier:

```bash
conda activate XeGas
```

#### Running full pipeline with image reconstruction

Run the full pipeline with:
```bash
python main.py --config [path-to-config-file]
```

#### Running previously processed subject scan from .mat file

If a subject scan has already been processed through the pipeline and you wish to reprocess the previously constructed images, you can run the pipeline on the subject's .mat file with:

```bash
python main.py --config [path-to-config-file] --force_readin
```

NOTE: 

### 3.2. Team Xenon Worflow for Duke Data Processing

Warning: this is the Team Xenon workflow only. Other users do not have to follow the exact procedures.

1. Create a new subject folder. This will typically have the format of `###-###` or `###-###X`.

2. Then log onto the `smb://duhsnas-pri/xenon_MRI_raw/` drive and enter the directory of interest corresponding to the recently scanned subject. Copy the files on your computer. Determine how many dixon scans are there (usually 1 or 2). If there is only 1, create a subfolder named `###-###` in your new subject folder and copy all twix files(should be at least three files: dixon, calibration, and BHUTE) into that subfolder.(NOTE: scan can be processed using only one dixon scan. In that case, only one dixon should be in the subfolder) If there are 2 dixons, create subfolders `###-###_s1` (for the first dixon scan) and `###-###_s2`(for the second dixon scan) and copy the twix files corresponding to the first dixon (cali, dixon, ute, and optionally dedicated ventilation) and copy the twix files corresponding the second dixon (cali, dixon, ute) into the other.

3. Process the spectroscopy using the MATLAB spectroscopy pipeline first. Instructions are on the repository ("Spectroscopy_Processing_Production").

4. Before running the gas exchange pipline, make sure you have the latest updates. You can do this by

   ```
   git pull
   ```

5. Create a new config file titled "[subject_id].py" in lower case by copying one of the demo config files. Then, edit the parameters like subject id and rbc/m ratio and save it. Run the pipeline.

6. Copy all the contents in the subject folder and paste it into `smb://duhsnas-pri/duhs_radiology/Private/TeamXenon/01_ClinicalOutput/Processed_Subjects`

7. Upload `.pdf` reports to Slack

## Acknowledgements:

Original Author: Ziyi Wang

Developers: Ziyi Wang, Junlan Lu, Sakib Kabir, David Mummy, Suphachart Leewiwatwong, and Isabelle Dummer.

Correspondence: David Mummy: david.mummy@duke.edu
