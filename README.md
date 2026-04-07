# AI-Based Credit Risk Scoring System

This project deploys a credit risk assessment engine to automate the model in order to substitute manual bottlenecks in underwriting with on-the-fly and data-driven scoring. With the help of machine learning models that have been trained on the German Credit Dataset, the system is able to categorize loan applicants into three risk groups: Low, Medium, and High.

# Project Overview
The scoring of traditional credit is based on a few variables and manual reviews that are slow, inconsistent and can be subject to human error. This system employs ensemble learning to recognize intricate patterns among many variables, including credit history, employment length, and loan purpose, at rates and with consistency that are orders of magnitude higher than manual methods.

Key Objectives
 -Automated Scoring: Eliminate manual underwriting and use an immediate scoring engine.
 -Statistical Evidence: Enable institutions to make approvals based on statistical trends, as opposed to subjective determination.
 -Interactive Interface: Develop a lifelike web dashboard of loan officers on Streamlit.

# Technology Stack
 -Language: Python
 -Data Processing: Pandas, NumPy 
 -Machine Learning: Scikit-Learn, XGBoost
 -Web Framework: Streamlit 

# Methodology & Architecture
The machine learning pipeline of the project is structured:
 -Data Input: The raw applicant and transaction data are fed.
 -Preprocessing: Implicates cleaning missing values, normalizing numerical variables and encoding categorical variables (e.g., Credit History, Purpose).
 -Model Training: Two ensemble models were considered:
     -Random Forest: It is a decision tree that involves multiple trees, which reduce overfitting and address the imbalance in classes.
     -XGBoost: It is based on gradient boosting to rectify the mistakes of the previous trees and is applicable to tabular data, with high accuracy.
 -Risk Classification: The model produces a default probability that is transformed to actionable levels:
     -Low Risk (0-35%): Recommended Action: Approve.
     -Medium Risk (35-65%): Recommended Action: Manual Review.
     -High Risk (65-100%): Recommended Action: Reject.

# Performance & Results
 -Precision: The models were within the bounds of the standard criteria of accuracy (75% -80%): standards of the German Credit Dataset.
 -Comparison of the models: XGBoost tended to score higher on AUC whereas the random forest was more predictable across various random seeds.
 -Lessons: The multiplicity of features (e.g., Credit History + Loan Term + Employment) was far more predictive than any individual feature.

# Dataset
 The German Credit Dataset (around 1,000 records) is used to train the system and the features used are:
 -Credit Amount: Sum of loan amount requested.
 -Duration: Duration of loan in months.
 -Credit History: History of previous repayments.
 -Employment: Number of years of consecutive employment.

# Future Scope
 -Explainability: SHAP values can be integrated to provide explanations on the reasons behind certain risk factors to loan officers.
 -Alternative Data: The use of utility payments or e-commerce history with applicants who do not have formal credit history.
 -Real-time API: Shifting to real-time scoring API to be directly integrated with loan origination systems.
