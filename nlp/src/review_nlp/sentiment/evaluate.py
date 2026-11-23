from sklearn.metrics import classification_report, confusion_matrix, f1_score


def evaluate(y_true, y_pred, labels: list[str]) -> dict:
    return {
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", labels=labels)),
        "report": classification_report(y_true, y_pred, labels=labels, zero_division=0),
        "confusion": confusion_matrix(y_true, y_pred, labels=labels),
    }