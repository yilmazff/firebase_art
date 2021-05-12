from bs4 import BeautifulSoup
import requests
import re

par_merger = lambda prs: {'par1': ' '.join(' '.join(list(prs.values())).split())}

regex_check = re.compile('[@<>\t\n~©Å]')

def crawl_doc(url,th,disp=True, skip_special=True):
    # th: threshold on the length of the paragraph to be captured
    r = requests.get(url)
    data = r.text
    soup = BeautifulSoup(data, 'html.parser')
    
    # set_trace()
    
    ### extract paragraphs longer than a threshold
    # traverse paragraphs from soup and collect them in a dict
    pars = {}
    i = 1
    for data in soup.find_all("p"):
        par = data.get_text()
        if len(par.split(' ')) > th: # if len(paragraph) > 'th' words, then collect it
            if skip_special and (regex_check.search(par) is not None):
                print('Paragraph contains special characters. Skipping...')
                continue
                
            key = 'par{}'.format(i)
            pars[key] = par
            i += 1
            if disp:
                print('"'+key+'"', par,'\n')

    return pars