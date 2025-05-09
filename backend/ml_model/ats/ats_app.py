# -*- coding: utf-8 -*-
"""ATS app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/19Ec8aDqVzEIWhprsEfnWgSmhJTGUk1MC
"""

from flask import Flask, request, jsonify
import torch
from transformers import BertForSequenceClassification, BertTokenizerFast

app = Flask(__name__)

# Load the fine-tuned model and tokenizer
model = BertForSequenceClassification.from_pretrained("./fine_tuned_model")
tokenizer = BertTokenizerFast.from_pretrained("./fine_tuned_model")
model.eval()

@app.route("/ats/sample", methods=["GET"])
def sample():
    """
    Returns a sample JSON record for evaluation.
    """
    sample_input = {
        "job_description": "Looking for a data scientist with experience in Python and machine learning.",
        "resume": "Experienced data scientist skilled in Python, machine learning, and data analysis."
    }
    return jsonify(sample_input)

@app.route("/ats/explain", methods=["GET"])
def explain():
    """
    Explains the input fields.
    """
    explanation = (
        "The 'job_description' field should contain the full job posting text. "
        "The 'resume' field should include the candidate's resume text. "
        "Both will be combined and tokenized by our model to determine if the candidate is a good match."
    )
    return explanation

@app.route("/ats/evaluate", methods=["POST"])
def evaluate():
    """
    Accepts JSON input and returns a prediction.
    """
    data = request.get_json()
    job_description = data["job_description"]
    resume = data["resume"]

    # Combine the texts using a [SEP] token
    combined_text = job_description + " [SEP] " + resume
    inputs = tokenizer(combined_text, return_tensors="pt", truncation=True, padding="max_length", max_length=256)

    with torch.no_grad():
        outputs = model(**inputs)

    logits = outputs.logits
    predicted_class = torch.argmax(logits, dim=1).item()

    # Map prediction to a label (assuming 1: Match, 0: No Match)
    result = "Match" if predicted_class == 1 else "No Match"
    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(debug=True)