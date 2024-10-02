import re
import requests
import os.path

def download_pdf(url_list, title, output_dir, verbose):
    """
    Request a .pdf file from the first successful URL in a list of URLs and save it to a file with a specified title. If the `verbose' argument is set to True, the user will be notified if the download was successful (including the URL used) or not.

    Parameters
    ----------
    url_list : list
        List of URLs to request the .pdf file for the paper in the bib entry from.
    title : string
        The prefix for the file name to download the .pdf to.
    output_dir : str, optional 
        The path to the output directory in which the .pdf files will be downloaded. If no directory is provided, then by default, the current directory is used.
    verbose : bool 
        If True, then print a message when a BibTeX entry has been successfully downloaded (including the URL used). If False, then suppress all output during download. 
    """

    # if `url_list' is None (i.e. something went wrong during the calls to the other functions), then skip the BibTeX entry
    if not url_list:
        return

    # iterate over the URLs produced by the define_urls function until one of them successfully returns a .pdf file
    for url in url_list:
        try:
            # request the .pdf file from the defined URL and create the .pdf filename
            response = requests.get(url)
            filename = "{}.pdf".format(title)

            # check that the request was successful (hence returned status code 200)
            if response.status_code == 200:

                # save the content of the response as a .pdf file with the name that was previously defined
                with open("{}/{}".format(output_dir, filename), "wb") as file:
                    file.write(response.content)

                # notify the user that the download was successful
                if verbose == True:
                    print("{}.pdf downloaded from {}".format(title, url))

                # since the download from the current URL was successful, don't attempt to download a file from the other URLs
                break

        # if something goes wrong while requesting the .pdf file, then skip the entry and print an error message to notify the user
        except:
            print("{}.pdf failed.".format(title))
            continue

def define_url(doi=None, eprint=None, ads_api_key=None):
    """
    Use the ADS API to retrieve metadata for the bib entry based on the DOI or arXiv ID, and define a list of URLs that contain the .pdf file for the paper and a prefix for the file name of the downloaded .pdf (which is automatically named depending on the number of authors). Note that at least one of either the DOI or arXiv IDs must be passed into the function.

    Parameters
    ----------
    doi : str, optional (default = None)
        The DOI of the paper.
    eprint : str, optional (default = None)
        The arXiv ID of the paper.

    Returns
    -------
    tuple or None
        A tuple containing a list of URLs at which .pdf files for the paper can be accessed and the formatted prefix for the downloaded .pdf file name, or None if request was not successful.
    """

    if not ads_api_key:
        print("Error: you must provide an ADS API key. One can be created by creating or logging into an ADS account and going to the following page: https://ui.adsabs.harvard.edu/user/settings/token")

    ads_api_access_header = {"Authorization" : "Bearer {}".format(ads_api_key)}
        
    query = None

    # check if DOI is present in bib entry; if so, use it to find ADS metadata.
    if 'doi' != None:
        query="doi:{}".format(doi)

    # if DOI is not present in bib entry; check if arXiv eprint number is, and if so, use it to find ADS metadata.
    elif 'eprint' != None:
        query="arXiv:{}".format(eprint)

    # provided there is either a DOI and/or arXiv number, define a dictionary containing the keys to retrieve from the ADS API
    if query != None:
        params = {"q" : query, "fl" : "title,bibcode,identifier,property,author,year", "rows" : 1}

    # using the ADS API, request the parameters in the `params' dictionary for the entry with the given DOI/arXiv number
    response = requests.get('https://api.adsabs.harvard.edu/v1/search/query', headers=ads_api_access_header, params=params)

    # if the request was successful (and hence returns status code 200)
    if response.status_code == 200:

        # parse the response and check that the ADS search found something
        data = response.json()
        if data['response']['numFound'] > 0:

            # access the information about the article, and pull the bibcode
            doc = data['response']['docs'][0]
            bibcode = doc['bibcode']

            # use the bibcode to define URLs to access the .pdf files for the article, in the order of 1) the ADS-hosted .pdf (common for older, scanned papers) 2) the e-print (arXiv) version of the paper 3) the .pdf from the publisher's website.
            # note that the arXiv version (`EPRINT_PDF') is preferred as there are often problems accessing .pdf files directly from publishers
            pdf_url = ["https://ui.adsabs.harvard.edu/link_gateway/{}/ADS_PDF".format(bibcode), "https://ui.adsabs.harvard.edu/link_gateway/{}/EPRINT_PDF".format(bibcode), "https://ui.adsabs.harvard.edu/link_gateway/{}/PUB_PDF".format(bibcode)]

            # depending on the amount of authors, create the name for the .pdf file as [Author]_[Year] (single author), [Author1]_and_[Author2]_[Year] (two authors), or [Author1]_et_al_[year]
            if len(doc['author']) == 1:
                paper_name = "{}_{}".format(doc['author'][0].split(",")[0],doc['year'])
            elif len(doc['author']) == 2:
                paper_name = "{}_and_{}_{}".format(doc['author'][0].split(",")[0],doc['author'][1].split(",")[0], doc['year'])
            else:
                paper_name = "{}_et_al_{}".format(doc['author'][0].split(",")[0], doc['year'])
            
            # remove all spaces from .pdf file name
            paper_name = paper_name.replace(" ","")
            return pdf_url, paper_name

    # If no DOI or arXiv ID was passed into the function, or if the request using the ADS API was unsuccessful, return None.
    else:
        return None

def extract_doi_arxiv(bibtex_entry):
    """
    Extract the DOI and/or arXiv ID from a BibTeX entry.

    Parameters
    ----------
    bibtex_entry : str
        The BibTeX entry to be searched.

    Returns
    -------
    tuple or None
        A tuple containing the DOI and arXiv ID extracted from the BibTeX entry, or None if neither were found.
    """

    # use regex search to get the DOIs and eprint (arXiv IDs) for the bib entry.
    doi_match = re.search(r"doi\s*=\s*{([^}]+)}", bibtex_entry, re.IGNORECASE)
    eprint_match = re.search(r"eprint\s*=\s*{([^}]+)}", bibtex_entry, re.IGNORECASE)

    # if search is successful, store the DOI and arXiv ID in the doi and eprint variables; else, return None
    doi = doi_match.group(1) if doi_match else None
    eprint = eprint_match.group(1) if eprint_match else None

    return doi, eprint


def adsabs_pdf_grab(bibtex_file, ads_api_key, output_dir="./", verbose=True, overwrite=False):
    """
    Download a .pdf file for each entry in a BibTeX file by extracting the DOI and arXiv ID for each entry and using this to search the NASA ADS ABS database using the ADS API. In the case that multiple papers from the same author(s) in a given year are requested, these will be downloaded as [Author][Year].pdf, [Author][Year]b.pdf, [Author][Year]c.pdf, [Author][Year]d.pdf, [Author][Year]e.pdf.

    Parameters
    ----------
    bibtex_file : str
        The path to the BibTeX .bib file containing the entries to download .pdf files for.
    ads_api_key : str
        A valid ADS API key.
    output_dir : str, optional (default = "./")
        The path to the output directory in which the .pdf files will be downloaded. If no directory is provided, then by default, the current directory is used.
    verbose : bool (default = True)
        If True, then print a message when a BibTeX entry has been successfully downloaded (including the URL used). If False, then suppress all output during download. 
    overwrite : bool (default = False)
        If True, then download .pdf files for all BibTeX entries, regardless of if they already exist in the output directory. If False, then skip entries that already have downloaded .pdf files in the output directory.

    """

    # open the .bib file and read the content
    with open(bibtex_file, "r") as file:
        content = file.read()

    # separate the entries in the .bib file using the "@" symbol (which each entry starts with in the .bib format) and skip the first empty entry
    entries = content.split('@')[1:]

    # set up a list for titles to keep track of what has already been processed --- this will be used to check for multiple papers in one year from the same author and name them appropriately (e.g. Holden2024a, Holden2024b, Holden2024c)
    titles = []

    # iterate over the entries in the .bib file
    for entry in entries[1:]:

        # get the DOI and arXiv IDs, and pass them into the function to define the .pdf URLs and file names
        doi, eprint_id = extract_doi_arxiv(entry)
        pdf_params = define_url(doi=doi, eprint=eprint_id, ads_api_key=ads_api_key)

        # check that the entry was successfully assigned .pdf URLs and file names
        if pdf_params:

            # check for previously-downloaded papers from the same author in the same year
            # if so, then append letters at the end of the file name from `b' to `e'.
            # note that this is done in the order that the entries appear in the .bib file, not publication date.
            if pdf_params[1]+"d" in titles:
                pdf_title = pdf_params[1]+"e"
            elif pdf_params[1]+"c" in titles:
                pdf_title = pdf_params[1]+"d"
            elif pdf_params[1]+"b" in titles:
                pdf_title = pdf_params[1]+"c"
            elif pdf_params[1] in titles:
                pdf_title = pdf_params[1]+"b"
            else:
                pdf_title = pdf_params[1]

            # assign the list of .pdf URLs to a new variable for clarity
            pdf_urls = pdf_params[0]

            # append the current title to the `titles' list to keep track of previously-processed files
            titles.append(pdf_title)

            if os.path.isfile("{}/{}.pdf".format(output_dir, pdf_title)) and overwrite is False:
                print("{}.pdf exists --- skipping.".format(pdf_title))
                continue

            else: 
                # pass the .pdf URLs and file names into the download_pdf function
                download_pdf(pdf_urls, pdf_title, output_dir, verbose)
