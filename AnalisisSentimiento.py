import ProcesadorTexto

class AnalisisSentimiento(ProcesadorTexto):

    def Analyze(self, str):
        """
        Descripcion: De los tweets recolectados, este metodo se encarga de identificar palabras clave
        para su analisis de sentimiento
        PreCondiciones: String obtenido corresponda a un tweet en su formato correcto. Que tweet tenga relacion a
        algun candidato del proceso constituyente
        PostCondiciones: Se entregue un sentimiento definido del tweet con su factor correspondiente.
        """
        return str

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