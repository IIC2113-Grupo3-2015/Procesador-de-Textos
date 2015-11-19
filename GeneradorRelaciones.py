# -*- coding: utf-8 -*- 
# Basado en códigos de:
    # http://www.didfinishlaunchingwithoptions.com/find-unique-named-entities-using-python-nltk/
    # http://www.nltk.org/book/ch07.html
    # https://www.youtube.com/watch?v=FLZvOKSCkxY&list=PLQVvvaa0QuDf2JswnfiGkliBInZnIC4HL

import ProcesadorTexto, psycopg2
import nltk, unicodedata
import unittest
from nltk.tree import ParentedTree as Tree
from pymongo import MongoClient

mon_host = 'localhost'
mon_port = 27017
mon_db = 'scrapper'

pos_host = 'localhost'
pos_port = 5432
pos_db = 'scrapper'
pos_user = 'scrapper'
pos_pass = 'scrapper'


try:
    conn = psycopg2.connect(database=pos_db, user=pos_user, password=pos_pass, host=pos_host, port=pos_port)
    cur = conn.cursor()
except:
    print ("Error de conexion")

candidatos = ["Michelle Bachelet", "Rodrigo Valdes", "Sebastian Pinera"]

class GeneradorRelaciones(ProcesadorTexto.ProcesadorTexto):

    #tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")  Revisar para mejorar analisis español

    def Analyse(self, entidades):
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
        #Quitar repetidos
        candidatosEncontrados = sorted(set(candidatosEncontrados))
        entidades = sorted(set(entidades))

        print(candidatosEncontrados)

        return [candidatosEncontrados, entidades]

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
            #print (chunk)
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
        client = MongoClient(mon_host, mon_port)
        db = client[mon_db]
        noticias = []
        doc1 = db.EmolModule.find({ "analyzed": { "$exists": False }})
        for document in doc1:
            db.EmolModule.update({"id":document['id']}, {"$set":{"analyzed":""}})       #OJO CON ID
            noticias.append(document['data'].encode("latin_1", errors="ignore").decode("latin_1", errors="ignore"))
        doc2 = db.LaTerceraModule.find({ "analyzed": { "$exists": False }})
        for document in doc2:
            db.LaTerceraModule.update({"id":document['id']}, {"$set":{"analyzed":""}})  #OJO CON ID
            noticias.append(document['data'].encode("latin_1", errors="ignore").decode("latin_1", errors="ignore"))
        #print(noticias)

        #LA LUPA
        doc3 = db.LaLupaModule.find({"analyzed": {"$exists": False}})
        for document in doc3:
            db.LaLupaModule.update({"id":document['id']}, {"$set":{"analyzed":""}})
            #Guardar PSQL
            cur.execute(""" INSERT INTO La_Lupa VALUES ('%s');""" %(document['data'].encode("latin_1", errors="ignore").decode("latin_1", errors="ignore")))
            conn.commit()
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
                    #pasar a minusculas
                    candidato1 = candidato1.lower()
                    candidato2 = candidato2.lower()

                    cur.execute(""" SELECT * FROM relaciones_candidatos WHERE nombre LIKE '%s' AND relacionado LIKE '%s';""" %(candidato1, candidato2))
                    tupla = cur.fetchall()
                    if tupla:
                        print("guardado: relaciones_candidatos")
                        cur.execute(""" UPDATE relaciones_candidatos SET cantidad = cantidad + 1 WHERE nombre LIKE '%s' AND relacionado LIKE '%s';""" %(candidato1, candidato2))
                    else:
                        print("primera tupla: relaciones_candidatos")
                        cur.execute(""" INSERT INTO relaciones_candidatos VALUES ('%s', '%s', 1);""" %(candidato1, candidato2))

        #Relacionar cada candidato con las entidades
        for candidato in candidatos:
            for entidad in entidades:
                #pasar a minusculas
                candidato = candidato.lower()
                entidad = entidad.lower()

                cur.execute(""" SELECT * FROM candidatos_entidades WHERE nombre LIKE '%s' AND entidad LIKE '%s';""" %(candidato, entidad))
                tupla = cur.fetchall()
                if tupla:
                    print("guardado: candidatos_entidades")
                    cur.execute(""" UPDATE candidatos_entidades SET cantidad = cantidad + 1 WHERE nombre LIKE '%s' AND entidad LIKE '%s';""" %(candidato, entidad))
                else:
                    print("primera tupla: candidatos_entidades")
                    cur.execute(""" INSERT INTO candidatos_entidades VALUES ('%s', '%s', 1);""" %(candidato, entidad))
        conn.commit()
        return 0

'''
g = GeneradorRelaciones()
noticias = g.getDB()
for noticia in noticias:
    noticia = g.quitarAcentos(noticia) #Para cuando reciba noticia de DB
    arbol = g.parts_of_speech(noticia)
    entidades = g.find_entities(arbol)
    a = g.Analyse(entidades)
    g.saveDB(a[0], a[1])
'''

# ------------------------------- TESTS UNITARIOS ----------------------------- 
class TestMetodosPrincipales(unittest.TestCase):
    def test_quitarAcentos(self):
        self.assertEqual(g.quitarAcentos('áéíóúñ'),'aeioun')

    def test_Analyse(self):
        texto_prueba = "me llamo Cristobal Alvarez. Mi amigo es Vicente Rodriguez"
        arbol_prueba = g.parts_of_speech(texto_prueba)
        entidades_prueba = g.find_entities(arbol_prueba)
        tuplas_prueba = g.Analyse(entidades_prueba)
        self.assertEqual(tuplas_prueba[0], [])
        self.assertEqual(tuplas_prueba[1],['Cristobal Alvarez', 'Vicente Rodriguez'])
        
#unittest.main()


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
