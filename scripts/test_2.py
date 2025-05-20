import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

from src.core import GalteaChat
from src.utils import should_use_rag

def calculate_metrics(ground_truths, predictions, confidence_scores):
    """Calculate accuracy metrics."""
    # Calculate confusion matrix metrics
    true_positives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                        if gt == 'Use RAG' and pred == 'Use RAG')
    false_positives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                         if gt == 'Skip RAG' and pred == 'Use RAG')
    false_negatives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                         if gt == 'Use RAG' and pred == 'Skip RAG')
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    # Calculate F1 score
    f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    # Calculate weighted accuracy based on confidence scores
    weighted_correct = sum(score/100 for gt, pred, score in zip(ground_truths, predictions, confidence_scores) 
                          if gt == pred)
    weighted_accuracy = (weighted_correct / len(ground_truths)) * 100
    
    return {
        'weighted_accuracy': weighted_accuracy,
        'f1_score': f1_score * 100
    }

def plot_performance_metrics(metrics_dict):
    """Plot performance metrics for all models."""
    models = list(metrics_dict.keys())
    metrics = ['weighted_accuracy', 'f1_score']
    
    # Set up the plot
    plt.figure(figsize=(10, 6))
    x = range(len(models))
    width = 0.35  # Adjusted width for two metrics
    
    # Create bars for each metric
    for i, metric in enumerate(metrics):
        values = [metrics_dict[model][metric] for model in models]
        plt.bar([xi + i*width for xi in x], values, width, label=metric.replace('_', ' ').title())
    
    # Customize the plot
    plt.xlabel('Models')
    plt.ylabel('Score (%)')
    plt.title('RAG Performance Metrics by Model')
    plt.xticks([xi + width/2 for xi in x], models, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('scripts/rag_performance_metrics.png')
    plt.close()

def test_rag_worthy():
    # Initialize the chat system
    chat = GalteaChat(documents_dir="docs")
    
    # Test questions
    test_questions = [
        # Questions that should be RAG-worthy (about document content)
        "How often should the DSG system oil be changed?",
        "What is included in the free 30-point inspection at an Official Service?",
        "What operations are covered by Volkswagen Plus Maintenance?",
        "What are the benefits of getting insurance with Volkswagen Insurance by Zurich?",
        
        # Questions that should not be RAG-worthy (general knowledge)
        "How does an internal combustion engine work?",
        "What is the ideal tire pressure for a compact car?",
        "What to do if an electric car won't start?",
        
        # Edge cases
        "What services are included in a technical inspection at Volkswagen?",
        "What type of oil does Volkswagen recommend for their engines?",
        "Where can I find the digital maintenance history of my Volkswagen?",
    ]
    
    # Load ground truths
    ground_truths_df = pd.read_csv('scripts/rag_ground_truths.csv')
    true_decisions = ground_truths_df['Decision'].tolist()
    confidence_scores = ground_truths_df['Confidence Score'].tolist()
    
    print("\n=== Testing RAG-Worthy Functionality ===")
    print("Testing with different models and questions...\n")
    
    # Test with different models
    models = ["gpt-4.1-nano", "gpt-4.1-mini", "gpt-4o-mini"]
    metrics_dict = {}
    
    for model in models:
        print(f"\n=== Testing with model: {model} ===")
        predictions = []
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            
            # Get document summaries
            summaries = chat.vector_db.get_all_summaries()
            
            # Check if RAG-worthy
            is_worthy = should_use_rag(question, summaries, model_name=model)
            prediction = 'Use RAG' if is_worthy else 'Skip RAG'
            predictions.append(prediction)
            
            print(f"Final decision: {prediction}")
            print("-" * 50)
        
        # Calculate metrics for this model
        metrics = calculate_metrics(true_decisions, predictions, confidence_scores)
        metrics_dict[model] = metrics
        
        # Print metrics
        print(f"\nModel Performance Metrics:")
        print(f"Weighted Accuracy: {metrics['weighted_accuracy']:.2f}%")
        print(f"F1 Score: {metrics['f1_score']:.2f}%")
    
    # Plot the results
    plot_performance_metrics(metrics_dict)
    print("\nPerformance plot has been saved as 'scripts/rag_performance_metrics.png'")
    print("\n=== End of RAG-Worthy Tests ===")

if __name__ == "__main__":
    test_rag_worthy() 