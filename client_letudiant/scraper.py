import re
import datetime

import bs4

HEADINGS = {
    'Domaine de formation': 'formation',
    'Mission': 'mission',
    'Profil': 'profile',
    "Niveau(x) d'études": 'studies',
    'Durée': 'duration_and_start_date',
    'duration': 'duration',
    'start_date': 'start_date',
    'Rémunération': 'remuneration'
}


def get_last_page_nb(search_page):
    soup = bs4.BeautifulSoup(search_page, 'html.parser')
    last_page_button = soup.select("a[class='c-pager__item c-pager__item--nav"
                                   " c-pager__item--nav--double']")
    last_page_url = last_page_button[0]["href"]
    last_page = re.match(r'.*page-(\d+)\.html', last_page_url).group(1)
    return int(last_page)


def get_offers_urls(search_page):
    soup = bs4.BeautifulSoup(search_page, 'html.parser')
    titles = soup.select('a[class="c-search-result__title"]')
    return [title['href'] for title in titles]


def scrape_offer(offer_page):
    soup = bs4.BeautifulSoup(offer_page, 'html.parser')
    info = {'date_updated': datetime.datetime.now().isoformat()}
    info.update(_get_offer_id_and_date_str(soup))
    info.update(_get_known_editorial_elements(soup))
    return info, soup


def _get_offer_id_and_date_str(soup):
    ref_info = soup.select('div[class="c-hero__etablissement__ref"]')[0]
    match = re.match(r'\s*R.f\.\s+(\d+)\s+-\s+Pub.*le\s+(.+?)\s*$',
                     ref_info.text)
    return {'id': int(match.group(1)), 'publication_date_str': match.group(2)}


def _get_known_editorial_elements(soup):
    elements = _get_editorial_elements(soup)
    res = {
        HEADINGS[k]: re.sub(r'\s+', ' ', '\n'.join(v)) for
        k, v in elements if k in HEADINGS}
    for k, v in elements:
        if k == 'Durée' and len(v) == 2:
            res['duration'] = re.sub(r'\s+', ' ', v[0])
            res['start_date'] = re.sub(r'\s+', ' ', v[1])
    return {k: v.strip() for k, v in res.items()}


def _get_editorial_elements(soup):
    editorial = soup.select('div[class="s-editorial"]')[0]
    elements = (c for c in editorial.children
                if isinstance(c, bs4.element.Tag))
    result = []
    try:
        h5 = next(elements)
    except StopIteration:
        return result
    while True:
        p, next_h5 = _tail(elements)
        result.append((h5.text, [pp.text for pp in p]))
        if next_h5 is None:
            return result
        h5 = next_h5


def _tail(elements):
    p = []
    while True:
        try:
            e = next(elements)
        except StopIteration:
            return p, None
        try:
            c = e['class'][0]
        except Exception:
            c = None
        if c == 'u-typo-h5':
            return p, e
        if c == 'c-box--wire':
            return p, None
        p.append(e)


def _get_offer_details(soup):
    pass
