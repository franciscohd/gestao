from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'funcionarios'


@app.route("/", methods=['POST'])
def home():
    return render_template('index.html')



@app.route("/registo", methods=['GET', 'POST'])
def registo():
    return render_template('registo.html')


@app.route("/addfuncionario", methods=['POST'])
def AddFuncionario():
    nome_funcionario = request.form['nome_funcionario']
    sobrenome_funcionario = request.form['sobrenome_funcionario']
    funcao = request.form['funcao']
    email = request.form['email']
    genero = request.form['genero']
    morada = request.form['morada']
    foto = request.files['foto']

    insert_sql = "INSERT INTO funcionarios VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if foto.filename == "":
        return "Por favor seleccione uma foto"

    try:

        cursor.execute(insert_sql, (nome_funcionario, sobrenome_funcionario, funcao, email, genero, morada))
        db_conn.commit()
        nome_completo = "" + nome_funcionario + " " + sobrenome_funcionario
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = str(nome_funcionario) + "-" + str(sobrenome_funcionario) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserida no MySQL RDS... a fazer upload da imagem para o S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=foto)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("tudo feito...")
    return render_template('AddEmpOutput.html', name=nome_completo)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
