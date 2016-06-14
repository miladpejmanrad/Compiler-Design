# By having class "Scope", we are able to create scopes and each scope has a name and has the ability to be inserted or to be searched through
class Scope:
    def __init__(self, name):
        self.data = {}
        self.name = name
        
    def name(self):
        return self.name
        
    def search(self, x):
        if x in self.data.keys():
            return True

    def insert(self, variable, Type, value, offset): # Here we insert the variable and its corresponding register, value and offset
        self.data[variable] = [Type , value, offset] 
    
scopes = [Scope("S0")] # We initialize S0 which is the global scope. The next scopes will be S1, S2, S3 etc.

def top(): # Shows the name of the scope that is currently at the top of the stack
    try:
        return scopes[(len(scopes)-1)].name
    except:
        print "No scope exists!"

def enter_new_scope(): # Makes a new instance of scope
    try:
        i = len(scopes) 
        scopes.append(Scope("S" + str(i)))
    except:
        pass


def leave_current_scope(): # This acts like a Pop(), so it gets rid of the current scope and goes to the previous scope which might be the global scope
    if len(scopes) > 0:
        del scopes[-1]
    else:
        print "No scope to leave!"
    
def current_scope(): # This returns the actual scope, not the name of it, which is currently on the top of the stack
    return scopes[(len(scopes)-1)]

def search(string): # This searches for a given string through all the scopes and returns "True" if it finds the string somewhere in one of the scopes, and otherwise returns "False"
    for scope in scopes:
        if scope.search(string) == True:
            return True
            break
    return False


def Type(string): # This searches for a given string through all the scopes and returns the type of the variable
    for scope in scopes:
        if scope.search(string) == True:
            return scope.data[string][0]


def size(string): # This searches for a given string through all the scopes and returns the value of the variable
    for scope in scopes:
        if scope.search(string) == True:
            return scope.data[string][1]


def offset(string): # This searches for a given string through all the scopes and returns the value of its offset
    for scope in scopes:
        if scope.search(string) == True:
            return scope.data[string][2]

def val(offset): # return the value of a variable given its offset
    for scope in scopes:
        for variable in scope.data:
            if type(scope.data[variable][2]) != list:
                if scope.data[variable][2] == offset:
                    return scope.data[variable][1]
            else:
                #print scope.data[variable][1]
                for i in range(len(scope.data[variable][1])):
                    if scope.data[variable][2][i] == offset:
                        return scope.data[variable][1][i]


def var(offset): # return the name of a variable given its offset
    for scope in scopes:
        for variable in scope.data:
            if type(scope.data[variable][2]) != list:
                if scope.data[variable][2] == offset:
                    return variable
            else:
                if offset in scope.data[variable][2]:
                    return variable


def offset_a(string): # This searches for a given array through all the scopes and returns the value of its offset
    for scope in scopes:
        if scope.search(string) == True:
            return scope.data[string][2][0]




'''
## Testing the program:
print "The current scope which is the global scope which is:", Top()
print
print "Insertin some strings ('main', 'x', 'y') to the global scope:"
print "Current_scope().insert('main')"
Current_scope().insert("main")
print "Current_scope().insert('x')"
Current_scope().insert("x")
print "Current_scope().insert('y')"
Current_scope().insert("y")
print
print "Entering a new scope: Enter_new_scope()"
Enter_new_scope()
print "checking the current scope: ", Top()
print "Insertin some strings ('Sweany', 'Bryce', 'Caragea') to the current scope:"
print "Current_scope().insert('Sweany')"
Current_scope().insert("Sweany")
print "Current_scope().insert('Bryce')"
Current_scope().insert("Bryce")
print "Current_scope().insert('Caragea')"
Current_scope().insert("Caragea")
print 
print "Searching for string 'Nielsen' returns False since its not in any of the scopes:"
print "Search('Nielsen')"
print Search("Nielsen")

print "Searching for string 'Sweany' returns True since it's already insterted in one of the scopes: "
print "Search('Sweany')"
print Search("Sweany")

print "Searching for string 'main' returns True since it's already insterted in one of the scopes: "
print "Search('main')"
print Search('main')

print "leaving the current scope and getting one scope closer to the global scope:", "Leave_current_scope()"
Leave_current_scope()
print "checking the current scope: ", Top()

print 
print "This program can have very large number of scopes in the stack and each scope can have very large number of strings"
'''