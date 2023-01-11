from collections import defaultdict

def preprocess_seeder(t):
    #cociente del conjunto s, por la funcion f
    result = defaultdict(list)
    for i,a in enumerate(t):
        result[a].append(i)
    tt=(tuple(k for k in sorted(result.keys(),key=lambda i:result[i][0])))
    return frozenset(frozenset(s) for s in result.values()),tt

def pattern_to_string(p):
    result=[]
    for c in p:
        result.append("-".join(str(i) for i in c))
    result="|".join(result)
    return "|"+result+"|"
