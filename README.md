# ZkFlowParser

ZkFlowParser is a Python script to extract information from [ZkFlow](https://byfishh.github.io/zk-flow/) website for a list of addresses and save results in Excel.

## Prerequisites

Ensure you have the following dependencies installed for ZkFlowParser:

- Python 3.x
- pandas
- selenium
- openpyxl

You can install the required packages using pip:

`$ pip install pandas selenium openpyxl`

Ensure Google Chrome browser is installed as ZkFlowParser relies on the Chrome web driver for automated web browsing.

## Usage

To use ZkFlowParser, follow these steps:

1. Create a text file with the addresses you want to process.

2. Run the script: `$ python ZkFlowParser.py [input_file] [output_file]`

3. Results will be saved in the specified output Excel file.