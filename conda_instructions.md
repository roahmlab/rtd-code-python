# Conda Quickstart commands

In your desired folder, run the following commands to get a conda environment called `rtd-code` setup.

```bash
# Create conda environment and install python 3.11.3 & pytorch 2.0.1
conda create -n rtd-code python==3.11.3 pytorch==2.0.1 torchvision==0.15.2 torchaudio==2.0.2 pytorch-cuda=11.8 -c pytorch -c nvidia
conda activate rtd-code

# Clone zonopy dependencies and RTD-Code, and install
git clone git@github.com:roahmlab/zonopy.git
git clone git@github.com:roahmlab/zonopy-robots.git
git clone git@github.com:roahmlab/rtd-code-python.git
pip install -r rtd-code-python/requirements.txt -e zonopy/ -e zonopy-robots/ -e rtd-code-python/
```
