import ProcesadorTexto, psycopg2
import Sentiment as senti
from pymongo import MongoClient

class AnalisisSentimiento(ProcesadorTexto.ProcesadorTexto):

    d = senti.parseDictionary()

    def Analyze(self, tweet, candidato, idTweet):
        """
        Descripcion: De los tweets recolectados, este metodo se encarga de identificar palabras clave
        para su analisis de sentimiento
        PreCondiciones: String obtenido corresponda a un tweet en su formato correcto. Que tweet tenga relacion a
        algun candidato del proceso constituyente
        PostCondiciones: Se entregue un sentimiento definido del tweet con su factor correspondiente.
        """
        #Se ejecutaria getDB (con mongo) afuera, con esa informacion se llama a analyze, que dentro usa saveDB (con postgres).

        #TODO: ver negacion

        #Tablas que hay que tener en Postgres:
        #   (1) Top3 tweets por candidato, por emocion (1 tabla en total, con campo idTweet (debe ser bigint!!), idCandidato, emocion y tagCount)
        #   (2) Count de tweets analizados por candidato(1 tabla en total, con campos idCandidato y count)
        #   (3) Promedio de tagCount por emocion, por candidato (1 tabla en total, con campos idCandidato, emocion y promedio)

        #Abrir conexión con psql
        conn = psycopg2.connect("dbname=postgres user=postgres password=genoadmin")
        cur = conn.cursor()

        #negemo 16, posemo 13, anger 18, sad 19, swear 66
        tags = ["Posemo", "Negemo", "Anger", "Sad", "Swear"]

        tokens = senti.getTokens(tweet, self.d[0], self.d[1])
        print(tokens)
        tags_count = []
        for i in range(0,5):
            tags_count.insert(i, tokens.count(tags[i]))
        print (tags_count)

        #Supuesto: en esta tabla siempre se mantienen, a lo más, 3 tweets por emocion, por candidato.
        #tops3s guarda una lista de listas de tuplas (idtweet, tagcount)
        top3s = []
        for i in range(0,5):
            cur.execute("SELECT idtweet, tagcount FROM tops WHERE emocion = %s AND idcandidato = %s;", [tags[i], candidato])
            top3s.insert(i, cur.fetchall())
            print (top3s)

        #Key que tiene el valor mínimo (para ver si se tiene que reemplazar con el nuevo). Guarda None si no hay nada. Quedan con el mismo orden que top3s.
        mins = []
        for i in range(0,5):
            mins.insert(i, ((min(top3s[i], key=lambda t: t[1])) if len(top3s[i]) == 3 else (0,0)))
            print (mins)

        #Aqui se guarda el tweet en los top3, si corresponde
        for i in range(0,5):
            if mins[i][1] < tags_count[i]:
                cur.execute("INSERT INTO tops VALUES (%s, %s, %s, %s);", [idTweet, candidato, tags[i], tags_count[i]])
                #La llave de esta tabla deberia ser idTweet y emocion
                cur.execute("DELETE FROM tops WHERE idtweet = %s AND emocion = %s;", [mins[i][0], tags[i]])

        #idcandidato es llave.
        cur.execute("SELECT count FROM tweetcount WHERE idcandidato = %s;", [candidato])
        paux = cur.fetchone()
        analyzed_count = paux[0] if paux else 0   
        proms = []
        for i in range(0,5):
            #emocion y candidato debiesen ser key, por lo que entrega un valor.
            cur.execute("SELECT promedio FROM proms WHERE emocion = %s AND idcandidato = %s;", [tags[i], candidato])
            paux = cur.fetchone()
            proms.insert(i, paux[0] if paux else 0)
            print (proms)

        #Actualizar promedio recalculado y conteo.
        #TODO: ver casos en que hay que insertar y no hacer update
        #Se supone que si no se ha analizado tweets del personaje, no va a haber entradas que le correspondan en estas tablas (2 y 3).
        if analyzed_count > 0:
            cur.execute("UPDATE tweetcount SET count = %s WHERE idcandidato = %s;", [(analyzed_count+1),candidato])
        else:
            cur.execute("INSERT INTO tweetcount VALUES (%s,%s);", [candidato,(analyzed_count+1)])
            pass

        for i in range(0,5):
            if analyzed_count > 0:
                cur.execute("UPDATE proms SET promedio = %s WHERE idcandidato = %s AND emocion = %s;", [((analyzed_count*proms[i] + tags_count[i]) / (analyzed_count + 1)),candidato,tags[i]])            
            else:
                cur.execute("INSERT INTO proms VALUES (%s,%s,%s);", [candidato,tags[i],tags_count[i]])
                pass
        conn.commit()


    def getDB(self):
        '''
        Descripcion: Obtener nuevos tweets agregados a la base de datos para su analisis
        Precondiciones: Que haya un nuevo tweet no analizado disponible en la base de datos. Que tweet este en formato
        correcto
        PostCondiciones: Obtener el tweet sin errores

        Se asume este formato:
        {
        "candidato": "Felipe Kast3",
        "tweet": "2) Pocas cosas le hacen más daño a la causa de quienes creemos en la libre competencia y el emprendimiento que la colusión",
        "_id": 213,
        "analyzed": ""
        }
        Campo analyzed agregado en saveDB. 
        '''

        client = MongoClient()
        db = client['tweets']
        doc = db.tweets.find_one({ "analyzed": { "$exists": False }})
        #Retorna None si no hay tweets no analizados.
        return doc

    def saveDB(self, idTweet):
        """
        Descripcion: Guardar el sentimiento analizado con su factor correspondiente en la base de datos
        PreCondiciones: Resultado de analisis en formato correcto y listo. Formato para guardar en base de datos
        conocido
        PostCondiciones: Datos guardados correctamente en Base de Datos.
        :
        """
        client = MongoClient()
        db = client['tweets']
        db.tweets.update_one({ "_id": idTweet}, {"$set": {"analyzed":""}})

'''
client = MongoClient()
db = client['tweets']
result = db.tweets.insert_one(
    {
        "candidato": "Felipe Kast3",
        "tweet": "2) Pocas cosas le hacen más daño a la causa de quienes creemos en la libre competencia y el emprendimiento que la colusión",
        "_id": 213,
        "analyzed": ""
    })
print (result.inserted_id)
print(AnalisisSentimiento().getDB()['tweet'])
an = AnalisisSentimiento()   
tw = an.getDB()
#En main hay que poner un ig getdb != None
an.Analyze("2) Pocas cosas le hacen más daño a la causa de quienes creemos en la libre y buena competencia y el emprendimiento que la colusión", tw['candidato'], tw['_id'] + 13)
an.saveDB(tw['_id'])
client = MongoClient()
db = client['tweets']
cursor = db.tweets.find()
for d in cursor:
    print(d)
''' 