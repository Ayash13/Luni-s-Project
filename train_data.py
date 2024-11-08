import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib

# Load the cleaned food and non-food datasets
food_data = pd.read_csv('cleaned_food_names.csv')
non_food_data = pd.read_csv('cleaned_non-food_names.csv')

# Add a 'label' column to mark entries as 'food' or 'non-food'
food_data['label'] = 'food'
non_food_data['label'] = 'non-food'

# Combine both datasets
data = pd.concat([food_data, non_food_data], ignore_index=True)

# Separate features (text) and labels
X = data['name']
y = data['label']

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a pipeline with TfidfVectorizer and a RandomForestClassifier
pipeline = Pipeline([
    ('tfidf', TfidfVectorizer(max_features=1000, min_df=2, max_df=0.9)),
    ('rf', RandomForestClassifier(class_weight='balanced'))
])

# Set up GridSearchCV for tuning the RandomForest model
param_grid = {
    'rf__n_estimators': [100, 200],
    'rf__max_depth': [10, 20, None]
}
grid_search = GridSearchCV(pipeline, param_grid, cv=3, scoring='accuracy', n_jobs=-1)

print("Training the model with grid search...")
grid_search.fit(X_train, y_train)

# Get the best model from grid search
best_model = grid_search.best_estimator_

# Test the model accuracy
accuracy = best_model.score(X_test, y_test)
print(f"Model accuracy on test set: {accuracy:.2f}")

# Save the best model
joblib.dump(best_model, 'food_classifier_model_rf.joblib')
print("Model saved as 'food_classifier_model_rf.joblib'")
