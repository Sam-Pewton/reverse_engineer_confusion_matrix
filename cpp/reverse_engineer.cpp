/**
 * CPP file to reverse engineer all possible matrices from output metrics.
 *
 * To exclude the optional parameters, set them to -1 in the main method.
 * 
 */
#include <iostream>
#include <cassert>
#include <iomanip>
#include <cmath>
#include <stdlib.h>
#include <vector>
#include <array>
#include <fstream>
#include <cstdio>

void reverse_engineer_confusion_matrices(int, int, int,
		double, double, double, double, double);
int * find_positives_vs_negatives(int, double, int);
double round_dp(double,int);
void find_matrices(int, int, int *, double, double,
		double, double, double, int);
bool check_metric(double, double, double, double, double, double, double,
		double, int);

/**
 * Main method
 *
 * Adjust the values in the modifiers to your target
 */
int main(){
	////////////// MODIFIERS//////////////
	const int DECIMAL_PLACES = 2;
	const int CLASS_A_COUNT = 981;
	const int CLASS_B_COUNT = 981;
	const double TARGET_ACCURACY = 0.75;

	// Optional modifiers - set to -1 if not needed.
	const double TARGET_SENSITIVITY = 0.86;
	const double TARGET_SPECIFICITY = 0.64;
	const double TARGET_F1 = 0.77;
	const double TARGET_PRECISION = 0.71;
	//////////////////////////////////////

	// Assertions..
	assert(DECIMAL_PLACES >= 0);
	assert(CLASS_A_COUNT && CLASS_B_COUNT > 0);
	assert(TARGET_ACCURACY >= 0 && TARGET_ACCURACY <= 1);
	assert((TARGET_SENSITIVITY >= 0 && TARGET_SENSITIVITY <= 1) ||
			TARGET_SENSITIVITY == -1);
	assert((TARGET_SPECIFICITY >= 0 && TARGET_SPECIFICITY <= 1) ||
			TARGET_SPECIFICITY == -1);
	assert((TARGET_F1 >= 0 && TARGET_F1 <= 1) || TARGET_F1 == -1);
	assert((TARGET_PRECISION >= 0 && TARGET_PRECISION <= 1) ||
			TARGET_PRECISION == -1);

	// Trigger main workload
	reverse_engineer_confusion_matrices(
			CLASS_A_COUNT,
			CLASS_B_COUNT,
			DECIMAL_PLACES,
			TARGET_ACCURACY,
			TARGET_SENSITIVITY,
			TARGET_SPECIFICITY,
			TARGET_F1,
			TARGET_PRECISION);

	return(0);
}

/**
 * reverse_engineer_confusion_matrix - Extract all possible confusion matrices
 * that meet the following criteria.
 *
 * Output is dumped to a csv file in the project data folder.
 *
 * Parameters
 *   int - the class size of class A
 *   int - the class size of class B
 *   int - the number of decimal places to round to
 *   double - the target accuracy
 *   double - the target sensitivity
 *   double - the target specificity
 *   double - the target f1 score
 *   double - the target precision
 */
void reverse_engineer_confusion_matrices(
		int class_a_count,
		int class_b_count,
		int decimal_places,
		double target_accuracy,
		double target_sensitivity,
		double target_specificity,
		double target_f1,
		double target_precision
		)
{
	int total_sample_size = class_a_count + class_b_count;

	// Extract the min max values for correct vs incorrect.
	int * min_max_values = find_positives_vs_negatives(
			total_sample_size,
			target_accuracy,
			decimal_places);

	// No combinations exit
	if (*(min_max_values) == -1)
	{
		std::cout << "There are no combinations that can achieve this accuracy." <<
			std::endl;
		exit(0);
	}

	// Calculate each of the matrices that are possible
	find_matrices(class_a_count, class_b_count, min_max_values,
			target_accuracy, target_sensitivity, target_specificity, target_f1,
			target_precision, decimal_places);
}

/**
 * check_metric - check the current state of the confusion matrix against all
 * of the target values.
 *
 * Parameters
 *   double - casted double version of TP for more mathematical accuracy
 *   double - casted double version of FN for more mathematical accuracy
 *   double - casted double version of FP for more mathematical accuracy
 *   double - casted double version of TN for more mathematical accuracy
 *   double - the target sensitivity
 *   double - the target specificity
 *   double - the target f1 score
 *   double - the target precision
 *   int - the number of decimal places to round to
 *
 * Returns
 *   bool - if the criteria is met or not
 */
bool check_metric(
		double TP,
		double FN,
		double FP,
		double TN,
		double target_sensitivity,
		double target_specificity,
		double target_f1,
		double target_precision,
		int decimal_places
		)
{
	bool meets_criteria = true;

	// Cycle through each of the metrics, calc and check against the targets
	if (round_dp(TP/(TP+FN), decimal_places) != target_sensitivity || target_sensitivity == -1)
		meets_criteria = false;
	if (round_dp(TN/(TN+FP), decimal_places) != target_specificity || target_specificity == -1)
		meets_criteria = false;
	if (round_dp(2*TP/(2*TP+FP+FN), decimal_places) != target_f1 || target_f1 == -1)
		meets_criteria = false;
	if (round_dp(TP/(TP+FP), decimal_places) != target_precision || target_precision == -1)
		meets_criteria = false;
	return meets_criteria;
}

/**
 * find_matrices - extract all of the matrices that fit the accuracy criteria.
 *
 * Parameters
 *   int - count of items in class A
 *   int - count of items in class B
 *   int * - the pointer to the min/max values array
 *   double - the target accuracy
 *   double - the target sensitivity
 *   double - the target specificity
 *   double - the target f1 score
 *   double - the target precision
 *   int - the number of decimal places to round to
 */
void find_matrices(
		int class_a_count,
		int class_b_count,
		int * min_max_values,
		double target_accuracy,
		double target_sensitivity,
		double target_specificity,
		double target_f1,
		double target_precision,
		int decimal_places
		)
{
	// Calculate the total number of combinations.
	int combinations = 1;
	if (*(min_max_values + 2) != -1)
		combinations = *(min_max_values) - *(min_max_values + 2) + 1;

	std::ofstream file;
	file.open("../data/cpp_output2.csv");
	file << "TP,FN,FP,TN,Accuracy,Sensitivity,Specificity,F1,Precision,\n";

	// Calculate and store the matrices.
	//std::vector<std::array<int,4>> matrices;
	for (int i = 0; i < combinations; i++)
	{
		// Base matrix
		int TP = class_a_count - i;
		if ((*(min_max_values) - i) < class_a_count)
			TP = *(min_max_values) - i;
		int FN = class_a_count - TP;
		int FP = *(min_max_values + 1) + i - FN;
		int TN = class_b_count - FP;

		if (check_metric((double)TP,(double)FN,(double)FP,(double)TN,
					target_sensitivity, target_specificity, target_f1, target_precision,
					decimal_places))
		{
			file << TP << "," << FN << "," << FP << "," << TN << ",";
			file << target_accuracy << ",";
			file << target_sensitivity << ",";
			file << target_specificity << ",";
			file << target_f1 << ",";
			file << target_precision << ",\n";
		}

		while (TP > 0 && TN < class_b_count)
		{
			--TP;
			++FN;
			--FP;
			++TN;

			if (check_metric((double)TP,(double)FN,(double)FP,(double)TN,
						target_sensitivity, target_specificity, target_f1, target_precision,
						decimal_places))
			{
				file << TP << "," << FN << "," << FP << "," << TN << ",";
				file << target_accuracy << ",";
				file << target_sensitivity << ",";
				file << target_specificity << ",";
				file << target_f1 << ",";
				file << target_precision << ",\n";
			}
		}
	}
	file.close();
}

/**
 * find_positives_vs_negatives - Extract the minima and maxima correct and
 * incorrect predictions.
 *
 * These values will be used to determine the values to check.
 *
 * Parameters
 *   int - the total sample size
 *   double - the target accuracy
 *   int - the total number of decimal places to round to
 *
 * Returns
 *   int * - pointer to static array
 *           max correct, min incorrect, min correct, max incorrect.
 */
int * find_positives_vs_negatives(
		int total_sample_size,
		double target_accuracy,
		int decimal_places
		)
{
	static int min_max_values[4] = {-1,-1,-1,-1};

	for(int i = total_sample_size; i > 0; i--)
	{
		int correct_preds = i;
		int incorrect_preds = total_sample_size - i;
		double calculated_accuracy = (double)correct_preds / (double)total_sample_size;

		if(round_dp(calculated_accuracy, decimal_places) == target_accuracy)
		{
			if(min_max_values[0] == -1)
			{
				min_max_values[0] = correct_preds;
				min_max_values[1] = incorrect_preds;
			}
			else
			{
				min_max_values[2] = correct_preds;
				min_max_values[3] = incorrect_preds;
			}
		}
	}
	return min_max_values;
}

/**
 * convert_specified_dp - round off a double precision number to a specified
 * amount of decimal places.
 *
 * Parameters
 *   double - number to round
 *   int - number of decimal places to round to
 *
 * Returns
 *   double - the rounded number
 */
double round_dp(double number, int decimal_places)
{
	double modifier = pow(10.0f, (double)decimal_places);
	return round(number * modifier) / modifier;
}
