import wikipedia
import requests
from bs4 import BeautifulSoup
from img_utils import get_image_with_url


WIKI_API_URL = "https://en.wikipedia.org/w/api.php"


def get_wiki_images(title, verbose=False):
    '''TODO: Retrieve the highest quality image from the source set'''

    wiki_params = {
        'action': 'parse',
        'page': title,
        'format': 'json'
    }

    # start a request session
    S = requests.Session()

    # obtain the html of the wiki page from a request session
    wiki_ses = S.get(url=WIKI_API_URL, params=wiki_params)
    wiki_data = wiki_ses.json()
    wiki_page = (wiki_data['parse']['text']['*'])

    # parse the wiki HTML
    soup = BeautifulSoup(wiki_page, 'html.parser')

    # if the wikipedia page contains an infobox as some popular pages do
    # then first obtain the infobox table and extract the images there
    main_tables = soup.findAll("table", {"class": "infobox"})
    table_images = []
    if main_tables:
        if verbose:
            print('[INFO] Found an infobox for the Wiki entry {}'.format(title))

        # iterate through the main tables and find entries that
        # span two columns which entries containing images should
        for cur_table in main_tables:
            multi_cols = cur_table.findAll("td", {"colspan": "2"})
            caption_next = False
            for cur_elem in multi_cols:
                if not caption_next:
                    cur_img = cur_elem.findAll("img")
                    if cur_img:
                        image = cur_img[0]['src']

                        # check if the caption is in the same element
                        cur_cap = cur_elem.findAll("div")
                        if cur_cap:
                            caption = cur_cap[0].text
                            image_and_caption = {
                                'image_url' : image,
                                'image_caption' : caption
                            }
                            table_images.append(image_and_caption)
                        else:
                            # caption should come right after an image entry
                            # otherwise
                            caption_next = True
                else:
                    caption = cur_elem.text
                    image_and_caption = {
                        'image_url' : image,
                        'image_caption' : caption
                    }
                    table_images.append(image_and_caption)
                    caption_next = False

    # the rest of the images should be in *thumbinner* classes
    # captions should be under another *div* class
    thumb_divs = soup.findAll("div", {"class": "thumbinner"})
    images = []
    for div in thumb_divs:
        image = div.findAll("img")[0]['src']
        caption = div.findAll("div")[0].text

        image_and_caption = {
            'image_url' : image,
            'image_caption' : caption
        }
        images.append(image_and_caption)

    img_caption_dict = {'title' : title}
    if images:
        img_caption_dict.update({ 'images': images})
    if table_images:
        img_caption_dict.update({ 'table_images': table_images})

    if verbose:
        print('[SUCCESS] Found {} many images for the Wikipedia entry titled {}'.format(len(images) + len(table_images), title))

    return img_caption_dict


def save_wiki_image(cur_keys, verbose=True):
    for par in cur_keys.keys(): # keys contain one keyword per paragraph (if the paragraph is chosen) for the document you chose
        keyw = cur_keys[par] # keyword for the given paragraph

        print('Obtaining wikipedia entry for the keyword {}'.format(keyw))
        wiki_titles = wikipedia.search(keyw)
        if wiki_titles[0] != keyw:
            print('Wikipedia entry not found for the keyword {}. Instead using {}'.format(keyw, wiki_titles[0]))
        wiki_images = get_wiki_images(wiki_titles[0], verbose=verbose)

        if 'table_images' in wiki_images:
            cur_img = get_image_with_url(wiki_images['table_images'][0]['image_url'], save_image=True, title=keyw, size=(512,512))
        elif 'images' in wiki_images:
            cur_img = get_image_with_url(wiki_images['images'][0]['image_url'], save_image=True, title=keyw, size=(512,512))
        else:
            print('No suitable wikipedia entry found for the keyword {}. Skipping...'.format(keyw))

    print('DONE!')
