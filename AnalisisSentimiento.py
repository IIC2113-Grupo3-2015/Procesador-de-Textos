import ProcesadorTexto
import Sentiment as sent

class AnalisisSentimiento(ProcesadorTexto.ProcesadorTexto):

    d = sent.parseDictionary()

    def Analyze(self, str):
        """
        Descripcion: De los tweets recolectados, este metodo se encarga de identificar palabras clave
        para su analisis de sentimiento
        PreCondiciones: String obtenido corresponda a un tweet en su formato correcto. Que tweet tenga relacion a
        algun candidato del proceso constituyente
        PostCondiciones: Se entregue un sentimiento definido del tweet con su factor correspondiente.
        """
        #TODO: ver negacion
        tokens = sent.getTokens(str, self.d[0], self.d[1])
        nPos = self.getPosNeg(tokens)[0]
        nNeg = self.getPosNeg(tokens)[1]
        print (nPos)
        print (nNeg)

        if nPos + nNeg > 0:
            prop = max([nPos/(nPos + nNeg), nNeg/(nPos + nNeg)])
        else:
            prop = 0
        if nPos < nNeg:
            prop *= -1

        return prop

    def getDB(self):
        """
        Descripcion: Obtener nuevos tweets agregados a la base de datos para su analisis
        Precondiciones: Que haya un nuevo tweet no analizado disponible en la base de datos. Que tweet este en formato
        correcto
        PostCondiciones: Obtener el tweet sin errores
        """
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

    def getPosNeg(self, tokens):
        #Retorna tupla con cantidad de (Posemo,Negemo)
        return [tokens.count("Posemo"), tokens.count("Negemo")]

print (AnalisisSentimiento().Analyze("Solo Bachelet se supera a ella misma. Llamó a Scioli para felicitarlo por el triunfo. Estaría ebria?"))