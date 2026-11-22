# Data notes (read before the viva)

`data/heart.csv` is the Cleveland heart-disease data in the common 1,025-row Kaggle form.

## 1. Duplicates / leakage
723 of 1,025 rows are exact duplicates -> **302 unique patients**. Splitting before de-duplicating
puts the same patient in train and test. Effect on the original scripts (random_state=2, 80/20):

| Model | Raw (leaky) | De-duplicated |
|---|---|---|
| Random Forest | 1.000 | 0.869 |
| KNN | 0.722 | 0.639 |

This project de-duplicates first (`data.load_dataset`) and a test asserts no patient is in both splits.

## 2. The `target` column is inverted
In this file `target = 1` means **no disease**. Evidence (corr. with target): exang -0.44, oldpeak -0.43,
ca -0.41, thal -0.34, sex -0.28, age -0.22, while max heart rate +0.42. Every clinical risk factor points the
"wrong" way for `target = 1 = disease`. The app derives `disease = 1 - target`
(`config.TARGET_ONE_MEANS_HEALTHY`). The original `app.py` printed "Has heart disease" for target = 1,
i.e. the opposite of the truth.
**Please confirm against your dataset's source / documentation.** Flip the one constant if I am wrong.

## 3. Category labels (verified by counts matching Cleveland)
- cp: 0 asymptomatic (143), 1 atypical angina (50), 2 non-anginal (86), 3 typical angina (23)
- restecg: 0 LV hypertrophy (147), 1 normal (151), 2 ST-T abnormality (4)
- slope: 0 downsloping (21), 1 flat (140), 2 upsloping (141)
- thal: 0 null (2), 1 fixed defect (18), 2 normal (165), 3 reversible defect (117)
Many online data-cards list these in the wrong order.

## 4. Statistical honesty
Only 302 patients; the test set is 61. Top models are within noise of each other (AUC ~0.87-0.89).
Selection uses 5-fold CV on the training split only. Do not claim one model is "significantly" better.
