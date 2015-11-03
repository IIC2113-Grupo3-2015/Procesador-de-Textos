import AnalisisSentimiento, GeneradorRelaciones

g = GeneradorRelaciones()
an = AnalisisSentimiento()
noticias = g.getDB()

while True:
	#Va analizando un tweet y una notica, de forma alternada.

	#------------TWITTER------------
    tw = an.getDB()
    if tw is not None:
        an.Analyze(tw)
        aux = []
        aux.append(an.id_tweet)
        an.saveDB(aux)

    #------------NOTICIAS-----------
    #Si se vacio la lista, obtener una nueva.
    if noticias is None or len(noticias) == 0:
    	noticias = g.getDB()

    #Verificar si la lista nueva es no vacía.
    if noticias is not None and len(noticias) != 0:
	    noticia = noticias.pop()
	    noticia = g.quitarAcentos(noticia) #Para cuando reciba noticia de DB
	    arbol = g.parts_of_speech(noticia)
	    entidades = g.find_entities(arbol)
	    a = g.Analyse(entidades)
	    g.saveDB(a[0], a[1])


