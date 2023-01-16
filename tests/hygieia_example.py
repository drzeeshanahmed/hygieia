from hygieia.clinical_feature_selection import clinical_feature_selection
from hygieia.genomic_feature_selection import genomic_feature_selection

clinical_feature_selection("Input_Data.csv", RandomForest=True, Chisq=True, Swarmplot=True)
genomic_feature_selection("Input_Data.csv", RandomForest=True, Chisq=True, Swarmplot=True, Heatmap=True)