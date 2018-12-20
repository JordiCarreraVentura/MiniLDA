from __future__ import division

import json
import random
import tqdm

from collections import (
    Counter,
    defaultdict as deft
)

from tqdm import tqdm


class MiniLDA:
    def __init__(
        self,
        max_iter = 100,
        min_word_freq = 3,
        max_word_freq = 30,
    ):
        self.Wf = Counter()
        self.is_feature = deft(bool)
        self.WT = deft(Counter)
        self.DT = deft(dict)
        self.bows = []
        self.max_iter = max_iter
        self.min_word_freq = min_word_freq
        self.max_word_freq = max_word_freq
        #self.nn = Counter()
        #self.n = 0
    
    def __word_count(self):
        for bow in self.bows:
            self.Wf.update(bow)
        for w, freq in self.Wf.items():
            if freq < self.min_word_freq \
            or freq > self.max_word_freq:
                continue
            self.is_feature[w] = True

    def __call__(self, docs):
        self.__init_bows(docs)
        self.__word_count()
        self.__init_DT(docs)
#         print self.DT
        i = 0
        prev_top_picks = self.__peek_tops()
        while True:
            print
            print i
            self.__calculate_WT(docs)
            self.__calculate_DT(docs)
            top_picks = self.__peek_tops()
            i += 1
            if i == self.max_iter \
            or self.__same_picks(prev_top_picks, top_picks):
                break
            prev_top_picks = top_picks
            
        print json.dumps(self.DT, indent=4)
        print i
        self.__display()


    def __display(self):
        best = Counter()
        doc_ids_by_topic_id = deft(set)
        for doc_id, topics in self.DT.items():
            topic_dist = sorted(topics.items(), reverse=True, key=lambda x: x[1])
            best_topic, best_prob = topic_dist[0]
            if not best_prob:
                continue
            for topic_id, prob in topic_dist[1:]:
                if prob / best_prob < 0.6:
                    break
                best[topic_id] += prob
                doc_ids_by_topic_id[topic_id].add(doc_id)
        
        covered = set([])
        topics = 0
        for topic_id, prob in best.most_common(20):
            topics += 1
            print topic_id
            print docs[topic_id]
            covered.update(doc_ids_by_topic_id[topic_id])
            intersection = Counter()
            for i in list(doc_ids_by_topic_id[topic_id]):
                intersection.update(docs[i])
            print intersection.most_common(10)
            for i in list(doc_ids_by_topic_id[topic_id])[:10]:
                print '\t', i, docs[i], set(docs[i]).intersection(docs[topic_id])
            print topics, round(len(covered) / len(docs), 2)
            print
                
        

    def __same_picks(self, prev_top_picks, top_picks):
        same = 0
        for doc_id, best_topic_id in prev_top_picks.items():
            if best_topic_id == top_picks[doc_id]:
                same += 1
        if same == len(prev_top_picks.keys()):
            return True
        return False

    def __peek_tops(self):
        top_picks = dict([])
        for doc_id, topics in self.DT.items():
            top = sorted(topics.items(), key=lambda x: x[1])[-1][0]
            top_picks[doc_id] = top
        return top_picks

    def __init_bows(self, docs):
        for doc_id, doc in enumerate(docs):
            bow = set(doc)
            self.bows.append(bow)
    
    def __getitem__(self, w):
        return self.WT.keys().index(w)
    
    def __init_DT(self, docs):
        self.DT = {
            doc_id: {
                topic_id: 1.0
                for topic_id in range(len(docs))
            }
            for doc_id in range(len(docs))
        }

    def __calculate_DT(self, docs):
        for doc_id, bow in enumerate(tqdm(self.bows)):
            prob_mass = 0
            proto_matrix = {
                topic_id: [0 for w in self.WT.keys()]
                for topic_id in range(len(docs))
            }
            prob_mass = 0.0
            for w in bow:
                if not self.is_feature[w]:
                    continue
                for topic_id, prob in self.WT[w].items():
                    proto_matrix[topic_id][self[w]] = prob
                    prob_mass += prob
            if prob_mass:
                _DT = {
                    topic_id: sum([prob / prob_mass for prob in probs])
                    for topic_id, probs in proto_matrix.items()
                }
                self.DT[doc_id] = {
                    topic_id: prob / sum(_DT.values())
                    for topic_id, prob in _DT.items()
                }
            else:
                self.DT[doc_id] = {
                    topic_id: 0.0 for topic_id in proto_matrix.keys()
                }

    def __calculate_WT(self, docs):
        for doc_id, bow in enumerate(tqdm(self.bows)):
            for w in bow:
                if not self.is_feature[w]:
                    continue
                self.WT[w][doc_id] += self.DT[doc_id][doc_id]
        self.WT = {
            w: {
                doc_id: p / len(topics)
                for doc_id, p in topics.items()
            } for w, topics in self.WT.items()
        }



if __name__ == '__main__':

    test = [
        [1, 2, 3, 4, 5] + [random.randrange(5, 1000) for _ in range(random.randrange(5))],
        [1, 2] + [random.randrange(5, 1000) for _ in range(random.randrange(5))],
        [1, 2, 4] + [random.randrange(5, 1000) for _ in range(random.randrange(5))],
        [4, 5] + [random.randrange(5, 1000) for _ in range(random.randrange(5))],
        [4, 5] + [random.randrange(5, 1000) for _ in range(random.randrange(5))]
    ]
    
#     test = [
#         [random.randrange(0, 5) for _ in range(random.randrange(1, 20))] +
#         [random.randrange(0, 50) for _ in range(random.randrange(1, 20))]
#         for _ in range(200)
#     ]
    
    minilda = MiniLDA(
        max_iter=10,
        min_word_freq=1
    )
    minilda(test)

#     for i, x in enumerate(test):
#         print '[%d]' % i, x
