import ProcesadorTexto, psycopg2, unittest
import Sentiment as senti
from pymongo import MongoClient

class AnalisisSentimiento(ProcesadorTexto.ProcesadorTexto):

    d = senti.parseDictionary()
    #Se actualizan al usar getDB
    candidato = ""
    id_tweet = 0

    mon_host = 'localhost'
    mon_port = 27017
    mon_db = 'scrapper'
    mon_coll = 'TweetModule'

    pos_host = 'localhost'
    pos_port = 5432
    pos_db = 'scrapper'
    pos_user = 'scrapper'
    pos_pass = ''

    def update_tops(self, cur, tags, tags_count):
        #Supuesto: en esta tabla siempre se mantienen, a lo más, 3 tweets por emocion, por candidato.
        #tops3s guarda una lista de listas de tuplas (idtweet, tagcount)
        top3s = []
        for i in range(0,5):
            cur.execute("SELECT idtweet, tagcount FROM tops WHERE emocion = %s AND idcandidato = %s;", [tags[i], self.candidato])
            top3s.insert(i, cur.fetchall())

        #Par key-value que tiene el valor mínimo (para ver si se tiene que reemplazar con el nuevo). Guarda (0,0) si hay menos de 3.
        mins = []
        for i in range(0,5):
            mins.insert(i, ((min(top3s[i], key=lambda t: t[1])) if len(top3s[i]) == 3 else (0,0)))

        #Aqui se guarda el tweet en los top3, si corresponde
        for i in range(0,5):
            if mins[i][1] < tags_count[i]:
                cur.execute("INSERT INTO tops VALUES (%s, %s, %s, %s);", [self.id_tweet, self.candidato, tags[i], tags_count[i]])
                #La llave de esta tabla deberia ser id_tweet y emocion
                cur.execute("DELETE FROM tops WHERE idtweet = %s AND emocion = %s;", [mins[i][0], tags[i]])

    def update_proms(self, cur, tags, tags_count):
        #idcandidato es llave.
        cur.execute("SELECT count FROM tweetcount WHERE idcandidato = %s;", [self.candidato])
        paux = cur.fetchone()
        analyzed_count = paux[0] if paux else 0   
        proms = []
        for i in range(0,5):
            #emocion y candidato debiesen ser key, por lo que entrega un valor.
            cur.execute("SELECT promedio FROM proms WHERE emocion = %s AND idcandidato = %s;", [tags[i], self.candidato])
            paux = cur.fetchone()
            proms.insert(i, paux[0] if paux else 0)

        #Actualizar promedio recalculado y conteo.
        #Se supone que si no se ha analizado tweets del personaje, no va a haber entradas que le correspondan en estas tablas (2 y 3).
        if analyzed_count > 0:
            cur.execute("UPDATE tweetcount SET count = %s WHERE idcandidato = %s;", [(analyzed_count+1),self.candidato])
        else:
            cur.execute("INSERT INTO tweetcount VALUES (%s,%s);", [self.candidato,(analyzed_count+1)])

        for i in range(0,5):
            if analyzed_count > 0:
                cur.execute("UPDATE proms SET promedio = %s WHERE idcandidato = %s AND emocion = %s;", [((analyzed_count*proms[i] + tags_count[i]) / (analyzed_count + 1)),self.candidato,tags[i]])            
            else:
                cur.execute("INSERT INTO proms VALUES (%s,%s,%s);", [self.candidato,tags[i],tags_count[i]])

    def count_tags(self, tokens, tags):
        tags_count = []
        for i in range(0,5):
            tags_count.insert(i, tokens.count(tags[i]))
        return tags_count
        

    def Analyze(self, str):
        """
        Descripcion: De los tweets recolectados, este metodo se encarga de identificar palabras clave
        para su analisis de sentimiento
        PreCondiciones: String obtenido corresponda a un tweet en su formato correcto. Que tweet tenga relacion a
        algun candidato del proceso constituyente
        PostCondiciones: Se entregue un sentimiento definido del tweet con su factor correspondiente.
        """
        #str es el contenido del tweet, retornado por getDB
        #Se ejecutaria getDB (con mongo) afuera, con esa informacion se llama a analyze, que dentro usa saveDB (con postgres).

        #TODO: ver negacion

        #Tablas que hay que tener en Postgres:
        #   (1) Top3 tweets por candidato, por emocion (1 tabla en total, con campo id_tweet (debe ser bigint!!), idCandidato, emocion y tagCount)
        #   (2) Count de tweets analizados por candidato(1 tabla en total, con campos idCandidato y count)
        #   (3) Promedio de tagCount por emocion, por candidato (1 tabla en total, con campos idCandidato, emocion y promedio (debiese ser double))

        #Abrir conexión con psql
        try:
            conn = psycopg2.connect(database=self.pos_db, user=self.pos_user, password=self.pos_pass, host=self.pos_host, port=self.pos_port)
            cur = conn.cursor()
        except:
            return False

        #posemo 13, negemo 16, anger 18, sad 19, swear 66

        #Contar las ocurrencias de los tags en el tweet.
        tags = ["Posemo", "Negemo", "Anger", "Sad", "Swear"]
        tokens = senti.getTokens(str, self.d[0], self.d[1])
        tags_count = count_tags(tokens, tags)

        #Modificar, si es necesario, la base de datos.
        update_tops(cur, tags, tags_count)
        update_proms(cur, tags, tags_count)

        #Commitear los cambios y cerrar conexión
        conn.commit()
        cur.close()
        conn.close()

        return True


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

        client = MongoClient(self.mon_host, self.mon_port)
        db = client[self.mon_db]
        doc = db[self.mon_coll].find_one({ "analyzed": { "$exists": False }})
        if doc is not None:
            self.id_tweet = doc['_id']
            self.candidato = doc['candidato']
            return doc['tweet']

        else:
            return None

    def saveDB(self, string_list):
        """
        Descripcion: Guardar el sentimiento analizado con su factor correspondiente en la base de datos
        PreCondiciones: Resultado de analisis en formato correcto y listo. Formato para guardar en base de datos
        conocido
        PostCondiciones: Datos guardados correctamente en Base de Datos.
        :
        """
        #Actualiza doc en mongo con campo analyzed, para no analizar de nuevo.

        #string list deberia tener solo un elemento: el id del tweet (pero DEBE ser una lista)
        client = MongoClient(self.mon_host, self.mon_port)
        db = client[self.mon_db]
        db[self.mon_coll].update_one({ "_id": string_list[0]}, {"$set": {"analyzed":""}})


# ------------------------------- TESTS UNITARIOS -----------------------------
class TestMetodoPrincipal(unittest.TestCase):
    #Como lo principal de este modulo es contar bien los tags en un tweet, se prueba este método.
    #Además, los otros incluyen accesos a DB, lo cual no se puede ver con test unitarios de este tipo.
    def test_count_tags(self):
        #Los valores esperados para el assertEqual son sacados de sp.dic
        an = AnalisisSentimiento()
        #13, 16, 18, 19, 66
        tags = ["Posemo", "Negemo", "Anger", "Sad", "Swear"]

        tokens = senti.getTokens("bueno bueno bueno", an.d[0], an.d[1])
        self.assertEqual(an.count_tags(tokens, tags),[3,0,0,0,0])

        tokens = senti.getTokens("malo malo mala mal", an.d[0], an.d[1])
        self.assertEqual(an.count_tags(tokens, tags),[0,4,3,0,0])

        tokens = senti.getTokens("Me siento abandonado por la sociedad", an.d[0], an.d[1])
        self.assertEqual(an.count_tags(tokens, tags),[0,1,0,1,0])

        tokens = senti.getTokens("Puros bastardos bobalicones en este país!", an.d[0], an.d[1])
        self.assertEqual(an.count_tags(tokens, tags),[0,2,1,0,2])

        #Profesora/Ayudante: disculpen el lenguaje de este test, pero lo creo necesario, ya que twitter no es una instancia formal y se van a analizar algunos así.
        #La palabra "hueón" y sus derivados son tan comunes y ambivalentes en sentido en el lenguaje coloquial, que solo lo dejé como Swear.
        tokens = senti.getTokens("Tendrá cara de hueón, pero igual es sensato", an.d[0], an.d[1])
        self.assertEqual(an.count_tags(tokens, tags),[1,0,0,0,1])
# --------------------------------------------------------------------------------

        
if __name__ == '__main__':
    #unittest.main()
    pass





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
an = AnalisisSentimiento()   
tw = an.getDB()
#En main hay que poner un ig getdb != None
an.Analyze(tw)
an.saveDB([an.id_tweet])
client = MongoClient()
db = client['tweets']
db.tweets.update_many({},{"$unset": {"analyzed": ""}})
cursor = db.tweets.find()
for d in cursor:
    print(d)
''' 