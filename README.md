# Shutterbug

Built to find candidates for stars with varying brightness in an arbitrary star field. Shutterbug can load any `.xlsx` or `.csv` file given that the files have the requisite headers and are formatted properly. 

## Prerequisites

- Python 3.13 or higher
- Astronomical data from Mirax64 that you wish to process, in either .csv or .xlsx form

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/AdaVoden/differential-photometry.git
    ```
2. **Install dependencies**

    ```bash
    pip install poetry
    poetry install
    ```
At this point Shutterbug is installed and ready for use.


## Usage

Basic usage of Shutterbug is loading datasets to process and outputting graphs as a result:

```bash
shutterbug --data-file name.csv
```

At which point it will begin processing your csv.

If you wish to load the GUI version, use the command

```bash
shutterbug-gui
```

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests

## License

MIT