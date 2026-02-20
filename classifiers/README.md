# Classifiers

This folder contains sklearn classifiers used to predict the success or failure of a Shonen Jump series based upon its early performance. Each classifier is stored using the pickle module as a pkl file.  

## File Contents
Each file consists of a (model, dictionary) pair where the dictionary contains the following keys:

- `Fitted On`: A list of series which were used when fitting the series.
- `Success Criteria`: The number of chapters a series has to run to be considered a success.
- `Basis Size`: The number of chapters used for each series in making a prediction starting from chapter 1.

## Subfolders
Certain groups of classifiers are sorted into appropriate subfolders for easy access and organization.  These are:

-`demos`: Contains classifiers created in the Jupyter notebook `predicting_success.ipynb` which walks through the steps of creating, comparing, and selecting classifiers.
-`simple`: Contains classifiers which only predict using the average placement of the first `Basis Size` chapters of a series (i.e. only univariate classifiers).

## Using Classifiers

The notebook `model_testing.ipynb` walks through how to access and use one of the stored classifiers.  In order to make predictions on a selection of series the process is generally as follows.

1. Load the (model,dictionary) pair using `pickle.load`:
```
with open('Demo_Classifier.pkl', 'rb') as f:
    loader = pickle.load(f) # Loader is a dictionary.
```
2. Access the model itself by selecting the 0 index element.
```
model=loader[0]
```
3. Load chapter information by using an ad-hoc SQL query, composing a dataframe manually for the desired series, or by using one of the appropriate functions from `sj_db_functions.py`.  In the latter case a dataframe can be constructed by calling `fetch_prediction_data` (or `average_placement` for classifiers in the `simple` folder) and specifying the basis size. Such a dataframe will only contain series with at least basis size chapters.  If specific series are desired the resulting dataframe can be cut down as desired.  In the following `selected_series` is a list of user chosen series for prediction.
```
df=fetch_prediction_data(loader[1]['Basis Size'])
cut_down=df[df['title'].isin(selected_series)]
```
4. Perform predictions using the selected data and model:
```
predictions=model.predict(cut_down)
```
5. The actual success or failure of each series can be quickly obtained by using the function `success_or_failure` function from `sj_db_functions.py` to judge the predictions.
```
actual=success_or_failure(selected_series)
```

