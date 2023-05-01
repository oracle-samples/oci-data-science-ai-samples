import glob
import json
import os
from collections import Counter
from datetime import datetime

import nbformat as nbf
from tqdm import tqdm


def parse_bibblock(input: str) -> dict:
    """Parse the adsbib format into a dictionary. On error return an empty dict"""

    # Set valid prefix and return if string does not start with it.
    prefix = "@notebook"
    input = input.strip("\n\t ")
    if not input.startswith(prefix):
        raise ValueError(f"Missing {prefix} prefix in {input}")

    # Strip out the field/value strings
    input = input[len(prefix) :].strip("{}")
    field_value_list = [l.strip(",\t") for l in input.split("\n") if len(l) > 0]
    if len(field_value_list) == 0:
        return {}

    # Get the filename and then the field/value pairs
    results = {"filename": field_value_list[0].strip(",")}
    for item in field_value_list[1:]:
        if ":" not in item:
            raise ValueError(f"Unable to parse: {item}")
        else:
            field, value = item.split(":", 1)

        results[field.strip(" ")] = value.strip(" ")

    if "keywords" in results:
        results["keywords"] = [
            k.strip() for k in results["keywords"].split(",") if len(k.strip()) > 0
        ]

    must_have = ["filename", "title", "summary", "developed_on", "keywords", "license"]

    # assert all the must_have fields are present in the results dictionary
    assert set(must_have).issubset(
        set(results.keys())
    ), f"Missing fields in {results['filename']}: {set(must_have) - set(results.keys())}"

    assert len(results["keywords"]), f"Must have at least one keyword"

    # change all dict keys to be snake case with no spaces

    return {k.replace(" ", "_"): v for k, v in results.items()}


def escape_underscore(str: str) -> str:
    return str.replace("_", "\_")


def find_git_last_commit_time_in_iso_str_format(file_name):
    all_git_controlled_files = os.popen("git ls-files").read().strip().split("\n")
    if file_name in all_git_controlled_files:
        cmd = f'git log --pretty=format:%cd -n 1 --date=unix --date-order -- "{file_name}"'
        time_string = os.popen(cmd).read()
        assert (
            time_string.strip() != ""
        ), f"Unable to get git timestamp for {file_name}, this can happen when you `rm` a notebook locally, rather than using `git rm`"
        return datetime.fromtimestamp(float(time_string.strip())).isoformat()
    else:
        return datetime.now().isoformat()


def make_readme_and_index():
    """produce a README file along with an index.json file used by the notebook explorer"""

    README_FILE = "README.md"
    INDEX_FILE = "index.json"

    def parse_notebook_metadata(nb):
        """Returns None if none of the raw cells contain a bib block, otherwise returns an unvalidated notebook bib block"""

        for cell in nb.cells:
            if cell.cell_type == "raw":
                try:
                    return parse_bibblock(cell["source"])
                except ValueError:
                    continue

        return None

    all_notebooks = {}
    ignored_notebooks = []

    files = glob.glob("[!_]*.ipynb")
    files.sort(key=os.path.getmtime)

    print("Parsing notebooks...")
    for notebook_file in tqdm(files, leave=True):
        if notebook_file == "getting_started.ipynb":
            continue

        notebook_metadata = parse_notebook_metadata(
            nbf.read(notebook_file, nbf.NO_CONVERT)
        )
        if notebook_metadata:

            assert (
                notebook_file == notebook_metadata["filename"]
            ), f"Notebook filename [{notebook_file}] does not match [{notebook_metadata.get('filename')}]"

            # augment with file system meta data
            # notebook_metadata["time_created"] = datetime.fromtimestamp(
            #     os.path.getmtime(notebook_file)
            # ).isoformat()
            notebook_metadata[
                "time_created"
            ] = find_git_last_commit_time_in_iso_str_format(notebook_file)
            notebook_metadata["size"] = os.path.getsize(notebook_file)

            all_notebooks[notebook_file] = notebook_metadata
        else:
            ignored_notebooks.append(notebook_file)

    with open(README_FILE, "w") as f:

        print(
            """
ADS Expertise Notebooks
=======================

The [Accelerated Data Science (ADS) SDK](https://accelerated-data-science.readthedocs.io/en/latest/) is maintained by the Oracle Cloud Infrastructure Data Science service team. It speeds up common data science activities by providing tools that automate and/or simplify common data science tasks, along with providing a data scientist friendly pythonic interface to Oracle Cloud Infrastructure (OCI) services, most notably OCI Data Science, Data Flow, Object Storage, and the Autonomous Database. ADS gives you an interface to manage the lifecycle of machine learning models, from data acquisition to model evaluation, interpretation, and model deployment.

The ADS SDK can be downloaded from [PyPi](https://pypi.org/project/oracle-ads/), contributions welcome on [GitHub](https://github.com/oracle/accelerated-data-science)

[![PyPI](https://img.shields.io/pypi/v/oracle-ads.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/oracle-ads/) [![Python](https://img.shields.io/pypi/pyversions/oracle-ads.svg?style=for-the-badge&logo=pypi&logoColor=white)](https://pypi.org/project/oracle-ads/)

    """,
            file=f,
        )

        # badges for the tags https://img.shields.io/badge/tensorflow-3-brightgreen?style=for-the-badge&logo=pypi&logoColor=white

        tags = Counter([])
        for _, notebook_metadata in all_notebooks.items():
            tags.update(notebook_metadata["keywords"])

        print("\n\n## Topics", file=f)
        for tag_name, tag_count in tags.most_common(30):
            print(
                f"""<img src="https://img.shields.io/badge/{tag_name.replace('-', ' ')}-{tag_count}-brightgreen?style=for-the-badge&logo=pypi&logoColor=white">""",
                file=f,
                end=" ",
            )

        # toc
        print("\n\n## Contents", file=f)

        for notebook_file, notebook_metadata in sorted(
            all_notebooks.items(),
            key=lambda nb: nb[1].get("title", None),
        ):
            print(
                f" - [{notebook_metadata['title']}](#{notebook_metadata['filename']})",
                file=f,
            )

        print("\n\n## Notebooks", file=f)
        for notebook_file, notebook_metadata in sorted(
            all_notebooks.items(),
            key=lambda nb: nb[1]["keywords"][0],
        ):

            print(
                f"### <a name=\"{notebook_metadata['filename']}\"></a> - {notebook_metadata['title']}",
                file=f,
            )

            print(
                f"\n<sub>Updated: {datetime.fromisoformat(notebook_metadata['time_created']).strftime('%m/%d/%Y')}</sub>",
                file=f,
            )

            print(
                f"#### [`{notebook_metadata['filename']}`]({notebook_metadata['filename']})",
                file=f,
            )
            print("\n ", file=f)
            print(f"{notebook_metadata['summary']}", file=f)
            print(
                f"\nThis notebook was developed on the conda pack with slug: `{notebook_metadata['developed_on']}`",
                file=f,
            )
            print("\n ", file=f)

            tags = "  ".join([f"`{kw}`" for kw in notebook_metadata["keywords"]])
            print(f"{tags}", file=f)

            print(f"\n<sub>{notebook_metadata['license']}</sup>", file=f)
            print(f"\n---", file=f)

        print(f"{len(all_notebooks)} notebooks processed into {README_FILE}")

    with open(INDEX_FILE, "w") as index_file:

        json.dump(
            sorted(all_notebooks.values(), key=lambda nb: nb["keywords"][0]),
            index_file,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
        )
        print(f"{len(all_notebooks)} notebooks proceesed into {INDEX_FILE}")

    if ignored_notebooks:
        print(f"{len(ignored_notebooks)} notebooks ignored (missing @notebook)")
        for nb_file in ignored_notebooks:
            print(f" - {nb_file}")


if __name__ == "__main__":
    make_readme_and_index()
