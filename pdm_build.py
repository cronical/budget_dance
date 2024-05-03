from pathlib import Path
def pdm_build_update_files(context, files):
    # this puts the file in site-packages
    # but its there anyway under dance/util/build
    # problem is its not a good place for it.
    # it should be placed in the application folder
    extra_file_path = Path.home() / "argus/budget-dance/dance/util/build"
    files["build_book"] = extra_file_path  
