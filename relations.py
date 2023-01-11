# -*- coding: utf-8 -*-
#!/usr/bin/env python

    
class Relation(object):
    """
    Relation
    """
    def __init__(self,sym,arity):
        self.sym = sym
        self.arity = arity
        self.r = set()
    
    def add(self, t):
        self.r.add(t)
    
    def __repr__(self):
        return repr(self.r)
    
    def __call__(self, *args):
        return args in self.r

    def __len__(self):
        return len(self.r)
        
    def __iter__(self):
        return iter(self.r)
        
    def spectrum(self):
        result = set()
        for t in self:
            result.add(len(set(t)))
        return result
    
    def restrict(self,subuniverse):
        result = Relation(self.sym,self.arity)
        subuniverse= set(subuniverse)
        for t in self.r:
            if set(t) <= subuniverse:
                result.add(t)
        return result        
