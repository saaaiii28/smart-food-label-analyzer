import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import joblib

def train_model():

    df = pd.read_csv("../data/food_dataset.csv")

    def classify(row):
        if row["sugar"] > 15 or row["sat_fat"] > 5:
            return "Risky"
        elif row["sodium"] > 300:
            return "Moderate"
        else:
            return "Safe"

    df["label"] = df.apply(classify, axis=1)

    X = df[["sugar", "sat_fat", "sodium", "fiber", "trans_fat"]]
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    model = LogisticRegression(max_iter=1000)
    model.fit(X_scaled, y)

    joblib.dump(model, "model.pkl")
    joblib.dump(scaler, "scaler.pkl")


def load_model():
    model = joblib.load("model.pkl")
    scaler = joblib.load("scaler.pkl")
    return model, scaler


if __name__ == "__main__":
    train_model()