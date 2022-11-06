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
import csv
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
    min_max_values = find_positives_vs_negatives(total_sample_size,
                                                 target_accuracy,
                                                 decimal_places)

    # No combinations can achieve the accuracy..
    if min_max_values[0] == -1:
        print("There are no combinations that can achieve this accuracy.")
        exit()

    # Trigger the workload
    find_matrices(class_a_count,
                  class_b_count,
                  min_max_values,
                  target_accuracy,
                  target_sensitivity,
                  target_specificity,
                  target_f1,
                  target_precision,
                  decimal_places)

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

    return [correct_a, incorrect_a, correct_b, incorrect_b]

def find_matrices(class_a_count : int,
                  class_b_count : int,
                  min_max_values : list,
                  target_accuracy : float,
                  target_sensitivity : float,
                  target_specificity : float,
                  target_f1 : float,
                  target_precision : float,
                  decimal_places : int):
    """Extract all of the matrices that fit the accuracy criteria and stream
    into a .csv file called output_python.csv in the data folder of the project

    Parameters
    ----------
    class_a_count : int
        count of items in class a
    class_b_count : int
        count of items in class b
    min_max_values : list
        min max combination values
    target_accuracy : float
        target accuracy value
    target_sensitivity : float
        target sensitivity value
    target_specificity : float
        target specificity value
    target_f1 : float
        target f1 value
    target_precision : float
        target precision value
    decimal_places : int
        decimal places to round to

    Returns
    -------
    list
        list of all possible matrices ([[TP, FN],[FP, TN]])
    """
    number_of_combinations = min_max_values[0] - min_max_values[2] + 1 if min_max_values[2] != -1 else 1

    # Stream data into .csv file as its calculated
    with open("../data/output_python.csv", "w", newline="\n") as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(["TP","FN","FP","TN","Accuracy","Sensitivity","Specificity","F1","Precision","\n"])

        # Get all matrices for all combinations
        for i in range(number_of_combinations):
            # Base matrix
            TP = min_max_values[0] - i if min_max_values[0]-i < class_a_count else class_a_count - i
            FN = class_a_count - TP
            FP = min_max_values[1] + i - FN
            TN = class_b_count - FP

            if check_metric(TP,FN,FP,TN, target_sensitivity, target_specificity, target_f1, target_precision, decimal_places):
                writer.writerow([str(TP), str(FN), str(FP), str(TN), str(target_accuracy), str(target_sensitivity), str(target_specificity), str(target_f1), str(target_precision),"\n"])

            while TP > 0 and TN < class_b_count:
                TP -= 1
                FN += 1
                FP -= 1
                TN += 1
                if check_metric(TP,FN,FP,TN, target_sensitivity, target_specificity, target_f1, target_precision, decimal_places):
                    writer.writerow([str(TP), str(FN), str(FP), str(TN), str(target_accuracy), str(target_sensitivity), str(target_specificity), str(target_f1), str(target_precision),"\n"])

def check_metric(TP : float,
                 FN : float,
                 FP : float,
                 TN : float,
                 target_sensitivity : float,
                 target_specificity : float,
                 target_f1 : float,
                 target_precision : float,
                 decimal_places : int):
    """Check the matrix against all of the metric criteria

    Parameters
    ----------
    TP : float
        TP value
    FN : float
        FN value
    FP : float
        FP value
    TN : float
        TN value
    target_sensitivity : float
        target sensitivity value
    target_specificity : float
        target specificity value
    target_f1 : float
        target f1 value
    target_precision : float
        target precision value
    decimal_places : int
        decimal places to round to

    Returns
    -------
    bool
        if the criteria is met or not
    """
    meets_criteria = True

    if convert_specified_dp(TP/(TP+FN), decimal_places) != target_sensitivity or target_sensitivity == -1:
        meets_criteria = False
    if convert_specified_dp(TN/(TN+FP), decimal_places) != target_specificity or target_specificity == -1:
        meets_criteria = False
    if convert_specified_dp(2*TP/(2*TP+FP+FN), decimal_places) != target_f1 or target_f1 == -1:
        meets_criteria = False
    if convert_specified_dp(TP/(TP+FP), decimal_places) != target_precision or target_precision == -1:
        meets_criteria = False
    return meets_criteria

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

if __name__ == "__main__":
    main()
