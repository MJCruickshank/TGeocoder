# TGeocoder
Automated parsing and geocoding of Telegram news channels

## Description

Telegram has become one of the main platforms Open Source Intelligence (OSINT) researchers use to obtain primary information and breaking news. However, following a large number of channels is time-consuming, and extracting key information can be a tedious process. Moreover, the textual format of the data lacks a spatial component and thus is unsuitable for geographic analysis. TGeocoder leverages the Telegram API and OpenAI's GPT-4o LLM model to automatically parse large numbers of Telegram messages, and convert them into a machine-readable tabular format, wherein events within each message are summarised. It then extracts location data contained within the messages and finds the Lat/Lon coordinates of each event. Finally, each of these events is plotted on an interactive Folium map. 

## Getting Started

### Requirements

- **Python 3.13** 
- **conda**: The installation script that installs the dependencies needs to use both conda and pip to fetch the required dependencies, so please use conda and create a new conda virtual environment.
- **OpenAI**: You will need an OpenAI API Key for the script to run.
- **Telegram**: A Telegram API ID, API Hash, and telephone number are also required. 

### Installing Package Dependencies

1. Create the conda environment. This will install all necessary package dependencies too.

```shell
conda env create -f environment.yml
```

2. Activate the conda environment created.

```shell
conda activate tgeocoder
```
## To Run

### In Jupyter Notebook

1. Open the file titled `TGeocoder.ipynb`
2. Add your Telegram and OpenAI API information
3. Add the name of the Telegram channel you wish to parse, as well as the number of messages
4. Run the notebook
