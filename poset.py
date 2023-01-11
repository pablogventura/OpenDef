# -*- coding: utf-8 -*-
#!/usr/bin/env python   
from counterexample import Counterexample
from minion import is_isomorphic
from parser import stdin_parser
from minion import automorphisms, isomorphisms, is_isomorphic_to_any, MinionSol,bihomomorphisms_from_any,bihomomorphisms_to_any, homomorphisms_surj
from itertools import chain
from misc import indent
from main import SetSized, GenStack
from isomorphisms import Isomorphism
from collections import defaultdict
from formulas import atomics, variables, RelSym
H = []

def main():
    model = stdin_parser()
    targets_rel = tuple(sym for sym in model.relations.keys() if sym[0]=="T")
    if not targets_rel:
        print("ERROR: NO TARGET RELATIONS FOUND")
        return
    is_open_positive_rel(model,targets_rel)

        
def is_isomorphic_to_any_via_bihomos(model, models, rels):
    global H
    models_eq=[]
    models_l=[]
    models_g=[]
    for m in models.iterate(len(model)):
        if m.rels_sizes(rels) == model.rels_sizes(rels):
            models_eq.append(m)
        elif m.rels_sizes(rels) < model.rels_sizes(rels):
            models_l.append(m)
        elif m.rels_sizes(rels) > model.rels_sizes(rels):
            models_g.append(m)
    iso = is_isomorphic_to_any(model, SetSized(models_eq), rels)
    if iso:
        # iso is a isomorphism, because is a bihomo to model_eq
        return iso
    for bh in bihomomorphisms_from_any(models_l, model, rels):
        # bh is a bihomo from models_l to model
        H.append(bh)
        if not bh.homo_wrt:
            raise Counterexample(bh)
    for bh in bihomomorphisms_to_any(model, models_g, rels):
        # bh is a bihomo from models_l to model
        H.append(bh)
        if not bh.homo_wrt:
            raise Counterexample(bh)
    return False

def is_open_positive_rel(model, target_rels):
    global H
    base_rels = tuple((r for r in model.relations if r not in target_rels))
    spectrum = sorted(model.spectrum(target_rels),reverse=True)
    if spectrum:
        size = spectrum[0]
    else:
        size = 0
    print ("Spectrum = %s"%spectrum)
    isos_count = 0
    auts_count = 0
    S = SetSized()
    
    genstack = GenStack(model.substructures(size))
    try:
        while True:
            try:
                current = genstack.next()
            except StopIteration:
                break
            iso = is_isomorphic_to_any_via_bihomos(current, S, base_rels)
            if iso:
                isos_count += 1
                H.append(iso)
                if not iso.iso_wrt(target_rels):
                    raise Counterexample(iso)
            else:
                for aut in automorphisms(current,base_rels):
                    auts_count += 1
                    H.append(aut)
                    if not aut.aut_wrt(target_rels):
                        raise Counterexample(aut)
                S.add(current)

                try:
                    # EL SIGUIENTE EN EL ESPECTRO QUE SEA MAS CHICO QUE LEN DE SUBUNIVERSE
                    size = next(x for x in spectrum if x < len(current)) 
                    genstack.add(current.substructures(size))
                except StopIteration:
                    # no tiene mas hijos
                    pass
        for a in S:
            for b in S:
                if len(b) < len(a):
                    for h in homomorphisms_surj(a,b,base_rels):
                        H.append(h)
                
        print("DEFINABLE")
        print("\nFinal state: ")
        
    except Counterexample as ce:
        print("NOT DEFINABLE")
        print("Counterexample:")
        print(indent(repr(ce.ce)))
        print("\nState before abort: ")
    except KeyboardInterrupt:
        print("CANCELLED")
        print("\nState before abort: ")
    
    print ("  Diversity = %s"%len(S))
    if S:
        for k in range(1,max(map(len,S))+1):
            print("    %s-diversity = %s"%(k,len(list(filter(lambda s: len(s)==k,S)))))
    print("  #Auts = %s" % auts_count)
    print("  #Isos = %s" % isos_count)
    print("  #H    = %s" % len(H))
    from itertools import product
    preorden=[]
    for t in product(model.universe,repeat=model.relations["T0"].arity):
        for h in H:
            if isinstance(h,Isomorphism):
                ht=h.inverse().vcall(t)
                if None not in ht:
                    preorden.append((t,ht))
            ht=h.vcall(t)
            if None not in ht:
                preorden.append((t,ht))
    print("  %s calls to Minion" % MinionSol.count)
    print("")
    
    print("Preorden:")
    po = defaultdict(set)
    for a,b in preorden:
        po[a].add(b)
        
    for a in po:
        print((a,po[a]))
    
    print("")
    #imprimo los atomos
    print("Atomos:")
    j,r=preorden_a_orden(product(model.universe,repeat=model.relations["T0"].arity),po)
    for k in j:
        print ((k,j[k]))
    print("son %s atomos" % len(j))
    print("")

    #impmrimo los bihomos
    print("Bihomos:")
    for i in r:
        print(i)
    print("ahora vienen")
    r = dict(r)
    estan={}
    noestan={}
    
    
    for k in j:
        if model.relations["T0"](*k):
            estan[k]=j[k]
            print("esta")
            print((k,j[k]))
        else:
            print("no esta")
            print((k,j[k]))
            noestan[k]=j[k]
    print("estan %s atomos" % len(estan))
    
    vs = variables(*range(model.relations["T0"].arity))
    formula=[]
    for k in estan:
        formula.append([])
        for f in atomics([RelSym(r,model.relations[r].arity) for r in base_rels],vs):
            vector = {}
            if f.satisfy(model,{vs[i]:e for i,e in enumerate(k)}):
                formula[-1].append(f)
            print("erre")
            print(r)
            print("erref")
            if k in r and r[k] in noestan:
                print("noestan "*80)
    print("#"*80)
    print (formula)
    
    
    
    
    
def preorden_a_orden(universo,r):
    clases=dict()
    rc=set()
    for e in universo:
        clases[e] = set([e])
    for a in r:
        for b in r[a]:
            if a!=b and b in r and a in r[b]:
                clases[a]=clases[a].union(clases[b])
                clases[b]=set()
    print("estamos al medio")
    for k in clases:
        print ((k,clases[k]))
    print("ya paso")
    for k in list(clases.keys()):
        if not clases[k]:
            print("borro %s" % repr(k))
            del clases[k]
               
    for a in r:
        if b in r[a]:
            if representante(a,clases)!=representante(b,clases):
                print("r"*80)
                print((representante(a,clases),representante(b,clases)))
                print("r"*80)
                rc.add((representante(a,clases),representante(b,clases)))
    return clases,rc

def representante(elemento,clases):
    for clase in clases:
        if elemento in clases[clase]:
            return clase
    print("el elemento %s, no esta representado en %s"%(elemento,clases))
    raise IndexError

if __name__ == "__main__":
    main()
