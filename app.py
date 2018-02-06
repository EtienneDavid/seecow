from flask import Flask
from flask import jsonify
from flask import render_template
import pandas as pd
from dateutil import parser

app = Flask(__name__)

code_exploitation = 72369100
milk_price = 340

tb_constant = 38
tb_variable = 2.6
tp_constant = 32
tp_variable = 6.6

penalite_cellule = {}
penalite_cellule[400] = -15.245
penalite_cellule[300] = -9.147
penalite_cellule[250] = -3.049

df_controleperformance = pd.read_csv("https://plateforme.api-agro.fr/explore/dataset/seenergi-controle-de-performance/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&apikey=0e7fd717ca09975637fdca3ceec566a4231a56c6d3f2b8190aca9d1d",sep=";")
df_lactation = pd.read_csv("https://plateforme.api-agro.fr/explore/dataset/seenergi-lactation/download/?format=csv&timezone=Europe/Berlin&use_labels_for_header=true&apikey=0e7fd717ca09975637fdca3ceec566a4231a56c6d3f2b8190aca9d1d", sep=";")

def get_reduced_df(code_exploitation, df_controleperformance, df_lactation):
    return [df_controleperformance[df_controleperformance["NUCHEP"] == code_exploitation],df_lactation[df_lactation["NUCHEP"] == code_exploitation]]

def get_lactationdays(nunati, selected_control, df_l):
    dff_l = df_l[df_l['NUNATI'] == nunati].sort_values('DADELA', ascending=False)
    last_lactation = parser.parse(dff_l['DADELA'].values[0])
    selected_control = parser.parse(selected_control)

    return (selected_control - last_lactation).days

def get_ca(milk_price, milk_production, tb,tp, cellule, tb_constant,tb_variable,tp_constant,tp_variable, penalite_cellule):
    added_tb = (tb-tb_constant)*tb_variable
    added_tp = (tp-tp_constant)*tp_variable

    if cellule > 400:
        added_cellule = penalite_cellule[400]
    elif 400 >= cellule > 300:
        added_cellule = penalite_cellule[300]
    elif 300 >= cellule > 250:
        added_cellule = penalite_cellule[250]
    else:
        added_cellule = 0

    ca = (milk_production/1000) * (milk_price + added_tb+added_tp+added_cellule)
    return ca


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
    data['cellule'] = dff_cp['CELL'].values
    
    jour_lactation = [get_lactationdays(i, selected_control, df_l) for i in dff_cp['NUNATI']]
    production_list = dff_cp['ETFEOB'].values
    data['etat_production'] = production_list

    #Verifie que la vache est bien en production, retourne -1 sinon
    data['jour_lactation'] = [jour_lactation[i] if production_list[i] == 'P' else -1 for i in range(len(jour_lactation)) ]

    data['CA'] = [get_ca(milk_price, dff_cp['LAIT_TECHNIQUE'].values[i], dff_cp['TB'].values[i],dff_cp['TP'].values[i], dff_cp['CELL'].values[i], tb_constant,tb_variable,tp_constant,tp_variable, penalite_cellule) for i in range(len(dff_cp))]
    data['added_value'] = [100*((((data['CA'][i]*1000)/dff_cp['LAIT_TECHNIQUE'].values[i])-milk_price)/milk_price) for i in range(len(dff_cp))]
    return data


# We request the data needed to generate the seecow dashboard
@app.route('/')
def table(name=None):
    df_cp, df_l = get_reduced_df(code_exploitation,df_controleperformance,df_lactation)
    data = get_cows_table(df_cp,df_l)
    return render_template('index.html', data=data)