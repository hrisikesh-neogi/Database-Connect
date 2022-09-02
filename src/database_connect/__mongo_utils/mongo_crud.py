#for mongodb
from typing import Any
import os
from numpy import unicode_
import pandas as pd
import pymongo
import json



class mongo_operation:
    """
    A single call to MongoDB operation.
    
    -------
    PARAMS:
        client_id: The client url that you get from mongodb webpage.
        db: The database one wants to connect to.

    on call:
            returns the database connection.
    """
    def __init__(self, client_url, database,collection_name):
        self.client_url = client_url
        self.database = database
        self.collection_name = collection_name
        self.__call__()
        

    def __call__(self):
        client = pymongo.MongoClient(self.client_url)
        self.db = client[self.database]
        self.collection = self.db[self.collection_name]
        



    def insert_record(self, record) -> Any: 
        """
        insert one record to mongodb

        ------
        :params
             collection_name: str,
                    name of the collection in mongodb
             record: dict,
                     the data to insert into mongodb. 
             
                     
        example: 
                #for one record
                insert_record( record = {'name':'python'})

                #for multiple record
                insert_record(
                              record = [
                                        {'name':'python',
                                        'used_as': 'programming_language'},
                                        {'name': 'R',
                                        'used_as': 'programming_language'}
                                        ]
                              )
        """

        
        if type(record) == list:
            for data in record:
                if type(data) != dict:
                    raise TypeError('record must be a dictionary. Example is given in the docstring of this function.')
            self.collection.insert_many(record)
        elif type(record)== dict:
            self.collection.insert_one(record)

    def bulk_insert(self, data, **kwargs):
        """ insert data from dataframe object / csv /excel file to mongodb
        
        ------
        PARAMS: 
              data : path of the csv file or pandas dataframe object
              collection_name : name of the collection
              
              **kwargs :
                        any parameters of pandas read function.
        
        """

       

        if type(data) != pd.core.frame.DataFrame:
            
            path = data
            if path.endswith('.csv'):
                data = pd.read_csv(path, encoding='utf8', **kwargs)
            elif path.endswith('.xlsx'):
                data = pd.read_excel(path, encoding = 'utf8', **kwargs)

    
            
        data_json = json.loads(data.to_json(orient='records'))
        self.collection.insert_many(data_json)
        # print('data inserted ')
        # lg.info('data inserted successfully')


    def find(self,  query={}):
        """
        To find data in mongo database
        returns dataframe of the searched data. 
        
        PARAMS: 
              query: dict,
                    query to find the data in mongo database 
                    -- example of query -- {"name":"sourav"}
        """
        
        if self.collection_name not in self.db.list_collection_names():
            raise NameError("Collection not found in mongo database. Check the spelling or check the name.")
        
        

        cursor = self.collection.find(query)
        data =  pd.DataFrame(list(cursor))
    

        return data 

    def update(self, where_condition,update_query):
        """
        To update data in mongo database
        
        PARAMS:
                where_condition: dict,
                               to find the data in mongo database -- example of query "{"name":"sourav"}"
                update_query : dict,
                               query to update the data in mongo database -- example of query 

        EXAMPLE:
                
                where_condition = {"name":'Rahul Roy'}
                update_query = {"name":'Sourav Roy'}

                ## it'll updata name from Rahul Roy to Sourav Roy.

        """

        
        self.collection.update_one(where_condition, {'$set':update_query})


