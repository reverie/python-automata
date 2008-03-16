import DFA
#5 / 10 8 7 3

#Basics:
states = range(5)
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
print "Given a binary input, d accepts if the number represented is divisible by 5 (plus the empty string):"
d.pretty_print()
#raw_input()
print 'd.input_sequence("1110101011101") #7517'
d.input_sequence("1110101011101") #7517
print "Current state:", d.current_state
print "Accepting:", d.status()
#raw_input()
print "Resetting..."
d.reset()
print d.current_state
d.input_sequence("10011011101") #1245
print d.current_state
print d.status()

#Various minimizations
a = ['1', '11', '111', '1111', '11110', '11111', '111111', '111110']
b = ['0', '1']
e = DFA.from_word_list(a,b)
print "a = ['1', '11', '111', '1111', '11110', '11111', '111111', '111110']"
print "b = ['0', '1']"
print "e = DFA.from_word_list(a,b)"
print "..."
#raw_input()
print "===The starting DFA==="
e.pretty_print()
#raw_input()
print "==Minimized==="
e.minimize()
e.pretty_print()
#raw_input()
print "==...then DFCA-Minimized==="
e.DFCA_minimize()
e.pretty_print()
#raw_input()
print "==...then Finite-Difference Minimized==="
e.hyper_minimize()
e.pretty_print()
#raw_input()
