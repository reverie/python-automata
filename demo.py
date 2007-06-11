import DFA

#Basics:
states = range(5)
start = 0
accepts = [0]
alphabet = ['0','1']
def delta(state, char):
 char = int(char)
 if char == 0:
  return state * 2 % 5 
 return (state*2+1)%5
d = DFA.DFA(states=states, start=start, accepts=accepts, alphabet=alphabet, delta=delta)
#Given a binary input, d accepts if the number represented is divisible by 5 (plus the empty string)
print d.current_state
d.input_sequence("1110101011101") #7517
print d.current_state
print d.status()
d.reset()
print d.current_state
d.input_sequence("10011011101") #1245
print d.current_state
print d.status()

#Finite difference minimization
states = range(5)
start = 0
accepts = [0, 2, 4]
alphabet = ['0']
def delta(state, char):
 if state < 4:
  return state+1
 else:
  return 4
e = DFA.DFA(states=states, start=start, delta=delta, accepts=accepts, alphabet=alphabet)
print "===The starting DFA==="
e.pretty_print()
print "===F-minimized==="
e.finite_difference_minimize()
e.pretty_print()

states = range(3)
alphabet = ['0', '1']
def delta(q, c):
    if q == 0:
        return int(c)
    else:
        return 2
start = 0
accepts = [1]
f = DFA.DFA(states=states, alphabet=alphabet, delta=delta, start=start, accepts=accepts)
