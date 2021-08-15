from flask import Flask,render_template,url_for,request,jsonify
from flask_table import Table, Col
from flask_sqlalchemy import SQLAlchemy

import os
import pickle
import pandas as pd
import numpy as np
import sqlite3

#Init App
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite3:///churnclient2.sqlite3'


@app.route('/')
def index():
	return render_template('index.html ')

@app.route('/test')
def test():
	return render_template('test.html ')	



@app.route('/predictun')
def predictun():
	return render_template('predictuniq.html ')	


@app.route('/predictplus')
def predictplus():
	return render_template('predictmul.html')


# @app.route("/predict_un")
# def predict_un():
	

@app.route('/predict_un',methods=['GET','POST'])
def predict_un():
	#loadind model
	pickle_in = open('models/model.pkl', 'rb')
	clf = pickle.load(pickle_in)
	

	if request.method == 'POST':
		namequery1 = request.form['namequery1']
		namequery2 = request.form['namequery2']
		namequery3 = request.form['namequery3']
		namequery4 = request.form['namequery4']
		namequery5 = request.form['namequery5']
		namequery6 = request.form['namequery6']
		namequery7 = request.form['namequery7']
				
		result = clf.predict(np.array([[namequery1, namequery3, namequery3, namequery4,namequery5,namequery6,namequery7]]).astype(np.float64))
		if result==1:
			res="Prediction : Client désouscrit ou  ayant une probabilité de Supérieur a 99 pourcent de départ."
		elif result==0:
			#print(res)
			res="Prediction : Client Existant sur le Service"
			#print(res)
		return render_template('predictuniq.html', prediction=res)


@app.route('/pred_plus',methods=['GET','POST'])
def pred_plus():
	if request.method == 'POST':
		client_numb=int(request.form.get('client_numb'))
		conn=sqlite3.connect('churnclient2.sqlite3')
		cur=conn.cursor()
		cur.execute('SELECT CLIENTNUM,Total_Trans_Ct,Total_Revolving_Bal,Total_Relationship_Count,Total_Ct_Chng_Q4_Q1,Total_Trans_Amt,Months_Inactive_12_mon,Total_Amt_Chng_Q4_Q1,Attrition_Flag FROM `dataweb1`ORDER BY RANDOM()LIMIT {}'.format(client_numb))
		datadb=cur.fetchall()
		cur.close()
		dat=np.array(datadb)
		df1=pd.DataFrame(dat, columns=['CLIENTNUM','Total_Trans_Ct','Total_Revolving_Bal','Total_Relationship_Count','Total_Ct_Chng_Q4_Q1','Total_Trans_Amt','Months_Inactive_12_mon','Total_Amt_Chng_Q4_Q1','Attrition_Flag'])
		indexs=df1['CLIENTNUM']
		df_x2= df1.drop(['CLIENTNUM','Attrition_Flag'],axis=1)

		#loadind model
		pickle_in = open('models/model.pkl', 'rb')
		clf = pickle.load(pickle_in)
		result = clf.predict(np.array(df_x2).astype(np.float64))

		#print(result)
		resul2=pd.DataFrame(result,columns=['prediction'])
		resul2=resul2.replace({1: "Attrited Customer",0:"Existant sur le Service"})
		df2=pd.concat([df1,resul2],axis=1)
		df2.columns = ['Identifiant Client','Nbre de Transactions','Solde renouvelable de la carte','Nombre de produits détenus','Changement du nbre de transactions','Montant de transaction','Nbre Mois Inactif','Montant des transaction Q4-Q1','Staut_Actuel','prediction']
		heat=['Identifiant Client','Nbre de Transactions','Solde renouvelable de la carte','Nombre de produits détenus','Changement du nbre de transactions','Montant de transaction','Nbre Mois Inactif','Montant des transaction Q4-Q1','Staut_Actuel','prediction']
		val=df2[heat].values
	return render_template('t.html', heat=heat, val=val)

if __name__=='main__':
	app.run(host='0.0.0.0')
