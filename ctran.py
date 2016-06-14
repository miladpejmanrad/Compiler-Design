# -----------------------------------------------------------------------------
# CTran compiler using PLY
# PLY is a pure Python package and stands for Python Lex and Yacc by David M. Beazley (http://www.dabeaz.com/ply/)
# ply.lex functions as the lexer and ply.yacc functions as yacc
# -----------------------------------------------------------------------------
import math
import os
import program1
from program1 import *
import ply.lex as lex
import ply.yacc as yacc


sizelist = [] # the sizelist for arrays
sizelist_array = {} # the dictionary of arrays and their sizelists
globalOffset = 0 # the global offset to keep track of the addresses of the memory
temp_registers = [] # to save what r1 and r2 will be
registers = [] # To store all the r1s and r2s and its corresponding operand
regs = {} # To store registers and their values
R = 2 # Storing r0, r1 and r2 for math operations and starting from 3 for all other registers (r3, r4 ... r31)
L = 0 # for if statements
Level = [] # The levels for if statements
hold = 0 # flag for keeping track of if we are inside an if statement
S = '' # the lines that are hold to be printed after an if statement
need = [] # list of the things needed for a do loop

# Saving the current directory to apply the code on all the files with "e" extension.
root = os.getcwd()

# The first part is to deal with the tokens and building the lexer
tokens = [ 'PLUS', 'PPLUS', 'MINUS', 'MMINUS', 'AMPERSAND', 'TILDA', 'TIMES', 'DIVIDE', 'MOD', 'SHIFTR', 'SHIFTL', 'COMMA', 'SEMICOLON', 'name', 'intLiteral', 'OBRACKET', 'CBRACKET', 'stringLiteral','PAREN_L','PAREN_R', 'COLON', 'EQUALS', 'POWER', 'floatLiteral', 'OR', 'HAT', 'DOT']

# I added these tokens as reserved words and intentionally NOT as regular expressions so that it doesn't mix up some similar words such as beginning or outputs
reserved = { 
    'void' : 'void',
    'and' : 'and',
    'or' : 'or',
    'not' : 'not',
    'begin' : 'begin',
    'end' : 'end',
    'gt' : 'gt',
    'ge' : 'ge',
    'le' : 'le',
    'lt' : 'lt',
    'eq' : 'eq',
    'neq' : 'neq',
    'int' : 'INT',
    'continue' : 'continue',
    'do' : 'do',
    'if' : 'if',
    'else' : 'else',
    'int' : 'int',
    'char' : 'char',
    'boolean' : 'boolean',
    'double' : 'double'
}

# Then combine the tokens and the reserved words
tokens = tokens + list(reserved.values())

# Regular expressions of the tokens
t_PLUS    = r'\+'
t_PPLUS    = r'\+\+'
t_MINUS   = r'\-'
t_MMINUS   = r'\-\-'
t_AMPERSAND = r'\&'
t_TILDA = r'\~'
t_TIMES   = r'\*'
t_POWER   = r'\*\*'
t_DIVIDE  = r'\/'
t_EQUALS  = r'=' 
t_PAREN_L  = r'\('
t_PAREN_R  = r'\)'
t_COLON = r'\:'
t_DOT = r'\.'
t_OBRACKET = r'\['
t_CBRACKET = r'\]'
# t_QUOTE = r'\"'
t_SEMICOLON = r'\;'
t_COMMA = r'\,'
t_SHIFTR = r'\>\>'
t_SHIFTL = r'\<\<'
t_MOD = r'\%'
t_OR = r'\|'
t_HAT = r'\^'

# name which is the variables such as x, array[3,4] etc.
def t_name(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value,'name') 
    return t


# Detects strings
def t_stringLiteral(t):
   r'\"([^\\\n]|(\\.))*?\"'
   t.type = reserved.get(t.value[1:-1],'stringLiteral') 
   return t


# RE for digits
def t_intLiteral(t):
    r'\d+'
    t.value = int(t.value)
    return t


# We should ignore some characters such as spaces and tabs
t_ignore = ' \t'


# keep track of the line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Now that we defined all the possible tokens via Regular Expressions and reserved words, we build the lexer
lex.lex()

# The second part is to make grammars and and to build the yacc and then feed in the lex into the yacc and parse the string

# Operator Symbol Precedence Level Assoc based on  the Dr. Sweany's requirements
precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('right', 'POWER'),
    ('left', 'PAREN_L', 'PAREN_R')
)


def p_Program(p):
    ''' Program : DeclList FuncList '''


def p_FuncList(p):
    ''' FuncList : Func
                 | Func FuncList '''


def p_Func(p):
    ''' Func : name PAREN_L ParmList PAREN_R colon Type DeclList SBlock '''
    leave_current_scope()

def p_colon(P):
	''' colon : COLON '''
	enter_new_scope()


def p_ParmList(p):
    ''' ParmList : name
                 | name COMMA ParmList
                 | '''


def p_DeclList(p):
    ''' DeclList : Decl
                 | Decl SEMICOLON DeclList
                 | '''

# declaration of variables except arrays
def p_Decl_literals(p):
    ''' Decl : Type name '''
    global globalOffset
    offset = globalOffset
    globalOffset += 4
    current_scope().insert(p[2], p[1], "NONE", offset)


# declaration of arrays
def p_Decl_arrays(p):
    ''' Decl : Type name OBRACKET SizeList CBRACKET '''
    global globalOffset, sizelist, sizelist_array

    mul = 1
    for x in sizelist:
        mul = mul * x
    sizelist_array[p[2]] = sizelist # to store the sizelist of an array
    sizelist = []
    offset = globalOffset
    globalOffset += mul * 4
    current_scope().insert(p[2], p[1], ["NONE"], [offset])


def p_SizeList(p):
    ''' SizeList : intLiteral
                 | intLiteral COMMA SizeList '''
    global sizelist
    sizelist.insert(0, p[1])
    p[0] = p[1]
    

def p_Type(p):
    ''' Type : int
             | char
             | boolean
             | void
             | double '''
    p[0] = p[1]

def p_SBlock(p):
    ''' SBlock : begin DeclList Stmts end '''


def p_Stmts(p):
    ''' Stmts : S
              | S Stmts '''



def p_S_equals(p):
	''' S : ID EQUALS E '''
	global regs, temp_registers, S
	temp_registers = []
	variable = p[1][0]
	value = p[3][1]  # The value of an integer or the offset of the variable
	for scope in scopes:
	    if scope.search(variable) == True:
	        if p[3][0] == 'not_a_variable':  
	            if type(scope.data[variable][1]) == list:  # x[24] = 2
	                
	                if p[1][1] not in scope.data[variable][2]: # if we haven't previously had x[24] = some number
	                    scope.data[variable][1].append(value)
	                    scope.data[variable][2].append(p[1][1])
	                    if hold == 0:
	                        out.write('\n\n\tr2 = {};'.format(value))
	                        out.write('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                    else:
	                        S += ('\n\n\tr2 = {};'.format(value))
	                        S += ('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                    break
	                else:    # to update a certain array
	                    for i in range(len(scope.data[variable][2])):
	                        if scope.data[variable][2][i] == p[1][1]:
	                            scope.data[variable][1][i] = value
	                            if hold == 0:
	                                out.write('\n\n\tr2 = {};'.format(value))
	                                out.write('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                            else:
	                                S += ('\n\n\tr2 = {};'.format(value))
	                                S += ('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                            break

	            else:   #  x = 4
	                scope.data[variable][1] = value
	                if hold == 0:
	                    out.write('\n\n\tr2 = {};'.format(value))
	                    out.write('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                else:
	                    S += ('\n\n\tr2 = {};'.format(value))
	                    S += ('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                break
	        else:  # x = y
	        	
	            if type(scope.data[variable][1]) == list:
	                if p[3][0] in regs: # verify this
	                    scope.data[variable][1].append(value)
	                    scope.data[variable][2].append(p[1][1])
	                    if hold == 0:
	                        out.write('\n\t*(globalData + {}) = {};\n'.format(p[1][1], current_used_register()))
	                    else:
	                        S += ('\n\t*(globalData + {}) = {};\n'.format(p[1][1], current_used_register()))
	                    break
	                
	                else:
	                    scope.data[variable][1].append(val(p[3][1]))
	                    scope.data[variable][2].append(p[1][1])


	                    if hold == 0:
	                        out.write('\n\n\tr2 = *(globalData + {});'.format(p[3][1]))
	                        out.write('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                    else:
	                        S += ('\n\n\tr2 = *(globalData + {});'.format(p[3][1]))
	                        S += ('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                    break 



	            if p[3][0] in regs:
	                if hold == 0:
	                    out.write('\n\n\t*(globalData + {}) = {};\n'.format(p[1][1], current_used_register()))
	                else:
	                    S += ('\n\n\t*(globalData + {}) = {};\n'.format(p[1][1], current_used_register()))
	                scope.data[variable][1] = value
	                break
	            else:
	                if hold == 0:
	                    out.write('\n\n\tr2 = *(globalData + {});'.format(value))
	                    out.write('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                else:
	                    S += ('\n\n\tr2 = *(globalData + {});'.format(value))
	                    S += ('\n\t*(globalData + {}) = r2;'.format(p[1][1]))
	                scope.data[variable][1] = value
	                break    


def p_S_print(p):
    ''' S : name PAREN_L ExprList PAREN_R'''
    global regs, registers, temp_registers, S
    
    if p[1] == "printLine":
        if hold == 0:
            out.write('\n\tprintLine();')
        else:
            S += ('\n\tprintLine();')
    
    elif p[1] == 'printString':
        if hold == 0:
            out.write('\n\tprintString({});'.format(p[3]))
        else:
            S += ('\n\tprintString({});'.format(p[3]))
    
    elif p[1] == 'printInt':
        if p[3][0] == 'not_a_variable':
            if hold == 0:
                out.write('\n\n\tr2 = {};'.format(p[3][1]))
                out.write('\n\tprintInt(r2);\n')
            else:
                S += ('\n\n\tr2 = {};'.format(p[3][1]))
                S += ('\n\tprintInt(r2);\n')
        
        elif p[3][0] in regs:
            if hold == 0:
                out.write('\n\tprintInt({});\n'.format(current_used_register()))
            else:
                S += ('\n\tprintInt({});\n'.format(current_used_register()))
            temp_registers = []
        else:
            if hold == 0:
                out.write('\n\n\tr2 = *(globalData + {});'.format(p[3][1]))
                out.write('\n\tprintInt(r2);\n')
            else:
                S += ('\n\n\tr2 = *(globalData + {});'.format(p[3][1]))
                S += ('\n\tprintInt(r2);\n')


def p_S(p):
    ''' S : ID EQUALS ConditionalExprn '''


def p_S_if(p):
	''' S : IF PAREN_L ConditionalExprn PAREN_R SBlock '''
	global hold, S
	x = p[3][0]

	if type(x[0]) == int:
		x0 = next_available_register()
		out.write('\n\t{} = {};'.format(x0, x[0]))
	else:
		x0 = x[0]

	if type(x[2]) == int:
		x2 = next_available_register()
		out.write('\n\t{} = {};'.format(x2, x[2]))
	else:
		x2 = x[2]


	if len(p[3]) == 1:
	    out.write('\n\tif ({} {} {}) goto {};'.format(x0, negate(x[1]), x2, Level[2] ))
	else:
	    y = p[3][1]
	    if type(y[0]) == int:
	    	y0 = next_available_register()
	    	out.write('\n\t{} = {};'.format(y0, y[0]))
	    else:
	    	y0 = y[0]
	    
	    if type(y[2]) == int:
	    	y2 = next_available_register()
	    	out.write('\n\t{} = {};'.format(y2, y[2]))
	    else:
	    	y2 = y[2]

	    if p[3][2] == 'and':
	        out.write('\n\tif ({} {} {}) goto {};'.format(x0, negate(x[1]), x2, Level[2] ))
	        out.write('\n\tif ({} {} {}) goto {};'.format(y0, negate(y[1]), y2, Level[2] ))
	    else:
	        out.write('\n\tif ({} {} {}) goto {};'.format(x0, x[1], x2, Level[0] ))
	        out.write('\n\tif ({} {} {}) goto {};'.format(y0, negate(y[1]), y2, Level[2] ))

	out.write('\n{}:'.format(Level[0]))
	out.write(S)
	S = ''
	hold = 0
	out.write('\n{}:'.format(Level[2]))
	out.write(('\n\tr22 = r22;'))
    


def p_S_if_else(p):
	''' S : IF PAREN_L ConditionalExprn PAREN_R SBlock ELSE SBlock ''' 
	global hold, S
	x = p[3][0]

	if type(x[0]) == int:
		x0 = next_available_register()
		out.write('\n\t{} = {};'.format(x0, x[0]))
	else:
		x0 = x[0]

	if type(x[2]) == int:
		x2 = next_available_register()
		out.write('\n\t{} = {};'.format(x2, x[2]))
	else:
		x2 = x[2]


	if len(p[3]) == 1:
	    out.write('\n\tif ({} {} {}) goto {};'.format(x0, negate(x[1]), x2, Level[1] ))
	else:
	    y = p[3][1]
	    if type(y[0]) == int:
	    	y0 = next_available_register()
	    	out.write('\n\t{} = {};'.format(y0, y[0]))
	    else:
	    	y0 = y[0]
	    
	    if type(y[2]) == int:
	    	y2 = next_available_register()
	    	out.write('\n\t{} = {};'.format(y2, y[2]))
	    else:
	    	y2 = y[2]

	    if p[3][2] == 'and':
	        out.write('\n\tif ({} {} {}) goto {};'.format(x0, negate(x[1]), x2, Level[1] ))
	        out.write('\n\tif ({} {} {}) goto {};'.format(y0, negate(y[1]), y2, Level[1] ))
	    else:
	        out.write('\n\tif ({} {} {}) goto {};'.format(x0, x[1], x2, Level[0] ))
	        out.write('\n\tif ({} {} {}) goto {};'.format(y0, negate(y[1]), y2, Level[1] ))
	out.write('\n{}:'.format(Level[0]))
	out.write(S)
	S = ''
	hold = 0
	f_else = 0
	out.write('\n{}:'.format(Level[2]))
	out.write(('\n\tr22 = r22;'))


def p_ConditionalExpr(p):
    ''' ConditionalExprn : ConditionalExpr '''
    global hold
    hold = 1
    p[0] = p[1]


def p_S_IF(p):
    ''' IF : if '''
    global Level, f_if
    Level = next_L()


def p_S_ELSE(p):
    ''' ELSE : else '''
    global f_else, S
    f_else = 1
    if hold == 0:
        out.write('\n\tgoto {};'.format(Level[2]))
        out.write('\n{}:'.format(Level[1]))
    else:
        S += ('\n\tgoto {};'.format(Level[2]))
        S += ('\n{}:'.format(Level[1]))


def p_S_do(p):
    ''' S : do X Y EQUALS Z Stmts Enddo '''



def p_S_do_X(p):
    ''' X : intLiteral '''
    global need
    need.append([p[1]])
    p[0] = p[1]


def p_S_do_name(p):
    ''' Y : ID '''
    global need
    need[-1].append(p[1][0]) # adding the name and offset of the ID
    p[0] = p[1]

def p_doList(p):
	''' Z : DoList'''
	global need, S
	for x in p[1]:      
	    need[-1].append(x)
	if hold == 0:
	    out.write('\n\n\tr2 = {};'.format(p[1][0]))
	    out.write('\n\t*(globalData + {}) = r2;'.format(offset(need[-1][1])))
	    out.write('\nLoop{}:'.format(need[-1][0]))
	else:
	    S += ('\n\n\tr2 = {};'.format(p[1][0]))
	    S += ('\n\t*(globalData + {}) = r2;'.format(offset(need[-1][1])))
	    S += ('\nLoop{}:'.format(need[-1][0]))
	for scope in scopes:
	    if scope.search(need[-1][1]) == True:
	        scope.data[need[-1][1]][1] = p[1][0]
	        break


def p_Enddo(p):
	'''Enddo : intLiteral continue'''
	global need, S

	for i in range(len(need)):
	    if need[i][0] == p[1]:
	        x = i
	        break
	if hold == 0:
	    out.write('\n\n\tr0 = *(globalData + {});'.format(offset(need[x][1])))
	    out.write('\n\tr1 = r0 + {};'.format(need[x][4]))
	    out.write('\n\t*(globalData + {}) = r1;'.format(offset(need[x][1])))
	    out.write('\n\tr2 = {};'.format(need[x][3]))
	    out.write('\n\tif(r1 <= r2) goto Loop{};'.format(p[1]))
	else:
	    S += ('\n\n\tr0 = *(globalData + {});'.format(offset(need[x][1])))
	    S += ('\n\tr1 = r0 + {};'.format(need[x][4]))
	    S += ('\n\t*(globalData + {}) = r1;'.format(offset(need[x][1])))
	    S += ('\n\tr2 = {};'.format(need[x][3]))
	    S += ('\n\tif(r1 <= r2) goto Loop{};'.format(p[1]))
	for scope in scopes:
	    if scope.search(need[x][1]) == True:
	        scope.data[need[x][1]][1] += need[x][4]
	        break

	del need[x]


def p_DoList_two(p):
    ''' DoList : E COMMA E '''
    p[0] = [value(p[1]), value(p[3]), 1]


def p_DoList_three(p):
    ''' DoList : E COMMA E COMMA E '''
    p[0] = [value(p[1]), value(p[3]), value(p[5])]


def p_ConditionalExpr_RelOp(p):
    ''' ConditionalExpr : E RelOp E '''
    p[0] = [RelOp(p[1], p[2], p[3])]



def p_ConditionalExpr_not(p):
    ''' ConditionalExpr : not PAREN_L ConditionalExpr PAREN_R'''


def p_ConditionalExpr_and(p):
    ''' ConditionalExpr : ConditionalExpr and PAREN_L ConditionalExpr PAREN_R '''


def p_ConditionalExpr_and_RelOp(p):
    ''' ConditionalExpr : ConditionalExpr and E RelOp E '''
    p[0] = [p[1][0],RelOp(p[3], p[4], p[5]),'and']
    


def p_ConditionalExpr_or(p):
    ''' ConditionalExpr : ConditionalExpr or PAREN_L ConditionalExpr PAREN_R '''


def p_ConditionalExpr_or_RelOp(p):
    ''' ConditionalExpr : ConditionalExpr or E RelOp E '''
    p[0] = [p[1][0],RelOp(p[3], p[4], p[5]),'or']


def p_ExprList(p):
    ''' ExprList : E COMMA ExprList
                 | E '''
    p[0] = p[1]
    global sizelist
    sizelist.insert(0,value(p[1]))
 

def p_ExprList_empty(p):
    ''' ExprList :  '''


def p_E_cal(p):
    ''' E : E BOP BitTerm'''


def p_E(p):
    ''' E : BitTerm '''
    p[0] = p[1]


def p_BitTerm_ShiftOp(p):
    ''' BitTerm : BitTerm ShiftOp ShiftTerm'''


def p_BitTerm(p):
    ''' BitTerm : ShiftTerm '''
    p[0] = p[1]


def p_ShiftTerm_AddOp(p):
    ''' ShiftTerm : ShiftTerm AddOp Term '''
    global regs, S
    register = next_available_register()
    if hold == 0:
        out.write('\n\n\tr1 = {};'.format(what(p[1])))
        out.write('\n\tr2 = {};'.format(what(p[3])))
        out.write('\n\tr0 = r1 {} r2;'.format(p[2]))
        out.write('\n\t{} = r0;'.format(register))
    else:
        S += ('\n\n\tr1 = {};'.format(what(p[1])))
        S += ('\n\tr2 = {};'.format(what(p[3])))
        S += ('\n\tr0 = r1 {} r2;'.format(p[2]))
        S += ('\n\t{} = r0;'.format(register))
    
    if p[2] == '+':
        p[0] = [register, value(p[1]) + value(p[3])]
    else:
        p[0] = [register, value(p[1]) - value(p[3])]
    regs[register] = p[0][1]


def p_ShiftTerm(p):
    ''' ShiftTerm : Term '''
    p[0] = p[1]


def p_Term_MulOp(p):
    ''' Term : Term MulOp Factor '''
    register = next_available_register()
    global regs, S
    if p[2] == '/':
        p[0] = [register, value(p[1]) / value(p[3])]
        if hold == 0:
            out.write('\n\n\tr1 = {};'.format(what(p[1])))
            out.write('\n\tr2 = {};'.format(what(p[3])))
            out.write('\n\tr0 = r1 {} r2;'.format(p[2]))
            out.write('\n\t{} = r0;'.format(register))  
        else:
            S += ('\n\n\tr1 = {};'.format(what(p[1])))
            S += ('\n\tr2 = {};'.format(what(p[3])))
            S += ('\n\tr0 = r1 {} r2;'.format(p[2]))
            S += ('\n\t{} = r0;'.format(register))     
    
    elif p[2] == '*':
        p[0] = [register, value(p[1]) * value(p[3])]
        if hold == 0:
            out.write('\n\n\tr1 = {};'.format(what(p[1])))
            out.write('\n\tr2 = {};'.format(what(p[3])))
            out.write('\n\tr0 = r1 {} r2;'.format(p[2]))
            out.write('\n\t{} = r0;'.format(register))
        else:
            S += ('\n\n\tr1 = {};'.format(what(p[1])))
            S += ('\n\tr2 = {};'.format(what(p[3])))
            S += ('\n\tr0 = r1 {} r2;'.format(p[2]))
            S += ('\n\t{} = r0;'.format(register))
    
    elif p[2] == '%':
        p[0] = [register, value(p[1]) % value(p[3])]
        if hold == 0:
            out.write('\n\n\tr1 = {};'.format(what(p[1])))
            out.write('\n\tr2 = {};'.format(what(p[3])))
            out.write('\n\tr0 = r1 / r2;')
            out.write('\n\tr1 = {};'.format(what(p[3])))
            out.write('\n\tr2 = r0;')
            out.write('\n\tr0 = r1 * r2;')
            out.write('\n\tr1 = {};'.format(what(p[1])))
            out.write('\n\tr2 = r0;')
            out.write('\n\tr0 = r1 - r2;')
            out.write('\n\t{} = r0;'.format(register))
        else:
            S += ('\n\n\tr1 = {};'.format(what(p[1])))
            S += ('\n\tr2 = {};'.format(what(p[3])))
            S += ('\n\tr0 = r1 / r2;')
            S += ('\n\tr1 = {};'.format(what(p[3])))
            S += ('\n\tr2 = r0;')
            S += ('\n\tr0 = r1 * r2;')
            S += ('\n\tr1 = {};'.format(what(p[1])))
            S += ('\n\tr2 = r0;')
            S += ('\n\tr0 = r1 - r2;')
            S += ('\n\t{} = r0;'.format(register))
    regs[register] = p[0][1]



def p_Term(p):
    ''' Term : Factor '''
    p[0] = p[1]


def p_Factor_POWER(p):
    ''' Factor : Factor POWER UOperand'''
    global regs, S
    register = next_available_register()
    if hold == 0:
        out.write('\n\n\tr0 = 1;')
        out.write('\n\tr1 = {};'.format(what(p[1])))
    else:
        S += ('\n\n\tr0 = 1;')
        S += ('\n\tr1 = {};'.format(what(p[1])))
    rng = value(p[3])
    if hold == 0:
        for x in range(rng):
            out.write('\n\tr0 = r0 * r1;')
        out.write('\n\t{} = r0;'.format(register))
    else:
        for x in range(rng):
            S += ('\n\tr0 = r0 * r1;')
        S += ('\n\t{} = r0;'.format(register))
    p[0] = [register, int(math.pow(value(p[1]), value(p[3])))]
    regs[register] = p[0][1]
    

def p_Factor(p):
    ''' Factor : UOperand '''
    p[0] = p[1]


def p_UOperand_UOP(p):
    ''' UOperand : UOP Primary '''
    p[0] = p[2]   # this should be changed upon request of the next projects
 

def p_UOperand(p):
    ''' UOperand : Primary '''
    p[0] = p[1]
    #print p[1]


def p_Primary(p):
    ''' Primary : PAREN_L E PAREN_R'''
    p[0] = p[2]


def p_Primary_ID(p):
    ''' Primary : ID '''
    p[0] = p[1]


def p_Primary_ExprList(p):  # I think this is for function calls
    ''' Primary : name PAREN_L ExprList PAREN_R '''


def p_Primary_intLiteral(p):
    ''' Primary : intLiteral '''
    p[0] = ['not_a_variable', p[1]]


def p_Primary_stringLiteral(p):
    ''' Primary : stringLiteral '''
    p[0] = p[1]


def p_Primary_floatLiteral(p):
    ''' Primary : floatLiteral '''
    p[0] = p[1]


def p_ID(p):
    ''' ID : name '''
    off = offset(p[1])
    p[0] = [p[1], off]
    #print p[0]


def p_ID_array(p): # Example: array[7] except for declaration
    ''' ID : name OBRACKET ExprList CBRACKET '''
    global sizelist, sizelist_array, temp_registers
    a = sizelist_array[p[1]]
    b = sizelist
    #print a
    #print b
    sizelist = []
    off = offset_array(a,b,p[1])
    p[0] = [p[1], off]
    global temp_registers 
    for i in range(len(sizelist_array[p[1]])):
        temp_registers = temp_registers[:-1]
    temp_registers.append(p[0])


def p_RelOp(p):
    ''' RelOp : DOT gt DOT
              | DOT ge DOT
              | DOT le DOT
              | DOT lt DOT
              | DOT eq DOT
              | DOT neq DOT '''
    p[0] = p[2]


def p_BOP(p):
    ''' BOP : AMPERSAND
            | OR
            | HAT '''
    p[0] = p[1]


def p_ShiftOp(p):
    ''' ShiftOp : SHIFTR
                | SHIFTL '''
    p[0] = p[1]


def p_MulOp(p):
    ''' MulOp : TIMES
              | DIVIDE
              | MOD '''
    p[0] = p[1]


def p_AddOp(p):
    ''' AddOp : MINUS
              | PLUS '''
    p[0] = p[1]


def p_UOP(p):
    ''' UOP : MMINUS
            | PPLUS
            | AMPERSAND
            | TILDA
            | MINUS '''
    p[0] = p[1]


# error handling
def p_error(p):
    print("Syntax error at '%s'" % p.value)

# Now that we have all the required grammar, we call the yacc and start parsing the input

yacc.yacc(debug=0, write_tables=0) #  I put 0 to prevent yacc from generating any kind of parser table file. Just delete the conditions of the inside of the parentheses and run the program again if you wanna take a look at the rules that are generated by the PLY


# Now apply the code for all of the files within current directory which has an "e" extension 
files = filter(os.path.isfile, os.listdir( os.curdir ))

def offset_array(a,b,name): 
    off = offset_a(name)
    s = 0
    size = len(a)
    if size > 1:
        for i in range(size):
            if len(a[i+1:]) > 0:
                mul = 1
                for j in a[i+1:]:
                    mul = j*mul
                mul = mul*4*b[i]
                s += mul
            else:
                s += b[i]*4
                return s + off
    else:
        return 4*b[0] + off


def value(x):  # get the value of the variable or register or return the integer
    if x[0] == 'not_a_variable':
        return x[1]
    
    elif x[0] in regs:
        return regs[x[0]]
    
    else:
        return val(x[1])


def what(x):  # return the intliteral or name of the register or the address of the variable
    if x[0] == 'not_a_variable':
        return x[1]

    elif x[0] in regs:
        return x[0]

    else:
        return '*(globalData + {})'.format(x[1])


def what_names(x):  # return the intliteral or name of the register or creates a new register if a variable is detected
    global S
    if x[0] == 'not_a_variable':
        return x[1]

    elif x[0] in regs:
        return x[0]

    else:
        r = next_available_register()
        if hold == 0:
            out.write('\n\n\t{} = *(globalData + {});'.format(r, x[1]))
        else:
            S += ('\n\n\t{} = *(globalData + {});'.format(r, x[1]))
        return r


def negate(relOp): # negation function
    if relOp == '>':
        return '<='
    
    elif relOp == '>=':
        return '<'
    
    elif relOp == '<=':
        return '>'

    elif relOp == '<':
        return '>='

    elif relOp == '==':
        return '!='

    elif relOp == '!=':
        return '=='


def next_L(): # creates a new unused register
    global L
    L += 1
    return ["IF" + str(L),"ELSE" + str(L) ,"END" + str(L) ]

def current_L(): # creates a new unused register
    global L
    return ["IF" + str(L),"ELSE" + str(L) ,"END" + str(L) ]


def next_available_register(): # creates a new unused register
    global R
    R += 1
    return ("r" + str(R))


def current_used_register(): # retruns the last used register
    global R
    return ("r" + str(R))


def RelOp(E1,relOp,E2): # to compare two statements with each other based on the operation
    if relOp == 'gt':
        return [what_names(E1),'>' ,what_names(E2)]
    
    elif relOp == 'ge':
        return [what_names(E1),'>=' ,what_names(E2)]
    
    elif relOp == 'le':
        return [what_names(E1),'<=' ,what_names(E2)]

    elif relOp == 'lt':
        return [what_names(E1),'<' ,what_names(E2)]

    elif relOp == 'eq':
        return [what_names(E1),'==' ,what_names(E2)]

    elif relOp == 'neq':
        return [what_names(E1),'!=' ,what_names(E2)]


for f in files:
    if 'ct' in f: # Looks for the files with an "e" extesion inside the current directory
        out = open(f[:-3]+".c" , 'w') # The output files will have the same name as their corresponding input. The only diffrence would be their extension which will be ".c" which is useful for CMachine.
        out.write('int r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21, r22, r23, r24, r25, r26, r27, r28, r29, r30, r31;\nint *iptr1;\nchar *cptr1;\nchar *fp, *sp;\nchar globalData[1024000];\nchar moreGlobalData[1024000];\n\nmain()\n{\n\tinitstack();')
        file = open(os.path.join(root, f),'r')
        yacc.parse(file.read())
        out.write('\n}')
        out.close()
        scopes = [Scope("S0")]
        R = 2