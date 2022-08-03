# import numpy as np
# import pandas as pd
# from sklearn.metrics import confusion_matrix, classification_report

# def mean_absolute_percentage_error(y_true, y_pred):
#     """Get Mean Absolute Percentage Error""" 
#     y_true, y_pred = np.array(y_true), np.array(y_pred)
#     return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


# def get_confusion_matrix(array_true, array_pred, classes):
#     """Create Confusion Matrix for Multiclass Classification"""
#     cm = pd.DataFrame(confusion_matrix(array_true, array_pred).T, columns=classes, index=classes)
#     cm.columns.names = ["True"]
#     cm.index.names = ["Predicted"]
#     if len(classes) == 2:
#         return cm.iloc[::-1, ::-1]
#     else:
#         return cm
    
# def get_clf_report(array_true, array_pred, classes):
#     """Create Performance Report for Classification Model"""
#     report = pd.DataFrame(classification_report(array_true, array_pred, target_names=[str(c) for c in classes], output_dict=True)).T
#     report.loc["accuracy"] = np.array([np.nan, np.nan, report.loc["accuracy", "f1-score"], report.loc["macro avg", "support"]])
#     return report