#!/usr/bin/env python
# -*- coding: utf8 -*-

# Minion interface based on Peter Jipsen 2011-03-26 alpha version
import os
import codecs
import subprocess as sp
from select import poll, POLLIN

from isomorphisms import Automorphism, Isomorphism, Homomorphism
import config
import files
from itertools import product
from collections import defaultdict
from misc import *

def identity_table(size):
    result = "I 1 %s\n" % size
    result += " ".join(str(i) for i in range(size))
    return result + "\n"

class MinionSol(object):
    count = 0

    def __init__(self, input_data, allsols=True, fun=lambda x: x):
        """
        Toma el input para minion, si espera todas las soluciones y una funcion para aplicar
        a las listas que van a ir siendo soluciones.
        """
        self.EOF = False
        self.id = MinionSol.count
        MinionSol.count += 1

        self.fun = fun
        self.allsols = allsols

        self.input_filename = config.minion_path + "input_minion%s_%s" % (self.id,os.getpid())
        files.create_pipe(self.input_filename) # TODO SACAR PIPE

        minionargs = ["-printsolsonly", "-randomseed", "0"]
        if allsols:
            minionargs += ["-findallsols"]
        minionargs += [self.input_filename]

        self.minionapp = sp.Popen([config.minion_path + "minion"] + minionargs,
                                  stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
        files.write(self.input_filename, input_data)
        self.solutions = []

    def __parse_solution(self):
        """
        Bloquea hasta conseguir una solucion, o el EOF
        La parsea y devuelve una lista
        """
        str_sol = self.minionapp.stdout.readline().decode('utf-8').strip()
        
        if str_sol:
            try:
                result = list(map(int, str_sol.strip().split(" ")))
                for i, v in enumerate(result):
                    if v == -1:
                        result[i] = None
                result = {i:v for i,v in enumerate(result)}
                # ACA IRIAN LAS TRADUCCIONES DE NOMBRES EN EL FUTURO
            except ValueError:
                str_sol += "\n"
                # leo toda la respuesta de minion para saber que paso
                str_sol += self.minionapp.stdout.read().decode('utf-8')
                raise ValueError("Minion Error:\n%s" % str_sol)
            if not self.allsols:
                self.EOF = True
                self.__terminate()
            return result
        else:
            str_err = self.minionapp.stderr.read().decode('utf-8')
            if str_err:
                raise ValueError("Minion Error:\n%s" % str_err)
            self.EOF = True
            self.__terminate()

    def __iter__(self):
        for solution in self.solutions:
            yield self.fun(solution)

        while not self.EOF:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                yield self.fun(solution)

    def __getitem__(self, index):
        try:
            return self.fun(self.solutions[index])
        except IndexError:
            for i, solution in enumerate(self):
                if i == index:
                    # no hace falta aplicar self.fun porque esta llamando a
                    # __iter__
                    return solution
            raise IndexError("There aren't so many solutions.")

    def __bool__(self):
        if self.solutions or self.EOF:
            return bool(self.solutions)
        else:
            solution = self.__parse_solution()
            if solution:
                self.solutions.append(solution)
                return True
            else:
                return False

    def __len__(self):
        if not self.EOF:
            for i in self:
                pass
        return len(self.solutions)

    def __terminate(self):
        """
        Mata a Minion
        """
        if hasattr(self, 'minionapp'):
            self.minionapp.stdout.close()
            self.minionapp.stdin.close()
            self.minionapp.stderr.close()
            self.minionapp.kill()

            del self.minionapp
        files.remove(self.input_filename)

    def __del__(self):
        """
        Si no lo habia matado, mata a Minion.
        """
        if not self.EOF:
            self.__terminate()



def automorphisms(model,subtype):
    result = "MINION 3\n**VARIABLES**\nDISCRETE f[%s]{0..%s}\n" % (len(model),len(model)-1)
    result += "**TUPLELIST**\n"
    result += model.minion_tables(subtype)
    result += identity_table(len(model))
    result += "**CONSTRAINTS**\n"
    result += model.minion_constraints(subtype)
    result += "alldiff([f["
    result += "],f[".join(str(i) for i in range(len(model)))
    result += "]])\n"
    result += "negativetable([f[" # evito identidades
    result += "],f[".join(str(i) for i in range(len(model)))
    result += "]],I)\n"
    result += "**EOF**" 

    
    
    return MinionSol(result,allsols=True,fun=lambda aut:(Automorphism({model.universe[k]:model.universe[aut[k]] for k in aut},model,subtype)))


def isomorphisms(source,target,subtype,allsols=True):
    if len(source)!=len(target):
        return [] # generador vacio
    
    if source.rels_sizes(subtype) != target.rels_sizes(subtype):
        return [] # generador vacio
    
    result = "MINION 3\n**VARIABLES**\nDISCRETE f[%s]{0..%s}\n" % (len(source),len(target)-1)
    result += "**TUPLELIST**\n"
    result += target.minion_tables(subtype)
    result += "**CONSTRAINTS**\n"
    result += source.minion_constraints(subtype)
    result += "alldiff([f["
    result += "],f[".join(str(i) for i in range(len(source)))
    result += "]])\n"
    result += "**EOF**" 
    
    
    
    return MinionSol(result,allsols,fun=lambda iso:(Isomorphism({source.universe[k]:target.universe[iso[k]] for k in iso},source,target,subtype)))

def bihomomorphisms(source,target,subtype,allsols=True):
    if len(source)!=len(target):
        return [] # generador vacio
    
    if source.rels_sizes(subtype) > target.rels_sizes(subtype):
        return [] # generador vacio
    
    result = "MINION 3\n**VARIABLES**\nDISCRETE f[%s]{0..%s}\n" % (len(source),len(target)-1)
    result += "**TUPLELIST**\n"
    result += target.minion_tables(subtype)
    result += "**CONSTRAINTS**\n"
    result += source.minion_constraints(subtype)
    result += "alldiff([f["
    result += "],f[".join(str(i) for i in range(len(source)))
    result += "]])\n"
    result += "**EOF**" 
    
    
    
    return MinionSol(result,allsols,fun=lambda iso:(Homomorphism({source.universe[k]:target.universe[iso[k]] for k in iso},source,target,subtype)))

def homomorphisms_surj(source,target,subtype,allsols=True):
    if len(source)<len(target):
        return [] # generador vacio
    
    if source.rels_sizes(subtype) > target.rels_sizes(subtype):
        return [] # generador vacio
    
    result = "MINION 3\n**VARIABLES**\nDISCRETE f[%s]{0..%s}\n" % (len(source),len(target)-1)
    result += "**TUPLELIST**\n"
    result += target.minion_tables(subtype)
    result += "**CONSTRAINTS**\n"
    result += source.minion_constraints(subtype)
    result += "**EOF**" 
    
    
    
    return MinionSol(result,allsols,fun=lambda iso:(Homomorphism({source.universe[k]:target.universe[iso[k]] for k in iso},source,target,subtype)))

def is_bihomomorphic(source,target,subtype):
    bh = bihomomorphisms(source,target,subtype,allsols=False)
    
    if bh:
        return bh[0]
    else:
        return False

def bihomomorphisms_to_any(source, targets, subtype):
    """
    Devuelve un iso si source es bihomomorfica a algun target
    sino, false. Usa multiples preguntas a minion en paralelo.
    """
    if not targets:
        return
    
    for target in targets:
        for bh in bihomomorphisms(source,target,subtype):
            yield bh
    return

def bihomomorphisms_from_any(sources, target, subtype):
    """
    Devuelve un iso si algun source es bihomomorfica al target
    sino, false. Usa multiples preguntas a minion en paralelo.
    """
    if not sources:
        return
    
    for source in sources:
        for bh in bihomomorphisms(source,target,subtype):
            yield bh
    return

def is_isomorphic(source, target, subtype):

    i = isomorphisms(source,target,subtype,allsols=False)
    
    if i:
        return i[0]
    else:
        return False


def is_isomorphic_to_any(source, targets, subtype):
    """
    Devuelve un iso si source es isomorfa a algun target
    sino, false. Usa multiples preguntas a minion en paralelo.
    """
    if not targets:
        return False
    
    for target in targets.iterate(len(source)):
        iso = is_isomorphic(source,target,subtype)
        if iso:
            return iso
    return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
