# Summary of steps

1. Install libraries. See [Libraries](./libraries.md).
1. Prepare data files. See [Data Files](./data_files.md).
    1. Save certain reports from Moneydance to the `data` folder.
    1. Prepare other imput files as json or tsv
1. [Acquire a registration key](./configure_api.md/#api-key) for the bureau of labor statistics (for inflation data)
1. Edit the [configuration file](./configuration.md) as described below.
1. Validate the file against the schema.  I use VS Code extension `YAML Language Support by Red Hat`
1. Run `dance/util/build_book.py`.