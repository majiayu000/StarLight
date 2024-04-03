import random
import pickle
import pandas as pd
import numpy as np
from math import exp


class Corpus:
    items_dict_path = "data/items_dict.dict"

    @classmethod
    def pre_process(cls):
        file_path = "data/rating.csv"
        cls.frame = pd.read_csv(file_path)
        cls.user_ids = set(cls.frame["UserID"].values)
        cls.item_ids = set(cls.frame["MovieID"].values)
        cls.item_dicts = {
            user_id: cls._get_pos_neg_item(user_id) for user_id in list(cls.user_ids)
        }
        cls.save()

    @classmethod
    def _get_pos_neg_item(cls, user_id):
        print(f"Process: {user_id}")
        pos_item_ids = set(cls.frame[cls.frame["UserID"] == user_id]["MovieID"])
        neg_item_ids = cls.item_ids ^ pos_item_ids
        neg_item_ids = list(neg_item_ids)[: len(pos_item_ids)]
        item_dict = {}
        for item in pos_item_ids:
            item_dict[item] = 1
        for item in neg_item_ids:
            item_dict[item] = 0
        return item_dict

    @classmethod
    def save(cls):
        with open(cls.items_dict_path, "rb") as f:
            items_dict = pickle.load(f)
        return items_dict


class LFM:
    def __init__(self) -> None:
        self.class_count = 5
        self.iter_count = 5
        self.lr = 0.02
        self.lam = 0.01
        self._init_mode()

    def _init_model(self):
        file_path = "data/rating.csv"
        self.dataframe = pd.read_csv(file_path)
        self.user_ids = set(self.dataframe["UserID"].values)
        self.item_ids = set(self.dataframe["MovieID"].values)
        self.items_dict = Corpus.load()

        array_p = np.random.rand(len(self.user_ids), self.class_count)
        array_q = np.random.rand(len(self.item_ids), self.class_count)
        self.p = pd.DataFrame(array_p, columns=range(0, self.class_count))
        self.q = pd.DataFrame(array_q, columns=range(0, self.class_count))

    def _predict(self, user_id, item_id):
        p = np.array(self.p.ix[user_id].values)
        q = np.array(self.q.ix[item_id].values)
        r = (p * q).sum()
        logit = 1.0 / (1 + exp(-r))
        return logit

    def _loss(self, user_id, item_id, y, step):
        loss = y - self._predict(user_id, item_id)
        print(f"Step: {step}, user_id: {user_id}, y: {y}, loss: {loss}")
        return loss

    def _optimize(self, user_id, item_id, e):
        gradient_p = -e * self.q.ix[item_id].values
        l2_p = self.lam * self.p.ix[user_id].values
        delta_p = self.lr * (gradient_p - l2_p)

        gradient_q = -e * self.p.ix[user_id].values
        l2_q = self.lam * self.q.ix[item_id].values
        delta_q = self.lr * (gradient_q - l2_q)

        self.p.loc[user_id] -= delta_p
        self.q.loc[item_id] -= delta_q

    def train(self):
        for step in range(self.iter_count):
            for user_id, item_dict in self.items_dict.items():
                for item_id, y in item_dict.items():
                    e = self._loss(user_id, item_id, y, step)
                    self._optimize(user_id, item_id, e)
            self.lr *= 0.9
        self.save()

    def predict(self, user_id, top_n=10):
        self.load()
        user_item_ids = set(
            self.dataframe[self.dataframe["UserID"] == user_id]["MovieID"]
        )
        other_item_ids = self.item_ids ^ user_item_ids
        interest_list = [self._predict(user_id, item_id) for item_id in other_item_ids]
        candidates = sorted(
            zip(list(other_item_ids), interest_list), key=lambda x: x[1], reverse=True
        )
        return candidates[:top_n]

    def save(self):
        self.p.to_csv("data/p.csv", index=False)
        self.q.to_csv("data/q.csv", index=False)
