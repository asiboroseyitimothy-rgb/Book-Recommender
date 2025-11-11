import pandas as pd
import numpy as np

# number of users and books
n_users = 50
n_books = 40

np.random.seed(42)
ratings_data = []

for user_id in range(1, n_users + 1):
    for book_id in range(1, n_books + 1):
        # 60% chance user didn't rate the book
        if np.random.rand() < 0.6:
            continue
        rating = np.random.randint(1, 6)  # rating 1-5
        ratings_data.append([user_id, book_id, rating])

# create DataFrame
ratings_df = pd.DataFrame(ratings_data, columns=['user_id','book_id','rating'])

# save to CSV
ratings_df.to_csv('data/ratings.csv', index=False)
print("ratings.csv created successfully!")
