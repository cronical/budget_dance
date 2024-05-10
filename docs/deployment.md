# Deployment

This is barely working.

Using python distribution manager with setuptools backend.

Invoke with `pdm build`.

This puts a wheel in `argus/budget-dance/dist`.

That can be installed.  Production is `~/budget-dance`.

Target must be prepped with `python -m venv .venv`.

In that folder, with the venv active use:

`pip3 install /Users/george/argus/budget-dance/dist/budget_dance-0.1.0-py3-none-any.whl`

The verion number above is 0.1.0 - that will change.

Add on ` --force_reinstall` if not the first time.

Configuration of the build is in `pyproject.toml` and `MANIFEST.in` in the project root. 

Data files seem to be only supported inside the package - maybe there is a way, but have not found it.

Two key data folders are `themes` and `docu`.  So are under `dance/`, and are listed in the manifest.  The file types have to be listed in `pyproject.toml`.

The documentation is built by `mkdocs build --no-directory-urls`.  That last bit is to support reading directly from the file system.

Needs a script to perform

`open .venv/lib/python3.11/site-packages/dance/docu/index.html`

The command lines which are *.py args in dev become scripts that are stored in

`~/.pyenv/shims/` but the `.py` is removed.




