from neo4j import *
import json
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


node = conn.query('''CALL db.labels()''')# finding types of nodes
out = [res.data() for res in node]
# with open("nodeType.json", "w") as outfile:
# 	json.dump(out, outfile)
print(out)

relation = conn.query('''CALL db.relationshipTypes()''') #finding types of relationships in the database
out = [res.data() for res in relation]
# with open("relationType.json", "w") as outfile:
# 	json.dump(out, outfile)


nodeProperty = conn.query('''CALL db.schema.nodeTypeProperties''') # finding the node property
out = [res.data() for res in nodeProperty]
# with open("nodeAttribute.json", "w") as outfile:
# 	json.dump(out, outfile)
print(out)
k=out[0]['nodeType']
for _ in out:
    print(k)
    if()



nodeRelation = conn.query('''CALL db.schema.visualization()''') # finding the relation between the nodes
out = [res.data() for res in nodeRelation]
# with open("nodesRelation.json", "w") as outfile:
# 	json.dump(out, outfile)
# for _ in out:
#     for __ in _['relationships']:
#         print(__[0]['name'] + " " + __[1] + " " +__[2]['name'] )



# print(node.type())
# y = json.dumps(nodeRelation)
# print(out)



