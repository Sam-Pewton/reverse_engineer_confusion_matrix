/**
 * CPP file to reverse engineer all possible matrices from output metrics.
 *
 * To exclude the optional parameters, set them to -1 in the main method.
 */
#include <iostream>
#include <cassert>
#include <iomanip>
#include <cmath>
#include <stdlib.h>
#include <vector>
#include <array>

void reverse_engineer_confusion_matrices(int,int,int,
		double,double,double,double,double);
int * find_positives_vs_negatives(int,double,int);
double round_dp(double,int);
std::vector<std::array<int, 4>> find_matrices(int, int, int *);
std::vector<std::array<int, 4>> check_metric(std::vector<std::array<int, 4>>,
		double, int, std::string);

/**
 * Main method
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
 * TODO Output is dumped to a csv file in the project data folder.
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

	// Calculate each of the matrices that are possible - use vectors?
	std::vector<std::array<int,4>> matrices = find_matrices(class_a_count,
			class_b_count, min_max_values);

	if (target_sensitivity != -1)
		matrices = check_metric(matrices, target_sensitivity, decimal_places, "sensitivity");
	if (target_specificity != -1)
		matrices = check_metric(matrices, target_specificity, decimal_places, "specificity");
	if (target_f1 != -1)
		matrices = check_metric(matrices, target_f1, decimal_places, "f1");
	if (target_precision != -1)
		matrices = check_metric(matrices, target_precision, decimal_places, "precision");

	// TODO Export to .csv file.
}

/**
 * check metric - check a particular metric against each of the supplied
 * matrices to determine if it is possible.
 *
 * Parameters
 *   std::vector<std::array<int, 4>> - all of the current matrices
 *   double - target value to achieve
 *   int - number of decimal places to round to
 *   std::string - metric to check
 *
 * Returns
 *   std::vector<std::array<int, 4>> - all matrices that achieve the target
 */
std::vector<std::array<int,4>> check_metric(
		std::vector<std::array<int,4>> matrices,
		double target_value,
		int decimal_places,
		std::string metric_name
		)
{
	std::vector<std::array<int,4>> new_matrices;

	for (int i = 0; i < matrices.size(); i++)
	{
		double TP = (double)matrices[i][0];
		double FN = (double)matrices[i][1];
		double FP = (double)matrices[i][2];
		double TN = (double)matrices[i][3];
		double result;

		// Calculate the required metric.
		if (metric_name == "sensitivity")
			result = round_dp(TP/(TP+FN), decimal_places);
		else if (metric_name == "specificity")
			result = round_dp(TN/(TN+FP), decimal_places);
		else if (metric_name == "f1")
			result = round_dp(2*TP/(2*TP+FP+FN), decimal_places);
		else if (metric_name == "precision")
			result = round_dp(TP/(TP+FP), decimal_places);
		else
		{
			std::cout << "Unknown metric, exiting." << std::endl;
			exit(0);
		}

		// Append the matrix if it achieves the correct result.
		if (result == target_value)
			new_matrices.push_back({(int)TP,(int)FN,(int)FP,(int)TN});
	}
	return new_matrices;
}

/**
 * find_matrices - extract all of the matrices that fit the accuracy criteria.
 *
 * Parameters
 *   int - count of items in class A
 *   int - count of items in class B
 *   TODO
 *
 * Returns
 *   TODO
 */
std::vector<std::array<int, 4>> find_matrices(
		int class_a_count,
		int class_b_count,
		int * min_max_values
		)
{
	// Calculate the total number of combinations.
	int combinations = 1;
	if (*(min_max_values + 2) != -1)
		combinations = *(min_max_values) - *(min_max_values + 2) + 1;

	// Calculate and store the matrices.
	std::vector<std::array<int,4>> matrices;
	for (int i = 0; i < combinations; i++)
	{
		// Base matrix
		int TP = class_a_count - i;
		if ((*(min_max_values) - i) < class_a_count)
			TP = *(min_max_values) - i;
		int FN = class_a_count - TP;
		int FP = *(min_max_values + 1) + i - FN;
		int TN = class_b_count - FP;
		matrices.push_back({TP,FN,FP,TN});

		while (TP > 0 && TN < class_b_count)
		{
			--TP;
			++FN;
			--FP;
			++TN;
			matrices.push_back({TP,FN,FP,TN});
		}
	}
	return matrices;
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
double round_dp(double number, int decimal_places) {
	double modifier = pow(10.0f, (double)decimal_places);
	return round(number * modifier) / modifier;
}
