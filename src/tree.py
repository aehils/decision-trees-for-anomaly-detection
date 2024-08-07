from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.metrics import precision_score, recall_score, f1_score
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt


import pandas as pd


# Load prepared data
df = pd.read_csv('prepared_operation_log.csv')

# Split data
X = df[['Timestamp', 'X', 'Y', 'Z', 'Proximity', 'Gripper']]  # features
y = df['Anomaly']  # target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


# Initialisation and training
clf = DecisionTreeClassifier(criterion='entropy')  # specifying 'entropy' as splitting criterion for ID3 approach
clf.fit(X_train, y_train)

# Predict on test set
predictions = clf.predict(X_test)
precision = precision_score(y_test, predictions)
recall = recall_score(y_test, predictions)
f1 = f1_score(y_test, predictions)

print(f"Tree depth: {clf.tree_.max_depth}")
print(f"Number of leaves: {clf.tree_.n_leaves}")
print(f"Precision: {precision}")
print(f"Recall: {recall}")
print(f"F1 Score: {f1}")

cm = confusion_matrix(y_test, predictions)
disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                              display_labels=clf.classes_)  
disp.plot(cmap=plt.cm.Blues)
plt.title('Confusion Matrix for Decision Tree Classifier')
plt.show()

# confusion matrix elements
tn, fp, fn, tp = cm.ravel()

# FPR and FNR
fpr = fp / (fp + tn)
fnr = fn / (fn + tp)

print("False Positive Rate: {:.2f}".format(fpr))
print("False Negative Rate: {:.2f}".format(fnr))

# DT visualiser
plt.figure(figsize=(10,5))  
plot_tree(clf, filled=True, 
        feature_names=['Timestamp', 'X', 'Y', 'Z', 'Proximity', 'Gripper'],
        class_names=['Normal', 'Anomalous'],
        fontsize=7,  
        proportion=False,  
        precision=2,
        node_ids=True,
        impurity=False)
plt.show()
