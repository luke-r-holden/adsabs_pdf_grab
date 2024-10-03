# adsabs_pdf_grab: A python function to download .pdf files for BibTeX entries using the ADS API

This Python function takes a BibTeX file as input, parses each entry, identifies the DOI and or arXiv ID, and uses these with the [NASA Astrophysics Data System](https://ui.adsabs.harvard.edu/) API to download a .pdf file for each entry. This allows the user to easily download .pdf files for all papers/articles/etc that they have in a .bib file, which, for example, they might have for an individual project, or a master file containing all papers that they cite in their work.

Input parameters:
 - A .bib file containing BibTeX entries. BibTeX entries can easily be generated on the ADS page for a given paper by going to View > Export Citation and "Select Export Format: BibTeX"; these entries can then be pasted into a .bib file, commonly used for citation management with LaTeX.
 - A valid ADS API token, which can be generated by signing up for/logging into an ADS account and visiting [this page in account settings](https://ui.adsabs.harvard.edu/user/settings/token).
 - The directory to download the .pdf files to. By default, this is the current working directory.

The user can also silence text prints to terminal (notifying the user of the success or failure of .pdf downloads) using the `verbose` boolean argument (default True), as well as if existing .pdf files should be redownloaded and overwritten (with the `overwrite` boolean argument, which is False by default).

## Running the code

### Requirements

This code was written in Python 3.12.6, and so it is recommended to use this version or later. 

adsabs_pdf_grab makes use of the `re`, `os`, and `requests` Python modules; the former two are included by default in Python releases, while the latter may need to be installed by the user (e.g. with `python3 -m pip install requests`). 

### Installation

To install, either clone this repository to the desired directory with `git clone https://github.com/luke-r-holden/adsabs_pdf_grab`, or directly download the `adsabs_pdf_grab.py` file from the GitHub repository web page.

### Usage

Either using a script, Python shell, or Jupyter notebook, the function can be imported with 
```
from adsabs_pdf_grab import adsabs_pdf_grab
```

Then, to run, use
```
adsabs_pdf_grab.adsabs_pdf_grab(bibtex_file="/path/to/bibtex_file.bib", ads_api_key='my_api_key', output_dir='/path/to/output_directory')
```
where `bibtex_file.bib` is the .bib file containing the BibTeX entries you wish to download .pdf files for, `ads_api_key` is your ADS API token (which you can generate and view [here](https://ui.adsabs.harvard.edu/user/settings/token) once logged in), and `output_dir` is the directory you want to download the .pdf files to.

Optionally, you can also supress all messages during the download process by setting the `verbose` argument to `False`:
```
adsabs_pdf_grab.adsabs_pdf_grab(bibtex_file="/path/to/bibtex_file.bib", ads_api_key='my_api_key', output_dir='/path/to/output_directory', verbose=False)
```

By default, any entries that already have a .pdf file of name "[Authors]\_[Year].pdf" in the output directory will be skipped. This behaviour can be overwritten setting the `overwrite` argument to `True', which will forcibly redownload all entries in the .bib file and overwrite existing .pdf files. For example:
```
adsabs_pdf_grab.adsabs_pdf_grab(bibtex_file="/path/to/bibtex_file.bib", ads_api_key='my_api_key', output_dir='/path/to/output_directory', overwrite=True)
```

## Additional notes

In the current version of adsabs_pdf_grab, .pdf files are searched for (and downloaded from) the following sources, in order:
 1) The .pdf file hosted on ADS (common for older papers and articles published before 2000).
 2) The [arXiv](https://arxiv.org/) page for the BibTeX entry.
 3) The publisher/journal page for the BibTeX entry.

The arXiv (pre-print) version of a given entry is given priority due to various issues arising from attempting to access .pdf files directly from publishers and journals, such as URL redirection, log-in screens for institutional access, and paywalls. For these reasons, it is much more reliable to request and download the .pdf file from arXiv.

If there are multiple papers published by the same author(s) in a given year, these are downloaded as [Author]\_[Year].pdf, [Author]\_[Year]b.pdf, [Author]\_[Year]c.pdf, [Author]\_[Year]d.pdf, [Author]\_[Year]e.pdf. Note that, since publishing more than five first-author papers in a single year is exceptionally uncommon (and impressive), this system only extends to the letter `e` --- be mindful of this if you are attempting to use `adsabs_pdf_grab` to download papers of authors that *have* published more than five papers in a single year.
