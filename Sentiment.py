def parseDictionary(dictionary = 'sp.dic'):
    file = open(dictionary, 'r', encoding = 'utf-8')
    file.readline()

    categories = dict()

    for line in file:
        if '%' in line:
            break
        processed_line = line.replace('\n', '')
        values = processed_line.split('\t')
        categories[int(values[0])] = values[1]
    file.readline()

    words = dict()
    suffixes = dict()

    for line in file:
        if '%' in line:
            break
        processed_line = (line.replace('\n', '')).replace("\uFFFD", "\"")
        values = processed_line.split('\t')
        if '*' not in values[0]:
            words[values[0]] = []
            for i in range(1,len(values)):
                category = categories[int(values[i])]
                words[values[0]].append(category)
        else:
            suffixes[values[0].replace('*', '')] = []
            for i in range(1,len(values)):
                category = categories[int(values[i])]
                suffixes[values[0].replace('*', '')].append(category)
    return [words, suffixes]



def getTokens(s, words, suffixes):
    s = s.lower()
    analysis = s.split()

    tokens = []

    for word in analysis:
        if word in words.keys():
            tokens += words[word]

    for word in analysis:
        for suffix in suffixes.keys():
            if word.startswith(suffix):
                tokens += suffixes[suffix]

    return tokens

if __name__ == '__main__':
    d = parseDictionary()
    s = ""
    print(getTokens(s, d[0], d[1]))
    print(getPosNeg(getTokens(s, d[0], d[1])))
