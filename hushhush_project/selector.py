import pandas as pd
import numpy as np
import os
import pickle
import seaborn as sns
import sqlite3
import matplotlib.pyplot as plt
import scipy.stats as st
from sklearn.cluster import KMeans
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split, KFold
from sklearn.preprocessing import RobustScaler
from sklearn.metrics import silhouette_score
pd.set_option('display.max_columns',100)
import warnings
warnings.filterwarnings('ignore')

np.random.seed(42)

CLUSTERS_DICT = {
    'Data Scientist': 1,
    'Python Web Developer': 2,
    'Java Developer': 0,
    'C++ Developer': 2,
    'Solutions Architect' :0,
    'AI Engineer': 2,   
}


def convert_k_to_num(value):
    if isinstance(value, str) and value.lower().endswith('k'):
        return float(value[:-1]) * 1000
    elif isinstance(value, str) and value.lower().endswith('m'):
        return float(value[:-1]) * 1000000
    else:
        return float(value)
    

def convert_to_months(s):
    years, months, days = 0, 0, 0
    
    if 'year' in s:
        years = int(s.split('year')[0].strip())
    
    if 'month' in s:
        months = int(s.split('month')[0].split(',')[-1].strip())
    
    if 'day' in s:
        days = int(s.split('day')[0].split(',')[-1].strip())
    
    total_months = years * 12 + months + days / 30
    
    return total_months


def get_data(role, number_of_condidates, selected_cadidates):
    
    database_path = 'candidate_data.db'

    # Create a connection to the SQLite database
    conn_data = sqlite3.connect(database_path)

    # SQL query to select all data from the training data table
    query_unseen = "SELECT * FROM unseen_data"

    # Load data from the SQL query into a pandas DataFrame
    df_unseen = pd.read_sql_query(query_unseen, conn_data)
    
    # Close the connection to the database
    conn_data.close()
    
    #Cleaning the data
    df_unseen = df_unseen[~df_unseen['user_id'].isin(selected_cadidates)]
    df_unseen['name'] = df_unseen['name'].str.replace('\n','')
    df_unseen['name'] = df_unseen['name'].str.strip()

    #Null Value Imputation
    df_unseen['job_role'].fillna('NA',inplace=True)
    df_unseen['tags'].fillna('NA',inplace=True)
    df_unseen['gold_badges'].fillna('NA',inplace=True)
    df_unseen['silver_badges'].fillna('0',inplace=True)
    df_unseen['bronze_badges'].fillna('0',inplace=True)
    df_unseen['questions'].fillna('0',inplace=True)
    df_unseen['answers'].fillna('0',inplace=True)
    df_unseen['reputation'].fillna('0',inplace=True)
    df_unseen['reached'].fillna('0',inplace=True)
    df_unseen['posts_edited'].fillna('0',inplace=True)
    df_unseen['votes_cast'].fillna('0',inplace=True)
    df_unseen['helpful_tags'].fillna('0',inplace=True)

    df_unseen[['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']]=df_unseen[['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']].apply(lambda x:x.str.replace(",",""))

    # 2. Clean k and m values
    df_unseen['reached'] = df_unseen['reached'].str.strip()
    
    df_unseen['reached'] = df_unseen['reached'].apply(convert_k_to_num)
    
    #3. Extract number of months
    df_unseen['member_since_in_months'] = df_unseen['member_since'].apply(convert_to_months)
    df_unseen['member_since_in_months'] = df_unseen['member_since_in_months'].round(2)
    
    df_unseen[['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']] = df_unseen[['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']].apply(pd.to_numeric)

    #Feature Engineering
    df_unseen['weighted_badge_score'] = (3 * df_unseen['gold_badges']) + (2 * df_unseen['silver_badges']) + df_unseen['bronze_badges']
    df_unseen['questions'] = np.where(df_unseen['questions']==0, 1, df_unseen['questions'])
    df_unseen['QA_ratio'] = (df_unseen['answers']/df_unseen['questions']).round(2)

    #dropping this because there's a weighted badge score
    df_unseen.drop(columns=['gold_badges', 'silver_badges', 'bronze_badges'], inplace=True)
    
    if role == 'Data Scientist':
        #Creating flags
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['tags'].str.contains('python|r'),1,0)
        df_unseen['Data_Analysis_Flag'] = np.where(df_unseen['tags'].str.contains('pandas|exploratory-data-analysis|dataframe|data-analysis'),1,0)
        df_unseen['DBMS_Flag'] = np.where(df_unseen['tags'].str.contains('sql'),1,0)
        df_unseen['Visualization_Flag'] = np.where(df_unseen['tags'].str.contains('tableau|powerbi|power-bi|seaborn|matplotlib|visualization|ggplot'),1,0)
        df_unseen['Modeling_Flag'] = np.where(df_unseen['tags'].str.contains('scikit-learn|statsmodels|machine-learning|regression'),1,0)
        df_unseen['Data_Analysis_Flag'] = np.where(df_unseen['Modeling_Flag']==1, 1, df_unseen['Data_Analysis_Flag'])
        df_unseen['Statistics_Flag'] = np.where(df_unseen['tags'].str.contains('statistics|scipy|anova|hypothesis|statistical|anova'),1,0)
        df_unseen['total_requirements_satisfied'] = df_unseen['Programming_Language_Flag']+df_unseen['DBMS_Flag']+df_unseen['Visualization_Flag']+df_unseen['Modeling_Flag']+df_unseen['Data_Analysis_Flag']+ df_unseen['Statistics_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[df_unseen['total_requirements_satisfied']>=2]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'],ans = st.boxcox(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],helpf = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'],vote = st.boxcox(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/data-scientist-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)
            
        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])
        
        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')
    
    elif role == 'Python Web Developer':
        #Creating flags
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['tags'].str.contains('python'),1,0)
        df_unseen['Web_Framework_Flag'] = np.where(df_unseen['tags'].str.contains('django|flask|fastapi|pyramid|tornado'),1,0)
        df_unseen['DBMS_Flag'] = np.where(df_unseen['tags'].str.contains('sql'),1,0)
        df_unseen['FrontEnd_Flag'] = np.where(df_unseen['tags'].str.contains('html|css|javascript|.js|react|angular'),1,0)
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['Web_Framework_Flag']==1, 1, df_unseen['Programming_Language_Flag'])
        df_unseen['total_requirements_satisfied'] = df_unseen['Programming_Language_Flag']+df_unseen['Web_Framework_Flag']+df_unseen['DBMS_Flag']+df_unseen['FrontEnd_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[df_unseen['total_requirements_satisfied']>=2]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'],ans = st.boxcox(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],helpf = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'],vote = st.boxcox(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/python-web-developer-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)

        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])
        
        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')
    
    elif role == 'Solutions Architect':
        #Creating flags
        df_unseen['Cloud_Services_Flag'] = np.where(df_unseen['tags'].str.contains('gcp|amazon|amazon-web-services|gcp|cloud|google-cloud-platform|azure'),1,0)
        df_unseen['DevOps_Flag'] = np.where(df_unseen['tags'].str.contains('devops|jenkins|docker|kubernetes|ansible|terraform'),1,0)
        df_unseen['Security_Flag'] = np.where(df_unseen['tags'].str.contains('security|oauth|ssl|encryption|cybersecurity|cyber-security'),1,0)
        df_unseen['total_requirements_satisfied'] = df_unseen['Cloud_Services_Flag'] + df_unseen['DevOps_Flag'] + df_unseen['Security_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[df_unseen['total_requirements_satisfied']>=1]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'] = 1/(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],helpf = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'] = 1/(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/solutions-architect-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)
            
        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])

        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')
        
    elif role == 'AI Engineer':
        #Creating flags
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['tags'].str.contains('python'),1,0)
        df_unseen['Machine_Learning_Flag'] = np.where(df_unseen['tags'].str.contains('scikit-learn|statsmodels|machine-learning|regression'),1,0)
        df_unseen['Neural_Network_Flag'] = np.where(df_unseen['tags'].str.contains('deep-learning|pytorch|keras|tensorflow|neural-networks'),1,0)
        df_unseen['Programming_Language_Flag'] = np.where((df_unseen['Machine_Learning_Flag']==1)|(df_unseen['Neural_Network_Flag']==1) , 1, df_unseen['Programming_Language_Flag'])
        df_unseen['total_requirements_satisfied'] = df_unseen['Programming_Language_Flag']+df_unseen['Machine_Learning_Flag']+df_unseen['Neural_Network_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[~(((df_unseen['total_requirements_satisfied']==1)&(df_unseen['Programming_Language_Flag']==1))|(df_unseen['total_requirements_satisfied']==0))]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'] = 1/(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],help = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'] = 1/(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

     

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/ai-engineer-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)
            
        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])

        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')
    
    elif role == 'Java Developer':
        #Creating flags
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['tags'].apply(lambda x:'java' in x),1,0)
        df_unseen['DBMS_Flag'] = np.where(df_unseen['tags'].str.contains('sql'),1,0)
        df_unseen['Web_Dev_Flag'] = np.where(df_unseen['tags'].str.contains('spring|hibernate'),1,0)
        df_unseen['Other_Skills_Flag'] = np.where(df_unseen['tags'].str.contains('maven|gradle|ant|git|svn|mercurial|junit|mockito|testng|selenium'),1,0)
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['Web_Dev_Flag']==1, 1, df_unseen['Programming_Language_Flag'])
        df_unseen['total_requirements_satisfied'] = df_unseen['Programming_Language_Flag']+df_unseen['DBMS_Flag']+df_unseen['Web_Dev_Flag']+df_unseen['Other_Skills_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[df_unseen['total_requirements_satisfied']>=1]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'],ans = st.boxcox(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],help = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'],vote = st.boxcox(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/java-developer-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)

        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])
        
        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')

    elif role == 'C++ Developer':
        #Creating flags
        df_unseen['tags'] = df_unseen['tags'].apply(lambda x:x.split(','))
        df_unseen['Programming_Language_Flag'] = np.where(df_unseen['tags'].apply(lambda x:'c++' in x),1,0)
        df_unseen['total_requirements_satisfied'] = df_unseen['Programming_Language_Flag']

        #Shortlisting Candidates with Valid Skill
        df_unseen = df_unseen[df_unseen['total_requirements_satisfied']==1]

        #Transformations
        df_unseen['reputation_st'],rep = st.boxcox(df_unseen['reputation']+1)
        df_unseen['reached_st'],reach = st.boxcox(df_unseen['reached']+1)
        df_unseen['questions_st'],ques = st.boxcox(df_unseen['questions']+1)
        df_unseen['answers_st'],ans = st.boxcox(df_unseen['answers']+1)
        df_unseen['posts_edited_st'],post = st.boxcox(df_unseen['posts_edited']+1)
        df_unseen['helpful_tags_st'],helpf = st.boxcox(df_unseen['helpful_tags']+1)
        df_unseen['votes_cast_st'],vote = st.boxcox(df_unseen['votes_cast']+1)
        df_unseen['weighted_badge_score_st'],badge = st.boxcox(df_unseen['weighted_badge_score']+1)
        df_unseen['QA_ratio_st'] = df_unseen['QA_ratio']**0.2

        #Scaling with Robust Scaler
        st_columns = [i for i in df_unseen.columns if i.endswith('_st')]
        scaler = RobustScaler()
        df_unseen[st_columns] = scaler.fit_transform(df_unseen[st_columns])
        scaled2 = scaler.fit_transform(df_unseen[['member_since_in_months','total_requirements_satisfied']])
        df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=df_unseen.index)
        df_unseen = pd.concat([df_unseen, df_scaled2], axis=1)
        st_columns1 = [i for i in df_unseen.columns if i.endswith('_st')]

        # Path to the pickle file
        pickle_file_path = 'model_pickle_files/cpluplus-developer-model.pkl'

        # Load the model from the pickle file
        with open(pickle_file_path, 'rb') as file:
            loaded_model = pickle.load(file)
            
        df_unseen['Cluster'] = loaded_model.predict(df_unseen[st_columns1])

        required_candidates = df_unseen[df_unseen['Cluster'] == CLUSTERS_DICT[role]].sort_values(by='reputation', ascending=False).head(number_of_condidates)
        
        return required_candidates.to_dict('records')
    else:    
        return None
