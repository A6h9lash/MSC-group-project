### Import required packages!
import os
from app import app
from flask import Flask, Markup, render_template, flash,url_for, render_template, request, redirect,g,send_from_directory, Response, request, send_file
from forms import KinaseSearchForm, PhosphositeSearchForm, InhibitorSearchForm
from models import Kinase, Phosphosite, Inhibitors
from db_setup import init_db, db_session
import pandas as pd
import numpy as np
import requests
from bokeh.plotting import figure, show, output_notebook, output_file
from bokeh.models import Span, ColumnDataSource, HoverTool
from bokeh.resources import CDN
from bokeh.embed import file_html

###############################################################################


init_db() #initialise the database

###############################################################################
@app.route("/") #define homepage route
def home():
  return render_template("layout.html")

#
@app.route("/about_us")
def about_us():
    return render_template("about.html")

#
@app.route("/contact_us")
def contact_us():
    return render_template("contact.html")
#
@app.route("/help")
def help():
    return render_template("help.html")

###### Kinase #################################################################
@app.route('/kinase', methods=['GET', 'POST'])
def kinase():
    search = KinaseSearchForm(request.form) # import search form and run a request
    if request.method == 'POST': # if the user is searching for information (ie posting a searchstring to retrieve data)
        return Kinase_search_results(search) # run the kinase search function
    return render_template('kinase.html', form=search)

@app.route('/Kinase_search_results')
def Kinase_search_results(search):
    results = []
    search_string = search.data['search'] # search string given the user input data
    if search_string:
        if search.data['select'] == 'Kinase Gene Name': # check if protein kinase name was selected
            qry = db_session.query(Kinase).filter(Kinase.Kinase_Gene_Name.contains(search_string))
            results = qry.all() # output all the query results
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Inhibitors.Targets.contains(search_string))\
            .join(Kinase, Inhibitors.Targets.contains(search_string) == Kinase.Kinase_Gene_Name.contains(search_string))
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.Kinase_Gene_Name.contains(search_string))\
            .join(Phosphosite, Kinase.Kinase_Gene_Name.contains(search_string) == Phosphosite.Kin_Gene_Name.contains(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
        elif search.data['select'] == 'Kinase Uniprot ID': # check if uniprot id was selected
            qry = db_session.query(Kinase).filter(Kinase.UniProt_ID.ilike(search_string))
            results = qry.all()
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Kinase.UniProt_ID.contains(search_string))\
            .join(Inhibitors, Kinase.Kinase_Gene_Name == Inhibitors.Targets)
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.UniProt_ID.contains(search_string))\
            .join(Phosphosite, Kinase.Kinase_Gene_Name == Phosphosite.Kin_Gene_Name.ilike(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
        elif search.data['select'] == 'Alias Name': # check if alias name was selected #search_string = search_string.upper()
            kinase = db_session.query(Kinase).filter(Kinase.Alias.contains(search_string)) # query alias name
            qry = db_session.query(Kinase).filter(Kinase.Alias.contains(search_string))
            results = qry.all() # output all the query results
            iqry = db_session.query(Kinase, Inhibitors)\
            .filter(Kinase.Alias.contains(search_string))\
            .join(Inhibitors, Kinase.Alias.contains(search_string) == Inhibitors.Targets.contains(search_string))
            inhibresults = iqry.all()
            pqry = db_session.query(Kinase, Phosphosite)\
            .filter(Kinase.Alias.contains(search_string))\
            .join(Phosphosite, Kinase.Alias.contains(search_string) == Phosphosite.Kin_Gene_Name.ilike(search_string))
            phosphresults = pqry.all() # run a join query to find out kinase substrates
    if not results: # if no results were found
        flash('No results found!') #flash the error message
        return redirect('/kinase') # and return back to kinase search
    else:
        return render_template("kinase_search_results.html", results=results, inhibresults=inhibresults, phosphresults=phosphresults)


@app.route('/kinase/<kinase>') # for the internal hyperlink a kinase profile route is defined, and the <kinase> is queried as before.
def kinaseprofile(kinase):
    kinase = db_session.query(Kinase).filter(Kinase.Kinase_Gene_Name.contains(kinase)) # query alias name
    results = kinase.all()
    return render_template('kinase_Search.html', results=results)

###### Inhbitor ###############################################################
@app.route('/Inhibitor', methods=['GET', 'POST'])
def Inhibitor():
    search = InhibitorSearchForm(request.form)
    if request.method == 'POST':
        return inhibitor_search_results(search)# run the inhibitor search function if the method is POST
    return render_template('Inhibitor.html', form=search)

@app.route('/inhibitor_search_results')
def inhibitor_search_results(search):
    results = []
    search_string = search.data['search'] # search string given the user input data   
    if search_string:
        if search.data['select'] == 'Inhibitor ChEMBL ID':
            qry = db_session.query(Inhibitors).filter(Inhibitors.ChEMBL_ID.contains(search_string)) # search for chembl ID that is
            # same as the search string - use ilike for case sensitive search
            results = qry.all()
        elif search.data['select'] == 'Inhibitor Name':
            qry = db_session.query(Inhibitors).filter(Inhibitors.INN_Name.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Targets':
            qry = db_session.query(Inhibitors).filter(Inhibitors.Targets.contains(search_string))
            results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/Inhibitor')
    else:
        # display results
        return render_template("inhibitor_search_results.html", results=results)

@app.route('/Inhibitor/<INN_Name>') # for the internal hyperlink an inhibitor profile route is defined.
def inhib_INN_Name_profile(INN_Name):
    qry = db_session.query(Inhibitors).filter(Inhibitors.INN_Name.contains(INN_Name))
    results = qry.all()
    return render_template('inhibitor_search.html', results=results) # render the inhibitor results page

###### Phosphosites ###########################################################
@app.route('/Phosphosites', methods=['GET', 'POST'])
def Phosphosites():
    search = PhosphositeSearchForm(request.form)
    if request.method == 'POST':
        return phosphosite_search_results(search)# run the phosphosite search function if the method is POST
    return render_template('Phosphosite.html', form=search)

@app.route('/phosphosite_search_results')
def phosphosite_search_results(search):
    results = []
    search_string = search.data['search']
    if search_string:
        if search.data['select'] == 'Substrate Gene Name':
            qry = db_session.query(Phosphosite).filter(Phosphosite.Substrate_Gene_Name.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Substrate Uniprot ID':
            qry = db_session.query(Phosphosite).filter(Phosphosite.Substrate_UniProt_ID.contains(search_string))
            results = qry.all()
        elif search.data['select'] == 'Substrate Name':
            qry = db_session.query(Phosphosite).filter(Phosphosite.Substrate_Name.contains(search_string))
            results = qry.all()
    if not results:
        flash('No results found!')
        return redirect('/Phosphosites')
    else:
        return render_template("phosphosite_search_results.html", results=results)

@app.route('/substrate/<Substrate>') # for the internal hyperlink a substrate profile route is defined.
def substrateprofile(Substrate):
    qry = db_session.query(Phosphosite).filter(Phosphosite.Kin_Gene_Name.ilike(Substrate))
    results = qry.all()
    return render_template('phosphosite_search.html', results=results) # render the inhibitor results page

###############################################################################
###TOOLS ###
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))

ALLOWED_EXTENSIONS= set(['tsv'])   #only tsv files are allowed

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/data_file_results', methods=['GET','POST'])
def data_file_results():
    #Open file and filter data:
    df= pd.read_csv('az20.tsv', sep='\t', header=0, index_col=False, usecols=list(range(0,7)), na_values='inf') 
    df.columns=['Substrate','Control_mean','Inhibitor_mean','Fold_change','p_value','ctrlCV','treatCV'] #rename columns
    df=df.fillna({'ctrlCV':0, 'treatCV':0}) #replace NaN in variance columns with 0
    df=df.dropna(axis='index', how='any')
    df=df[~df.Substrate.str.contains("None")]
    M= r"\([M]\d+\)" #matches M in brackets with one or more digits
    df=df[~df.Substrate.str.contains(M)] #drops rows with M residue
    phos=df.Substrate.str.findall(r"\((.\d+)").apply(','.join, 1)
    df.insert(1, "Phosphosite", phos, True) #inserts phosphosite data as the second column
    df[["Substrate"]]=df.Substrate.str.extract(r"(.+)\(")

    #Data for volcano plot:
    df["Log_Fold_change"]=np.log(df["Fold_change"])
    df["Log_p_value"]=-np.log10(df["p_value"])

    #Volcano plot:
    p = figure(plot_width=700, plot_height=500)
    p.title.text="AZ20 Volcano Plot"
    p.title.text_font_size = "25px"
    p.xaxis.axis_label ="Log Fold Change"
    p.yaxis.axis_label ="-Log p-value"
    sig=Span(location=1.3, dimension='width', line_color='green', line_width=1.5, line_dash='dashed')
    p.add_layout(sig) #adds horizontal line where points below line are non-sig fold changes(-log(0.05)=1.3)
    p.scatter(x=df.Log_Fold_change, y=df.Log_p_value)

    #Embedding
    html =file_html(p, CDN)
    return html

###############################


if __name__ == "__main__":
  app.run(debug=True)
