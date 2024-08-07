import pandas as pd

# load CSV
data = pd.read_csv('/Users/elishaokara/Documents/IndividualProject/exalens/factory-sim-main/operation_log.csv')

# filtering rows where 'idle'
filtered_data = data[data['Robot State'] != 'idle']

# filtered data back to CSV
filtered_data.to_csv('/Users/elishaokara/Documents/IndividualProject/DTclassifier/clean_operation_log.csv', index=False)
