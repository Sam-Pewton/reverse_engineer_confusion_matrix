# Reverse Engineer Confusion Matrix
Reverse Engineer confusion matrices from a variety of generated metrics.

## About the Project

This repository houses a project that will extract all possible confusion matrices that correspond to particular output metrics for a given dataset size.

The metrics that are available to use are:
* Accuracy (Mandatory)
* Sensitivity
* Specificity
* F1 Score
* Precision

Any confusion matrix that meets the specified requirements is saved and outputted to `./data/output.csv`. Please note that this file is overwritten on each run, if you would like to save the results generated, please copy and rename the file you wish to keep.

At present, this project will only work for binary classification.

## Getting Started

todo

### Prerequisites

* [Python 3.*](https://www.python.org/downloads/)
* [pandas](https://pandas.pydata.org/docs/getting_started/install.html)
* Text Editor/IDE

<p align="right">(<a href="#top">back to top</a>)</p>

### Installation

```sh
git clone https://github.com/Sam-Pewton/reverse_engineer_confusion_matrix
```

<p align="right">(<a href="#top">back to top</a>)</p>

### Usage

#### Python

IDE:
1. Open `./python/reverse_engineer.py` in your IDE
2. Modify lines 35:44 with your required parameters. If you do not wish to use an optional parameter, <b>set it to -1</b>.
3. Run the file. If any matches are made, the output is exported to `./data/output.csv`

Terminal:
1. Open `./python/reverse_engineer.py` in a text editor of your choice
2. Modify lines 35:44 with your required parameters. If you do not wish to use an optional parameter, <b>set it to -1</b>.
3. Open the terminal to the location of the file.
4. Execute `python reverse_engineer.py`. If any matches are made, the output is exported to `./data/output.csv`

<p align="right">(<a href="#top">back to top</a>)</p>

### Contributing
If you have a suggestion that would enhance this project, please fork the repo and create a pull request from your feature branch. 

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/your_new_feature`)
3. Commit your Changes (`git commit -m 'what you did and why'`)
4. Push to the Branch (`git push origin feature/your_new_feature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>
