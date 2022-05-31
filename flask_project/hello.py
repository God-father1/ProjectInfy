from neo4j import *
from flask import Flask, render_template, request, jsonify,redirect,url_for
import os,sys,requests, json
from random import randint


class Neo4jConnection:

    def __init__(self, uri, user, pwd):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query))
        except Exception as e:
            print("Query failed:", e)
        finally:
            if session is not None:
                session.close()
        return response

conn = Neo4jConnection(uri="bolt://localhost:7687", user="neo4j", pwd="root")

# app = Flask(__name__)
#
# @app.route('/login/#out/<name>')
# def success(name):
#    return 'RESULT is \n %s' % name
# node=[]
# @app.route('/login',methods = ['POST', 'GET'])
# def login():
#    if request.method == 'POST':
#       user = request.form['nm']
#       node = conn.query(user)
#       print(node)
#       out = [res.data() for res in node]
#       return redirect(url_for('success',name = out))
#    else:
#       user = request.args.get('nm')
#       return redirect(url_for('success',name = node))
#
# if __name__ == '__main__':
#    app.run(debug = True)

app = Flask(__name__)
@app.route('/')
def home():
  return render_template('index.html')
@app.route('/login',methods=['POST', 'GET'] )
def extract():
  text=str(request.form.get('nm'))
  payload = json.dumps({"sender": "Rasa", "text": text})
  headers = {"Content-type": "application/json", "Accept": "text/plain"}
  response = requests.request("POST",   url="http://localhost:5005/model/parse", headers=headers, data=payload)
  response=response.json()

  print(response)
  #query=response["text"]
  # print(query.capitalize() )
  entity=response["entities"]
  nodes={}
  for i in entity:
      nodes[i["entity"].capitalize()]=i["value"]
  # print(nodes)
  irelation=response["intent"]["name"]
  # print(irelation)
  res = queryGeneration(nodes,irelation)
  return render_template('index.html', result=res,text=text)

def queryGeneration(nodes,irelation):
    print(nodes,irelation)
    print(nodes.keys(),len(nodes))
    key=list(nodes.keys())
    key.sort()
    # print(key[0]=="Edge" and key[1]=="Movie")
    if((len(nodes)<=3) and (key[0]=="Edge" and key[1]=="Movie")):
        qstring = "MATCH (p:Person)-[r]->(m:Movie) WHERE (type(r)=~'(?i)("+nodes["Edge"]+")') AND (m.title=~'(?i)("+nodes["Movie"]+")') return p.name"
        res=conn.query(qstring)
        if not res:
            print("Generating New Query...")
            qstring = "MATCH (p:Person)-[r]->(m:Movie) WHERE (type(r)=~'(?i)("+irelation.upper()+")') AND (m.title=~'(?i)("+nodes["Movie"]+")') return p.name"
            res=conn.query(qstring)
        print(qstring)
        out = [res.data() for res in res]
        print(out)
        if out:
            return out
        else:
            return "Query Generation Engine is Facing problem in generating query..Please try rephrasing the text...."
    elif((len(nodes)==1) and (key[0]=="Person")):
        qstring = '''MATCH (a:Person{name:"'''+ nodes["Person"]+'''"})-[]->(m:Movie) RETURN m'''
        print(qstring)
        res=conn.query(qstring)
        if not res:
            print("Generating New Query...")
            qstring = "MATCH (p:Person)-[r]->(m:Movie) WHERE (type(r)=~'(?i)("+irelation.upper()+")') AND (m.title=~'(?i)("+nodes["Movie"]+")') return p.name"
            res=conn.query(qstring)
        print(qstring)
        out = [res.data() for res in res]
        print(out)
        if out:
            return out
        else:
            return "Query Generation Engine is Facing problem in generating query..Please try rephrasing the text...."
    else:
        print("Nothing ...")
    print("closing connection...")
    conn.close()

if __name__ == "__main__":
  app.run(debug=True)

# <table style="width:100%">
#    {% for dict_item in history_list %}
#    {% for key, value in dict_item.items() %}
#     <tr>
#         <th> {{ key }} </th>
#         <td> {{ value }} </td>
#     </tr>
#    {% endfor %}
# {% endfor %}
# </table>
