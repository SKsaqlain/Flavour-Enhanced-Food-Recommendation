from collections import Counter, defaultdict
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
import sys
import json
import math
import numpy as np
import os
import pandas as pd
import re
from scipy.sparse import csr_matrix
import time
import pickle
import csv
import os.path

my_path = os.path.abspath(os.path.dirname(__file__))

def append_to_data(data, profile, predict_on):
    profile = json.loads(profile)
    dish_ids = list(map(int, profile.keys()))
    ratings = list(map(int, profile.values()))

    d = pd.DataFrame(columns = ['dishId', 'userId', 'rating'])
    d['dishId'] = dish_ids
    d['rating'] = ratings
    d['userId'] = predict_on

    data = data.append(d)
    return data

def tokenize_string(my_string):
    return re.findall('[\w\-]+', my_string.lower())


def tokenize(db):
    """
    The meta tags associated with each dish is broken down (tokenized) as a list of tags
    Eg: egg|flour|ghee|paratha will be tokenized as [egg, flour, ghee, paratha]
    """
    tokenlist=[]
    for index,row in db.iterrows():
        tokenlist.append(tokenize_string(row.tags))
    db['tokens']=tokenlist
    return db

def featurize(db, include_flavours):
    """
    Each row will contain a csr_matrix of shape (1, num_features).
    Each entry in this matrix will contain the tf-idf value of the term
    Formula : tfidf(i, d) := tf(i, d) / max_k tf(k, d) * log10(N/df(i))
    where:
    i is a term
    d is a document 
    tf(i, d) is the frequency of term i in document d
    max_k tf(k, d) is the maximum frequency of any term in document d
    N is the number of documents
    """
    def tf(word, doc):
        return doc.count(word) / Counter(doc).most_common()[0][1]

    def df(word, doclist):
        return sum(1 for d in doclist if word in d)

    def tfidf(word, doc, dfdict, N):
        return tf(word, doc) * math.log10((N / dfdict[word]))

    def getcsrmatrix(tokens,dfdict,N,vocab, dish_flavours, max_vocab):
        matrixRow_list = []
        if include_flavours:
            matrixRow_list = np.zeros((1,len(vocab) + len(dish_flavours) - 1),dtype='float')
        else:
            matrixRow_list = np.zeros((1,len(vocab)),dtype='float')
        for t in tokens:
            if t in vocab:
                matrixRow_list[0][vocab[t]] = tfidf(t,tokens,dfdict,N)

        if include_flavours:
            matrixRow_list[0][max_vocab] = dish_flavours['bitter']
            matrixRow_list[0][max_vocab] = dish_flavours['rich']
            matrixRow_list[0][max_vocab + 1] = dish_flavours['salt']
            matrixRow_list[0][max_vocab + 3] = dish_flavours['spicy']
            matrixRow_list[0][max_vocab + 2] = dish_flavours['sweet']
            matrixRow_list[0][max_vocab + 5] = dish_flavours['umami']

        return csr_matrix(matrixRow_list)

    flavour = pd.read_csv(os.path.join(my_path,'../Utilities/Team 2/tastes.csv'), names = ['dishId', 'bitter', 'rich', 'salt', 'spicy', 'sweet', 'umami'])

    N=len(db)

    doclist = db['tokens'].tolist()
    vocab = { i:x for x,i in enumerate(sorted(list(set(i for s in doclist for i in s)))) }
    max_vocab = max(vocab.values()) + 1

    dfdict = {}
    for v in vocab.items():
        dfdict[v[0]] = df(v[0],doclist)

    csrlist = []
    for index, row in db.iterrows():
        dish_flavours = flavour[flavour.dishId == row['dishId']].to_dict(orient = 'record')[0]
        csrlist.append(getcsrmatrix(row['tokens'],dfdict,N,vocab, dish_flavours, max_vocab)) # row['dishId'] and df with flavour scores

    db['features'] =  csrlist
    return (db,vocab)


def my_train_test_split(ratings):
    """
    Returns a random split of the ratings matrix into a training and testing set.
    """
    train_set, test_set = train_test_split(ratings, test_size = 0.20, random_state = 42)
    return train_set, test_set
    '''
    test = set(range(len(ratings))[::10])
    train = sorted(set(range(len(ratings))) - test)
    test = sorted(test)
    return ratings.iloc[train], ratings.iloc[test]
    '''

def cosine_sim(a, b, include_flavours):
    """
    """

    v1 = a.toarray()[0]
    v2  = b.toarray()[0]
    def cos_sim(v1, v2):
        x = (math.sqrt(sum([i*i for i in v1]))*math.sqrt(sum([i*i for i in v2])))
        if x:
            return sum(i[0] * i[1] for i in zip(v1, v2)) / x
        else:
            return 0
    # s1 = cos_sim(v1, v2)
    # return s1
    s1 = cos_sim(v1[:-6], v2[:-6])
    if include_flavours:
        s2 = cos_sim(v1[-6:], v2[-6:])
        return s1 * 0.5 + s2 * 0.5
    else:
        return s1

def make_predictions(db, ratings_train, ratings_test, include_flavours):
    """
    Using the ratings in ratings_train, prediction is made on the ratings for each
    row in ratings_test.
    This is done by computing the weighted average
    rating for every other dish that the user has rated.
    """
    result = []
    x = 0
    for index,row in ratings_test.iterrows():
        # mlist contains dishIds rated by the user in the train set
        mlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['dishId'])
        # csr list contains tfidf scores of tags for dishes rated by the user
        csrlist = list(db.loc[db['dishId'].isin(mlist)]['features'])
        # mrlist contains scores of dishes rated by the user (dishes in mlist)
        mrlist = list(ratings_train.loc[ratings_train['userId'] == row['userId']]['rating'])
        # computing similarity between dishes user rated and the current dish in the test set

        sim = [cosine_sim(c,db.loc[db['dishId'] ==row['dishId']]['features'].values[0], include_flavours) for c in csrlist]
        # computing similarity times the rating for known dish
        wan = sum([ v*mrlist[i] for i,v in enumerate(sim) if v>0])
        wadlist = [i for i in sim if i>0]
        ## check for sum(wadlist) > 1
        if len(wadlist)>0 and sum(wadlist) >= 1:
            result.append(wan/sum(wadlist))
            x = x + 1
        else:
            result.append(np.mean(mrlist)) # if dish did not match with anything approx as average of users rating
    return np.array(result)

def main(data, db, predict_on, include_flavours):
    """
    """
    total_dishes = db.shape[0]

    db = tokenize(db)
    db, vocab = featurize(db, include_flavours)
    
    ratings_train, ratings_test = my_train_test_split(data)
    predictions = make_predictions(db, ratings_train, ratings_test, include_flavours)

    predicted_test_error = mean_squared_error(ratings_test.rating, predictions) ** 0.5

    def predict_on_user(predict_on):
        ratings_test = pd.DataFrame(columns = ['userId', 'dishId'])
        ratings_test['userId'] = [predict_on] * total_dishes
        ratings_test.dishId = range(1, total_dishes + 1)
           
        predictions_uid = make_predictions(db, ratings_train, ratings_test, include_flavours)

        predictions_uid = list(enumerate(predictions_uid))

        predictions_uid = sorted(predictions_uid, key = lambda x: x[1], reverse = True)

        predictions_uid = list(map(lambda x: (x[0] + 1, x[1]), predictions_uid))

        return predictions_uid

    return (predicted_test_error, predict_on_user(predict_on = predict_on))
    

def start(profile = None, type = 'all', predict_on = 100, flavours = False, retrain = False):
    time_start = time.time()
    data = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/review.csv'))
    data = data[data['userId'].isin(data['userId'].value_counts()[data['userId'].value_counts() >= 5].index)]

    if not retrain:
        if flavours:
            final_scores = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_flavour_scores.pickle"), "rb" ))
            predictions = final_scores[predict_on]

        else:
            final_scores = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_scores.pickle"), "rb" ))
            predictions = final_scores[predict_on]

        predicted_test_error = None

    else:
        if profile:
            data = append_to_data(data, profile, predict_on)

        if type == 'all':
            db = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/meta_cuisine.csv'))
        elif type == 'meta':
            db = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/database.csv'), names = ['dishId', 'tags'])

        dishes = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/id_name_mapping.csv'), names = ['dishId', 'dish_name'])

        predicted_test_error, predictions = main(data, db, predict_on = predict_on, include_flavours = flavours)
        
        predictions = pd.DataFrame(predictions, columns = ['dishId', 'rating'])
        predictions = predictions.merge(dishes, on = 'dishId', how = 'left')
        predictions.columns = ['dishId', 'rating', 'dishName']

        if flavours:
            if os.path.exists(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_flavour_scores.pickle")):
                final_scores = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_flavour_scores.pickle"), "rb" ))
                final_scores[predict_on] = predictions
            else:
                final_scores = {}
                final_scores[predict_on] = predictions

            pickle.dump(final_scores, open(os.path.join(my_path,'../Utilities/Team 3/tfidf_final_flavour_scores.pickle'), 'wb'))

        else:
            if os.path.exists(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_scores.pickle")):
                final_scores = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tfidf_final_scores.pickle"), "rb" ))
                final_scores[predict_on] = predictions

            else:
                final_scores = {}
                final_scores[predict_on] = predictions

            pickle.dump(final_scores, open(os.path.join(my_path,'../Utilities/Team 3/tfidf_final_scores.pickle'), 'wb'))

    data = data[data.userId == predict_on]
    original_rating = data.merge(predictions, how = 'left', on = 'dishId')
    original_rating.columns = ['dishId', 'userId', 'rating', 'reformed', 'dishName']
    
    time_end = time.time()

    answer = {"user" : predict_on, "predicted_test_error": predicted_test_error, "time" : round(time_end - time_start, 2), "predicted_rating" : predictions, "original_rating" : original_rating}
    return answer

def getpipedtags():
    objects = []

    tagged_dishes = pickle.load(open(os.path.join(my_path,"../Utilities/Team 3/tagged_dishes.pickle"), "rb" ))

    for i in range(1, len(tagged_dishes)):
        tags = '|'.join(tagged_dishes[i][0])
        objects.append([i, tags])

    with open(os.path.join(my_path,"../Utilities/Team 3/database.csv"), 'w+') as f:
        writer = csv.writer(f)
        writer.writerows(objects)

def add_cuisine_tags():
    a = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/database.csv'), names = ['dishId', 'tags'])
    b = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/cuisine_tags.csv'))

    b = b.drop(['dishName'], axis = 1)
    b = b.drop_duplicates(subset=['dishId'])

    merged = pd.merge(a, b, on = ['dishId'], how = 'left')

    merged = merged.fillna('')

    newlist = merged['tags'] + "|" + merged['cuisine']
    newlist = list(newlist)

    x_list = []
    for i in newlist:
        if i.endswith('|'):
            x_list.append(i[:len(i) - 1])
        else:
            x_list.append(i)

    merged['all_tags'] = x_list
    merged = merged.drop(['tags', 'cuisine'], axis = 1)
    merged.columns = ['dishId', 'tags']
    merged.to_csv(os.path.join(my_path,'../Utilities/Team 3/meta_cuisine.csv'), index = False)

def correct_tags():
    df = pd.read_csv(os.path.join(my_path,'../Utilities/Team 3/meta_cuisine.csv'))

    new_tags = []

    current_tags = list(df['tags'])

    for i in current_tags:
        new_tags.append(i.replace(" ", ""))

    df['tags'] = new_tags

    df.to_csv(os.path.join(my_path,'../Utilities/Team 3/meta_cuisine.csv'), index = False)

if __name__ == '__main__':
    getpipedtags()
    add_cuisine_tags()
    correct_tags()
    start()