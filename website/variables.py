
def init():
    global status
    global total_data
    global first
    global chart
    global chart1
    global list_of_category
    global time_now
    global visualization
    global X_pca
    global centroid
    
    
    status = 0
    total_data = 0
    first = 0
    chart = ""
    chart1 = ""
    list_of_category = []
    time_now = 0
    visualization = ""
    X_pca = 0
    centroid = 0
    
def percentage():
    global status
    global total_data
    return int(status/total_data*100)