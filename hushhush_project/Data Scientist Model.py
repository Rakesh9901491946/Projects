#!/usr/bin/env python
# coding: utf-8

# ## Importing required libraries

# In[28]:


import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as st
from sklearn.model_selection import cross_val_score, GridSearchCV, train_test_split, KFold
from sklearn.preprocessing import RobustScaler
pd.set_option('display.max_columns',100)
import warnings
warnings.filterwarnings('ignore')


# ## Reading the data

# In[29]:


df1 = pd.read_csv('0to50k_profile_data.csv')
print('df1 :',df1.shape)
df2 = pd.read_csv('50to100k_profile_data.csv')
print('df2 :',df2.shape)
df3 = pd.read_csv('0to50k_activity_data.csv')
print('df3 :',df3.shape)
df4 = pd.read_csv('50to100k_activity_data.csv')
print('df4 :',df4.shape)
df5 = pd.read_csv('stackoverflow_0to100k.csv')
print('df5 :',df5.shape)
df6 = pd.read_csv('part2.csv')
print('df6 :',df5.shape)

# joining df1 and df2
df_p = pd.concat([df1,df2])
df_p = df_p.drop_duplicates(['user_id'])
print('concat profiles:', df_p.shape)
df_a = pd.concat([df3,df4])
df_a.drop(columns=['Name'],inplace=True)
df_a = df_a.drop_duplicates(['user_id'])
print('concat activities:', df_a.shape)

#joining 2 dfs to get view_count and score
df_j = pd.concat([df5,df6])
df_j = df_j.drop_duplicates(['user_id'])
print('concating view count and score :', df_j.shape)
# df['name'] = df['name'].str.replace('\n','')
# df['name'] = df['name'].str.strip()

df_p['user_id'] = df_p['user_id'].astype(str)
df_a['user_id'] = df_a['user_id'].astype(str)
df_j['user_id'] = df_j['user_id'].astype(str)

#merging profiles and activities
df = pd.merge(df_p, df_a, how = 'inner', on = 'user_id')
df = df.drop_duplicates(['user_id'])
print('merging profiles and activities :', df.shape)

#merging finaldf with view count and score
# df = pd.merge(df, df_j[['user_id','view_count','score']], how = 'left', on = 'user_id')
# print('merging finaldf with view count and score:', df.shape)
# df = df.drop_duplicates(['user_id'])
df.columns = df.columns.str.lower()
df = df.reindex(['name', 'job_role', 'tags', 'member_since', 'gold_badges',
       'silver_badges', 'bronze_badges', 'reputation', 'reached', 'questions',
       'answers', 'user_id', 'location', 'people_reached',
       'posts_edited', 'helpful_tags', 'votes_cast'],axis=1)
df['name'] = df['name'].str.replace('\n','')
df['name'] = df['name'].str.strip()
print('finaldf :', df.shape)


# In[30]:


df.info()


# ## Cleaning Corrected Data

# df3['name'] = df3['name'].str.replace('\n','')
# df3['name'] = df3['name'].str.strip()
# df3['Stats'] = df3['Stats'].str.replace('\n','')
# 
# def split_stats(s):
#     parts = s.split(' ,')
#     pre_parts, post_parts = parts[0], parts[1]
#     reached = pre_parts.split(',')[-1]
#     reputation = ''.join(pre_parts.split(',')[:-1])
#     if len(post_parts.split(','))==2:
#         answers = post_parts.split(',')[0]
#         questions = post_parts.split(',')[1]
#     elif len(post_parts.split(','))==3 and len(post_parts.split(',')[1])==3:
#         answers = ''.join(post_parts.split(',')[0:-1])
#         questions = post_parts.split(',')[-1]
#     elif len(post_parts.split(','))==3 and len(post_parts.split(',')[1])!=3:
#         answers = post_parts.split(',')[0]
#         questions = ''.join(post_parts.split(',')[1:])
#     elif len(post_parts.split(','))==4:
#         answers = ''.join(post_parts.split(',')[0:-2])
#         questions = ''.join(post_parts.split(',')[-2:])
#     elif len(post_parts.split(','))==3 and len(post_parts.split(',')[1])==2:
#         print(post_parts.split(',')[1])
#     else:
#         pass
#     return reputation, reached, answers, questions
# df3[['reputation', 'reached', 'answers', 'questions']] = pd.DataFrame(df3['Stats'].apply(split_stats).tolist(), index=df3.index)
# 
# df = pd.merge(df, df3, how = 'left', on = 'name')

# ## Null Value Imputation

# In[31]:


df['job_role'].fillna('NA',inplace=True)
df['tags'].fillna('NA',inplace=True)
df['gold_badges'].fillna('NA',inplace=True)
df['silver_badges'].fillna('0',inplace=True)
df['bronze_badges'].fillna('0',inplace=True)
df['questions'].fillna('0',inplace=True)
df['answers'].fillna('0',inplace=True)
df['reputation'].fillna('0',inplace=True)
df['reached'].fillna('0',inplace=True)
df['posts_edited'].fillna('0',inplace=True)
# df['upvotes'].fillna('0',inplace=True)
# df['answer_votes'].fillna('0',inplace=True)
# df['question_vote'].fillna('0',inplace=True)
df['votes_cast'].fillna('0',inplace=True)
# df['downvotes'].fillna('0',inplace=True)
df['helpful_tags'].fillna('0',inplace=True)
# df['view_count'].fillna(0,inplace=True)
# df['score'].fillna(0,inplace=True)
df['tags'] = df['tags'].str.lower()
df.isnull().sum()


# # DATA CLEANING

# ## 1. Remove , from all numerical columns

# In[32]:


for i in ['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']:
    df[i] = df[i].str.replace(',','') 
    print(i)


# ## 2. Clean k and m values

# In[33]:


df['reached'] = df['reached'].str.strip()

def convert_k_to_num(value):
    if isinstance(value, str) and value.lower().endswith('k'):
        return float(value[:-1]) * 1000
    elif isinstance(value, str) and value.lower().endswith('m'):
        return float(value[:-1]) * 1000000
    else:
        return float(value)
    
df['reached'] = df['reached'].apply(convert_k_to_num)


# ## 3. Cleaning Member_Since

# In[34]:


def convert_to_months(s):
    # Initialize years, months, and days
    years, months, days = 0, 0, 0
    
    # Find and convert years, if present
    if 'year' in s:
        years = int(s.split('year')[0].strip())
    
    # Find and convert months, if present
    if 'month' in s:
        months = int(s.split('month')[0].split(',')[-1].strip())
    
    # Find and convert days, if present
    if 'day' in s:
        days = int(s.split('day')[0].split(',')[-1].strip())
    
    # Convert everything to months (approximation)
    total_months = years * 12 + months + days / 30  # Convert days to a fraction of a month
    return total_months

# Apply the conversion function to your 'Member_Since' column
df['member_since_in_months'] = df['member_since'].apply(convert_to_months)
df['member_since_in_months'] = df['member_since_in_months'].round(2)


# ## Type Casting

# In[35]:


for i in ['silver_badges', 'bronze_badges','posts_edited', 'helpful_tags', 'votes_cast', 'reputation','reached', 'answers', 'questions']:
    print(i)
    df[i] = df[i].astype(int) 


# ## Feature Engineering

# ## DATA SCIENTIST SKILLS
# 
# ### programming languages - python, r
# ### data analysis - pandas, numpy
# ### visualisation - tableau, matplotlib, seaborn, powerbi
# ### dbms - sql
# ### modeling - machine learning, deep learning, scikit-learn, regression, classification
# ### statistics

# ## Creating flags for all the skills

# In[36]:


df['weighted_badge_score'] = (3 * df['gold_badges']) + (2 * df['silver_badges']) + df['bronze_badges']
df['questions'] = np.where(df['questions']==0, 1, df['questions'])
df['QA_ratio'] = (df['answers']/df['questions']).round(2)

#dropping this because there's a weighted badge score
df.drop(columns=['gold_badges', 'silver_badges', 'bronze_badges'], inplace=True)


# In[37]:


ds_df = df.copy()
ds_df['Programming_Language_Flag'] = np.where(ds_df['tags'].str.contains('python|r'),1,0)
ds_df['Data_Analysis_Flag'] = np.where(ds_df['tags'].str.contains('pandas|exploratory-data-analysis|dataframe|data-analysis'),1,0)
ds_df['DBMS_Flag'] = np.where(ds_df['tags'].str.contains('sql'),1,0)
ds_df['Visualization_Flag'] = np.where(ds_df['tags'].str.contains('tableau|powerbi|power-bi|seaborn|matplotlib|visualization|ggplot'),1,0)
ds_df['Modeling_Flag'] = np.where(ds_df['tags'].str.contains('scikit-learn|statsmodels|machine-learning|regression'),1,0)
ds_df['Data_Analysis_Flag'] = np.where(ds_df['Modeling_Flag']==1, 1, ds_df['Data_Analysis_Flag'])
ds_df['Statistics_Flag'] = np.where(ds_df['tags'].str.contains('statistics|scipy|anova|hypothesis|statistical|anova'),1,0)
ds_df['total_requirements_satisfied'] = ds_df['Programming_Language_Flag']+ds_df['DBMS_Flag']+ds_df['Visualization_Flag']+ds_df['Modeling_Flag']+ds_df['Data_Analysis_Flag']+ ds_df['Statistics_Flag']


# In[38]:


ds_df.head()


# ## Transformations

# In[39]:


for column in ['reputation', 'reached', 'questions', 'answers',
        'posts_edited', 'helpful_tags', 'votes_cast',
        'weighted_badge_score', 'QA_ratio']:
    
    print('\033[1m'+column.upper()+'\033[0m','\n')
    plt.figure(figsize=(22,25))
    
    raw_skewness = ds_df[column].skew()
    
    plt.subplot(8,2,1)
    sns.distplot(ds_df[column])
    plt.title('Original distribution')
    
    plt.subplot(8,2,2)
    st.probplot(ds_df[column],dist='norm',plot=plt)
    
    
    #log transformation
    log_transform = np.log(ds_df[column]+1)
    log_skew=log_transform.skew()

    plt.subplot(8,2,3)
    sns.distplot(log_transform)
    plt.title('Log Transformation')

    plt.subplot(8,2,4)
    st.probplot(log_transform,dist='norm',plot=plt)
    
    #Reciprocal Transformation  
    recip_transform = 1/(ds_df[column]+1)
    recip_skew=recip_transform.skew()

    plt.subplot(8,2,5)
    sns.distplot(recip_transform)
    plt.title('Reciprocal Transformation')

    plt.subplot(8,2,6)
    st.probplot(recip_transform,dist='norm',plot=plt)
    
    #Exponential Transformation
    
    exp_2 = ds_df[column]**0.2
    exp_2_skew=exp_2.skew()
    
    plt.subplot(8,2,7)
    sns.distplot(exp_2)
    plt.title('exp_2 Transformation')
    
    plt.subplot(8,2,8)
    st.probplot(exp_2,dist='norm',plot=plt)
    
    exp_3 = ds_df[column]**0.3
    exp_3_skew=exp_3.skew()
    
    plt.subplot(8,2,9)
    sns.distplot(exp_3)
    plt.title('exp_3 Transformation')
    
    plt.subplot(8,2,10)
    st.probplot(exp_3,dist='norm',plot=plt)
    
    #Square Root Transformation
    
    sqrt_transform = ds_df[column]**(1/2)
    sqrt_transform_skew=sqrt_transform.skew()
    
    plt.subplot(8,2,11)
    sns.distplot(sqrt_transform)
    plt.title('Square Root Transformation')
    
    plt.subplot(8,2,12)
    st.probplot(sqrt_transform,dist='norm',plot=plt)
    
    #Cube Root Transformation
    
    cube_transform = ds_df[column]**(1/3)
    cube_transform_skew=cube_transform.skew()
    
    plt.subplot(8,2,13)
    sns.distplot(cube_transform)
    plt.title('Cube Root Transformation')
    
    plt.subplot(8,2,14)
    st.probplot(cube_transform,dist='norm',plot=plt)
    
    #Boxcox Transformation
    box,param = st.boxcox(ds_df[column]+1)
    boxcox_skew=pd.DataFrame(box).skew()

    plt.subplot(8,2,15)
    plt.tight_layout()
    sns.distplot(pd.DataFrame(box))
    plt.title('Boxcox Transformation')

    plt.subplot(8,2,16)
    st.probplot(box,dist='norm',plot=plt)
    
    trans_result= {'Actual':raw_skewness, 'Log':log_skew,'Reciprocal':recip_skew,'Exponential power 0.2':exp_2_skew,
                       'Exponential power 0.3':exp_3_skew,'Square Root':sqrt_transform_skew,
                       'Cube Root':cube_transform_skew,'Boxcox':boxcox_skew[0]}
    print(pd.DataFrame(trans_result.items(), columns=['Transformation', 'Skew']).to_string(index=False))
    
    lst=list(trans_result.values())
    idx = min((abs(x), x) for x in lst)[1]
    for i in trans_result:
        if (trans_result[i]==idx):
            print('\n','Best Transformation for ',column,':','\n',i,'=',trans_result[i])
    plt.tight_layout() 
    
    plt.show()


# In[40]:


ds_df['reputation_st'],rep = st.boxcox(ds_df['reputation']+1)
ds_df['reached_st'],reach = st.boxcox(ds_df['reached']+1)
ds_df['questions_st'],ques = st.boxcox(ds_df['questions']+1)
ds_df['answers_st'],ans = st.boxcox(ds_df['answers']+1)
ds_df['posts_edited_st'],post = st.boxcox(ds_df['posts_edited']+1)
ds_df['helpful_tags_st'],help = st.boxcox(ds_df['helpful_tags']+1)
ds_df['votes_cast_st'],vote = st.boxcox(ds_df['votes_cast']+1)
ds_df['weighted_badge_score_st'],badge = st.boxcox(ds_df['weighted_badge_score']+1)
ds_df['QA_ratio_st'] = ds_df['QA_ratio']**0.2


# ## Scaling with Robust Scaler

# In[41]:


st_columns = [i for i in ds_df.columns if i.endswith('_st')]
scaler = RobustScaler()
ds_df[st_columns] = scaler.fit_transform(ds_df[st_columns])
scaled2 = scaler.fit_transform(ds_df[['member_since_in_months','total_requirements_satisfied']])
df_scaled2 = pd.DataFrame(scaled2, columns=['member_since_in_months_st','total_requirements_satisfied_st'], index=ds_df.index)
ds_df = pd.concat([ds_df, df_scaled2], axis=1)


# In[42]:


from statsmodels.stats.outliers_influence import variance_inflation_factor

def calc_vif(X):

    # Calculating VIF
    vif = pd.DataFrame()
    vif["variables"] = X.columns
    vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(X.shape[1])]

    return(vif)


# In[43]:


st_columns1 = [i for i in ds_df.columns if i.endswith('_st')]
calc_vif(ds_df[st_columns1])


# In[44]:


corr_matrix = ds_df[st_columns1].corr()
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f")
plt.show()


# ## Modelling

# In[45]:


# kmodel.drop(columns='Cluster',inplace=True)
wcss = []
results = []

for i in range(1, 11):  # Test different numbers of clusters
    kmeans = KMeans(n_clusters=i, random_state=42)
    kmeans.fit(kmodel[st_columns1])  # X is your data
    wcss.append(kmeans.inertia_)
    results.append({'Number of Clusters': i, 'WCSS': kmeans.inertia_})
    
elbow_data = pd.DataFrame(results)
    
plt.plot(range(1, 11), wcss)
plt.title('Elbow Method')
plt.xlabel('Number of clusters')
plt.ylabel('WCSS')
plt.show()


# In[46]:


elbow_data


# In[47]:


kmodel = ds_df[ds_df['total_requirements_satisfied']>=3]
from sklearn.cluster import KMeans
kmeans = KMeans(n_clusters=4, random_state=42)
kmeans.fit(kmodel[st_columns1])
kmodel['Cluster'] = kmeans.labels_
kmodel_inference = kmodel[['reputation', 'reached',
       'questions', 'answers',
       'posts_edited', 'helpful_tags', 'votes_cast', 'member_since_in_months',
       'weighted_badge_score', 'QA_ratio','total_requirements_satisfied','Cluster']]


# In[48]:


kmodel_inference.groupby('Cluster').mean().round(2)


# In[49]:


kmodel_inference.Cluster.value_counts().reset_index(name='No of Candidates')


# ## Visualizing Clusters

# In[55]:


import seaborn as sns
palette = {0: "red", 1: "green", 2: "blue", 3: "lightgreen"} 
sns.pairplot(kmodel_inference, hue='Cluster', palette = palette)
plt.show()


# In[52]:


corr_matrix = kmodel_inference.groupby('Cluster').mean().round(2)
corr_matrix.sort_values(by='Cluster',inplace=True)
plt.figure(figsize=(10, 8))
sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap = 'viridis')
plt.title('Heatmap of Clusters')
plt.show()


# In[ ]:




