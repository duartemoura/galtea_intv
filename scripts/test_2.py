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
    correct = sum(1 for gt, pred in zip(ground_truths, predictions) if gt == pred)
    total = len(ground_truths)
    accuracy = (correct / total) * 100
    
    # Calculate confusion matrix metrics
    true_positives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                        if gt == 'Use RAG' and pred == 'Use RAG')
    false_positives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                         if gt == 'Skip RAG' and pred == 'Use RAG')
    false_negatives = sum(1 for gt, pred in zip(ground_truths, predictions) 
                         if gt == 'Use RAG' and pred == 'Skip RAG')
    
    precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
    recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
    
    # Calculate weighted accuracy based on confidence scores
    weighted_correct = sum(score/100 for gt, pred, score in zip(ground_truths, predictions, confidence_scores) 
                          if gt == pred)
    weighted_accuracy = (weighted_correct / len(ground_truths)) * 100
    
    return {
        'accuracy': accuracy,
        'weighted_accuracy': weighted_accuracy,
        'precision': precision * 100,
        'recall': recall * 100
    }

def plot_performance_metrics(metrics_dict):
    """Plot performance metrics for all models."""
    models = list(metrics_dict.keys())
    metrics = ['accuracy', 'weighted_accuracy', 'precision', 'recall']
    
    # Set up the plot
    plt.figure(figsize=(15, 6))
    x = range(len(models))
    width = 0.2  # Reduced width to accommodate more metrics
    
    # Create bars for each metric
    for i, metric in enumerate(metrics):
        values = [metrics_dict[model][metric] for model in models]
        plt.bar([xi + i*width for xi in x], values, width, label=metric.replace('_', ' ').title())
    
    # Customize the plot
    plt.xlabel('Models')
    plt.ylabel('Score (%)')
    plt.title('RAG Performance Metrics by Model')
    plt.xticks([xi + width*1.5 for xi in x], models, rotation=45)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig('scripts/rag_performance_metrics.png')
    plt.close()

def test_rag_worthy():
    # Initialize the chat system
    chat = GalteaChat(documents_dir="data")
    
    # Test questions
    test_questions = [
        # Questions that should be RAG-worthy (about document content)
        "¿Cada cuánto se debe cambiar el aceite del sistema DSG?",
        "¿Qué incluye la revisión gratuita de 30 puntos al llegar a un Servicio Oficial?",
        "¿Qué operaciones cubre el Mantenimiento Plus Volkswagen?",
        "¿Qué beneficios tiene contratar un seguro con Volkswagen Seguros by Zurich?",
        
        # Questions that should not be RAG-worthy (general knowledge)
        "¿Cómo funciona un motor de combustión interna?",
        "¿Cuál es la presión ideal de los neumáticos en un coche compacto?",
        "¿Qué hacer si un coche eléctrico no arranca?",
        
        # Edge cases
        "¿Qué servicios están incluidos en una inspección técnica en Volkswagen?",  
        "¿Qué tipo de aceite recomienda Volkswagen para sus motores?",
        "¿Dónde puedo encontrar el historial digital de mantenimiento de mi Volkswagen?",
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
        print(f"Accuracy: {metrics['accuracy']:.2f}%")
        print(f"Weighted Accuracy: {metrics['weighted_accuracy']:.2f}%")
        print(f"Precision: {metrics['precision']:.2f}%")
        print(f"Recall: {metrics['recall']:.2f}%")
    
    # Plot the results
    plot_performance_metrics(metrics_dict)
    print("\nPerformance plot has been saved as 'scripts/rag_performance_metrics.png'")
    print("\n=== End of RAG-Worthy Tests ===")

if __name__ == "__main__":
    test_rag_worthy() 