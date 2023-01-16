#For Matrix Manipulation and Data Management
import pandas as pd

#For Machine Learning and Feature Analysis
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.feature_selection import RFECV
from sklearn import preprocessing
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2

#For Data Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from  matplotlib.colors import LinearSegmentedColormap

#For Utility 
from datetime import datetime

def genomic_feature_selection(filename, RandomForest=False, Chisq=False, Swarmplot=False, Heatmap=False):
    
    # Reading Data and Filling Missing Entries
    df = pd.read_csv(filename)
    df.fillna('Other', inplace=True)

    # Encoding and Authenticating Target Labels
    df = df[df['Age'] != 'Other']
    le = preprocessing.LabelEncoder()
    le.fit(df['Type'])
    df['Type'] = le.transform(df['Type'])

    # Grabbing Genes for Analysis
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    genomic_list = [col for col in df.columns if col not in ['ID', 'Sex', 'Race', 'Age']]
    genomic_list_no_type = [col for col in genomic_list if col != 'Type']
    
    # Splitting Matrix
    genomic_and_target_features = genomic_list
    genomic_df = df[genomic_and_target_features]

    genomic_features = genomic_df[genomic_list_no_type]
    y = genomic_df['Type']
    
    x_train, x_test, y_train, y_test = train_test_split(genomic_features, y, 
                                                        test_size=0.2, random_state = 42)

    # Random Forest
    if RandomForest == True:
        rf1 = RandomForestRegressor(random_state = 42)
        rf1.fit(x_train,y_train)
        feature_tpm_selector1 = RFECV(rf1, cv=5)
        feature_tpm_selector1.fit(x_train, y_train)
        
        f_i = list(zip(genomic_list_no_type, rf1.feature_importances_))
        f_i.sort(key = lambda x : x[1])
        
        plt.figure(figsize = (10,10))
        plt.barh([x[0] for x in f_i],[x[1] for x in f_i], color = '#32CD32')
        plt.savefig(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "RF-GenomicFeatureSelection.png")
        
    # Chi-Squared Test
    if Chisq == True: 
        chisq_selected_features = SelectKBest(score_func = chi2, k = "all")
        fit = chisq_selected_features.fit(x_train, y_train)
        dfscores = pd.DataFrame(fit.scores_)
        dfcolumns = pd.DataFrame(x_train.columns)
        featuresScores = pd.concat([dfcolumns, dfscores], axis = 1)
        featuresScores.columns = ['Genomic Feature', 'Score']
        (featuresScores.nlargest(len(genomic_list_no_type),'Score')).to_csv(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "Chiq-GenomicFeatureSelection.tsv", sep='\t', index=False)

    # Swarmplot
    if Swarmplot == True:
        sns.set(style="whitegrid", palette="muted")
        genomic_df_melt = pd.melt(genomic_df, id_vars = "Type",
                                    var_name = "Features",
                                    value_name = "Value")
        plt.figure(figsize=(20,20))
        sns.swarmplot(x="Features", y="Value", hue="Type", data=genomic_df_melt, palette="dark:#32CD32")
        plt.xticks(rotation=90)
        plt.savefig(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "Swarmplot-GenomicFeatureSelection.png")

    # Heatmap
    if Heatmap == True:
        genomic_df=genomic_df.apply(lambda x: pd.to_numeric(x, errors='ignore'))
        f,ax = plt.subplots(figsize=(20, 20))
        sns.heatmap(genomic_df.corr(), annot=True, linewidths=.5, fmt= '.1f', ax=ax, cmap = LinearSegmentedColormap.from_list('rg',[ "black", "#32CD32"], N=256), 
                        linecolor = 'black')
    plt.savefig(filename + "_" + datetime.now().strftime("%m-%d-%Y-%I-%M-%S-%p") + "_" + "Heatmap-GenomicFeatureSelection.png")