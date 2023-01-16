#For Matrix Manipulation and Data Management
import pandas as pd

#For Machine Learning and Feature Analysis
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

#For Data Visualization
import matplotlib.pyplot as plt
import seaborn as sns

#For Utility 
import sys
from datetime import datetime

def clinical_feature_selection(filename, RandomForest=bool, Chisq=bool, Swarmplot=bool):
    
    # Reading Data and Filling Missing Entries
    df = pd.read_csv(filename)
    df.fillna('Other', inplace=True)
    
    # Polishing Inconsistent Race Labels
    df['Race'].replace({'White ': 'White', 'Black ': 'Black', 'Other ': 'Other', 'Decline to Answer ': 'Decline to Answer', 'Asian ': 'Asian'}, inplace=True)
    
    # Assigning Values for Race (Electronic Health Record Standards)
    df['Race'].replace({'White': 1, 'Black': 2, 'Other': 6, 'Decline to Answer': 7, 'Asian': 19}, inplace=True)
    
    # Polishing Inconsistent Sex Labels
    df['Sex'].replace({'Female ': 'Female', 'Male ': 'Male', 'Other ': 'Other'}, inplace=True)

    # Assigning Values for Sex (Electronic Health Record Standards)
    df['Sex'].replace({'Female': 1, 'Male': 2, 'Other': 999}, inplace=True)
    
    # Authenticating Race and Sex Values
    accepted_race_values = [1, 2, 6, 7, 19]
    accepted_sex_values = [1, 2, 999]
    
    if not set(df['Race'].unique()).issubset(set(accepted_race_values)):
         sys.exit("(Execution Error) Accepted Race Values:  \"White\", \"Black\", \"Other\", \"Decline to Answer\", \"Asian\"")
         
    if not set(df['Sex'].unique()).issubset(set(accepted_sex_values)):
         sys.exit("(Execution Error) Accepted Sex Values:  \"Female \",  \"Male \",  \"Other\"")
        
    # Encoding Target Labels
    df = df[df['Age'] != 'Other']
    le = preprocessing.LabelEncoder()
    le.fit(df['Type'])
    df['Type'] = le.transform(df['Type'])
    
    # Splitting Matrix
    clinical_and_target_features = ['Sex', 'Race', 'Age', 'Type']
    clinical_df = df[clinical_and_target_features]
    
    clinical_features = clinical_df[['Sex', 'Race', 'Age']]
    y = clinical_df['Type']
    
    x_train, x_test, y_train, y_test = train_test_split(clinical_features, y, 
                                                                test_size=0.2, random_state = 42)
    
    # Random Forest
    if RandomForest == True: 
         rf = RandomForestRegressor(random_state=0)
         rf.fit(x_train, y_train)
         f_i = list(zip(clinical_features, rf.feature_importances_))
         f_i.sort(key = lambda x : x[1])
         
         plt.barh([x[0] for x in f_i],[x[1] for x in f_i], color='#32CD32')
         plt.savefig(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "RF-ClinicalFeatureSelection.png")
    
    # Chi-Squared Test
    if Chisq == True: 
         chisq_selected_features = SelectKBest(score_func = chi2, k = 3)
         fit = chisq_selected_features.fit(x_train, y_train)
         dfscores = pd.DataFrame(fit.scores_)
         dfcolumns = pd.DataFrame(x_train.columns)
         featuresScores = pd.concat([dfcolumns, dfscores], axis = 1)
         featuresScores.columns = ['Clinical Feature', 'Score']
         
         (featuresScores.nlargest(3,'Score')).to_csv(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "Chiq-ClinicalFeatureSelection.tsv", sep='\t', index=False)
    
    # Swarmplot
    if Swarmplot == True:
         sns.set(style="whitegrid", palette="muted")
         
         clinical_df_melt = pd.melt(clinical_df, id_vars = "Type",
                                    var_name = "Features",
                                    value_name = "Value")

         plt.figure(figsize=(10,10))
         sns.swarmplot(x="Features", y="Value", hue="Type", data=clinical_df_melt, palette="dark:#32CD32")
         plt.xticks(rotation=90)
         plt.savefig(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "Swarmplot-ClinicalFeatureSelection.png")