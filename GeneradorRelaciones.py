import ProcesadorTexto

class GeneradorRelaciones(ProcesadorTexto):

    def Analyze(self, str):
        """
        Descripcion:De las noticias, este metodo se encarga de hacer relaciones entre candidatos y eventos importantes
        (EJ: Juan Perez involucrado en SQM)
        PreCondiciones: Noticia a analizar en formato correcto. Que noticia tenga relacion con algun candidato del
        proceso constituyente
        PostCondiciones:Se entregue relacion entre candidatos y eventos de manera correcta
        """
        return str

    def getDB(self):
        """
        Descripcion: Obtener nuevas noticias agregadas a la base de datos para su analisis
        Precondiciones: Que haya una nueva noticia no analizada disponible en la base de datos. Que noticia este en
         formato correcto
        PostCondiciones: Obtener la noticia sin errores:
        """
        return 0

    def saveDB(self, string_list):
        """
        Descripcion: Guardar las relaciones analizadas en la base de datos.
        PreCondiciones: Resultado de analisis en formato correcto y listo. Formato para guardar en base de datos
        conocido
        PostCondiciones: Datos guardados correctamente en Base de Datos.
        :
        """
        return 0