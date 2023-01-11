#!/usr/bin/env python
# -*- coding: utf8 -*-

# TERMS

from unicode import subscript
from itertools import product, combinations
from collections import defaultdict

class Term(object):
    """
    Clase general de los terminos de primer orden
    """
    def __init__(self):
        pass

    def free_vars(self):
        raise NotImplemented

    def evaluate(self, model, vector):
        """
        Evalua el termino en el modelo para el vector de valores
        """
        raise NotImplemented

    def __hash__(self):
        return hash(repr(self))

    def __eq__(self,other):
        return hash(self) == hash(other)

class Variable(Term):
    """
    Variable de primer orden
    """
    def __init__(self, sym):
        if isinstance(sym,int):
            self.sym = "x" + subscript(sym)
        else:
            self.sym = sym

    def __repr__(self):
        return self.sym

    def free_vars(self):
        return {self}

    def evaluate(self, model, vector):
        try:
            return vector[self]
        except KeyError:
            raise ValueError("Free variable %s is not defined" % (self))

class OpSym(object):
    """
    Simbolo de operacion de primer orden
    """
    def __init__(self, op, arity):
        self.op = op
        self.arity = arity

    def __call__(self, *args):
        if len(args) != self.arity or any((not isinstance(a, Term)) for a in args):
            raise ValueError("Arity not correct or any isn't a term")

        return OpTerm(self,args)

    def __repr__(self):
        return self.op

class OpTerm(Term):
    """
    Termino de primer orden de la aplicacion de una funcion
    """
    def __init__(self, sym, args):
        self.sym = sym
        self.args = args

    def __repr__(self):
        result = repr(self.sym)
        result += "("
        result += ", ".join(map(repr,self.args))
        result += ")"
        return result

    def free_vars(self):
        return set.union(*[f.free_vars() for f in self.args])

    def evaluate(self, model, vector):
        args = [t.evaluate(model,vector) for t in self.args]
        return model.operations[self.sym.op](*args)

# FORMULAS

class Formula(object):
    """
    Clase general de las formulas de primer orden

    >>> x,y,z = variables("x","y","z") # declaracion de variables de primer orden

    >>> R = RelSym("R",2) # declaro una relacion R de aridad 2

    >>> f = OpSym("f",3) # declaro una operacion f de aridad 3

    >>> R(x,y) | R(y,x) & R(y,z)
    (R(x, y) ∨ (R(y, x) ∧ R(y, z)))

    >>> -R(f(x,y,z),y) | R(y,x) & R(y,z)
    (¬ R(f(x, y, z), y) ∨ (R(y, x) ∧ R(y, z)))

    >>> a = forall(x, -R(f(x,y,z),y))
    >>> a
    ∀ x ¬ R(f(x, y, z), y)
    >>> a.free_vars() == {y,z}
    True

    >>> a = R(x,x) & a
    >>> a
    (R(x, x) ∧ ∀ x ¬ R(f(x, y, z), y))
    >>> a.free_vars() == {x, y, z}
    True

    >>> exists(x, R(f(x,y,z),y))
    ∃ x R(f(x, y, z), y)

    >>> (-(true() & true() & false())) | false()
    ⊤

    """
    def __init__(self):
        pass

    def __and__(self, other):
        if isinstance(self,TrueFormula):
            return other
        elif isinstance(other,TrueFormula):
            return self

        return AndFormula([self,other])

    def __or__(self, other):
        if isinstance(self,FalseFormula):
            return other
        elif isinstance(other,FalseFormula):
            return self

        return OrFormula([self,other])

    def __neg__(self):
        if isinstance(self,TrueFormula):
            return false()
        elif isinstance(self,FalseFormula):
            return true()

        return NegFormula(self)

    def free_vars(self):
        raise NotImplemented

    def satisfy(self,model,vector):
        raise NotImplemented

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash(repr(self))

class NegFormula(Formula):
    """
    Negacion de una formula
    """
    def __init__(self, f):
        self.f = f

    def __repr__(self):
        return "¬ %s" % self.f

    def free_vars(self):
        return self.f.free_vars()

    def satisfy(self,model,vector):
        return not self.f.satisfy(model,vector)


class BinaryOpFormula(Formula):
    """
    Clase general de las formulas tipo f1 η ... η fn
    """
    def __init__(self, subformulas):
        self.subformulas = subformulas

    def free_vars(self):
        result = set()
        for f in self.subformulas:
            result = result.union(f.free_vars())
        return result

class OrFormula(BinaryOpFormula):
    """
    Disjuncion entre formulas
    """
    def __repr__(self):
        result = " ∨ ".join(str(f) for f in self.subformulas)
        result = "(" + result + ")"
        return result

    def __or__(self, other):
        if isinstance(self,FalseFormula):
            return other
        elif isinstance(other,FalseFormula):
            return self

        return OrFormula(self.subformulas + [other])

    def satisfy(self,model,vector):
        # el or y el and de python son lazy
        return any(f.satisfy(model,vector) for f in self.subformulas)

class AndFormula(BinaryOpFormula):
    """
    Conjuncion entre formulas
    """
    def __repr__(self):
        result = " ∧ ".join(str(f) for f in self.subformulas)
        result = "(" + result + ")"
        return result

    def __and__(self, other):
        if isinstance(self,TrueFormula):
            return other
        elif isinstance(other,TrueFormula):
            return self

        return AndFormula(self.subformulas + [other])

    def satisfy(self,model,vector):
        # el or y el and de python son lazy
        return all(f.satisfy(model,vector) for f in self.subformulas)

class RelSym(object):
    """
    Simbolo de relacion de primer orden
    """
    def __init__(self, rel, arity):
        self.rel = rel
        self.arity = arity

    def __call__(self, *args):
        if len(args) != self.arity or any((not isinstance(a, Term)) for a in args):
            raise ValueError("Arity not correct or any isn't a term")

        return RelFormula(self,args)

    def __repr__(self):
        return self.rel

class RelFormula(Formula):
    """
    Formula de primer orden de la aplicacion de una relacion
    """
    def __init__(self, sym, args):
        self.sym = sym
        self.args = args

    def __repr__(self):
        result = repr(self.sym)
        result += "("
        result += ", ".join(map(repr,self.args))
        result += ")"
        return result

    def free_vars(self):
        return set.union(*[f.free_vars() for f in self.args])

    def satisfy(self, model, vector):
        args = [t.evaluate(model,vector) for t in self.args]
        return model.relations[self.sym.rel](*args)

class EqFormula(Formula):
    """
    Formula de primer orden que es una igualdad entre terminos
    """
    def __init__(self, t1, t2):
        if not (isinstance(t1, Term) and isinstance(t2, Term)):
            raise ValueError("Must be terms")

        self.t1=t1
        self.t2=t2

    def __repr__(self):
        return "%s == %s" % (self.t1,self.t2)

    def free_vars(self):
        return set.union(self.t1.free_vars(), self.t2.free_vars())

    def satisfy(self, model, vector):
        return self.t1.evaluate(model,vector) == self.t2.evaluate(model,vector)

class QuantifierFormula(Formula):
    """
    Clase general de una formula con cuantificador
    """
    def __init__(self, var, f):
        self.var = var
        self.f = f

    def free_vars(self):
        return self.f.free_vars() - {self.var}

class ForAllFormula(QuantifierFormula):
    """
    Formula Universal
    """
    def __repr__(self):
        return "∀ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        for i in model.universe:
            vector[self.var] = i
            if not self.f.satisfy(model,vector):
                return False
        return True

class ExistsFormula(QuantifierFormula):
    """
    Formula Existencial
    """
    def __repr__(self):
        return "∃ %s %s" % (self.var, self.f)

    def satisfy(self, model, vector):
        vector = vector.copy()
        for i in model.universe:
            vector[self.var] = i
            if self.f.satisfy(model,vector):
                return True
        return False

class TrueFormula(Formula):
    """
    Formula de primer orden constantemente verdadera
    """

    def __repr__(self):
        return "⊤"

    def free_vars(self):
        return set()

    def satisfy(self, model, vector):
        return True

class FalseFormula(Formula):
    """
    Formula de primer orden constantemente falsa
    """

    def __repr__(self):
        return "⊥"

    def free_vars(self):
        return set()

    def satisfy(self, model, vector):
        return False
# Shortcuts

def variables(*lvars):
    """
    Declara variables de primer orden
    """
    return tuple(Variable(x) for x in lvars)

def forall(var, formula):
    """
    Devuelve la formula universal
    """
    return ForAllFormula(var, formula)

def eq(t1,t2):
    if t1==t2:
        return true()
    return EqFormula(t1,t2)

def exists(var, formula):
    """
    Devuelve la formula existencial
    """
    return ExistsFormula(var, formula)

def true():
    """
    Devuelve la formula True
    """
    return TrueFormula()

def false():
    """
    Devuelve la formula False
    """
    return FalseFormula()

# Formulas generators

def grafico(term, vs, model):
    result = {}
    for tupla in product(model.universe, repeat=len(vs)):
        result[tupla] = term.evaluate(model,{v:a for v,a in zip(vs,tupla)})
    return tuple(sorted(result.items()))

def generate_terms(funtions, vs, model):
    """
    Devuelve todos los terminos (en realidad solo para infimo y supremo)
    usando las funciones y las variables con un anidaminento de rec
    """
    result = []
    graficos = set()

    for v in vs:
        g = grafico(v,vs,model)
        if not g in graficos:
            result.append(v)
            graficos.add(g)
    nuevos=[1]
    while nuevos:
        nuevos =[]
        for f in funtions:
            for ts in product(result,repeat=f.arity):
                g = grafico(f(*ts),vs,model)
                if not g in graficos:
                    nuevos.append(f(*ts))
                    graficos.add(g)
            result += nuevos
    return result

def atomics(relations, terms, equality=True):
    """
    Genera todas las formulas atomicas con relations
    de arity variables libres

    >>> R = RelSym("R",2)
    >>> vs = variables(*range(2))
    >>> list(atomics([R],vs))
    [R(x₀, x₀), R(x₀, x₁), R(x₁, x₀), R(x₁, x₁), x₀ == x₁]
    >>> list(atomics([R],vs,equality=False))
    [R(x₀, x₀), R(x₀, x₁), R(x₁, x₀), R(x₁, x₁)]
    """
    terms
    for r in relations:
        for t in product(terms,repeat=r.arity):
            yield r(*t)

    if equality:
        for t in combinations(terms,2):
            yield eq(*t)

def fo_type_to_relsym(fo_type):
    """
    Devuelve una lista de RelSym para un tipo
    """
    result = []
    for r in fo_type.relations:
        result.append(RelSym(r,fo_type.relations[r]))

    return result

def fo_type_to_opsym(fo_type):
    """
    Devuelve una lista de OpSym para un tipo
    """
    result = []
    for f in fo_type.operations:
        result.append(OpSym(f,fo_type.operations[f]))

    return result

def bolsas(model, arity):
    """
    Algoritmo estilo Carlos para generar el algebra de lindenbaum
    de abiertas definibles en el modelo con la aridad dada

    >>> from . import fotheories
    >>> j=fotheories.SetsED.find_models(4)[2]
    >>> r = RelSym("r",1)
    >>> x0, = variables(0)
    >>> bolsas(j,1) == {- r(x0): [(0,)], r(x0): [(1,), (2,), (3,)]}
    True
    """
    result = {true(): list(product(model.universe,repeat=arity))}
    vs = variables(*range(arity))
    # lo comentado es para usar terminos con funciones y no solo variables
    terms = generate_terms(fo_type_to_opsym(model.fo_type),vs,model)
    formulas = atomics(fo_type_to_relsym(model.fo_type),terms)
    for formula in formulas:
        nuevas = defaultdict(list)
        for foriginal,bolsa in result.items():
            for tupla in bolsa:
                # TODO CUANDO UNA FORMULA NO TIENE NADIE QUE LA SATISFACE
                # O TODOS LA SATISFACEN, NO VALE LA PENA AGREGARLA
                if formula.satisfy(model,{v:i for v,i in zip(vs, tupla)}):
                    nuevas[foriginal & formula].append(tupla)
                else:
                    nuevas[foriginal & (-formula)].append(tupla)
        result = nuevas

    return dict(result)












