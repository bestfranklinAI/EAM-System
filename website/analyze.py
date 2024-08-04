#########################################################################################import library
import pandas as pd
import numpy as np
import glob

#Google translation API
from googletrans import Translator

#For progress bar
from tqdm import tqdm

#For interactive GUI window
from tkinter import *
from tkinter import messagebox

#for LLM access
import httpx
from string import Template

#For K-Means clustering algorithm
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

#Sub chinese characters
import re

#Visualization
from sklearn.decomposition import PCA

#Generate random number
import random


#Meta data import
from . import FILTER_SELECTION

#path
from os.path import join, dirname, realpath


#Progress bar
from . import variables
import time

#File name
from datetime import datetime
from .func import write_json


#Visualization of K-Means chart
import plotly.graph_objs as go



#Store path
STORE_PATH = join(dirname(realpath(__file__)), 'static/modified_uploads/')
ANALYZE_PATH = join(dirname(realpath(__file__)), 'static/analyzed_uploads/')
FILTER_PATH = join(dirname(realpath(__file__)), 'static/filter_config/')
VISUAL_PATH = join(dirname(realpath(__file__)), 'static/visuals/')




#########################################################################################helper function

def dropdown(options):

    # Create the main window
    root = Tk(screenName="Filter")

    # Set the window size
    root.geometry("300x150")


    # Variable to hold the selected option
    selected_month = StringVar()
    selected_month.set(options[0])  # Set the default option

    # Create the dropdown menu
    dropdown_menu = OptionMenu(root, selected_month, *options)
    dropdown_menu.pack(pady=20)

    # Function to display the selected option
    def show_selection():
        root.destroy()
        return

    # Button to trigger the function
    button = Button(root, text="Confirm", command=show_selection)
    button.pack()

    # Start the application
    root.mainloop()
    return selected_month.get()
    


def error(message):

    root = Tk()
    root.withdraw()  # Hide the main window
    
    # Display the error message in a message box
    messagebox.showerror("Error", message)



def ask(OLLAMA_ENDPOINT, OLLAMA_CONFIG, PROMPT_TEMPLATE, text):
    prompt = PROMPT_TEMPLATE.substitute(text=text)
    response = httpx.post(
        OLLAMA_ENDPOINT,
        json={"prompt": prompt, **OLLAMA_CONFIG},
        headers={"Content-Type": "application/json"},
        timeout=100,
    )
    if response.status_code != 200:
        print("Error", response.status_code)
        return None
    return response.json()["response"].strip()


def GPT(PROMPT, PROMPT_TEMPLATE, progress_bar = True):
    global pbar
    OLLAMA_ENDPOINT = "http://localhost:11434/api/generate"
    OLLAMA_CONFIG = {
        "model": "llama3.1",
        "keep_alive": "5m",
        "stream": False,
    }

    prompt = [OLLAMA_ENDPOINT, OLLAMA_CONFIG, PROMPT_TEMPLATE, PROMPT]
    if progress_bar:
        pbar.update(1)
        variables.status = variables.status + 1
    
    return ask(*prompt)


def remove_chinese(text):
    return re.sub(r'[\u4e00-\u9fff]+', '', str(text))

    
    
    
    
def translate(text):   
    global pbar
    if text == 'nan' or text == 'NaN' or text == np.nan:
        pbar.update(1)
        return np.nan
    translator = Translator()
    raw_trans = translator.translate(text, dest='en')

    translation = raw_trans.text
    pbar.update(1)
    variables.status = variables.status + 1
    # print(translation)
    return translation




def style(df, random = False):
    df = df.drop(columns=["設備所屬部門 Equipment Department", "報單人部門 Reporter Department", "業務類型 FM Type", "逼切性 Priority", "狀態 Status", "報單人Repoter", "報單人賬號Reporter", "報單時間 Creation Time", "責任人 Principal", "工單完成時間 Completion Time", "實際縂工時 Actual Total Working Hours", "操作 Operation", "服務類型 Service Type", "translated", "distance", "detailed_summary", "filter_1", "filter_2", "filter_3", "filter_4"])
    print(f"rows: {df.shape[0]}")
    
    if random:
        return df.sample(n=15).style.set_properties(subset=['工單描述 Wo Description'], **{'width': '500px'})
    else :
        return df.style.set_properties(subset=['工單描述 Wo Description'], **{'width': '500px'})





#########################################################################################Main Program 
row_limited = 51
#########################################################################################Define a function that can be called (argument : csv file, filter, limit)
def data_process(csv, filter_by, path):
    global row_limited

    #Data Processing (Remove chinese words and translation)
    
    select_filter = True
    # filter_by = dropdown(["服務類型 Service Type", "工作組 Work Unit"])


    # list_of_csvs = glob.glob('*.csv')
    df = pd.read_csv(path+csv)

    #Remove chinese words
    df['設施設備 Equipment'] = df['設施設備 Equipment'].apply(remove_chinese)
    
    #Split to 4 filter columns
    split_columns = df['服務類型 Service Type'].str.split(pat='/',n=3, expand=True)
    df['filter_1'] = split_columns[0]
    df['filter_2'] = split_columns[1]
    df['filter_3'] = split_columns[2]
    df['filter_4'] = split_columns[3]
    
    #Temporary store the csv file
    df.to_csv(STORE_PATH+csv, index = False)
    
    # counts = df["服務類型 Service Type"].value_counts()

    if(select_filter):
        if filter_by == "服務類型 Service Type":
            # counts = df["服務類型 Service Type"].value_counts()

            # selected_rows = counts[counts > 50].sort_values(ascending=False).index

            # list_of_filters = list(selected_rows)
            
            filter_lists = []
            filter_lists.append(list(df["filter_1"].value_counts().index))
            filter_lists.append(list(df["filter_2"].value_counts().index))
            filter_lists.append(list(df["filter_3"].value_counts().index))
            filter_lists.append(list(df["filter_4"].value_counts().index))
            

            return filter_lists
            
            
            
        elif filter_by == "工作組 Work Unit":
            counts = df["工作組 Work Unit"].value_counts()

            selected_rows = counts[counts > 50].sort_values(ascending=False).index

            list_of_filters = list(selected_rows)

            return list_of_filters

            
    # else:
    #     filter = "General"
    #     df_sort = df
    #     return NONE
 
 
 
def check_filter(csv, filter_by, filter):
    df = pd.read_csv(STORE_PATH+csv)

    if(filter_by == "服務類型 Service Type"):
        ####Handle filter
        df_sort = df
        if filter[0] != "ALL":
            df_sort = df_sort[df_sort["filter_1"] == (filter[0])]
        if filter[1] != "ALL":
            df_sort = df_sort[df_sort["filter_2"] == (filter[1])]
        if filter[2] != "ALL":
            df_sort = df_sort[df_sort["filter_3"] == (filter[2])]
        if filter[3] != "ALL":
            df_sort = df_sort[df_sort["filter_4"] == (filter[3])]
    else:
        df_sort = df[df[filter_by] == filter]  

    num = df_sort.shape[0]
    ######
    ###consider edge case
    if num == 0:
        return -1
    
    df_sort.to_csv(STORE_PATH+csv, index = False)   
    return 1
        
      
      
def data_translate(csv, filter_by, limit, cookie):
    global row_limited
    global pbar
    
    df_sort = pd.read_csv(STORE_PATH+csv)
    
    # if(filter_by == "服務類型 Service Type"):
    #     ####Handle filter
    #     df_sort = df
    #     if filter[0] != "ALL":
    #         df_sort = df_sort[df_sort["filter_1"] == (filter[0])]
    #     if filter[1] != "ALL":
    #         df_sort = df_sort[df_sort["filter_2"] == (filter[1])]
    #     if filter[2] != "ALL":
    #         df_sort = df_sort[df_sort["filter_3"] == (filter[2])]
    #     if filter[3] != "ALL":
    #         df_sort = df_sort[df_sort["filter_4"] == (filter[3])]
    # else:
    #     df_sort = df[df[filter_by] == filter]  
    
    
    
    
    
    
    ######
    num = df_sort.shape[0]

    
    

    
    
    if(limit == "TRUE"):
        df_sort = df_sort[:row_limited] #delete this
        
        
        


    if filter_by == "服務類型 Service Type":
        if num < 15:
            true_k = 2
        elif num < 50:
            true_k = 3
        elif num < 100:
            true_k = 4
        elif num < 200:
            true_k = 5
        elif num < 500:
            true_k = 6
        else:
            true_k = 8
    else:
        if num < 10:
            # error("The number of row is smaller than 10")
            true_k = 2
            

        elif num <= 50:
            true_k = 5
            

        elif num <= 100:
            true_k = 10
            
        elif num <= 200:
            true_k = 15

        elif num <= 500:
            true_k = 20

        elif num <= 800:
            true_k = 25

        else:
            true_k = 30


    variables.total_data = len(df_sort)
    with tqdm(total=len(df_sort)) as pbar:
            df_sort["translated"] = df_sort["工單描述 Wo Description"].apply(translate)
    
    variables.first = 1
    #########################################################################################Using GPT to format the summary      
            
    PROMPT_TEMPLATE = Template(
        """Summarize this sentence into two parts and output should strictly follows this template, DO NOT include unnecessary words or sentences: 
        
        <what is broken> | <the reason for maintenance>
        

    ${text}

    """
    )

    variables.status = 0
    variables.total_data = len(df_sort)
    
    with tqdm(total=len(df_sort)) as pbar:
            df_sort.loc[:, "Summary"] = df_sort.loc[:, "translated"].apply(GPT, args=(PROMPT_TEMPLATE,))
            
    variables.first = 2





    # df_sort[["what is broken","the reason for maintenance"]] = df_sort["Summary"].str.split(pat = "|", n = 1, expand=True).astype(str)
    split = df_sort.loc[:, "Summary"].str.split(pat = "|", n = 1, expand=True)
    df_sort.loc[:, "what is broken"] = split[0]
    df_sort.loc[:, "the reason for maintenance"] = split[1]
    df_sort.loc[:, "detailed_summary"] = ""

    for row in df_sort.index:
        if type(df_sort.loc[row, "設施設備 Equipment"]) == str:
            df_sort.loc[row, "detailed_summary"] = str(df_sort.loc[row, "設施設備 Equipment"]) + " " + str(df_sort.loc[row, "Summary"])
        else:
            df_sort.loc[row, "detailed_summary"] = df_sort.loc[row, "Summary"]
        

    #########################################################################################K-Means Clustering

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(df_sort['detailed_summary'])

    model = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1)

    fitted_model = model.fit(X)
    fitted_model


    label = fitted_model.predict(X)
    df_sort.loc[:, "category"] = label



    #########################################################################################Data Processing (Outliers)

    array = fitted_model.transform(X)

    selection_matrix = np.array(df_sort["category"]).reshape(-1,1) == np.arange(true_k)

    distance = np.sum(array * selection_matrix, axis=1)

    df_sort.loc[:, "distance"] = distance

    mask = df_sort["distance"] < df_sort["distance"].quantile(q=0.8)
    df_sort = df_sort[mask]
    X= X[mask]
    
    time_now = str(datetime.now())
    filename = "[" + time_now + "]" + csv
    df_sort.to_csv(ANALYZE_PATH + filename, index = False)


    ########################################################################################Common area for Maintenance
    variables.list_of_category = list(df_sort["category"].value_counts().index)
    variables.chart =  style(df_sort).to_html(na_rep = "N/A")
    
    
    
    ########Data visualization#########
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)
    centroid = pca.transform(model.cluster_centers_)
    
    
    #coordinates categorized by category
    data_points_coordinates = [X_pca[df_sort["category"] == i] for i in range(true_k)]

    #Initialize colors for plotting
    # colors = ["blue", "green", "orange", "purple", "yellow"]
    colors = ["blue", "green", "yellow", "purple", "orange", "pink", "black", "gray", "brown", "cyan"]
    scatter = []

    # Create a scatter plot for the PCA-transformed data
    for i in range(true_k):
        scatter.append(go.Scatter(
            x=data_points_coordinates[i][:, 0],
            y=data_points_coordinates[i][:, 1],
            mode='markers',
            marker=dict(size=10, color=colors[i%10]),
            name='Category ' + str(i)
        ))

    centroid_scatter = []
    # Create a scatter plot for the centroids
    for i in range(true_k):
        centroid_scatter.append(go.Scatter(
            x=[centroid[i][0],],
            y=[centroid[i][1],],
            mode='markers',
            marker=dict(size=15, color='red'),
            name='Centroids ' + str(i)
        ))

    # Create a layout
    layout = go.Layout(
        title='PCA Visualization',
        xaxis=dict(title='Principal Component 1'),
        yaxis=dict(title='Principal Component 2')
    )

    # Create a figure and add the scatter plots
    fig = go.Figure(data=[*scatter, *centroid_scatter], layout=layout)
    variables.visualization = fig.to_html(full_html=False)
    
    
    # Save the figure to an HTML file
    html_filename = csv.rsplit(".", 1)[0] + ".html"
    
    with open(VISUAL_PATH + "[" + time_now + "]" + html_filename, "w") as chart:
                chart.write(fig.to_html(full_html=False))
    
    
    # fig.write_html(VISUAL_PATH + "[" + time_now + "]" + html_filename)

    
    
    ############################################
    
    
    #Save the configuration file
    variables.time_now = time_now
    write_json(FILTER_PATH, filename, cookie)

    


def category(filter, csv, time="", html = True):
    # category = int(input("Please input the category(0-19):"))
    if time == "":
        df_sort = pd.read_csv(ANALYZE_PATH+csv)
    else:
        df_sort = pd.read_csv(ANALYZE_PATH+"["+str(time)+"]"+csv)
    if filter != "ALL":
        df_sort_category = df_sort[df_sort["category"] == int(filter)]
    else:
        df_sort_category = df_sort
    percentage = f"Percentage : {int(df_sort_category.shape[0]/df_sort.shape[0]*100)}%, Category {filter} : {df_sort_category.shape[0]}/{df_sort.shape[0]}"
    return (style(df_sort_category).to_html(na_rep = "N/A"), percentage) if html else df_sort_category

#########################################################################################History
def history_csv_category(csv):
    df_sort = pd.read_csv(ANALYZE_PATH+csv)
    return df_sort["category"].value_counts().index











    # #########################################################################################Visualization



    # pca = PCA(n_components=2)
    # # X_pca = pca.fit_transform(X)[df_sort["category"] == category]
    # X_pca = pca.fit_transform(X)
    # centroid = pca.transform(model.cluster_centers_)

    # random_numbers = np.random.uniform(-0.02, 0.02, size=X_pca.shape)
    # X_pca += random_numbers

    # plt.scatter(X_pca[:, 0], X_pca[:, 1])
    # plt.scatter(centroid[:, 0], centroid[:, 1], s=10, c='red')
    # plt.xlabel('Principal Component 1')
    # plt.ylabel('Principal Component 2')
    # plt.show()


    #########################################################################################Summary of possible reasons / categories (GPT)
def AI(filter, csv):

    df_sort_category = category(filter, csv, html = False)
    
    reasons = []
    for row in df_sort_category.index:
        reasons.append(df_sort_category.loc[row, "detailed_summary"])
        


    PROMPT_TEMPLATE = Template(
        """You are provided with a list of description of one single maintenance reasons in the following format:
        <what is broken> | <the reason for maintenance>
        
        Here is the data for analysis:

        "${text}"
        
        Please generalize ONE maintenance reason in the following format, DON't include unnecessary words or sentences, DON'T chat, DIRECTLY give the output:
        
        
        **What is broken:** <specific type or name of the equipment that required maintenance> 
        \n  
        **Common location:** <Common location that required maintenance>
        \n
        **The reason for maintenance:** <summary of the main reason for maintenance>
        \n
        **Detailed Summary** : <holistic analysis of the common pattern of maintenance reason in 3-5 bullet points in mark down format separate by a new line character>
        \n
        

    """)

    summary = str(GPT(str(reasons), PROMPT_TEMPLATE, progress_bar=False))
    # summary_list = summary.split(sep="|", maxsplit=3)
    
    return summary



    #########################################################################################Load existing csv file
    # list_of_csvs = glob.glob('*.csv')
    # dfs = {csv : pd.read_csv(csv) for csv in list_of_csvs}
    # simplified = True
    # file = "General.csv"
    # if(simplified):
    #     display(style(dfs[file]))
    # else:
    #     display(dfs[file])
        
        
        
        
        
    # dfs[file]["category"].value_counts()



    # category = int(input("Please input the category(0-19):"))
    # style(dfs[file][dfs[file]["category"] == category])





