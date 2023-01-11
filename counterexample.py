# -*- coding: utf-8 -*-
#!/usr/bin/env python   

class Counterexample(Exception):
    def __init__(self,ce):
        self.ce = ce
