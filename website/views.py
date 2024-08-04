from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from . import db, FILE_PATH, FILTER_SELECTION, LIMIT
import json, glob
from .func import allowed_file, read_json
from os.path import join, dirname, realpath, basename


#import analyze function
from .analyze import data_process, data_translate, category, history_csv_category, check_filter, AI

#import subprocess
from threading import Thread
from . import variables



UPLOADS_PATH = join(dirname(realpath(__file__)), 'static/uploads/')
ANALYZE_PATH = join(dirname(realpath(__file__)), 'static/analyzed_uploads/')
FILTER_PATH = join(dirname(realpath(__file__)), 'static/filter_config/')
VISUAL_PATH = join(dirname(realpath(__file__)), 'static/visuals/')



views = Blueprint('views', __name__)


# @views.route('/', methods=['GET', 'POST'])
# @login_required
# def home():
#     if request.method == 'POST': 
#         note = request.form.get('note')#Gets the note from the HTML 

#         if len(note) < 1:
#             flash('Note is too short!', category='error') 
#         else:
#             new_note = Note(data=note, user_id=current_user.id)  #providing the schema for the note 
#             db.session.add(new_note) #adding the note to the database 
#             db.session.commit()
#             flash('Note added!', category='success')

#     return render_template("home.html", user=current_user)


# @views.route('/delete-note', methods=['POST'])
# def delete_note():  
#     note = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
#     noteId = note['noteId']
#     note = Note.query.get(noteId)
#     if note:
#         if note.user_id == current_user.id:
#             db.session.delete(note)
#             db.session.commit()
#             flash(f'Note {noteId} is deleted', category='success')
#     return jsonify({})



@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    return render_template("home.html", user=current_user)




@views.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        if uploaded_file and allowed_file(uploaded_file.filename):
            uploaded_file.save(join(UPLOADS_PATH, uploaded_file.filename))
            flash("File uploaded successfully!", category= 'success')
        else:
            flash("File not uploaded! Please check the file extension!", category= 'error')
    return render_template('upload.html', user=current_user)



@views.route('/analysis', methods=['GET', 'POST'])
@login_required
def analysis():
    if request.method == 'POST':
        selected_option = request.form.get('option')
        flash(f"Selected option: {selected_option}", category='success')
        session['selected_option'] = {"File selected": str(selected_option)}
        session['from_analysis'] = True
        return redirect(url_for('.model'))
        
    
    session.clear()
    files = glob.glob(join(UPLOADS_PATH, '*.csv'))
    filenames_only = [basename(file) for file in files]
    return render_template('analysis.html', user=current_user,files = filenames_only)




@views.route('model', methods=['GET', 'POST'])
@login_required
def model():
    if request.method == 'POST':
        if request.form.get('restart')=='restart':
            return redirect(url_for('.analysis'))
        
        selected_filter = request.form.get('filter')
        cookie = session['selected_option']
        
        if 'Filter selected' not in cookie:
            cookie['Filter selected'] = str(selected_filter)
            flash(f"Selected filter: {selected_filter}", category='success')
            return render_template('model.html', user=current_user, option_list = LIMIT, dictionary = cookie, instruction = 'Please select the limit of the data you want to analyze (For debugging).', mode = 0)
        
        
        
        
        elif 'Limit selected' not in cookie:
            cookie['Limit selected'] = str(selected_filter)
            flash(f"Limit: {selected_filter}", category='success')
            session["list_of_filter"] = data_process(cookie['File selected'], cookie['Filter selected'], UPLOADS_PATH)
            if cookie["Filter selected"] == '服務類型 Service Type':
                return render_template('model.html', user=current_user, option_list = session["list_of_filter"], dictionary = cookie, instruction = 'Please select the ' + cookie['Filter selected'] + ' you want to analyze.', mode = 4)
            else:
                return render_template('model.html', user=current_user, option_list = session["list_of_filter"], dictionary = cookie, instruction = 'Please select the ' + cookie['Filter selected'] + ' you want to analyze.', mode = 0)
        
        
        
        
        elif 'Type selected' not in cookie:
            if cookie['Filter selected'] == '服務類型 Service Type':
                selected_filter = [str(request.form.get(f'filter{i}')) for i in range(4)]
                cookie['Type selected'] = list(selected_filter)
            else:
                cookie['Type selected'] = selected_filter
            flash(f"Selected type: {selected_filter}", category='success')
            
            validation = check_filter(cookie['File selected'], cookie['Filter selected'], cookie['Type selected'])

            if validation == 1: 
                return render_template('model.html', user=current_user, dictionary = cookie,  mode = 1)
            
            else:
                cookie.pop('Type selected', None)
                flash(f"NO entry is matching the filter criteria! Please select a valid filter!", category='error')
                if cookie["Filter selected"] == '服務類型 Service Type':
                    return render_template('model.html', user=current_user, option_list = session["list_of_filter"], dictionary = cookie, instruction = 'Please select the ' + cookie['Filter selected'] + ' you want to analyze.', mode = 4)
                else:
                    return render_template('model.html', user=current_user, option_list = session["list_of_filter"], dictionary = cookie, instruction = 'Please select the ' + cookie['Filter selected'] + ' you want to analyze.', mode = 0) 
        
        
        # else:
        #     chart = data_translate(cookie['File_selected'], cookie['Filter selected'], cookie['Type selected'],  cookie['Limit selected'])
        #     return render_template('model.html', user=current_user, dictionary = cookie,  mode = 2, visual = chart)
        
        
        
        elif request.form.get('start') == 'start':
            variables.init() #initialize the global status variable
            t1 = Thread(target=data_translate, args=(cookie['File selected'], cookie['Filter selected'],  cookie['Limit selected'], cookie))
            t1.start()
            return render_template('model.html', user=current_user, dictionary = cookie,  mode = 2)
        
        elif request.form.get('result') == 'result':
            # cookie['list_of_category'] = variables.list_of_category
            variables.list_of_category.append("ALL")            
            return render_template('model.html', user=current_user, dictionary = cookie,  mode = 5, visual = variables.chart, option_list = variables.list_of_category, diagram = variables.visualization)
        
        
        elif request.form.get('category') == 'category':
            variables.chart1, percentage = category(selected_filter, cookie['File selected'], variables.time_now)
            return render_template('model.html', user=current_user, dictionary = cookie,  mode = 5, visual = variables.chart1, option_list = variables.list_of_category, diagram = variables.visualization, data = percentage)
            
            
        else:
            return render_template('home.html', user=current_user)
            




    
    #Get request
    if "from_analysis" not in session.keys() or session['from_analysis'] == False:
        return redirect(url_for('.analysis'))
    else:
        session['from_analysis'] = False
        return render_template('model.html', user=current_user, option_list = FILTER_SELECTION, dictionary = session['selected_option'], instruction = 'Please select the type of filter for analysis.', mode = 0)
    
    
    
    
    
#Progress bar
@views.route('/status', methods=['GET'])
@login_required 
def getStatus():
    if variables.status == 0 or variables.total_data == 0:
        return json.dumps({'percentage':0})
    statusList = {'percentage':variables.percentage(),  'boolean': variables.first}
    return json.dumps(statusList)



#History
@views.route('/history', methods=['GET', 'POST'])
@login_required
def history():

    if request.method == "POST":
        if 'selected_option' not in session:
            session["selected_option"] = {}
        cookie = session['selected_option']
        selected_filter = request.form.get('option')
        

        if 'history_csv' not in cookie:
            cookie['history_csv'] = str(selected_filter)
            
            ###Read historical visualization
            html_file_name = cookie['history_csv'].rsplit(".",1)[0] + ".html"
            with open(VISUAL_PATH + html_file_name, "r") as file:
                historical_diagram = file.read()
            
            
            
            cookie['category_list'] = ["ALL"]
            cookie['category_list'].extend(list(history_csv_category(selected_filter)))
            return render_template('history.html', user=current_user, files = cookie['category_list'], mode = 0, instruction = 'Please select the category you want to view.', diagram = historical_diagram)
        

        elif request.form.get('submit') == 'submit':
            cookie['category'] = selected_filter
            session["category"] = selected_filter
            chart, percentage = category(cookie['category'], cookie["history_csv"])
            filter_config = read_json(FILTER_PATH, cookie["history_csv"])         
            
            ##Read historical visualization
            html_file_name = cookie['history_csv'].rsplit(".",1)[0] + ".html"
            with open(VISUAL_PATH + html_file_name, "r") as file:
                historical_diagram = file.read()

            return render_template('history.html', user=current_user, visual = chart, mode = 1, files = cookie['category_list'], instruction = 'Please select the category you want to view.', dictionary = filter_config, diagram = historical_diagram, data=percentage)
        

        #AI summary button
        elif request.form.get('AI') == 'AI':

            summary = AI(session['category'], cookie["history_csv"])
            chart, percentage = category(cookie['category'], cookie["history_csv"])
            filter_config = read_json(FILTER_PATH, cookie["history_csv"])         
            
            ##Read historical visualization
            html_file_name = cookie['history_csv'].rsplit(".",1)[0] + ".html"
            with open(VISUAL_PATH + html_file_name, "r") as file:
                historical_diagram = file.read()
            
            
            return render_template('history.html', user=current_user, visual = chart, mode = 2, files = cookie['category_list'], instruction = 'Please select the category you want to view.', dictionary = filter_config, diagram = historical_diagram, data=percentage, summary = summary)
            
    
    else:
        files = glob.glob(join(ANALYZE_PATH, '*.csv'))
        filenames_only = [basename(file) for file in files]
        filenames_only.sort(reverse=True)
        session.clear()
        return render_template('history.html', user=current_user, files = filenames_only, mode = 0, instruction = 'Please select the csv file you want to view.')


