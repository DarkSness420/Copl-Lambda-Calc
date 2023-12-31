#Ryan Behari
#s3618765
#Assignment 2 Interpreter
#Universiteit Leiden
#Assignment 1 code is reused for this assignment#

import sys
import copy
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

#ERRORS#
class error:
    def __init__(self, name, description, startPos, endPos):
        self.startPos = startPos
        self.endPos = endPos
        self.name = name
        self.description = description

    def showError(self):
        message = f'{self.name}: {self.description}'
        message += f'\nfrom {self.startPos.fileName}, line: {self.startPos.lineNum+1}'
        return message
    
class illegalCharacterError(error):
    #Error if and illegal character has been found
    def __init__(self,description,startPos,endPos):
        super().__init__('illegal character', description,startPos,endPos)

class illegalNumberError(error):
    #Error if a number has been found this isn't part of a variable
    def __init__(self,description,startPos,endPos):
        super().__init__('disallowed integer', description,startPos,endPos)

class missingExprError(error):
    #Missing expression after lambda variable
    def __init__(self,description,startPos,endPos):
        super().__init__('missing expression', description,startPos,endPos)

class missingVarError(error):
    #Missing variable after a lambda symbol has been found
    def __init__(self,description,startPos,endPos):
        super().__init__('missing variable', description,startPos,endPos)

class missingParenError(error):
    #There is missing a closed or open parenthese
    def __init__(self,description,startPos,endPos):
        super().__init__('missing a parenthese', description,startPos,endPos)

#POSITION#
class position:
    def __init__(self,index,lineNum,colomNum, fileName, fileText):
        self.index = index
        self.lineNum = lineNum
        self.colomNum = colomNum
        self.fileName = fileName
        self.fileText = fileText
        
    
    def next(self, currentCharacter):
        self.colomNum += 1
        self.index += 1
        #check if newline character is found
        if(currentCharacter == '\n'):
            #since we start on a new line, the first word is again at column 0
            self.lineNum += 1
            self.colomNum = 0
        return self
    
    def copyPos(self):
        #returns this object
        return position(self.index,self.lineNum,self.colomNum,self.fileName,self.fileText)

#TOKENS#
TYPE_VAR = 'VAR'
TYPE_LEFTPAREN = 'LEFTPAREN'
TYPE_RIGHTPAREN = 'RIGHTPAREN'
TYPE_LAMBDA = 'LAMBDA'

class token:
    #This function is for creating a new token
    def __init__(self, Type, Value = None):
        self.Type = Type
        self.Value = Value
        self.internIndex = 0

    #Function to represent the token for display
    def __repr__(self):
        #if the token has a value, print type and then the value
        #if it doesn't have one, just print the type.
        if (self.Value):
            return f'{self.Type}:{self.Value}'
        else:
            return f'{self.Type}'
        
#LEXER#
class lexer:

    #Makes tokens from the characters in the text
    #Position is set at -1 because method next will advance
    #it to 0 (first character) to start.
    def __init__(self,fileName,text):
        self.fileName = fileName
        self.text = text
        #start at index and column -1 so we start reading at 0
        self.position = position(-1,0,-1, fileName, text) 
        self.currentCharacter = None
        self.next()

    #Function to read the next character if there is any.
    def next(self):
        self.position.next(self.currentCharacter)
        if (self.position.index < len(self.text)):
            self.currentCharacter = self.text[self.position.index]
        else:
            self.currentCharacter = None

    def createTokens(self):
        # Grammar rules: ⟨expr⟩ ::= ⟨var⟩ | '(' ⟨expr⟩ ')' | '\' ⟨var⟩ ⟨expr⟩ | ⟨expr⟩ ⟨expr⟩ #
        tokens = []
        lastNormalChar = None
        parenthesisOpenAmount = 0
        while(self.currentCharacter != None):
            #Ignore whitespaces and tabs
            if self.currentCharacter in letters:
                #begin of variable found, continue to see if there are more letters or digits 
                newVariable = '' #The construction of the variable name
                while (self.currentCharacter and (self.currentCharacter in letters or self.currentCharacter.isdigit())) and self.currentCharacter != None :
                    newVariable += self.currentCharacter
                    lastNormalChar = self.currentCharacter
                    self.next()
                #No letter or digit found directly after, thus end of variable name
                tokens.append(token(TYPE_VAR,newVariable))
            elif(self.currentCharacter in ' \t\n'):
                #ignore spaces,tabs and newlines
                self.next()
            elif (self.currentCharacter == '('):
                tokens.append(token(TYPE_LEFTPAREN))
                lastNormalChar = self.currentCharacter
                parenthesisOpenAmount += 1
                self.next()       
            elif (self.currentCharacter == ')'):
                #missing expression found
                if(lastNormalChar == '('):
                    startPos = self.position.copyPos()
                    illegalChar = self.currentCharacter
                    return [], missingExprError(illegalChar, startPos, self.position)
                elif (parenthesisOpenAmount == 0):
                    #Missing an opening parenthese somewhere
                    startPos = self.position.copyPos()
                    illegalChar = self.currentCharacter
                    return [], missingParenError(illegalChar, startPos, self.position)
                    
                tokens.append(token(TYPE_RIGHTPAREN))
                parenthesisOpenAmount -= 1
                lastNormalChar = self.currentCharacter
                self.next()
            elif (self.currentCharacter == '\\' or self.currentCharacter == 'λ'):
                tokens.append(token(TYPE_LAMBDA))
                lastNormalChar = self.currentCharacter
                self.next()
                while (self.currentCharacter and self.currentCharacter in ' \t\n'):
                    lastNormalChar = self.currentCharacter
                    self.next()
                if(self.currentCharacter not in letters):
                    startPos = self.position.copyPos()
                    character = '?'
                    return [], missingVarError(character, startPos, self.position)
                    
            else:
                #Unallowed character found
                startPos = self.position.copyPos()
                illegalChar = self.currentCharacter
                self.next()
                if(illegalChar.isdigit()):
                    #Numbers only allowed in variables after alpha character(s)
                    return [], illegalNumberError(illegalChar, startPos, self.position)
                else:
                    #Other disallowed symbols
                    return [], illegalCharacterError(illegalChar, startPos, self.position)
        if(parenthesisOpenAmount != 0):
            #missing some close parenthesis
            startPos = self.position.copyPos()
            illegalChar = '?'
            return [], missingParenError(illegalChar, startPos, self.position)
            
        return tokens, None


#PARSER#

class Parser:
    def __init__(self, Tokens: token):
        self.Tokens = Tokens
        #give this token an index number in case there are more of the same variables
        self.tokenIndex = 0 
    
    def parse(self):
        #Parse the expression and put it in a node
        Node = self.expression()
        return Node
    
    def expression(self):
        nextType = self.Tokens[self.tokenIndex].Type
        if(nextType == TYPE_VAR):
            #If a variable has been found, this is the end of the expression
            return self.variable()
        elif(nextType == TYPE_LAMBDA):
            #If there is a lambda, this is the start of a function
            return self.function()
        elif(nextType == TYPE_LEFTPAREN):
            #We can split this expression into a node
            #with expression A and expression B
            return self.application()
        
    def variable(self):
        if(self.tokenIndex < len(self.Tokens)):
            if(self.Tokens[self.tokenIndex].Type == TYPE_VAR):
                #create a variable node out of the current token
                self.tokenIndex += 1
                return VarNode(self.Tokens[self.tokenIndex-1])
    
    def function(self):
        if(self.tokenIndex < len(self.Tokens)):
            if(self.Tokens[self.tokenIndex].Type == TYPE_LAMBDA):
                #Lambda token found, so we should find the variable
                #and after that is the expression part, this is a function alltogether.
                self.tokenIndex += 1
                ourVar = self.variable()
                ourExpr = self.expression()
                return FunctionNode(ourVar, ourExpr)
       
    def application(self):
        if(self.tokenIndex < len(self.Tokens)):
            if(self.Tokens[self.tokenIndex].Type == TYPE_LEFTPAREN):
                #Put the left part of the application into A
                self.tokenIndex += 1
                A = self.expression()
                if(self.tokenIndex < len(self.Tokens)):
                    #Put the right part of the application into B
                    B = self.expression()
                    self.tokenIndex += 1
                    #Now just return a node with these two expressions
                    return ApplicationNode(A, B)
    
class FunctionNode:
    def __init__(self,variable, expr):
        self.variable = variable
        self.expr = expr
    
    def __repr__(self):
        #display lambda following the variable and then the expression
        return '\\'+str(self.variable)+str(self.expr)
    
    def replace(self, varNode, new, newIndex):
        if (self.expr.replace(varNode,new,newIndex)):
            self.expr = new

    def renameVars(self,index):
        #rename a given variable for conversions
        #and/or reductions by just creating a new node
        #and replacing the existing one
        self.expr.renameVars(2*index+2)
        newVar = VarNode(token(TYPE_VAR,self.variable.token.Value, 2*index+2))
        self.replace(VarNode(self.variable.token), newVar, 2*index+2)
        self.variable = newVar

class ApplicationNode():
    def __init__(self, exprA, exprB):
        self.exprA = exprA
        self.exprB = exprB

    def __repr__(self):
        #display the leftside and rightside expressions
        return "("+str(self.exprA)+" "+str(self.exprB)+")"
    
    def replace(self, varNode, new, newIndex):
        #We can just copy the existing nodes
        #and rename them and replace the old node
        NEW = copy.deepcopy(new)
        NEW.renameVariables(newIndex)
        
        if self.exprA.replace(varNode, NEW, 2*newIndex+1):
            self.exprA = NEW
        if self.exprB.replace(varNode, NEW, 2*newIndex+2):
            self.exprB = NEW

    def renameVariables(self, index: FunctionNode):
        self.exprA.renameVariables(2*index+1)
        self.exprB.renameVariables(2*index+2)

class VarNode:
    def __init__(self, token):
        self.token = token

    def __repr__(self):
        #put spaces in front and at the end of a variable
        #its easier to put this in the right format later on
        #using our putInCorrectFormat function 
        if(self.token.Value):
            return ' ' + str(self.token.Value) + ' '
        else:
            return str(self.token.Type)

    def replace(self, varNode, new, newIndex):
        return ((varNode.token.Value == self.token.Value) and (varNode.token.internIndex == self.token.internIndex))

    def renameVariables(self, index: FunctionNode):
        #just as a placeholder for our other functions
        pass


#INTERPRETER#
class Interpreter:
    def __init__(self, maxReductionSteps = 8):
        self.maxReductionSteps = maxReductionSteps
    
    def reduce(self,ast):
        reducedNode = self.eval(ast)
        return reducedNode
    
    def isFunc(self, Node):
        #check if the Node is a function node
        return type(Node) == FunctionNode
    
    def isVar(self, Node):
        #check if the Node is a variable node
        return type(Node) == VarNode
    
    def isApplication(self,Node):
        #check if the Node is an application node
        return type(Node) == ApplicationNode
    
    def eval(self, Node):
        #The maximum amount the tree gets reduced
        #is 'maxReductionSteps' amount of times
        for i in range(self.maxReductionSteps):
            if(self.isApplication(Node)):
                if(self.isVar(Node.exprA)):
                    Node.exprB =self.eval(Node.exprB)
                    return Node
                elif (self.isFunc(Node.exprA)):
                    #Take our variable's internal index, so we know
                    #which variable to take/make for our new expression
                    #for our new node
                    newIndex = Node.exprA.variable.token.internIndex
                    Node.exprA.replace(Node.exprA.variable, Node.exprB,newIndex)
                    Node = Node.exprA.expr
                elif (self.isApplication(Node.exprA) and self.isVar(Node.exprB)):
                    previous = Node.exprA
                    Node.exprA = self.eval(Node.exprA)
                    if(previous == Node.exprA):
                        #check if it has not been simplified further
                        return Node
                else:
                    previous = Node.exprA
                    Node.exprA = self.eval(Node.exprA)
                    if(previous == Node.exprA):
                        #Also here check if there hasnt been made any simplifications
                        return Node
            elif(self.isFunc(Node)):
                #evaluate the current expression further
                Node.expr = self.eval(Node.expr)
                return Node
            else:
                return Node
            

        return Node


def readFile(fileName):
    #read the file if it can be found
    try:
        with open(fileName, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print('File has not been found')
        sys.exit(1)

def run(fileName,text):
    #Runs our lexer on this expression from the file
    ourlexer = lexer(fileName,text)
    tokensS, errorMess = ourlexer.createTokens()
    return tokensS, errorMess

def putInCorrectFormat(inpString):
    #Puts an expression in the correct space format
    ourString = ''
    lastNormalChar = ''
    spaceLastChar = False
    for char in inpString:
        if(char in ' \n\t'):
            #Check if currentcharacter is a space, enter or tab
            spaceLastChar = True
        elif(spaceLastChar ==  True and (lastNormalChar in letters or lastNormalChar.isdigit()) and char in letters):
            #check if last normal character was a digit or number (thus a var)
            #and if this character is also a variable if so, put a space
            ourString += ' ' + char
            spaceLastChar = False
            lastNormalChar = char
        else:
            #Just add this character
            spaceLastChar = False
            ourString += char
            lastNormalChar = char
    
    return ourString

def main():
    #Check if there is an argument given
    if (len(sys.argv) != 2):
        print("Usage: python ./assignment2.py <filename>")
        sys.exit(1)
    else:
        fileContent = readFile(sys.argv[1])

    #run our lexer and collect the tokens and possible errors
    ourResult, ourError = run(sys.argv[1], fileContent)

    if ourError: 
        #Print the collected error if there is one
        print(ourError.showError())
        sys.exit(1)
    else: 
        #Print the parsed tokens
        print('Parsed tokens:', end = ' ')
        print(ourResult)

        #Parse the expressions using our tokens
        #Then put  the abstract syntax tree into
        #the interpreter and simplify it using
        #Beta reductions and alpha conversions
        Pars = Parser(ourResult)
        AST = Pars.parse()
        Interp = Interpreter()
        reduced_AST = Interp.reduce(AST)
        print('Reduced expression: ', end = '')
        print(putInCorrectFormat(str(reduced_AST)))
        sys.exit(0)

if __name__ == '__main__':
    main()
        
