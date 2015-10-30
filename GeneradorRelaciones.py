# -*- coding: utf-8 -*- 
# Basado en códigos de:
    # http://www.didfinishlaunchingwithoptions.com/find-unique-named-entities-using-python-nltk/
    # http://www.nltk.org/book/ch07.html
    # https://www.youtube.com/watch?v=FLZvOKSCkxY&list=PLQVvvaa0QuDf2JswnfiGkliBInZnIC4HL

import ProcesadorTexto, psycopg2
import nltk, unicodedata
from nltk.tree import ParentedTree as Tree
from pymongo import MongoClient

try:
    conn = psycopg2.connect("dbname='mydb' user='postgres' host='localhost' password='1234'")
    cur = conn.cursor()
except:
    print ("Error de conexion")

candidatos = ["Diego Steinsapir", "Alberto Hinrichsen", "Roberto Sanchez", "Cristiano Ronaldo"]

class GeneradorRelaciones(ProcesadorTexto.ProcesadorTexto):

    #tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")  Revisar para mejorar analisis español

    def Analyze(self, entidades):
        """
        Descripcion:De las noticias, este metodo se encarga de hacer relaciones entre candidatos y eventos importantes
        (EJ: Juan Perez involucrado en SQM)
        PreCondiciones: Noticia a analizar en formato correcto. Que noticia tenga relacion con algun candidato del
        proceso constituyente
        PostCondiciones:Se entregue relacion entre candidatos y eventos de manera correcta

        # Primero relacionar entre candidatos
        candidatosEncontrados = []
        for enti in entidades:  #Revisar repeticiones y apellidos solos
            if enti in candidatos:
                candidatosEncontrados.append(enti)
                entidades.remove(enti)
        # Relacionar candidatos con NE's
        """
        # Primero relacionar entre candidatos
        candidatosEncontrados = []
        for enti in entidades:  
            if enti in candidatos:
                candidatosEncontrados.append(enti)
                entidades.remove(enti)
        return [candidatos, entidades]

    def quitarAcentos(self, s):
        #Also removes tilde (~) from ñ
        return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

    def arreglarNoticia(self, news):
        # Quitar doble comillas, quitar acentos, arreglar parrafos
        return news

    def parts_of_speech(self, corpus):
        "returns named entity chunks in a given text"
        sentences = nltk.sent_tokenize(corpus)  #Uso toknenizer para español
        tokenized = [nltk.word_tokenize(sentence) for sentence in sentences]
        pos_tags  = [nltk.pos_tag(sentence) for sentence in tokenized]
        chunked_sents = nltk.ne_chunk_sents(pos_tags, binary=True)
        return chunked_sents

    def find_entities(self, chunks):

        def traverse(tree):
              
            entity_names = []
            if hasattr(tree, 'label') and tree.label:
                if tree.label() == 'NE':
                    entity_names.append(' '.join([child[0] for child in tree]))
                else:
                    for child in tree:
                        entity_names.extend(traverse(child))
        
            return entity_names
        
        named_entities = []
        
        for chunk in chunks:
            #chunk.draw()
            entities = sorted(list(set([word for tree in chunk
                                for word in traverse(tree)])))
            for e in entities:
                if e not in named_entities:
                    named_entities.append(e)
        return named_entities

    def quitarRepetidos(self, entidades):
        #Quitar de lista de entidades todos los repetidos (Nombres encontrados dos veces, apellidos solos)
        return entidades

    def getDB(self):
        """
        Descripcion: Obtener nuevas noticias agregadas a la base de datos para su analisis
        Precondiciones: Que haya una nueva noticia no analizada disponible en la base de datos. Que noticia este en
         formato correcto
        PostCondiciones: Obtener la noticia sin errores:
        """
        client = MongoClient()
        db = client['noticias']
        doc = db.noticias.find()
        noticias = []
        for document in doc:
           noticias.append(document['noticia'])
        return noticias

    def saveDB(self, candidatos, entidades):
        """
        Descripcion: Guardar las relaciones analizadas en la base de datos.
        PreCondiciones: Resultado de analisis en formato correcto y listo. Formato para guardar en base de datos
        conocido
        PostCondiciones: Datos guardados correctamente en Base de Datos.
        :
        """
        #cur.execute("INSERT INTO relaciones_candidatos VALUES (%s,%s);",['Prueba2', 'Hola2'])
        #Relacionar cada candidato con los demas
        for candidato1 in candidatos:
            for candidato2 in candidatos:
                if candidato1 != candidato2:
                    c = 1+1
                    #print (candidato1, candidato2)
                    cur.execute(""" INSERT INTO relaciones_candidatos VALUES ('%s', '%s');""" %(candidato1, candidato2))

        #Relacionar cada candidato con las entidades
        for candidato in candidatos:
            for entidad in entidades:
                b = 1+1
                #print(candidato, entidad)
                cur.execute(""" INSERT INTO candidatos_entidades VALUES ('%s', '%s');""" %(candidato, entidad))
        conn.commit()
        return 0


g = GeneradorRelaciones()

noticias = g.getDB()
for noticia in noticias:
    noticia = g.quitarAcentos(noticia) #Para cuando reciba noticia de DB

    arbol = g.parts_of_speech(noticia)
    entidades = g.find_entities(arbol)
    a = g.Analyze(entidades)
    g.saveDB(a[0], a[1])

''' ------------------------------ Metodo 2 ------------------------------
tokenized = tokenizer.tokenize(noticia) 

for token in tokenized:
    palabras = nltk.word_tokenize(token)
    tagged = nltk.pos_tag(palabras)

    ne = nltk.ne_chunk(tagged, binary = True)

    ne.draw()
    #print (tagged)
    #print(parentTree.read_node())
    #print(""+ne)
    -------------------------------------------------------------------
'''
#TODO: algunos nombres no se agarran en el analyzer (¿?)