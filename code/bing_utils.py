import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re


BING_SEARCH_URL = "https://api.bing.microsoft.com/v7.0/images/search"
regex_check = re.compile('[@<>\t\n~©Å]')


def _retrieve_bing_api_keys(path='../metadata/bing_api_key.json'):
    """Retrieve the Bing API key from the file it is stored in"""
    import json
    with open(path) as fn:
        api_key = json.load(fn)
    return api_key['key']


def get_bing_results(search_term, api_key=_retrieve_bing_api_keys(), verbose=False):
    """Query Bing API and return search results"""

    headers = {"Ocp-Apim-Subscription-Key" : api_key}
    params = {"q": search_term} # , "license": "public", "imageType": "photo"}
    
    response = requests.get(BING_SEARCH_URL, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    if verbose:
        print('[INFO] Total of {} images found.'.format(len(search_results['value'])))

    return {res['imageId']: {'image_url': res['contentUrl'],
                             'thumb_url': res['thumbnailUrl'],
                             'site_url': res['hostPageUrl']}
            for res in search_results['value']}


def get_image_text_from_site(site_url, image_url='', min_num_words=10, min_num_sentences=2, adjacent_only=False , verbose=False):

    try:
        cur_ses = requests.get(site_url)
        soup = BeautifulSoup(cur_ses.text, 'html.parser')
    except:
        if verbose:
            print("Connection error for the website {}.\nSkipping...".format(site_url))
        return defaultdict(list)

    # list the paragraphs and images in the website in order
    pars_and_imgs = soup.findAll(["p", "img"])

    img_url_pars = defaultdict(list)
    for i, cur_tag in enumerate(pars_and_imgs):
        # check if p class contains an image
        cur_imgs = cur_tag.findAll("img")
        
        # work with the img tag if image is found instead of the p tag
        if cur_imgs:
            cur_tag = cur_imgs[0]
        
        # if the current tag is an image tag
        if cur_tag.name == "img":
            
            try:
                im_source = cur_tag["src"]
            except KeyError as e:
                if verbose:
                    print("This is an image tag, but does not contain an image source: {}".format(cur_tag))
                continue
            
            if (not image_url) or (cur_tag["src"] == image_url):
                
                if adjacent_only:
                    # obtain text next to the image both before and after an image
                    # while text usually follows an image, 
                    # sometimes image comes after a description
                    if i == 0:
                        cur_idx_list = [1]
                    elif i == len(pars_and_imgs) - 1:
                        cur_idx_list = [len(pars_and_imgs) - 2]
                    else:
                        cur_idx_list = [i-1, i+1]
                        
                    # only record paragraphs that satisfy minimum number of words 
                    # and minimum number of sentences requirements
                    for k in cur_idx_list:
                        cur_par = pars_and_imgs[k].text
                        if regex_check.search(cur_par) is not None:
                            continue
                        if (len(cur_par.split(' ')) >= min_num_words) and (len(cur_par.split('. ')) >= min_num_sentences):
                            img_url_pars[cur_tag["src"]].append(cur_par)
                else:
                    # Go towards both beginning and end to find the first
                    # two paragraphs that satisfy the conditions
                    tow_begin = list(range(i-1, -1, -1))
                    tow_end = list(range(i+1, len(pars_and_imgs), 1))
                    tow_max = int(min(i, len(pars_and_imgs) - i))

                    # iterate the indices toward both ends one at a time
                    cur_idx_list = slicezip(tow_begin[:tow_max], tow_end[:tow_max])
                    cur_idx_list += tow_begin[tow_max:] + tow_end[tow_max:]

                    # only record paragraphs that satisfy minimum number of words 
                    # and minimum number of sentences requirements
                    for k in cur_idx_list:
                        cur_par = pars_and_imgs[k].text
                        if regex_check.search(cur_par) is not None:
                            continue
                        if (len(cur_par.split(' ')) >= min_num_words) and (len(cur_par.split('. ')) >= min_num_sentences):
                            img_url_pars[cur_tag["src"]].append(cur_par)
                            if len(img_url_pars[cur_tag["src"]]) > 1:
                                break
    
    return img_url_pars


def get_bing_results_per_paragraph(model, keys, par_embeddings, verbose=True):
    """
    Inputs:
        keyw: keyword
    Output:
        imList [list]: list of returned images (from Bing)
        parList [list]: list of tuples where each tuple contains paragraphs for the corresponding image from imList
    """
    results = {}
    for par in keys.keys(): # keys contain one keyword per paragraph (if the paragraph is chosen) for the document you chose
        keyw = keys[par] # keyword for the given paragraph
        
        bing_res = get_bing_results(keyw, verbose=verbose)
        bing_res_urls = list(bing_res.values())
        
        # Obtain paragraphs for the bing images from the original websites
        if verbose:
            print('Obtaining paragraphs for the bing images for the keyword {}...'.format(keyw))
        parList = [list(get_image_text_from_site(irs['site_url'], irs['image_url'], verbose=verbose).values()) for irs in bing_res_urls]
        if verbose:
            print('DONE!')

        # Record the indices for images for which any paragprahs have been found
        # and only keep these images
        idxList = [i for i, cur_p in enumerate(parList) if cur_p]
        parList = [tuple(parList[i][0]) for i in idxList]
        imList = [bing_res_urls[i]['thumb_url'] for i in idxList]
        
        if verbose:
            print('Computing scores for the images...')
        # scoreList = pipeline(parList,keyw,wv,bwv,l=2)
        scoreList = model.check_semantic_similarity(parList, par_embeddings[par])
        if verbose:
            print('DONE!')
        ### if scoreList is empty, we have to just return the first google (or bing) result
        results[par] = {'keyword':keyw,'images':imList,'scores':scoreList}
    return results


def slicezip(a, b):
    result = [0]*(len(a)+len(b))
    result[::2] = a
    result[1::2] = b
    return result

