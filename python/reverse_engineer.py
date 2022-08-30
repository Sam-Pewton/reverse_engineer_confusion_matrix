"""Module to reverse engineer all possible matrices from output metrics.

To exclude the optional parameters, set them to -1 in main.

REQUIRED PARAMETERS
-------------------
DECIMAL_PLACES
    This is required to format the calculations to the same size as the target
    values.
CLASS_A_COUNT
    This is required as it formulates the dataset/subset size.
CLASS_B_COUNT
    This is required as it formulates the dataset/subset size.
TARGET_ACCURACY
    This is required as a bare minimum.

OPTIONAL PARAMETERS
-------------------
TARGET_SENSITIVITY
TARGET_SPECIFICITY
TARGET_F1
TARGET_PRECISION

Author
------
Sam Pewton
"""
import pandas as pd
import math

def main():
    """Main method
    """
    ####### MODIFIERS #######
    # Required
    DECIMAL_PLACES = 2
    CLASS_A_COUNT = 981
    CLASS_B_COUNT = 981
    TARGET_ACCURACY = 0.75

    #Optional - set to -1 if not needed
    TARGET_SENSITIVITY = 0.86
    TARGET_SPECIFICITY = 0.64
    TARGET_F1 = 0.77
    TARGET_PRECISION = 0.71
    #########################
    reverse_engineer_confusion_matrices(CLASS_A_COUNT,
                                        CLASS_B_COUNT,
                                        DECIMAL_PLACES,
                                        TARGET_ACCURACY,
                                        TARGET_SENSITIVITY,
                                        TARGET_SPECIFICITY,
                                        TARGET_F1,
                                        TARGET_PRECISION)

def reverse_engineer_confusion_matrices(class_a_count : int,
                                        class_b_count : int,
                                        decimal_places : int,
                                        target_accuracy : float,
                                        target_sensitivity : float,
                                        target_specificity : float,
                                        target_f1 : float,
                                        target_precision : float):
    """Extract all possible confusion matrices that meet the target criteria.

    Output is dumped to a csv file in the project data folder.

    Parameters
    ----------
    class_a_count : int
        the total number of items in class A
    class_b_count : int
        the total number of items in class B
    decimal_places : int
        the number of decimal places to round to
    target_accuracy : float
        the target accuracy to match
    target_sensitivity : float
        the target sensitivity to match
    target_specificity : float
        the target specificity to match
    target_f1 : float
        the target f1 score to match
    target_precision : float
        the target precision score to match

    Returns
    -------
    None.
    """
    # Accuracy score must be between 0 and 1 inclusive
    if target_accuracy < 0 or target_accuracy > 1:
        print("Accuracy metric is not achievable.")
        exit()

    # Total size of set
    total_sample_size = class_a_count + class_b_count

    # Find minimum and maximum correct and incorrect predictions.
    # c = correct, i = incorrect. a|b values partner together.
    c_a, i_a, c_b, i_b = find_positives_vs_negatives(total_sample_size,
                                                     target_accuracy,
                                                     decimal_places)

    # No combinations can achieve the accuracy..
    if c_a == -1:
        print("There are no combinations that can achieve this accuracy.")
        exit()

    # Get all matrices matching the accuracies
    matrices = find_matrices(class_a_count,
                             class_b_count,
                             c_a,
                             i_a,
                             c_b,
                             i_b)

    if target_sensitivity >= 0 or target_sensitivity <= 1:
        matrices = check_sensitivity(matrices,
                                     target_sensitivity,
                                     decimal_places)

    if target_specificity >= 0 or target_specificity <= 1:
        matrices = check_specificity(matrices,
                                     target_specificity,
                                     decimal_places)

    if target_f1 >= 0 or target_f1 <= 1:
        matrices = check_f1(matrices, target_f1, decimal_places)

    if target_precision >= 0 or target_precision <= 1:
        matrices = check_precision(matrices, target_precision, decimal_places)

    if len(matrices) == 0:
        print("There are no combinations meeting this criteria.")
        exit()

    print(str(len(matrices)), "different matrices fit the criteria." \
            "\nExporting data to ../data/output.csv")
    export_to_csv(matrices,
                  target_accuracy,
                  target_sensitivity,
                  target_specificity,
                  target_f1,
                  target_precision)

def check_precision(matrices, target_precision, decimal_places):
    """Check the precision score of all matrices for a given target.

    Any matrices not meeting the target are removed.

    Parameters
    ----------
    matrices : list
        all current matrices
    target_precision : float
        the target precision to achieve
    decimal_places : int
        the number of decimal places to round to

    Returns
    -------
    list
        list of matrices matching the target precision.
    """
    new_matrices = []

    for matrix in matrices:
        TP = matrix[0][0]
        FN = matrix[0][1]
        FP = matrix[1][0]
        TN = matrix[1][1]
        precision = convert_specified_dp(TP/(TP+FP), decimal_places)
        if precision == target_precision:
            new_matrices.append(matrix)

    return new_matrices

def check_f1(matrices : list, target_f1 : float, decimal_places : int):
    """Check the f1 score of all matrices for a given target.

    Any matrices not meeting the target are removed.

    Parameters
    ----------
    matrices : list
        all current matrices
    target_f1 : float
        the target precision to achieve
    decimal_places : int
        the number of decimal places to round to

    Returns
    -------
    list
        list of matrices matching the target f1 score.
    """
    new_matrices = []

    for matrix in matrices:
        TP = matrix[0][0]
        FN = matrix[0][1]
        FP = matrix[1][0]
        TN = matrix[1][1]
        f1 = convert_specified_dp(2*TP/(2*TP+FP+FN), decimal_places)


        if f1 == target_f1:
            new_matrices.append(matrix)

    return new_matrices

def check_sensitivity(matrices : list,
                      target_sensitivity : float,
                      decimal_places : int):
    """Check the sensitivity (TPR) of all matrices for a given target.

    Any matrices not meeting the target are removed.

    Parameters
    ----------
    matrices : list
        all current matrices
    target_sensitivity : float
        the target precision to achieve
    decimal_places : int
        the number of decimal places to round to

    Returns
    -------
    list
        list of matrices matching the target sensitifity score.
    """
    new_matrices = []

    for matrix in matrices:
        TP = matrix[0][0]
        FN = matrix[0][1]
        FP = matrix[1][0]
        TN = matrix[1][1]
        sensitivity = convert_specified_dp(TP/(TP+FN), decimal_places)

        if sensitivity == target_sensitivity:
            new_matrices.append(matrix)

    return new_matrices

def check_specificity(matrices, target_specificity, decimal_places):
    """Check the specificity (TNR) of all matrices for a given target.

    Any matrices not meeting the target are removed.

    Parameters
    ----------
    matrices : list
        all current matrices
    target_specificity : float
        the target precision to achieve
    decimal_places : int
        the number of decimal places to round to

    Returns
    -------
    list
        list of matrices matching the target sensitifity score.
    """
    new_matrices = []

    for matrix in matrices:
        TP = matrix[0][0]
        FN = matrix[0][1]
        FP = matrix[1][0]
        TN = matrix[1][1]
        specificity = convert_specified_dp(TN/(TN+FP), decimal_places)

        if specificity == target_specificity:
            new_matrices.append(matrix)

    return new_matrices

def find_positives_vs_negatives(total_sample_size : int,
                                target_accuracy : float,
                                decimal_places : int):
    """Extract the minima and maxima correct and incorrect predictions.

    These values will be used to determine the values to check.

    Parameters
    ----------
    total_sample_size : int
        the total number of items belonging to both classes
    target_accuracy : float
        the target accuracy to try and achieve
    decimal_places : int
        the total decimal places to round to

    Return
    ------
    int
        The maximum correct predictions
    int
        The minimum incorrect predictions
    int
        The minimum correct predictions
    int
        The maximum incorrect predictions
    """
    # Variables to house stopping conditions for later.
    correct_a = -1
    incorrect_a = -1
    correct_b = -1
    incorrect_b = -1

    for num in range(total_sample_size, 0, -1):
        correct_preds = num
        incorrect_preds = total_sample_size - num
        calculated_accuracy = correct_preds / total_sample_size
        if convert_specified_dp(calculated_accuracy, decimal_places) == target_accuracy:
            if correct_a == -1:
                correct_a = correct_preds
                incorrect_a = incorrect_preds
            else:
                correct_b = correct_preds
                incorrect_b = incorrect_preds

    return correct_a, incorrect_a, correct_b, incorrect_b

def find_matrices(class_a_count : int,
                  class_b_count : int,
                  correct_a : int,
                  incorrect_a : int,
                  correct_b : int,
                  incorrect_b : int):
    """Extract all of the matrices that fit the accuracy criteria

    Parameters
    ----------
    class_a_count : int
        count of items in class a
    class_b_count : int
        count of items in class b
    correct_a : int
        highest number of correct predictions, groups with incorrect_a
    incorrect_a : int
        lowest number of incorrect predictions, groups with correct_a
    correct_b : int
        lowest number of correct predictions, groups with incorrect_b
    incorrect_b : int
        highest number of incorrect predictions, groups with correct_b

    Returns
    -------
    list
        list of all possible matrices ([[TP, FN],[FP, TN]])
    """
    matrices = []
    number_of_combinations = correct_a - correct_b + 1 if correct_b != -1 else 1

    # Get all matrices for all combinations
    for i in range(number_of_combinations):
        # Base matrix
        TP = correct_a - i if correct_a-i < class_a_count else class_a_count - i
        FN = class_a_count - TP
        FP = incorrect_a + i - FN
        TN = class_b_count - FP
        matrices.append([[TP,FN],[FP,TN]])

        while TP > 0 and TN < class_b_count:
            TP -= 1
            FN += 1
            FP -= 1
            TN += 1
            matrices.append([[TP,FN],[FP,TN]])

    return matrices

def convert_specified_dp(number : float, decimal_places : int):
    """Round off a floating point number to a specified amount of decimal
    places.

    Parameters
    ----------
    number : float
        the number to round
    decimal_places : int
        the number of decimal places to round to

    Returns
    -------
    float
        the rounded number
    """
    multiplier = pow(10, decimal_places)
    lhs = math.floor(number * multiplier)
    rhs = (number * multiplier) % 1
    rhs = math.floor(rhs) if rhs < 0.5 else math.ceil(rhs)
    return (lhs + rhs) / multiplier

def export_to_csv(matrices : list,
                  target_accuracy : float,
                  target_sensitivity : float,
                  target_specificity : float,
                  target_f1 : float,
                  target_precision : float):
    """Export all located matrices to output csv.

    Output csv file is located in the data folder of the project.

    Parameters
    ----------
    matrices : list
        all located matrices
    target_accuracy : float
        the target accuracy
    target_sensitivity : float
        the target sensitivity
    target_specificity : float
        the target specificity
    target_f1 : float
        the target f1 score
    target_precision : float
        the target precision

    Returns
    -------
    None.
    """
    data = {
            "TP" : [],
            "FN" : [],
            "FP" : [],
            "TN" : [],
            "Accuracy" : [],
            "Sensitivity" : [],
            "Specificity" : [],
            "F1" : [],
            "Precision" : []
           }

    for matrix in matrices:
        data["TP"].append(matrix[0][0])
        data["FN"].append(matrix[0][1])
        data["FP"].append(matrix[1][0])
        data["TN"].append(matrix[1][1])
        data["Accuracy"].append(target_accuracy)
        data["Sensitivity"].append(target_sensitivity)
        data["Specificity"].append(target_specificity)
        data["F1"].append(target_f1)
        data["Precision"].append(target_precision)

    pd.DataFrame.from_dict(data).to_csv("../data/output.csv")

if __name__ == "__main__":
    main()
