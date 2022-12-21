import psycopg2
import json
from collections import defaultdict

# first connect with database
# then generate schema script

NUM = 2000 # rows to generate per table

to_data_type = {'integer': 'integer',
                'character varying': 'varchar',
                'timestamp without time zone': 'datetime',
                'text': 'varchar',
                'boolean': 'bool',
                'bytea': 'varchar',
                'date': 'date',
                'double precision':'decimal',
                'bigint': 'integer'}

class Table:
    def __init__(self, tableName: str, tableSize: int):
        self.tableName = tableName
        self.tableSize = tableSize
        self.primaryKey = []    # [col1, col2, ...]
        self.foreignKeys = []   # list of ForeignKey objs
        self.attributes = []    # [[colname1, datatype1], [colname2, datatype2], ...]
    
    def __str__(self):
        attributes_str = [' {}, {}'.format(attr[0], attr[1]) for attr in self.attributes]
        attributes_str = ';'.join(attributes_str)
        pk_str = ''
        if len(self.primaryKey) > 0:
            pk_str = ', '.join(self.primaryKey)
            pk_str = '; p({})'.format(pk_str)
        fk_str = ''
        if len(self.foreignKeys) > 0:
            fk_str = ['f({})'.format(str(fk)) for fk in self.foreignKeys]
            fk_str = '; '.join(fk_str)
            fk_str = '; ' + fk_str
        return "T[{}; {};{}{}{}]".format(self.tableName, NUM, attributes_str, pk_str, fk_str)

class ForeignKey:
    def __init__(self, column: str, referred_table: str, referred_column: str):
        self.column = column
        self.referred_table = referred_table
        self.referred_column = referred_column
    
    def __str__(self):
        return '{}, {}.{}'.format(self.column, self.referred_table, self.referred_column)

conn = psycopg2.connect(database="redmine", user='redmine', password='my_password', host='127.0.0.1')
print("Connected!")
cur = conn.cursor()
# get all table names from the database
cur.execute("select table_name from information_schema.tables where table_type = 'BASE TABLE' and table_schema = 'public';")
tables = [x[0] for x in cur.fetchall()]
table_to_obj = {}
# fetch column information of a table 
for t in tables:
    if t not in table_to_obj:
        table_to_obj[t] = Table(t, NUM)
    # get columns
    cur.execute("select column_name, data_type \
        from information_schema.columns where table_name = '{}';".format(t))
    columns = cur.fetchall()
    for c_name, data_type in columns:
        table_to_obj[t].attributes.append((c_name, to_data_type[data_type]))

    # get primary key
    cur.execute("SELECT a.attname, format_type(a.atttypid, a.atttypmod) AS data_type \
        FROM   pg_index i \
        JOIN   pg_attribute a ON a.attrelid = i.indrelid \
        AND a.attnum = ANY(i.indkey) \
        WHERE  i.indrelid = '{}'::regclass \
        AND    i.indisprimary;".format(t))
    pk = [elm[0] for elm in cur.fetchall()]
    table_to_obj[t].primaryKey = pk


# Deal with ConstrOpt constraints, add foreign constraints to Table obj
class_to_table = defaultdict(str)
f = open("./redmine/constraint")
cst = json.load(f)
for t in cst:
    _class = t['class']
    table = t['table']
    class_to_table[_class] = table

def process_fk_cst(cst: list) -> list:
    fk_cst = []
    for c in cst:
        if c['^o'] == 'ForeignKeyConstraint': 
            column = c['field_name']
            if c['class_name'] in class_to_table:
                referred_table = class_to_table[c['class_name']]
                referred_column = table_to_obj[referred_table].primaryKey[0]
                fk_cst.append(ForeignKey(column, referred_table, referred_column))
    return fk_cst

for elm in cst:
    table = elm['table']
    fk_cst = process_fk_cst(elm['constraints'])
    table_to_obj[table].foreignKeys = fk_cst
for t in table_to_obj:
    print(table_to_obj[t], '\n')

f.close()

# Example
# T[part; 200000; p_partkey, integer; p_name, varchar; p_mfgr, varchar; p_category, varchar; p_brand1, varchar; p_color, varchar; p_type, varchar; p_size, integer; p_container, varchar; p(p_partkey)]
# T[lineorder; 6001171000; lo_orderkey, integer; lo_linenumber, integer; lo_custkey, integer; lo_partkey, integer; lo_suppkey, integer; lo_orderdate, integer; lo_orderpriority, varchar; lo_shippriority, varchar; lo_quantity, integer; lo_extendedprice, integer; lo_ordertotalprice, integer; lo_discount, integer; lo_revenue, integer; lo_supplycost, integer; lo_tax, integer; lo_commitdate, integer; lo_shipmode, varchar; p(lo_orderkey, lo_linenumber); f(lo_custkey, customer.c_custkey); f(lo_partkey, part.p_partkey); f(lo_suppkey, supplier.s_suppkey); f(lo_orderdate, dwdate.d_datekey); f(lo_commitdate, dwdate.d_datekey)]
