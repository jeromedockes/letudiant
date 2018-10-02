import pathlib

import requests
import pandas as pd

from . import scraper, utils


LETUDIANT_DOMAIN = "https://jobs-stages.letudiant.fr"
INTERNSHIP_URL = "https://jobs-stages.letudiant.fr/stages-etudiants/annonce"
SEARCH_PAGE = ("https://jobs-stages.letudiant.fr/stages-etudiants/offres/"
               "libelle_libre-Comptabilit%C3%A9/domaines-101/niveaux-9_1/"
               "pays-france/page-{}.html")


def get_search_results(out_dir):
    search_dir = pathlib.Path(out_dir) / 'search_results_{}'.format(
        utils.time_stamp())
    search_dir.mkdir(parents=True)
    page_nb = 1
    last_page_nb = None
    while last_page_nb is None or page_nb <= last_page_nb:
        print('getting search results page {}'.format(page_nb))
        current_page = requests.get(
            SEARCH_PAGE.format(page_nb)).content.decode('utf-8')
        if last_page_nb is None:
            last_page_nb = scraper.get_last_page_nb(current_page)
        with open(str(search_dir / 'page_{}.html'.format(page_nb)), 'w') as f:
            f.write(current_page)
        yield current_page
        page_nb += 1


def get_offers_urls(search_dir):
    search_dir = pathlib.Path(search_dir)
    urls = []
    for page in search_dir.glob('page_*.html'):
        with open(str(page), 'rb') as f:
            content = f.read().decode('utf-8')
        urls += scraper.get_offers_urls(str(content))
    print('{} internships found'.format(len(urls)))
    return [LETUDIANT_DOMAIN + url for url in urls]


def get_offers(urls, offers_dir):
    offers_dir = pathlib.Path(offers_dir)
    offers_dir.mkdir(parents=True, exist_ok=True)
    for url in urls:
        file_name = pathlib.Path(url).name
        out_file = offers_dir / file_name
        if not out_file.is_file():
            page = requests.get(url)
            with open(str(out_file), 'wb') as f:
                f.write(page.content)
            print('downloaded {}'.format(file_name))
        else:
            print('already have {}'.format(file_name))


def read_offers(offers_dir):
    offers_dir = pathlib.Path(offers_dir)
    offers = []
    for offer_page in offers_dir.glob('*.html'):
        print('reading ', offer_page.name)
        with open(str(offer_page), 'rb') as f:
            offer = f.read().decode('utf-8')
        info, _ = scraper.scrape_offer(offer)
        info['url'] = '/'.join([INTERNSHIP_URL, offer_page.name])
        offers.append(info)
    return pd.DataFrame(offers)
