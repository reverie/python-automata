# python-automata, the Python DFA library
# Author: Andrew Badr
# Version: June 9, 2007
# Contact: andrewbadr@gmail.com
# Your code contributions are welcome.

#Copyright terms:
#You may redistribute and/or modify python-automata under the terms of the GNU General Public License, version 2, as published by the Free Software Foundation.

class DFA:
    """This class represents a deterministic finite automon."""
    def __init__(self, states, alphabet, delta, start, accepts):
        """The inputs to the class are as follows:
         -states: an iterable (lists or sets would work) containing the states of the DFA (usually Q)
         -alphabet: an iterable containing the symbols in the DFA's alphabet (usually Sigma)
         -delta: a complete function from [states]x[alphabets]->[states]. See note below. (usually delta)
         -start: the state at which the DFA begins operation. (usually s or q_0)
         -accepts: an iterable containing the "accepting" or "final" states of the DFA

        Making delta a function rather than a transition table makes it much easier to define certain DFAs. 
        And if you want to use transition tables, you can just do this:
         delta = lambda x,y: table[x][y]
        """
        self.states = states
        self.start = start
        self.delta = delta
        self.accepts = accepts
        self.alphabet = alphabet
        self.current_state = start
#
# Administrative functions:
#
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
#
# Simulating execution:
#
    def input(self, char):
        """Updates the DFA's current state based on a single character of input."""
        self.current_state = self.delta(self.current_state, char)
    def input_sequence(self, char_sequence):
        """Updates the DFA's current state based on an iterable of inputs."""
        for char in char_sequence:
            self.input(char)
    def status(self):
        """Indicates whether the DFA's current state is accepting."""
        return (self.current_state in self.accepts)
    def reset(self):
        """Returns the DFA to the starting state."""
        self.current_state = self.start
    def accepts(self, char_sequence):
        """Indicates whether the DFA accepts a given string."""
        state_save = self.current_state
        self.reset()
        self.input_sequence(char_sequence)
        valid = self.status()
        self.current_state = state_save
        return valid
#
# Minimization methods and their helper functions
#
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
    def reachable_from(self, q0, inclusive=True):
        """Returns the set of states reachable from given state q0. The optional
        parameter "inclusive" indicates that q0 should always be included.
        """
        reached = []
        if inclusive:
            reached.append(q0)
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
        """Returns the reachable subset of the DFA's states."""
        return self.reachable_from(self.start)
    def minimize(self):
        """Classical DFA minimization, using the simple O(n^2) algorithm.
        Side effect: can mix up the internal ordering of states.
        """
        #Step 1: Delete unreachable states
        reachable = self.reachable()
        self.states = reachable
        new_accepts = []
        for q in self.accepts:
            if q in self.states:
                new_accepts.append(q)
        self.accepts = new_accepts

        #Step 2: Partition the states into equivalence classes        
        changed = True
        classes = [self.accepts, [x for x in set(self.states).difference(set(self.accepts))]]
        while changed:
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
                        old_class = []
                        for c in cl:
                            if c not in new_class:
                                old_class.append(c)
                        classes.remove(cl)
                        classes.append(old_class)
                        classes.append(new_class)
                        break
        #Step 3: Construct the new DFA
        new_states = []
        new_start = None
        new_delta = None
        new_accepts = []
        #alphabet stays the same
        new_current_state = None
        state_map = {}
        #build new_states, new_start, new_current_state:
        for state_class in classes:
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
                transitions[state][alpha] = state_map[self.delta(state, alpha)]
        new_delta = (lambda s, a: transitions[s][a])
        self.states = new_states
        self.start = new_start
        self.delta = new_delta
        self.accepts = new_accepts
        self.current_state = new_current_state
    def find_fin_inf_parts(self):
        """Returns the partition of the state-set into the finite-part and 
        infinite-part as a 2-tuple. A state is in the finite part iff there 
        are finitely many strings that reach it from the start state.

        See "The DFAs of Finitely Different Regular Languages" for context.
        """
        #O(n^2): can this be improved?
        reachable = {}
        for state in self.states:
            reachable[state] = self.reachable_from(state, inclusive=False)
        finite_part = filter(lambda x: x not in reachable[x], self.states)
        infinite_part = filter(lambda x: x in reachable[x], self.states)
        return (finite_part, infinite_part)
    def pluck_leaves(self):
        """Returns a maximal list S of states s_0...s_n such that for every 
        0<=i<=n: 
            -s_i induces a finite language
            -s_i's outgoing transitions are all to s_0...s_i
        This is also a maximal list of vertices satisfying the first property alone.
        """
        #Step 1: Build the states' profiles
        loops    = {}
        inbound  = {}
        outbound = {}
        can_loop = {} #can_loop indicates that this state does not reach an accepting state,
                      #so that we can know if self-loops are allowed for this state.
                      #This is necessary for unminimized input.
        for state in self.states:
            inbound[state] = []
            outbound[state] = []
            loops[state] = 0
            can_loop[state] = (state not in self.accepts)
        for state in self.states:
            for c in self.alphabet:
                next = self.delta(state, c)
                inbound[next].append(state)
                outbound[state].append(next)
                if state == next:
                    loops[state] += 1
        #Step 2: Pluck:
        to_pluck = []
        for state in self.states:
            if len(outbound[state]) == loops[state]:
                if state not in self.accepts:
                    to_pluck.append(state)
        plucked = []
        while len(to_pluck):
            state = to_pluck.pop()
            plucked.append(state)
            for incoming in inbound[state]:
                if not can_loop[state]:
                    can_loop[incoming] = False
                outbound[incoming].remove(state)
                if (len(outbound[incoming]) == loops[incoming]):
                    if (loops[incoming]==0) or (can_loop[incoming]):
                        to_pluck.append(incoming)
        return plucked
    def is_finite(self):
        """Indicates whether the DFA's language is a finite set."""
        plucked = self.pluck_leaves()
        return (self.start in plucked)
        #(f, i) = self.find_fin_inf_parts()
        #return (self.start in f)

    def states_finitely_different(self, q1, q2):
        """Indicates whether q1 and q2 only have finitely many distinguishing strings."""
        d1 = DFA(states=self.states, start=q1, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        d2 = DFA(states=self.states, start=q2, accepts=self.accepts, delta=self.delta, alphabet=self.alphabet)
        sd_dfa = symmetric_difference(d1, d2)
        return sd_dfa.is_finite()
    def finite_difference_minimize(self):
        """Alters the DFA into a smallest possible DFA recognizing a finitely different language.
        In other words, if D is the original DFA and D' the result of this function, then the 
        symmetric difference of L(D) and L(D') will be a finite set, and there will be no possible
        D' with fewer states than this one.

        See "The DFAs of Finitely Different Regular Languages" for context.
        """
        #Step 1
        self.minimize()
        #Step 2
        (fin_part, inf_part) = self.find_fin_inf_parts()
        #Step 3
        sd = symmetric_difference(self, self)
        similar_states = sd.pluck_leaves()
        state_classes = []
        for state in self.states:
            placed = False
            for sc in state_classes:
                rep = sc[0]
                if (state, rep) in similar_states:
                    sc.append(state)
                    placed = True
                    break #only for speed, not logic
            if not placed:
                state_classes.append([state])
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
    def levels(self):
        """Returns a dictionary mapping each state to its distance from the starting state."""
        levels = {}
        seen = [self.start]
        levels[self.start] = 0
        level_number = 0
        level_states = [self.start]
        while len(level_states):
            next_level_states = []
            next_level_number = level_number + 1
            for q in level_states:
                for c in self.alphabet:
                    next = self.delta(q, c)
                    if next not in seen:
                        seen.append(next)
                        levels[next] = next_level_number
                        next_level_states.append(next)
            level_states = next_level_states
            level_number = next_level_number
        return levels
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
        self.minimize()
        ###Step 0: Numbering the states
        state_count = len(self.states)
        n = state_count - 1
        ###Step 1: Computing the gap function
        levels = self.levels()

        ###Step 2: Merging states
        pass
#
# Boolean set operations on languages
#
def cross_product(D1, D2, accept_method):
    """A generalized cross-product constructor over two DFAs. 
    The third argument is a binary boolean function f, and a state (q1, q2) in the final
    DFA accepts if f(A[q1],A[q2]), where A indicates the acceptance-value of a state.
    """
    assert(D1.alphabet == D2.alphabet)
    states = []
    for s1 in D1.states:
        for s2 in D2.states:
            states.append((s1,s2))
    start = (D1.start, D2.start)
    def delta(state_pair, char):
        next_D1 = D1.delta(state_pair[0], char)
        next_D2 = D2.delta(state_pair[1], char)
        return (next_D1, next_D2)
    alphabet = D1.alphabet
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
    f = bool.__or__
    return cross_product(D1, D2, f)

def symmetric_difference(D1, D2):
    """Constructs an unminimized DFA recognizing the symmetric difference of the languages of two given DFAs."""
    f = bool.__xor__
    return cross_product(D1, D2, f)

def inverse(D):
    """Constructs an unminimized DFA recognizing the inverse of the language of a given DFA."""
    new_accepts = []
    for state in D.states:
        if state not in D.accepts:
            new_accepts.append(state)
    return DFA(states=D.states, start=D.start, delta=D.delta, accepts=new_accepts, alphabet=D.alphabet)
# 
# Constructing new DFAs
# 
def from_finite_word_list(language):
    """Placeholder. Will construct the acyclic DFA accepting a given finite language."""
    pass

def modular_zero(n, base=2):
    """Returns a DFA that accepts all binary numbers equal to 0 mod n. Use the optional
    parameter "base" if you want something other than binary. The empty string is always 
    included in the DFA's language.
    """
    states = range(n)
    alphabet = map(str, range(base))
    delta = lambda q, c: ((q*base+int(c)) % n)
    start = 0
    accepts = [0]
    return DFA(states=states, alphabet=alphabet, delta=delta, start=start, accepts=accepts)
