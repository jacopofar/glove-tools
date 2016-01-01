import psycopg2
from psycopg2.extras import Json
import datetime
conn = psycopg2.connect("host=localhost dbname=postgres port=5433 user=myuser password=mypassword")
print("connected to the database...")

def get_vector(word):
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM word_vectors WHERE word = %s", (word,))
        foundres = cur.fetchone()
        if foundres == None:
            cur.close()
            return None
        foundvec = list(map(float,foundres[1]))
        cur.close()
        return foundvec

def get_difference(vec1, vec2):
    return list(map(lambda x:x[0]-x[1],zip(vec1,vec2)))

def get_sum(vec1, vec2):
    return list(map(lambda x:x[0]+x[1],zip(vec1,vec2)))

def vector_with_example(example_original,example_result,original):
    ex_orig = get_vector(example_original)
    ex_res = get_vector(example_result)
    orig = get_vector(original)
    if ex_orig == None or ex_res == None or orig == None:
        return None
    return get_sum(orig,get_difference(ex_res,ex_orig))

def vector_distance(vec1,vec2):
    return sum(map(lambda x:(x[0]-x[1])**2,zip(vec1,vec2)))

def get_ball(vector):
    #it's necessary to give a name to the cursor to have it server-side
    with conn.cursor('retrieve_all_balls') as cur:
        cur.execute("SELECT radius,central_vector,id FROM vector_balls")
        nearest = 9999
        radius = 0
        for row in cur:
            thisvec = list(map(float,row[1]))
            this_distance = vector_distance(thisvec,vector)
            if this_distance < nearest:
                nearest = this_distance
                radius = row[0]
            if this_distance <row[0]:
                print("found ball at distance "+str(this_distance)+" with radius "+str(row[0]))
                return row[2]
    print("no balls found, the nearest was at distance "+str(nearest)+" with radius "+str(radius))
    return None

def nearest_with_ball(vector,ignoreus=[]):
    ball_id = get_ball(vector)
    if ball_id == None:
        return None
    with conn.cursor() as cur:
        cur.execute("SELECT words,vectors FROM vector_balls WHERE id = %s",(ball_id,))
        ball_elems = cur.fetchone()
        mindistance = 99999
        best_word = None
        best_vector = None
        for (w,vec) in zip(ball_elems[0],ball_elems[1]):
            if w in ignoreus:
                continue
            thisvec = list(map(float,vec))
            this_distance = vector_distance(thisvec,vector)
            if this_distance <mindistance:
                mindistance = this_distance
                best_word = w
                best_vector = vec
    return (best_word,best_vector)

def nearests(vector,size = 100):
    #it's necessary to give a name to the cursor to have it server-side
    with conn.cursor('retrieve_all_vectors') as cur:
        cur.execute("SELECT * FROM word_vectors")
        processed = 0
        distances = [999999] * size
        mindistance = 999999
        bests_so_far = [None] * size
        vectors_so_far = [None] * size
        for row in cur:
            thisvec = list(map(float,row[1]))
            this_distance = vector_distance(thisvec,vector)
            processed +=1
            if processed %100000 == 0:
                pass #print("nearests "+str(size)+":processed "+str(processed))
            if this_distance < mindistance:
                to_be_replaced = distances.index(max(distances))
                distances[to_be_replaced] = this_distance
                bests_so_far[to_be_replaced] = row[0]
                vectors_so_far[to_be_replaced] = thisvec
                mindistance = max(distances)
                #print(row[0])
                #print(this_distance)
        return (bests_so_far,distances,vectors_so_far)

def save_ball(central_vector,words,vectors,radius):
    with conn.cursor() as cur:
        cur.execute("INSERT INTO vector_balls (words, vectors, central_vector, radius) VALUES (%s, %s, %s, %s)", (Json(words), Json(list(map(get_vector,words))),Json(central_vector),radius))
        conn.commit()

#as the name suggest, this method retrieves the nearest using the ball table, if not present uses the linear search and index the data for the next use
def get_nearest_maybe_index_it(vector,size=800,ignoreus =[]):
    candidate = nearest_with_ball(vector,ignoreus)
    if candidate != None:
        return candidate
    nearests_words = nearests(vector,size)
    save_ball(vector,nearests_words[0],nearests_words[2],max(nearests_words[1]))
    mindistance = 99999
    best_word = None
    best_vector = None
    for (w,vec) in zip(nearests_words[0],nearests_words[2]):
        if w in ignoreus:
            continue
        thisvec = list(map(float,vec))
        this_distance = vector_distance(thisvec,vector)
        if this_distance <mindistance:
            mindistance = this_distance
            best_word = w
            best_vector = vec
    return (best_word,best_vector)


#print(nearest(vector_with_example("worm","earth","bird"),["earth","bird","birds"]))
def print_similar(startword):
    print("\n\nsimilar to: "+startword)
    ignore_these = [startword]
    start_vector = get_vector(startword)
    if start_vector == None:
        print("  the word is unknown, skipping it")
        return
    for i in range(1,10):
        foundword = get_nearest_maybe_index_it(start_vector,ignoreus=ignore_these)[0]
        print("  "+foundword)
        ignore_these.append(foundword)


article_snippet="""Throughout its long history, France has been a leading global center of culture, making significant contributions to art, science, and philosophy. It hosts Europe's third-largest number of cultural UNESCO World Heritage Sites (after Italy and Spain) and receives around 83 million foreign tourists annually, the most of any country in the world.[18] France remains a great power with significant cultural, economic, military, and political influence.[19] It is a developed country with the world's sixth-largest economy by nominal GDP[20] and ninth-largest by purchasing power parity.[21] According to Credit Suisse, France is the fourth wealthiest nation in the world in terms of aggregate household wealth.[22] It also possesses the world's largest exclusive economic zone (EEZ), covering 11,691,000 square kilometres (4,514,000 sq mi).[23]

French citizens enjoy a high standard of living, and the country performs well in international rankings of education, health care, life expectancy, civil liberties, and human development.[24][25] France is a founding member of the United Nations, where it serves as one of the five permanent members of the UN Security Council. It is a member of the Group of 7, North Atlantic Treaty Organization (NATO), Organisation for Economic Co-operation and Development (OECD), the World Trade Organization (WTO), and La Francophonie. France is a founding and leading member state of the European Union (EU).[26]"""

#with size 200, took 423 minutes, then 2m and 4s
#with size 800, n/a time to store, 4m 54s to retrieve the second time

for w in article_snippet.split(' '):
    print_similar(w)

exit()

searchme = vector_with_example("deer","horn","cat")
print(get_nearest_maybe_index_it(searchme,ignoreus=["horn","cat","kitty","horns","saxophone"]))

central_one = get_vector("elephant")
print(get_nearest_maybe_index_it(central_one))

central_one = get_vector("ciao")
print(get_nearest_maybe_index_it(central_one))


central_one = get_vector("elephant")
print(get_nearest_maybe_index_it(central_one))

#nearests_words = nearests(central_one,100)
#print(nearests_words)
#save_ball(central_one,nearests_words[0],nearests_words[2],max(nearests_words[1]))
#nearest(get_vector("dog"))
#get_vector("dog")
#get_vector("elephant")
#get_vector("asfsdfesrydhyy5fc t")
