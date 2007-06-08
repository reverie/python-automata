# python-automata, the Python DFA library
# By Andrew Badr
# Version June 7, 2007
# Contact andrewbadr@gmail.com
# Your contributions are welcome.

#Copyright terms:
#You may redistribute it and/or modify python-automata under the terms of the GNU General Public License, version 2, as published by the Free Software Foundation.

class DFA:
    def __init__(self, states, alphabet, delta, start, accepts):
        self.states = states
        self.start = start
        self.delta = delta
        self.accepts = accepts
        self.alphabet = alphabet
        self.current_state = start
    def pretty_print(self):
        print "--------------------------"
        print "States:", self.states
        print "Alphabet:", self.alphabet
        print "Starting state:", self.start
        print "Accepting states:", self.accepts
        print "Transition function:"
        print "\t","\t".join(map(str,self.states))
        for c in self.alphabet:
            results = map(lambda x: self.delta(x, c), self.states)
            print c, "\t", "\t".join(map(str, results))
        print "Current state:", self.current_state
        print "Currently accepting:", self.status()
    def validate(self):
        """Checks that: 
        (1) The accepting-state set is a subset of the state set.
        (2) The start-state is a member of the state set.
        (3) The current-state is a member of the state set.
        (4) Every transition returns a member of the state set.

        Obviously, this function will not work on infinite DFAs
        """
        assert set(self.accepts).issubset(set(self.states))
        assert self.start in self.states
        assert self.current_state in self.states
        for state in self.states:
            for char in self.alphabet:
                assert self.delta(state, char) in self.states
    def input(self, char):
        """Updates the DFA's current-state based on a single input"""
        self.current_state = self.delta(self.current_state, char)
    def input_sequence(self, char_sequence):
        """Updates the DFA's current-state based on an iterable of inputs"""
        for char in char_sequence:
            self.current_state = self.delta(self.current_state, char)
    def status(self):
        """Indicates whether the DFA's current state is accepting"""
        return (self.current_state in self.accepts)
    def reset(self):
        self.current_state = self.start
    def state_merge(self, q1, q2):
        """Merges q1 into q2. All transitions to q1 are moved to q2
        If q1 was the start or current state, those are moved to q2
        """
        self.states.remove(q1)
        if q1 in self.accepts:
            self.accepts.remove(q1)
        if self.current_state == q1:
            self.current_state = q2
        if self.start == q1:
            self.start = q2
        transitions = {}
        for state in self.states: #without q1
            transitions[state] = {}
            for char in self.alphabet:
                next = self.delta(state, char)
                if next == q1:
                    next = q2
                transitions[state][char] = next
        self.delta = (lambda s, c: transitions[s][c])
    def reachable_from(self, q0):
        reached = [q0]
        to_process = [q0]
        while len(to_process):
            q = to_process.pop()
            for c in self.alphabet:
                next = self.delta(q, c)
                if next not in reached:
                    reached.append(next)
                    to_process.append(next)
        return reached
    def reachable(self):
        return self.reachable_from(self.start)
    def minimize(self):
        """Classical DFA minimization, using the simple O(n^2) algorithm"""
        """Side effect: can mix up the order of states"""
        #print "starts with %d states" % len(self.states)
        #print self.states

        #Step 1: Delete unreachable states
        reachable = self.reachable()
        #print "but only these are reachable:", reachable
        self.states = reachable
        #print "New self.states:", self.states
        #print "Old acceptance list:", self.accepts
        new_accepts = []
        for q in self.accepts:
            if q in self.states:
                new_accepts.append(q)
        self.accepts = new_accepts
        #print "New acceptance list:", self.accepts

        
        changed = True
        classes = [self.accepts, [x for x in set(self.states).difference(set(self.accepts))]]
        while changed:
            #print classes
            changed = False
            for cl in classes:
                local_change = False
                for alpha in self.alphabet:
                    next_class = None
                    new_class = []
                    for state in cl:
                        next = self.delta(state, alpha)
                        if next_class == None:
                            for c in classes:
                                if next in c:
                                    next_class = c
                        elif next not in next_class:
                            new_class.append(state)
                            changed = True
                            local_change = True
                    if local_change == True:
                        #print "split a class:"
                        #print " %s minus %s on character %s" % (cl, new_class, alpha)
                        old_class = []
                        for c in cl:
                            if c not in new_class:
                                old_class.append(c)
                        classes.remove(cl)
                        classes.append(old_class)
                        classes.append(new_class)
                        break
        #print "end up with %s classes" % len(classes)
        new_states = []
        new_start = None
        new_delta = None
        new_accepts = []
        #alphabet stays the same
        new_current_state = None
        state_map = {}
        #build new_states, new_start, new_current_state:
        for state_class in classes:
            #print "Processing state class:", state_class
            representative = state_class[0]
            new_states.append(representative)
            for state in state_class:
                state_map[state] = representative
                if state == self.start:
                    new_start = representative
                if state == self.current_state:
                    new_current_state = representative
        #build new_accepts:
        for acc in self.accepts:
            if acc in new_states:
                new_accepts.append(acc)
        transitions = {}
        #build new_delta:
        for state in new_states:
            transitions[state] = {}
            for alpha in self.alphabet:
                #print "transitions[%s][%s] = state_map[self.delta(%s, %s)]" % (state, alpha, state, alpha)
                #print "transitions[%s][%s] = state_map[%s]" % (state, alpha, self.delta(state, alpha))
                transitions[state][alpha] = state_map[self.delta(state, alpha)]
        #print transitions
        new_delta = (lambda s, a: transitions[s][a])
        self.states = new_states
        self.start = new_start
        self.delta = new_delta
        self.accepts = new_accepts
        self.current_state = new_current_state
    def find_fin_inf_parts(self):
        """Returns the partition of the state-set into the finite-part and infinite-part.
        A state is in the finite part iff there are finitely many strings that reach it from the start state.
        See "The DFAs of Finitely Different Regular Languages" for context.
        """
        reachable = {}
        for state in self.states:
            reachable[state] = set()
            for char in self.alphabet:
                reachable[state].add(self.delta(state, char))
        changed = True
        while changed:
            changed = False
            for state in self.states:
                for reached in list(reachable[state]):
                    for reached2 in list(reachable[reached]):
                        if reached2 not in reachable[state]:
                            reachable[state].add(reached2)
                            changed = True
        #print "REACHABILITY:", reachable
        finite_part = []
        infinite_part = []
        for state in self.states:
            if state in reachable[state]:
                infinite_part.append(state)
            else:
                finite_part.append(state)
        return (finite_part, infinite_part)
    def is_finite(self):
        """Indicates whether the DFA's language is a finite set. Could be improved to O(n).
        Minimizes the DFA as a side-effect."""
        self.minimize()
        (fin_part, inf_part) = self.find_fin_inf_parts()
        if len(inf_part) != 1:
            return False
        sink_candidate = inf_part[0]
        if sink_candidate in self.accepts:
            return False
        for char in self.alphabet:
            if self.delta(sink_candidate, char) != sink_candidate:
                return False
        return True
    def states_finitely_different(self, q1, q2):
        """Indicates whether q1 and q2 only have finitely many distinguishing strings."""
        d1 = DFA(states=self.states, start=q1, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        d2 = DFA(states=self.states, start=q2, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        sd_dfa = symmetric_difference(d1, d2)
        return sd_dfa.is_finite()
    def finite_difference_minimize(self):
        """Alters the DFA into a smallest possible DFA recognizing a finitely different language.

        See "The DFAs of Finitely Different Regular Languages" for context.
        This implementation does not achieve the running time advertised in that paper,  because:
          -This library's classical minimization algorithm is suboptimal, and
          -This library's algorithm to check if a DFA's language is finite is suboptimal
        """
        #print "Before f-minimization, there are %s states" % len(self.states)
        #Step 1
        self.minimize()
        #Step 2
        (fin_part, inf_part) = self.find_fin_inf_parts()
        #print "Finite part:", fin_part
        #print "Infinite part:", inf_part
        #Step 3
        state_classes = []
        for state in self.states:
            placed = False
            for sc in state_classes:
                rep = sc[0]
                if self.states_finitely_different(state, rep):
                    sc.append(state)
                    placed = True
                    break
            if not placed:
                state_classes.append([state])
        #print "State classes:", state_classes
        #Step 4
        for sc in state_classes:
           fins = filter(lambda s: s in fin_part, sc)
           infs = filter(lambda s: s in inf_part, sc)
           if len(infs) != 0:
               rep = infs[0]
               for fp_state in fins:
                   self.state_merge(fp_state, rep)
           else:
               rep = fins[0]
               for fp_state in fins[1:]:
                   self.state_merge(fp_state, rep)
        #print "After f-minimization, there are %s states" % len(self.states)
    def DFCA_minimize(self, l):
        """DFCA minimization.
        Input: (self) is a DFA accepting a finite language, and (l) is the length of the longest word in its language
        Result: (self) is DFCA-minimized

        See "Minimal cover-automata for finite languages" for context on DFCAs, and
        "An O(n^2) Algorithm for Constructing Minimal Cover Automata for Finite Languages"
        for the source of this algorithm. (Campeanu, Paun, Santean, and Yu)
        
        There exists a faster, O(n*logn)-time algorithm due to Korner, from CIAA 2002.
        """
        assert(self.is_finite())
        ###Step 0: Numbering the states
        ###Step 1: Computing the gap function


        ###Step 2: Merging states
        pass

def cross_product(D1, D2, accept_method):
    """A generalized cross-product constructor over two DFAs. 
    The third argument is a binary boolean function f, and a state in the final
    DFA accepts if f(a,b), where a and b indicate the acceptance-value of the 
    original states.
    """
    states = []
    for s1 in D1.states:
        for s2 in D2.states:
            states.append((s1,s2))
    start = (D1.start, D2.start)
    def delta(state_pair, char):
        next_D1 = D1.delta(state_pair[0], char)
        next_D2 = D2.delta(state_pair[1], char)
        return (next_D1, next_D2)
    alphabet = D1.alphabet #==D2.alphabet, necessarily
    accepts = []
    for (s1, s2) in states:
        a1 = (s1 in D1.accepts)
        a2 = (s2 in D2.accepts)
        if accept_method(a1, a2):
            accepts.append((s1, s2))
    return DFA(states=states, start=start, delta=delta, accepts=accepts, alphabet=alphabet)

def intersection(D1, D2):
    """Constructs an unminimized DFA recognizing the intersection of the languages of two given DFAs."""
    f = bool.__and__
    return cross_product(D1, D2, f)

def union(D1, D2):
    """Constructs an unminimized DFA recognizing the union of the languages of two given DFAs."""
    f = lambda x,y: x or y
    return cross_product(D1, D2, f)

def symmetric_difference(D1, D2):
    """Constructs an unminimized DFA recognizing the symmetric difference of the languages of two given DFAs."""
    f = lambda x,y: x^y
    return cross_product(D1, D2, f)

def inverse(D):
    """Constructs an unminimized DFA recognizing the inverse of the languages of a given DFA."""
    new_accepts = []
    for state in D.states:
        if state not in D.accepts:
            new_accepts.append(state)
    return DFA(states=D.states, start=D.start, delta=D.delta, accepts=new_accepts, alphabet=D.alphabet)
