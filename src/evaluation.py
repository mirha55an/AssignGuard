import pandas
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score

def evaluate_model(similarity_matrix, doc_names, labels_csv, threshold=0.70):
    # Load labels CSV 
    labels_df = pandas.read_csv(labels_csv)
    
    actual_labels = []
    predicted_labels = []
    
    for _, row in labels_df.iterrows():
        
        doc1 = row['doc1']
        doc2 = row['doc2']
        actual_label = row['label']
        
        #Find indexes of documents
        idx1 = doc_names.index(doc1)
        idx2 = doc_names.index(doc2)
        
        # Get similarity score from matrix 
        similarity_score = similarity_matrix[idx1][idx2]
        
        # Convert Similarity Score into prediction
        predicted_label = 1 if similarity_score >= threshold else 0
        
        # Store labels
        actual_labels.append(actual_label) 
        predicted_labels.append(predicted_label)
        
        # Compute evaluation metrics 
        precision = precision_score(actual_labels, predicted_labels) 
        recall = recall_score(actual_labels, predicted_labels) 
        f1 = f1_score(actual_labels, predicted_labels)
        
        # Print results 
        print(f"Threshold: {threshold}") 
        print(f"Precision: {precision:.2f}") 
        print(f"Recall: {recall:.2f}") 
        print(f"F1 Score: {f1:.2f}") 
        # Return results 
        return { "precision": precision, "recall": recall, "f1_score": f1 }