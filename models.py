# -*- coding: utf-8 -*-
#!/usr/bin/env python


from itertools import combinations
from functools import lru_cache
class PartialOrderedDict(dict):
    def __lt__(self, other): # <
        return self <= other and self != other
    def __gt__(self, other): # >
        return self >= other and self != other
    def __le__(self, other): # <=
        for k in self:
            if not self[k] <= other[k]:
                return False
        return True
    def __ge__(self, other): # >=
        for k in self:
            if not self[k] >= other[k]:
                return False
        return True
class RelationalModel(object):
    def __init__(self,universe,relations):
        """
        Relational Model
        Input: a universe list, relations dict
        """
        self.universe= list(universe)
        self.relations = relations

    def subuniverses(self,size):
        if size:
            for subu in combinations(self.universe,size):
                yield subu
    
    def substructures(self,size):
        for s in self.subuniverses(size):
            relations={}
            for r in self.relations:
                relations[r]=self.relations[r].restrict(s)
            yield RelationalModel(s,relations)

    def __repr__(self):
        return ("RelationalModel(universe=%s,relations=%s)"%(self.universe,self.relations))
    
    @lru_cache(maxsize=None)
    def rels_sizes(self,subtype):
        return PartialOrderedDict({r:len(self.relations[r]) for r in subtype})
    
    def rel_minion_name(self,r):
        return r.replace("|","b").replace("-","e")
    
    @lru_cache(maxsize=None)    
    def minion_tables(self,subtype):
        result = ""
        for r in subtype:
            result += "%s %s %s\n" % (self.rel_minion_name(r), len(self.relations[r]), self.relations[r].arity)
            for t in self.relations[r]:
                result += " ".join(str(self.universe.index(x)) for x in t) + "\n"
            result += "\n"
        return result[:-1]
        
    def minion_constraints(self,subtype):
        result = ""
        #table([f[0],f[0],f[0]],bv)
        result = ""
        for r in subtype:
            for t in self.relations[r]:
                result += "table([f["
                result += "],f[".join(str(self.universe.index(x)) for x in t)
                result += "]],%s)\n" % self.rel_minion_name(r)
        return result        
    def __len__(self):
        return len(self.universe)
    def spectrum(self,subtype):
        result=set()
        return result.union(*[self.relations[r].spectrum() for r in subtype])
        
