# -*- coding: utf-8 -*-
#!/usr/bin/env python   
from counterexample import Counterexample
from minion import is_isomorphic
from parser import stdin_parser
from minion import automorphisms, isomorphisms, is_isomorphic_to_any, MinionSol,bihomomorphisms_from_any,bihomomorphisms_to_any, homomorphisms_surj
from itertools import chain
from misc import indent
from main import SetSized, GenStack

def main():
    model = stdin_parser()
    targets_rel = tuple(sym for sym in model.relations.keys() if sym[0]=="T")
    if not targets_rel:
        print("ERROR: NO TARGET RELATIONS FOUND")
        return
    is_open_positive_rel(model,targets_rel)

        
def is_isomorphic_to_any_via_bihomos(model, models, rels):
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
        if not bh.homo_wrt:
            raise Counterexample(bh)
    for bh in bihomomorphisms_to_any(model, models_g, rels):
        # bh is a bihomo from models_l to model
        if not bh.homo_wrt:
            raise Counterexample(bh)
    return False

def is_open_positive_rel(model, target_rels):
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
                if not iso.iso_wrt(target_rels):
                    raise Counterexample(iso)
            else:
                for aut in automorphisms(current,base_rels):
                    auts_count += 1
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
                        if not h.homo_wrt(target_rels):
                            raise Counterexample(h)
                
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
    print("  %s calls to Minion" % MinionSol.count)


if __name__ == "__main__":
    main()
