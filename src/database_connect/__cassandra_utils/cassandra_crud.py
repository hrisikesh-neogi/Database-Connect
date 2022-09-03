from cassandra import AlreadyExists,InvalidRequest
from cassandra.cluster import NoHostAvailable                           
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
        if cassandra_operations.global_session != None:
            self.__delete_sessions
        

    @property
    def session(self): 

        if cassandra_operations.global_session is None:
            cloud_config = {
                'secure_connect_bundle': str(self.zip)
            }
            auth_provider = PlainTextAuthProvider(str(self.client_id),
                                                str(self.client_secret))
            cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
            cassandra_operations.global_session= cluster.connect(str(self.keyspace))
        return cassandra_operations.global_session

    
    @session.deleter
    def __delete_sessions(self):
        del cassandra_operations.global_session

      
    def __get_keyspace_names(self):
        keyspace_names = [keyspace.keyspace_name for keyspace in self.session.execute("select * from system_schema.keyspaces")]
        if self.keyspace in keyspace_names:
            self.__keyspace_is_available = True
        else:
            self.__keyspace_is_available = False

            

    def lists(self, list_by=None):
        """
        returns a list of keyspaces or tables

        PARAMS
        -------
        list_by:
                {'table','keyspace'}
                if 'table', returns list of all tables
                if 'keyspace', returns list of all keyspaces
        """
        try:
            if list_by == 'table':
                available_list = [table.table_name for table in self.session.execute(f"select * from system_schema.tables where keyspace_name = '{self.keyspace}';")]

            

            elif list_by == 'keyspace':
                available_list = [keyspace.keyspace_name for keyspace in self.session.execute("select * from system_schema.keyspaces")]


            return available_list

        except UnboundLocalError:
            raise Exception("list_by must be either 'table' or 'keyspaces'")


    def __get_table_names(self, table_name = None):
        table_names = [table.table_name for table in self.session.execute(f"select * from system_schema.tables where keyspace_name = '{self.keyspace}';")]
        if table_name == None:
            table = self.table
            
        else:
            table = table_name

        if table in table_names:
            self.__table_is_available = True
        else:
            self.__table_is_available = False

        return self.__table_is_available

    def __value_transformations(self,values_to_insert):
        """
        by default the values will be in a single quotation, that is why
        when we split the values, it will be inside quotation which if tried to upload
        throw errors. That is why the values need to be out of quotation.
        See the example below.

        Args:
            values (str): a string containing values

        Returns:
            tuple: the transformed values
            which makes int and float values our of quotations.

        Example:
                raw_values = "hrisikesh neogi, ineuron.ai, 1234"

                after splitting with comma, the values will be looking like - 
                raw_values = ["hrisikesh neogi", "ineuron.ai", "1234"]


        """
        
        values = values_to_insert.split(',')
        for value in values:
            try:
                index_of_value = values.index(value)
                value = value.strip()
                if value.isdigit():
                    value = int(value)
                else:
                    value = float(value)
                
                
                values.pop(index_of_value)
                values.insert(index_of_value,value)
                
                
            
            except:
                pass
        return tuple(values)

    def create_table(self, columns, table_name = None ): 

        """
        to create a new table in cassandra database

        ------
        PARAMS:
              column: str,
                        pass the column names along with the specific data type. 

                        example:
                              column = "Level_Name text, Module_Name text, Date text, Time text, User text PRIMARY KEY , Message text"

        
        """
        try:
            self.__get_keyspace_names()
        except NoHostAvailable:
            raise LookupError(f"The Keyspace named {self.keyspace} is not available. You need to create it in datastax page.")
            
        if table_name == None:    
            if not self.__get_table_names():
            
                table = self.table
            else:
                raise AlreadyExists(keyspace=self.keyspace, table=self.table)
                
        else:
            table = table_name

        query = f" CREATE TABLE IF NOT EXISTS {table}({columns});"
        self.session.execute(query).one()
        

            
        # print(row)
        # print('database connected and table created')
        # lg.log(logfile, f'cassandra db:'+
        #         f'\n database connected and {self.tab} has been created')

    def insert_data(self, columns,values, table_name=None):
        """ insert data into cassandra database

        -------
        PARAMS:
            columns: str
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

        values = self.__value_transformations(values)
        if table_name == None:
            if not self.__get_table_names():
                self.create_table(columns)
            table = self.table
        else:
            if not self.__get_table_names(table_name=table_name):
                self.create_table(table_name=table_name, column= columns)  #creating new table
            table = table_name

          

        

        
        column_names = ','.join([name.split(' ')[0] if len(name.split(' ')[0])>1 else name.split(' ')[1] for name in [column for column in columns.split(',')] ])
        query = f" insert into {table} ({column_names}) values{values};"

        self.session.execute(query).one()
    






    def read_data(self, table_name = None):
        if table_name == None:
            table = self.table
        else:
            table = table_name
        
        query = f"select * from {self.keyspace}.{table};"
        data_in_database = self.session.execute(query)
        column_names = data_in_database.column_names

        data = pd.DataFrame(data_in_database, columns = column_names )
        return data

    
        


    def __create_Table_for_uploading_data(self,table_name, columns):
            """
            if url/path is given, this function is being utilised

            PARAMS:
            input_data:input give to the main function by user
                columns : list of column names of pandas dataframe object
            """
            #by default we will be setting the first column as primary key
            columns = [column for column in columns ]
            first_column = columns.pop(0)
            first_column = first_column+' '+'text'+' '+'PRIMARY KEY'+','
            rest_column_names = ','.join([column+' '+'text' for column in columns]) #by default it will add a text datatype to each column so that it can create a table
            
            all_column_names = first_column+rest_column_names

            #creating table
            self.create_table(columns=all_column_names,
                                table_name=table_name)

            print("new table created")
            # return table_name, column_names


    def __load_data(self,data,columns = None, create_new_table = False, **kwargs):
        """
        load data from pandas dataframr or from a path_string

        PARAMS:
                data: path of data/url of data/pandas dataframe
        """

        # raw_data_file = data


        if type(data) != pd.core.frame.DataFrame:
            if data.endswith(".csv"):
                data = pd.read_csv(data,encoding="utf8", **kwargs)
            elif data.endswith(".xlsx"):
                data = pd.read_excel(data, encoding="utf8" **kwargs)


        output_data = [[data.loc[i, col] for col in data.columns ] for i in range(len(data)) ]

        if create_new_table == False:
           
            column_names = ','.join([column for column in data.columns])
            return output_data, column_names

        else:
            list_of_columns = [column for column in data.columns]
            return output_data,list_of_columns   #columns = list of dataframe columns

        


    def __upload(self,input_data, create_new_table,table_name):
        """
       data_to_upload = list data to upload
       data_columns = list of pandas dataframe columns
       """ 
        
        # else:
        #     table = table_name
        
        if create_new_table == True:
            if table_name != None:

                data_to_upload, data_columns = self.__load_data(input_data, create_new_table=True)
                self.__create_Table_for_uploading_data(table_name=table_name,columns=data_columns)

                data_columns_to_upload = ','.join([column for column in data_columns])
                #creating new table
                
                self.table = table_name  #assignining new table

            else:
                raise ValueError("Make sure you pass a table name and set create_new_table=True if you want your data to be uploaded in a new table")
        
        else: #if create_new_table == False:
            data_to_upload, data_columns_to_upload = self.__load_data(input_data, create_new_table=False)

        #uploading the data

        if table_name == None:
            table_name = self.table

            
        try:
            for row in data_to_upload:
                values_to_insert = ','.join([f"'{value}'" for value in row])

                query = f" insert into {table_name} ({data_columns_to_upload}) values({values_to_insert});"
                self.session.execute(query).one()
            print("data uploaded successfully")
        except InvalidRequest: #EXCEPTION happens as the column of the data is not foudn in the given table name. 
            error_message = """ Error happend:
            The table name which is assigned while calling the cassandra operations class 
            does not match the column names of the dataset. 
            You can set some parameters to handle the error.
            set:
                create_new_table = True
                table_name = yourPreferredName """ 
            raise Exception(error_message)
        


    def bulk_upload(self, data, table_name=None, create_new_table=False):
        """ insert data from dataframe object / csv /excel file to cassandra database 
        
        ------
        PARAMS: 
              data : path of the csv file or pandas dataframe object
              table_name: in case you need to change the table name that is going to be used here.
              create_new_table: default - False
                                if True, creates a new table with the csv name or from the table_name parameter.
                                if you have manually created a new table, you can keep it as False
              
              **kwargs :
                        any parameters of pandas read function.
        
        """
        

        # inserting data from csv
        
        try:
            self.__upload(input_data=data,
                            table_name=table_name,
                            create_new_table=create_new_table)
            
        
        
        except AlreadyExists:
            raise Exception("""The table which is passed to the class instance, already exists. 
                                You need to create a new table. Just pass the parameter table_name with your new table name.
                                    
                                    """)


    def update_table(self, where_condition, update_statement, table_name = None):  
        """
        where_condition: dict,
                               to find the data in mongo database -- example of query "{"name":"sourav"}"
                update_statement : dict,
                               query to update the data in mongo database -- example of query 

        EXAMPLE:
                
                where_condition = {"name":'Rahul Roy'}
                update_statement = {"name":'Sourav Roy'}

                ## it'll updata name from Rahul Roy to Sourav Roy.
        """
        if table_name == None:
            table = self.table
        else:
            table = table_name

        #update_statement_transformation   #to create string from the dictionary

        transform = lambda x: ''.join(x)
        update_column = transform(update_statement.keys())
        update_value = transform(update_statement.values())
        update_statement = f"{update_column} = '{update_value}'"

        #where_condition transformation
        query_on_column = transform(where_condition.keys())
        query_on_value = transform(where_condition.values())

        where_condition = f"{query_on_column} = '{query_on_value}'"

        query = f"UPDATE {self.keyspace}.{table} SET {update_statement} WHERE {where_condition};"
        self.session.execute(query).one()



    def delete_record(self, condition, table_name = None):
        """
            Delete record in cassandra database.

            ------
            PARAMS:
                  condition: str,
                  pass the where_condition withc column name and values

                Example:

                    condition = {'id': 'abc'} -- here id is column and the value is abc.



        """
        if table_name == None:
            table = self.table
        else:
            table = table_name

        transform = lambda x: ''.join(x)
        condition_on_column = transform(condition.keys())
        condition_on_value = transform(condition.values())
        condition = f"{condition_on_column} = '{condition_on_value}'"
    
        query = f"DELETE FROM {self.keyspace}.{table} WHERE {condition};"
        self.session.execute(query).one()
       


    