from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import pandas as pd

# Load data
df = pd.read_csv('prepared_operation_log.csv')


# features and target
X = df[['Timestamp', 'X', 'Y', 'Z', 'Proximity', 'Gripper']]  # Including Timestamp
y = df['Anomaly']


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# feature scaling
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# classifier initialisation
knn = KNeighborsClassifier(n_neighbors=5)

# classifier training
knn.fit(X_train_scaled, y_train)

predictions = knn.predict(X_test_scaled)

# evaluation - classification metrics
from sklearn.metrics import classification_report
print(classification_report(y_test, predictions))

# Generate the confusion matrix
cm = confusion_matrix(y_test, predictions)

# confusion matrix visualiser
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=knn.classes_)
disp.plot(cmap=plt.cm.Blues)
plt.title('Confusion Matrix for KNN Classifier')
plt.show()
