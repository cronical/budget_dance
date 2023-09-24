# Summary of steps

1. Prepare data files. See [Data Files](./data_files.md).
    1. Save certain reports from Moneydance to the `data` folder.
    1. Prepare other imput files as json or tsv
1. [Acquire a registration key](./setup_api.md/#api-key) for the bureau of labor statistics (for inflation data)
1. Edit the [control file](#the-setup-control-file) as described below.
1. Validate the file against the schema.  I use VS Code extension `YAML Language Support by Red Hat`
1. Run `dance/setup/create_wb.py`