import pymongo

def getMongoClient(host='localhost', port=27017):
    client = pymongo.MongoClient(host='localhost', port=27017)
    return client

def getMongoDatabase(host='localhost', port=27017, dbname="test"):
    """注意: 在 MongoDB 中，数据库只有在内容插入后才会创建! 就是说，数据库创建后要创建集合(数据表)并插入一个文档(记录)，数据库才会真正创建。"""
    client = pymongo.MongoClient(host='localhost', port=27017)
    return client.get_database(dbname)

def getMongoCollection(database,collectionname):
    """注意: 在 MongoDB 中，集合只有在内容插入后才会创建! 就是说，创建集合(数据表)后要再插入一个文档(记录)，集合才会真正创建。"""
    return database.get_collection(collectionname)

def testInsertOne():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    tb.insert_one({"name": "xaioming", "age": 23})

def testInsertMany():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    tb.insert_many([{"name": "xaioming", "age": 24},{"name": "xaioming", "age": 25}])

def testUpdate():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    tb.update_one({"age": 24},{"$set":{"name": "xaioming", "age": 23}},upsert=True)

def testFindOne():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    return tb.find_one({"age": 24},{"_id": 0,"name": 1, "age": 1})

def testFind():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    return tb.find({},{"_id": 0,"name": 1})

def testUpdateMany():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    tb.update_many({"age": 24},{"$set":{"age": 11}} )

def testDeleteMany():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    tb.delete_many({"age": 11})

def testSort():
    database = getMongoDatabase(dbname="test1")
    tb = database.get_collection("aa")
    return tb.find().sort([("name",1),("age",pymongo.DESCENDING)])

print([a for a in testSort()])