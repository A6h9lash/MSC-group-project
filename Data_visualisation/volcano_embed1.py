import pandas as pd
import numpy as np
import requests
from bokeh.plotting import figure, show, output_notebook, output_file
from bokeh.models import Span, ColumnDataSource, HoverTool
from bokeh.resources import CDN
from bokeh.embed import file_html

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