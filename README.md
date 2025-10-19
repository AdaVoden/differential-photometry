# shutterbug

Built to find candidates for stars with varying brightness in an arbitrary star field. Shutterbug can load any `.xlsx` or `.csv` file given that the files have the requisite headers and are formatted properly. 

### Installation

To install, you need a version of `Poetry`. This makes the installation commands:

```bash
pip install poetry
poetry install
```

At this point Shutterbug is installed and ready for use.

### Usage

Basic usage of Shutterbug is loading datasets to process and outputting graphs as a result

```bash
shutterbug -f name.csv -o path/to/dir
```

At which point it will begin processing your csv or csvs.