import ProcesadorTexto
import Sentiment as senti

class AnalisisSentimiento(ProcesadorTexto.ProcesadorTexto):

    d = senti.parseDictionary()
    #TODO: definir método para verificar cuales tweets son nuevos
    last_analyzed_tweet = None

    def Analyze(self, tweet, idCandidato, idTweet):
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
        #   (1) Top3 tweets por candidato, por emocion (1 tabla en total, con campo idTweet, idCandidato, emocion y tagCount)
        #   (2) Count de tweets analizados por candidato(1 tabla en total, con campos idCandidato y count)
        #   (3) Promedio de tagCount por emocion, por candidato (1 tabla en total, con campos idCandidato, emocion y promedio)

        #negemo 16, posemo 13, anger 18, sad 19, swear 66
        tags = ["Posemo", "Negemo", "Anger", "Sad", "Swear"]

        tokens = senti.getTokens(tweet, self.d[0], self.d[1])
        tags_count = []
        for i in range(1,6):
            tags_count.insert(i, tokens.count(tags[i]))

        #TODO: sacar de DB Postgres, Tabla (1). Debiesen ser 3 tuplas tweetID - count (del tag)
        top3_posemo = {}
        top3_negemo = {}
        top3_anger = {}
        top3_sad = {}
        top3_swear = {}
        top3s = [top3_posemo, top3_negemo, top3_anger, top3_sad, top3_swear]

        #Key que tiene el valor mínimo (para ver si se tiene que reemplazar con el nuevo). Guarda None si no hay nada.
        #Quedan con el mismo orden que top3s.
        mins = []
        for i in range(1,6):
            mins.insert(i, (min(top3s, key=top3s.get) if top3s else None))

        #Aqui se guarda el tweet en los top3, si corresponde
        for i in range(1,6):
            if mins[i] == None or mins[i] < tags_count[i]:
                #TODO: Guardar en base de datos el tweet que se esta analizando y borrar el mínimo, en Tabla (1).
                pass

        #TODO: sacar de DB Postgres. analyzed_count estaria en Tabla (2), promedios en la (3)
        analyzed_count = 0
        prom_posemo = 0
        prom_negemo = 0
        prom_anger = 0
        prom_sad = 0
        prom_swear = 0
        proms = [prom_posemo, prom_negemo, prom_anger, prom_sad, prom_swear]

        for i in range(1,6):
            #TODO: guardar en Tabla (2) (analyzed_count + 1)
            #TODO: guardar en Tabla (3) promedios recalculados ((analyzed_count*prom[i] + tags_count[i]) / (analyzed_count + 1))
            pass

        #return prop

    def getDB(self):
        """
        Descripcion: Obtener nuevos tweets agregados a la base de datos para su analisis
        Precondiciones: Que haya un nuevo tweet no analizado disponible en la base de datos. Que tweet este en formato
        correcto
        PostCondiciones: Obtener el tweet sin errores
        """
        #Se debe chequear con 
        return 0

    def saveDB(self, string_list):
        """
        Descripcion: Guardar el sentimiento analizado con su factor correspondiente en la base de datos
        PreCondiciones: Resultado de analisis en formato correcto y listo. Formato para guardar en base de datos
        conocido
        PostCondiciones: Datos guardados correctamente en Base de Datos.
        :
        """
        return 0

#print (AnalisisSentimiento().Analyze("Solo Bachelet se supera a ella misma. Llamó a Scioli para felicitarlo por el triunfo. Estaría ebria?"))