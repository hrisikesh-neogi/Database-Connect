from cassandra import AlreadyExists
import pandas as pd
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider




class cassandra_operations:

    # session = None
    global_session = None
    def __init__(self, zip_path, client_id, client_secret, keyspace,table_name):
        self.zip = zip_path
        self.client_id = client_id       
        self.client_secret = client_secret
        self.keyspace = keyspace
        self.table = table_name
        

    @property
    def session(self): 

        if cassandra_operations.global_session is None:
            print("hello")
            cloud_config = {
                'secure_connect_bundle': str(self.zip)
            }
            auth_provider = PlainTextAuthProvider(str(self.client_id),
                                                str(self.client_secret))
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            cassandra_operations.global_session= cluster.connect(str(self.keyspace))
        return cassandra_operations.global_session

      

    def __get_table_names(self):
        table_names = [table.table_name for table in self.session.execute(f"select * from system_schema.tables where keyspace_name = '{self.keyspace}';")]
        if self.table in table_names:
            self.__table_is_available = True
        else:
            self.__table_is_available = False

        return self.__table_is_available

    def create_table(self, column): 

        """
        to create a new table in cassandra database

        ------
        PARAMS:
              column: str,
                        pass the column names along with the specific data type. 

                        example:
                              column = "Level_Name text, Module_Name text, Date text, Time text, User text PRIMARY KEY , Message text"

        
        """
        
            
        if not self.__get_table_names():
            query = f" CREATE TABLE IF NOT EXISTS {self.tab}({column});"
            self.session.execute(query).one()
        else:
            print("table is already available in cassandra database")
            raise AlreadyExists(f"table {self.tab} is already available in cassandra database")

            
        # print(row)
        # print('database connected and table created')
        # lg.log(logfile, f'cassandra db:'+
        #         f'\n database connected and {self.tab} has been created')

    def insert_data(self, column,values):
        """ insert data into cassandra database

        -------
        PARAMS:
            column: str
            pass the column names along with the specific data type. 

            EXAMPLE:
                    column = "Level_Name text, Module_Name text, Date text, Time text, User text PRIMARY KEY , Message text"
            values: str,
                        pass the values in string format in an order of the column names. 
                    EXAMPLE:
                            values = ")

        N.B:
            if the table is already created, you can pass directly the column names instead of passing the datatypes also. Data types 
            are required so that if the table is not created, then the table could be created.

        
        """
        if not self.__get_table_names():
            self.create_table(column)
        
        query = f" insert into {self.tab} ({column}) values({values});"

        self.session.execute(query).one()
        






    def read_data(self):
        
        query = f"select * from {self.keyspace}.{self.tab};"
        data_in_database = self.session.execute(query)
        column_names = data_in_database.column_names

        data = pd.DataFrame(data_in_database, columns = column_names )
        return data

    def cass_update_tab(self, update_query, where_condition):  
        """
        where_condition: dict,
                               to find the data in mongo database -- example of query "{"name":"sourav"}"
                update_query : dict,
                               query to update the data in mongo database -- example of query 

        EXAMPLE:
                
                where_condition = {"name":'Rahul Roy'}
                update_query = {"name":'Sourav Roy'}

                ## it'll updata name from Rahul Roy to Sourav Roy.
        """
        
        query = f"UPDATE {self.keyspace}.{self.tab} SET {update_query} WHERE {where_condition};"
        self.session.execute(query).one()
        

    def cass_bulk_up(self, data):
        """ insert data from dataframe object / csv /excel file to cassandra database 
        
        ------
        PARAMS: 
              data : path of the csv file or pandas dataframe object
              
              **kwargs :
                        any parameters of pandas read function.
        
        """

        

        

        # inserting data from csv
        if type(data) != pd.core.frame.DataFrame:
            if data.endswith(".csv"):
                data = pd.read_csv(data,encoding="utf8")
            elif data.endswith(".xlsx"):
                data = pd.read_excel(data, encoding="utf8")

        column_names = ','.join([column for column in data.columns])

        data = [[data.loc[i, col] for col in data.columns ] for i in range(len(data)) ]
        for row in data:
            values_to_insert = ','.join([f"'{value}'" for value in row])

            query = f" insert into {self.tab} ({column_names}) values({values_to_insert});"

            self.session.execute(query).one()


    def delete_cass(self, condition):
        """
            Delete record in cassandra database.

            ------
            PARAMS:
                  condition: str,
                  pass the where_condition withc column name and values

                Example:

                    condition = "WHERE id = 29575fbh"
                            --- here id is column name and '29575fbh' is the value upon which the condition will run. 



        """
    
        query = f"DELETE FROM {self.keyspace}.{self.table} {condition};"
        self.session.execute(query).one()
       


    