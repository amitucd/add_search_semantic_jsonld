##Postgresql Select query to retrieve search terms
import os
import psycopg2
from flask import  render_template, request, redirect, url_for, make_response, jsonify, Flask
import json
import pandas as pd

# Establish a database connection
connection = psycopg2.connect(
    host="localhost",
    database="ml_models",
    user="postgres",
    password="123"
)
# Create a cursor
cursor = connection.cursor()
app = Flask(__name__)

@app.route('/add_ndi', methods=['GET','POST'])
def add_docker_images():
    if request.method=="POST":
        data=request.get_json()
        print(data)
        if data['name']=="":
            return jsonify({"status":False})
        else:
            reqs=dict(zip(data["req"].split(","),[True]*len(data["req"].split(","))))
            try:
                reqs.pop("")
            except:
                pass
            data1={
                "@context": "http://schema.org",
                "name": data["name"],
                "url": data["url"],
                "description": data["desc"],
                "category": data["category"],
                "sub-type": data["sub_type"],
                "requirements": reqs,
                "tags": data["tags"].split(",")
            }
            cursor = connection.cursor()
            # Insert the tagged ML model into the table
            cursor.execute("""INSERT INTO ml_models (model_data) VALUES (%s)""", (json.dumps(data1),))
            # Commit the transaction
            connection.commit()
            cursor.close()
            return jsonify({"status":True})
    return app.make_response(render_template("add_docker_image.html"))


@app.route('/search_images', methods=['GET','POST'])
def search_docker_images():
    if request.method=="POST":
        data=request.get_json()
        data['tags']=data['tags'].split(",")
        try:
            data['tags'].remove("")
        except:
            pass
        data=dict((k, v) for k, v in data.items() if v)
        print(json.dumps(data))
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM ml_models WHERE model_data @> %s""", (json.dumps(data),))
        #cursor.execute("""SELECT * FROM ml_models WHERE model_data <@ %s""", (json.dumps(data),))
        filtered_models = cursor.fetchall()
        filtered_models=pd.DataFrame.from_records(filtered_models,columns=["id","model"])['model'].tolist()
        cursor.close()
        return jsonify(filtered_models)
    return app.make_response(render_template("search_docker_image.html"))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5050)
