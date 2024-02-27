Setup Guide
===========

*rtd-code-python requires Python 3 or higher. For best results, use Python 3.11.3*

General Setup
-------------

1. Clone the repository and open a terminal in the root directory
2. Install *virtualenv* with ``py -m pip install virtualenv``
3. Create a new Virtual Environment with ``py -m venv rtd_venv``
4. Activate the Virtual Environment with ``rtd_venv\scripts\activate``
5. Install *rtd-code-python* and its dependencies with ``py -m pip install -r requirements.txt``
6. Optionally, open a terminal inside ``scripts\demos`` and run the demo scripts

(Alternative) Conda Quickstart
------------------------------

Another way to setup rtd-code-python is through the creation and use of a conda environment.
In your desired folder, run the following commands to get a conda environment called ``rtd-code`` setup

.. code-block:: bash

    # Create conda environment and install python 3.11.3 & pytorch 2.0.1
    # Adjust the torch packages according to your system
    conda create -n rtd-code python==3.11.3 pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia
    conda activate rtd-code

    # Clone zonopy dependencies and RTD-Code, and install
    git clone git@github.com:roahmlab/zonopy.git
    git clone git@github.com:roahmlab/zonopy-robots.git
    git clone git@github.com:roahmlab/rtd-code-python.git
    pip install -r rtd-code-python/requirements.txt -e zonopy/ -e zonopy-robots/ -e rtd-code-python/


Obtaining URDFs
---------------

To obtain the URDFs used in the demos, please visit the `ARMOUR <https://github.com/roahmlab/armour>`_ repository and download the ``urdfs`` folder.
Place the ``urdfs`` folder in the parent directory of the rtd-code-python repository in order to run ``scripts\demos\planner_demo.py``.
