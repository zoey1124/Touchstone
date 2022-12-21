Say we use redmine as an example app. 
In order to test how good is TouchStone, we need to 
1. Convert redmine schema to TouchStone scheme input, including data constraints
    a. collect schema information from database
    b. convert constraint information from data condtraints
    c. queries to query tree table, turn this into cardinality constraints (can only select a subset from queries)
2. Run TouchStone 
    a. run through example for start.conf
3. Convert generated data into database 
4. Run query to check to see generated data quality 