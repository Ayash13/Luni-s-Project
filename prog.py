import joblib

# Load the trained Random Forest model
model = joblib.load('food_classifier_model_rf.joblib')

# Function to classify input text as "food" or "non-food"
def classify_item(text):
    prediction = model.predict([text])[0]
    return prediction

# User input loop
print("Enter an item to check if it's food or non-food (or type 'exit' to quit):")
while True:
    user_input = input("Item name: ")
    if user_input.lower() == 'exit':
        break
    result = classify_item(user_input)
    print(f"The item '{user_input}' is classified as: {result}")
