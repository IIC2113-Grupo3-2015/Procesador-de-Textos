# -*- coding: utf-8 -*- 
# Basado en códigos de:
    # http://www.didfinishlaunchingwithoptions.com/find-unique-named-entities-using-python-nltk/
    # http://www.nltk.org/book/ch07.html
    # https://www.youtube.com/watch?v=FLZvOKSCkxY&list=PLQVvvaa0QuDf2JswnfiGkliBInZnIC4HL

import ProcesadorTexto
import nltk, unicodedata
from nltk.tree import ParentedTree as Tree

class GeneradorRelaciones(ProcesadorTexto.ProcesadorTexto):

    #tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")  Revisar para mejorar analisis español

    def Analyze(self, str):
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
        return str

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


texto = u"""hola ñññ áéíóú yo soy Diego Steinsapir. Su buen amigo.
                A Steinsapir le gusta andár en bicicleta. Soquimich dejó la cagada.
                Alberto es un pajarón. El ladrón Roberto. Coca-Cola es una buena empresa.
                Él es un buen hombre. Cristiano Ronaldo juega Futbol. El Tubo es un piante.
                Juan de Dios es mi amigo. El reloj se llama Casio Watch. Mi computador es Windows.
                Yo soy Daniel y mi hermano es Cristian. La presidente Bachelet. Un amigo de Cristobal"""

g = GeneradorRelaciones()

noticia = g.quitarAcentos(texto) #Para cuando reciba noticia de DB


print(noticia)
arbol = g.parts_of_speech(noticia)
print (g.find_entities(arbol)) #Primero de lista de NE's    


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