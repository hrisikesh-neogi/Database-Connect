# database-connect
A single Package for all the database connectivities  ( E.g : MySQL, MongoDb, Cassandra)

# How to Use

* [install latest package](https://pypi.org/project/database-connect/)
 


> * in jupyter notebook - 

```python
    !pip install database-connect
```

> * in command prompt - 

```python
    pip install database-connect
```

## Database Operations
> * import database_connect module
```python
    import database_connect as connection
```
### Let's Do The Operations
* For MongoDb Operations

```python
   import database_connect as connection

   #create the parameters
   client_url = 'paste_your_mongodb_connection_url'  #should be a string
   database = 'your_database_name' #should be a string
   collection_name = 'your_collection_name' #should be a string

   #let's create the mongo object
   mongo = connection.mongo_operation(client_url=client_url, 
                            database=database,
                            collection_name=collection_name)

```

* For Cassandra Operations
```python
    import database_connect as connection
    zip_path = 'paste_the_zip_path' #should be a string
    client_id = 'paste_the_client_id' #should be a string
    client_secret = 'paste_the_client_secret' #should be a string
    keyspace = 'paste_the_keyspace name' #should be a string #note: keyspace should be created manually in datastax cassandra. Keyspaces are not allowed to create from backend.
    table_name = 'paste_the_table_name' 

    cassandra = connection.cassandra_operations(zip_path,
                                                client_id,
                                                client_secret,
                                                keyspace,
                                                table_name)
    ```
   