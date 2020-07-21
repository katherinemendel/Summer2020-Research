from gensim.models import Word2Vec

#https://www.kaggle.com/jonathanbesomi/covid19-word-embeddings/data


WV_PATH = '/Users/katiemendel1/Desktop/collected-twitter-data/CORD19_word2vec_abstract_13032020_200.model'

model_wv = Word2Vec.load(WV_PATH)
print(model_wv.wv.most_similar("nonrebreathing"))
"""
n95, n-95, mask, facepiece, wear, facemask, nonrebreathing, ffr, respirator, 
filtering, elastomeric, foldtype, cloth
"""