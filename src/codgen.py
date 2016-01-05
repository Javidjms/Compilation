class CodeGenerator(object):
    listInstruction = []        #Liste des instructions a print en assembleur
    listInstructionCount = 0    #Nombre d'instructions print == numero de ligne
    onCall = 0
    calling = ""
    nextAddr = -1
    
    def __init__ (self):
        listInstruction = []
        listInstructionCount = 0
        onCall = 0
        
    def addInstruction(self,instr):     #Operation de base d'ajout d'instructons
        self.listInstruction.append(instr)
        self.listInstructionCount+=1
        
    def get_instruction_counter(self):
        return self.listInstructionCount
    
    def get_instruction_at_index(self,index):
        return self.listInstruction[index]

    def setOnCall(self, val, ident):
        self.onCall = val
        self.calling = ident
        self.nextAddr = -1
        
    def getCalling(self):
        return self.calling
    
    def getNextCallAddr(self):
        self.nextAddr = self.nextAddr + 1
        return self.nextAddr
    
########################################################################
#   POINTS DE GENERATION
########################################################################

#Section de declaration du fichier assembleur
    def beginCompil(self):
        self.addInstruction("global main")
        self.addInstruction("extern printf")
        self.addInstruction("extern scanf")
        self.addInstruction("segment .data")
        self.addInstruction("formatout: db '%d', 10, 0")
        self.addInstruction("formatin: db '%d', 0")
        self.addInstruction("debugPrint: db 'DEBUG POINT', 0")

#Declaration du main 
    def beginProgPrinc(self):
        self.addInstruction("segment .text")
        self.addInstruction("main:")

#Fin de l'assembleur
    def endCompil(self,nVariables):
        nOctetsLiberables = nVariables * 4
        self.addInstruction("add esp,%d" % nOctetsLiberables)
        self.addInstruction("mov eax,1")
        self.addInstruction("mov ebx,0")
        self.addInstruction("int 80h")
        
    def debutDeclaLocVars(self):    
        self.addInstruction("pop edx")      #On pop l'adresse de retour dans edx
        
    def declaNLocVar(self, nVar):
        for i in range(nVar):
            self.addInstruction("push 0")

    def debutProc(self):
        self.addInstruction("push edx")     #on rempile l'adresse de retour
        self.addInstruction("push ebp")     
        self.addInstruction("mov ebp,esp")
    
    def affectInstr(self,adresseIdent,totalAdresse):
        self.addInstruction("pop eax")                              #On pop la valeur a affecter
        adresse = ((totalAdresse - adresseIdent + 1) * 4);          #Dans la pile on a: (de maniere decroissante) Les adresses d'arguments, puis les adresse locales
        self.addInstruction("mov dword[ebp + %d],eax" % adresse)
     
    def affectInstrInOut(self,adresseIdent,totalAdresse):
        self.addInstruction("pop ebx")                              #On pop la valeur a affecter
        adresse = ((totalAdresse - adresseIdent + 1) * 4);          #Dans la pile on a: (de maniere decroissante) Les adresses d'arguments, puis les adresse locales
        self.addInstruction("mov eax, dword[ebp + %d]" % adresse)
        self.addInstruction("mov dword[eax],ebx")

####Operations logique Binaire    
    def orInstr(self):              #Instruction ou
        self.addInstruction("pop ebx")
        self.addInstruction("pop eax")
        self.addInstruction("mov ecx,1")
        self.addInstruction("add eax,ebx")
        self.addInstruction("cmp eax,0")
        self.addInstruction("cmovg eax,ecx")
        self.addInstruction("push eax")
        
    def andInstr(self):             #Instruction et
        self.addInstruction("pop ebx")
        self.addInstruction("pop eax")
        self.addInstruction("mov ecx,1")
        self.addInstruction("mul ebx")
        self.addInstruction("cmp eax,0")
        self.addInstruction("cmovne eax,ecx")
        self.addInstruction("push eax")
        
    def opRelInstr(self,opRel):     #Operation de comparaison (opRel)
        self.addInstruction("pop ebx")
        self.addInstruction("pop eax")
        self.addInstruction("mov ecx,1")
        self.addInstruction("cmp eax,ebx")
        self.addInstruction("mov eax,0")        
        self.addInstruction("cmov%s eax,ecx" % str(opRel))
        self.addInstruction("push eax")
    

#####Operations arithmetique####
    #Suivant (opArith)
    def opArithAddInstr(self,opArith):  #Operation de somme    
        self.addInstruction("pop ebx")
        self.addInstruction("pop eax")
        self.addInstruction("%s eax,ebx" % str(opArith))
        self.addInstruction("push eax")
        
    def opArithMulInstr(self,opArith):  #Operation de multiplication 
        self.addInstruction("pop ebx")
        self.addInstruction("pop eax")
        self.addInstruction("%s ebx" % str(opArith))
        self.addInstruction("push eax")
    

#####Operations Unaire (opUN)####
    def opUnaireInstr(self,opUn):
        if opUn == "neg":     
            self.addInstruction("pop eax")
            self.addInstruction("neg eax")
            self.addInstruction("push eax")
        else:
            self.addInstruction("pop eax")
            self.addInstruction("mov ebx,1")
            self.addInstruction("mov ecx,0")
            self.addInstruction("cmp eax,0")
            self.addInstruction("cmovg eax,ecx")
            self.addInstruction("cmovle eax,ebx")
            self.addInstruction("push eax")

    def identInstrIn(self,adresseIdent, totalAdresse, mode):    #Rajout d'un identificateur en mode IN
        adresse = ((totalAdresse - adresseIdent + 1) * 4);
        if self.onCall == 1:									#Si on est en appel de fonction / procedure
            if mode == "inout":									#Selon le mode de reception
                self.addInstruction("lea eax,[ebp + %d]" % adresse)		#On envoie l'adresse
                self.addInstruction("push eax")
            else :
                self.addInstruction("push dword[ebp + %d]" % adresse)	#Ou on envoie la valeur directement
        else:
            self.addInstruction("push dword[ebp + %d]" % adresse)

    def identInstrInOut(self,adresseIdent, totalAdresse, mode):    #Rajout d'un identificateur en mode INOUT
        adresse = ((totalAdresse - adresseIdent + 1) * 4);
        if self.onCall == 1:
            if mode == "inout":											#Selon le mode de reception
                self.addInstruction("push dword[ebp + %d]" % adresse)	#On envoie la valeur (on est en inout, la valeur directe est l'adresse de la case reelle)
            else :
                self.addInstruction("mov eax, dword[ebp + %d]" % adresse)	#Ou on envoie la valeur de la case
                self.addInstruction("push dword[eax]")
        else:
            self.addInstruction("mov eax, dword[ebp + %d]" % adresse)
            self.addInstruction("push dword[eax]")
        
    def entierInstr(self,entier):   #Ajout d'un entier dans la pile
        self.addInstruction("push %s" % str(entier))
        
    def boolInstr(self,booleen):    #Test sur un booleen, 0 dans la pile si booleen faux, 1 sinon
        if booleen == "true":
            self.addInstruction("push 1")
        else:
            self.addInstruction("push 0")
    
    def esGetInstr(self,adresseIdent,totalAdresse):     #Instruction GET
        adresse = ((totalAdresse - adresseIdent + 1) * 4);
        self.addInstruction("lea eax, [ebp + %d]" % adresse)
        self.addInstruction("push eax")
        self.addInstruction("push dword formatin")
        self.addInstruction("call scanf")
        self.addInstruction("add esp,8")
        
    def esPutInstr(self):                               #Instruction PUT
        self.addInstruction("push dword formatout")
        self.addInstruction("call printf")
        self.addInstruction("add esp,8")


#####Boucle While#####        
    def whileInit(self):                        #Initialisation                                
        xxx = self.listInstructionCount             #On utilise le numero de ligne pour generer des labels
        self.addInstruction("l%s:" % str(xxx))      #On genere un label pour le retour de boucle
        return xxx                                  #On retourne le label ou se branchera le retour de boucle
    
    def whileCond(self):                        #Test de la condition
        self.addInstruction("pop eax")
        self.addInstruction("cmp eax,1")
        yyy = self.listInstructionCount             #On utilise le numero de ligne pour generer des labels
        self.addInstruction("jne l%s" % str(yyy))   #(jne <==> branchement si !=) 
        return yyy                                  #On retourne le label ou se branchera le echec de condition de boucle
    
    def whileEnd(self,xxx, yyy):                #Fin de la boucle #### Param: xxx est le label de retour en boucle // yyy: est le label de sortie de boucle
        self.addInstruction("jmp l%s" % str(xxx))   #On retourne en boucle
        self.addInstruction("l%s:" % str(yyy))      #Label de branchement pour la sortie de boucle


#####If (Then Else)        
    def ifInit(self):                               #Initialisation
        self.addInstruction("pop eax")
        self.addInstruction("cmp eax,1")
        xxx = self.listInstructionCount             #On utilise le numero de ligne pour generer des labels differents
        self.addInstruction("jne l%s" % str(xxx))   #On genere un label pour le retour de boucle
        return xxx                                  #retourne le label ou le If se branchera
    
    def ifCondElse(self,xxx):                       #Param: xxx est le "label" sur lequel le If se branchera 
        yyy = self.listInstructionCount
        self.addInstruction("jmp l%s" % str(yyy))   #Si la condition du If == True, jump hors du else
        self.addInstruction("l%s:" % str(xxx))      #Sinon, point de branchement du If si la condition a echouer
        return yyy                                  #Retourne le label ou le else se branchera
        
    def ifEnd(self,yyy):                            #Param: yyy est le "label" sur lequel le Else/If se branchera
        self.addInstruction("l%s:" % str(yyy))      #Point de branchement du else/If

#Fonctions pour NNP

    def retour(self, label, isFonction):
        if isFonction == 1:
            self.addInstruction("pop eax")
        self.addInstruction("leave")
        self.addInstruction("ret")
        self.addInstruction('l%s :' % label)


    # Point de generation pour l'appel a une fonction ou une procedure
    #
    # ident identificateur du fonction ou de la procedure a appeler
    def callIdent(self, ident, isFonction, nParam):
        self.addInstruction("call %s" % str(ident))
        totalOctets = nParam * 4
        self.addInstruction("add esp,%d" % totalOctets)
        if isFonction == 1:
            self.addInstruction("push eax")


    # Point de generation de nettoyage la pile apres l'appel a chaque procedure
    #
    # nbArgLoc le nombre d'arguments et de variables locales de la procedure dont on sort
    def nettoyageApresAppel(self, nbArgLoc):
        nbOctetsANettoyer = nbArgLoc*4
        self.addInstruction("add esp,%d" % nbOctetsANettoyer) # on remet le pointeur avant tous les arguments
        # il faudra appeler get_Total_Adresse(parent) pour avoir le nb total de variables locales + arguments, le parent etant l'ident de la fonction appelee

    # Point de generation mettant l'identificateur avant la definition de la procedure correspondante
    #
    # ident identificateur de la procedure a definir
    def saveIdent(self, ident):
        label = self.listInstructionCount
        self.addInstruction('jmp l%s' % label)
        self.addInstruction('%s :' % ident)
        return label

    # En python dans anasyn : penser a mettre un boolean "fonction" a true ou a false.
    # appelProcedure, puis callIdent, puis debutProc
    #
    #Mettre les appels aux points de generation dans anasyn.py
    #
