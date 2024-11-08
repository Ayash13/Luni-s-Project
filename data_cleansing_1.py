import pandas as pd

file_path = 'non_food_items.csv'
data = pd.read_csv(file_path)

cleaned_data = data[['name']]

print(cleaned_data.head())

cleaned_data.to_csv('cleaned_non-food_names.csv', index=False)
