import psycopg2
from psycopg2.extras import Json
import datetime
conn = psycopg2.connect("host=localhost dbname=postgres port=5433 user=myuser password=mypassword")
print("connected to the database...")
with open("/home/user/glovevectors/glove.840B.300d.txt", "r") as vectorfile:
    processed = 0
    cur = conn.cursor()
    for line in vectorfile:
        elems = list(line.split(' '))
        if len(elems[0]) > 31 :
            continue
        processed+=1
        if processed%1000 == 0:
            print(datetime.datetime.utcnow().isoformat()+ " processed "+str(processed)+" lines")
            conn.commit()
            cur.close()
            cur = conn.cursor()
        cur.execute("INSERT INTO word_vectors (word, vector) VALUES (%s, %s)",(elems[0], Json(list(map(float,elems[1:])))))

conn.close()

#        for (ind,v) in enumerate(elems[1:]):
