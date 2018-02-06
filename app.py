from flask import Flask
from flask import jsonify
from flask import render_template
import pandas as pd

app = Flask(__name__)

code_exploitation = 72369100
df_controleperformance = pd.read_csv("https://plateforme.api-agro.fr/explore/dataset/seenergi-controle-de-performance/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&apikey=0e7fd717ca09975637fdca3ceec566a4231a56c6d3f2b8190aca9d1d",sep=";")
df_lactation = pd.read_csv("https://plateforme.api-agro.fr/explore/dataset/seenergi-lactation/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&apikey=0e7fd717ca09975637fdca3ceec566a4231a56c6d3f2b8190aca9d1d", sep=";")

def get_reduced_df(code_exploitation, df_controleperformance, df_lactation):
    return [df_controleperformance[df_controleperformance["NUCHEP"] == code_exploitation],df_lactation[df_lactation["NUCHEP"] == code_exploitation]]

def get_cows_table(df_cp, df_l, selected_control=None):
    if selected_control== None:
        # If no control date is provided, we take the last available control
        selected_control = df_cp['DAPAUL'].sort_values(ascending=False).unique()[0]
    
    dff_cp = df_cp[df_cp['DAPAUL']==selected_control]

    data = {}
    # Le nom de travail se compose des quatres derniers chiffres de l'identifiant
    data['nom'] = [str(int(i))[:-4] for i in dff_cp['NUNATI'].values]
    data['race'] = dff_cp['RACE'].values
    data['rang'] = dff_cp['NULACT'].values
    data['tb'] = dff_cp['TB'].values
    data['tp'] = dff_cp['TP'].values
    data['çellule'] = dff_cp['CELL'].values

    return data


# We request the data needed to generate the seecow dashboard
@app.route('/')
def table(name=None):
    df_cp, df_l = get_reduced_df(code_exploitation,df_controleperformance,df_lactation)
    data = get_cows_table(df_cp,df_l)
    print(data)
    return render_template('index.html', data=data)