from collections import defaultdict

class SetSized(object):
    def __init__(self,values=[]):
        self.dict = defaultdict(set)
        for v in values:
            self.add(v)
    
    def add(self,e):
        self.dict[len(e)].add(e)
    
    def __iter__(self):
        print("WARNING: __iter__ SetSized")
        for i in self.sizes():
            for v in self.iterate(i):
                yield v

    def __len__(self):
        return sum(self.len(s) for s in self.sizes())
    def len(self,size):
        return len(self.dict[size])
    def sizes(self):
        return sorted(self.dict.keys())
    def iterate(self,size):
        return iter(self.dict[size])
