from keybert import KeyBERT
from collections import defaultdict
import scipy

class firebase:

    def __init__(self, model_name='distilbert-base-nli-mean-tokens'):

        self.model = KeyBERT(model_name)

    def generate_keys(self, pars, num_words=1, thresh=0.4, top_n=1):
        """
        pars: [dict]  paragraphs
        l:    [int]   desired #words in each keyword to be extracted from the given paragraph
        thresh:    [float] similarity threshold to decide upon keeping the keyword
        """
        output = defaultdict(list) # [dict] pairs of paragraph number and its associated keyword
        par_embeddings = dict()
        keywords_found = []
        
        # set_trace()
        
        for key in pars:
            keywords = self.model.extract_keywords(pars[key], keyphrase_ngram_range=(1, num_words), stop_words=None, top_n=top_n)
            for keyword in keywords:
                if keyword[1] > thresh: # check similarty score
                    # if the keyword is found before, skip
                    if keyword[0] in keywords_found:
                        continue
                    output[key].append(keyword[0])
                    keywords_found.append(keyword[0])
                    par_embeddings[key] = self.model._extract_embeddings(pars[key])
        
        if top_n == 1:
            return {k: v[0] for k, v in output.items()}, par_embeddings
        return output, par_embeddings


    def check_semantic_similarity(self, parList, orig_embedding):
    
        out = []
        for pars in parList:
            new_embeddings = self.model._extract_embeddings(pars)
            
            if len(new_embeddings.shape) < 2:
                new_embeddings = new_embeddings.reshape(1,-1)
            
            score = scipy.spatial.distance.cdist(orig_embedding, new_embeddings, "cosine")
            out.append(score.max())
            
        return out
