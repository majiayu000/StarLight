import math
import pandas as pd


class UserCf:
    def __init__(self) -> None:
        self.file_path = "data/ratings.csv"
        self._init_frame()

    def _init_frame(self):
        self.frame = pd.read_csv(self.file_path)

    @staticmethod
    def _consine_sim(target_movies, movies):
        # & means union class....
        union_len = len(set(target_movies) & set(movies))
        if union_len == 0:
            return 0
        product = len(target_movies) * len(movies)
        consine = union_len / math.sqrt(product)
        return consine

    def _get_top_n_users(self, target_user_id, top_n):
        target_movies = self.frame[self.frame["UserId"] == target_user_id]["MovieID"]
        other_users_id = [i for i in set(self.frame["UserId"]) if i != target_user_id]
        other_movies = [
            self.frame[self.frame["UserId"]] == i["MovieID"] for i in other_user_id
        ]

        sim_list = [self._consine_sim(target_movies, movies) for movies in other_movies]
        sim_list = sorted(
            zip(other_users_id, sim_list), key=lambda x: x[1], reverse=True
        )
