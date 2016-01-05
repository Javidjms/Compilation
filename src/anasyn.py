#!/usr/bin/python

##	 @package anasyn
#	 Syntactical Analyser package.
#

import sys, argparse, re
import logging

import analex
import codgen

logger = logging.getLogger('anasyn')

DEBUG = False
LOGGING_LEVEL = logging.DEBUG

class TableIdent(object):

    cpt_varprocglobal = 0
    nomProcPrinc = ""
    nomProcActu = ""
    cpt_var = 0
    cpt_varspecif = 0
    table_Identificateurs = list()
    ligne = list()
    listTemp = list()
    remplissageListTemp = False
    listTempIndex = -1
    expression = False
    
    def __init__(self,ident):
        self.nomProcPrinc = ident
        self.nomProcActu = ident
        self.ligne = [ident,None,0,None,"Procedure",None]
        (self.table_Identificateurs).append(self.ligne)
        self.ligne = [None,None,None,None,None,None]

    def _set_ligne(self,index,val):
        self.ligne[index]=val

    def _init_ligne(self):
        self.ligne = [None,None,None,None,None,None]

    def _ajouterLigne(self):
        self.table_Identificateurs.append(self.ligne)
        self.ligne = [None,None,None,None,None,None]

    def _set_procActu(self,ident):
        self.nomProcActu = ident

    def _get_procActu(self):
        return self.nomProcActu

    def _set_procPrinc(self,ident):
        self.nomProcPrinc = ident

    def _get_procPrinc(self):
        return self.nomProcPrinc

    def _incrVarProcGlobal(self):
        self.cpt_varprocglobal +=1

    def _get_varProcGlobal(self):
        return self.cpt_varprocglobal

    def _incrCptVar(self):
        self.cpt_var += 1

    def _initCptVar(self):
        self.cpt_var = 0

    def _get_CptVar(self):
        return self.cpt_var

    def _incrCptVarProcGlobal(self):
        self.cpt_varprocglobal += 1

    def _incrCptVarSpecif(self):
        self.cpt_varspecif += 1

    def _initCptVarSpecif(self):
        self.cpt_varspecif = 0

    def _get_CptVarSpecif(self):
        return self.cpt_varspecif

    def _setElemLigne(self,elem,numLigne,index):
        self.table_Identificateurs[numLigne][index]=elem

    def _get_ligne(self,index):
        return self.ligne[index]

    def _get_tailleTable(self):
        return len(self.table_Identificateurs)

    def affichage(self):
        for ligne in self.table_Identificateurs:
        	print ligne
    
    ## Liste temporaire pour verifier la liste des parametres insere lors d'un appel de fonction ou procedure
    def _debutremplirListParam(self):
    	self.remplissageListTemp = True
    	self.listTemp.append([])
    	self.listTempIndex+=1
    	
    def _finremplirListParam(self):
    	self.remplissageListTemp = False
    
    def _supprimerListParam(self):
    	self.listTemp.pop()
    	self.listTempIndex-=1
    
    def _getListTemp(self):
    	return self.listTemp[self.listTempIndex]
    
    def _getRemplissage(self):
    	return self.remplissageListTemp
    	
    def _remplir(self,liste):
    	if(self._getRemplissage() and not self._getExpression()):
    		self.listTemp[self.listTempIndex].append(liste)

    ##is_Ident
    #Return boolean , Vrai si identificateur deja dans la table, faux sinon
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def is_Ident(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return True
    	return False

    ##get_Ident_Type
    #Return type? , Retourne le type de l'identificateur (prerequis: l'ident doit etre present dans la table)
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def get_Ident_Type(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[1]

    ##get_Ident_Mode
    #Return mode? , Retourne le mode de l'identificateur (prerequis: l'ident doit etre present dans la table)
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def get_Ident_Mode(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[5]
			
	##get_Ident_Target_Mode
    #Return mode? , Retourne le mode de l'identificateur pour la fonction cible (prerequis: l'ident doit etre present dans la table)
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def get_Ident_Target_Mode(self,addr,cible):
    	for ligne in self.table_Identificateurs:
    		if ligne[2]==addr and ligne[3]==cible:
    			return ligne[5]
			
    ##is_Fonction
    #Return boolean , Vrai si l'ident est une fonction, faux sinon
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def is_Fonction(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[4]=="Fonction"
    	return False

    ##is_Procedure
    #Return boolean , Vrai si l'ident est une procedure, faux sinon
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def is_Procedure(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[4]=="Procedure"
    	return False

    ##is_Parametre
    #Return boolean , Vrai si l'ident est un parametre, faux sinon
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def is_Parametre(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[4]=="Parametre"
    	return False

    ##is_Variable
    #Return boolean , Vrai si l'ident est une variable, faux sinon
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def is_Variable(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[4]=="Variable"
    	return False

    ##get_Ident_Adresse
    #Return adresse , Retourne l'adresse de l'identificateur (prerequis: l'ident doit etre present dans la table)
    ####Param:#####
    #ident		 identificateur a tester
    #parent	 ident de la procedure appeller
    def get_Ident_Adresse(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[2]

    ##get_Total_Adresse
    #Return int, Retourne le nombre d'identificateur liee au parent
    ####Param:#####
    #parent	 ident de la procedure appeller
    def get_Total_Adresse(self,parent):
    	total = 0
    	for ligne in self.table_Identificateurs:
    		if ligne[3]==parent:
    			total = total + 1
    	return total
    	
	##get_Total_Param
    #Return int, Retourne le nombre de parametres liee a l'identificateur
    ####Param:#####
    #parent	 ident de la procedure appeller
    def get_Total_Param(self,parent):
    	total = 0
    	for ligne in self.table_Identificateurs:
    		if ligne[3]==parent:
		        if self.is_Parametre(ligne[0], parent):
        			total = total + 1
    	return total
    	
        #Retourne les lignes du tableau d'identificateur de l'ident (fonction ou procedure)
    def get_Table_FP(self,ident):
    	table = []
    	for ligne in self.table_Identificateurs:
    		if ligne[3]==ident:
    			table.append(ligne)
    	return table
    	
    	#Retourne le type de structure de l'ident : parametre, fonction,type
    def get_Ident_Structure(self,ident,parent):
    	for ligne in self.table_Identificateurs:
    		if ligne[0]==ident and ligne[3]==parent:
    			return ligne[4]

    def _debutexpression(self):
    	self.expression = True
    	
    def _finexpression(self):
    	self.expression = False
    	
    def _getExpression(self):
    	return self.expression

class AnaSynException(Exception):
	def __init__(self, value):
		self.value = value
	def __str__(self):
				return repr(self.value)

########################################################################
#### Syntactical Diagrams ####
########################################################################


#Fonction d'erreur semantique
#Affiche un message d'erreur et indique la ligne et la colonne de l'erreur
def ErreurSemantique(lexical_analyser,message):
	lineIndex=lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index].get_line_index()+1
	colIndex =lexical_analyser.lexical_units[lexical_analyser.lexical_unit_index].get_col_index()+1
	msg = "ligne "+str(lineIndex)+" colonne "+str(colIndex)+" :"+message
	logger.error(msg)
	sys.exit(0)

####################################################
#Format du tableau
# 0 | 1  | 2     |  3   |  4   |  5
#Nom|Type|Adresse|Parent|Status|Mode(in,inout)
####################################################

codeGenerator = codgen.CodeGenerator()

#program
def program(lexical_analyser):

	global table_Identificateurs	#	Import de la table des Id
	codeGenerator.beginCompil()		# //Point de generation\\ Initialisation de la compilation

### [specifProgPrinc] (is) [corpsProgPrinc] ###
	specifProgPrinc(lexical_analyser)		#	[specifProgPrinc]
	lexical_analyser.acceptKeyword("is")	#	(is)
	corpsProgPrinc(lexical_analyser)		#	[corpsProgPrinc]
	

#specifProgPrinc
def specifProgPrinc(lexical_analyser):

### (procedure) (identificateur) ###
	lexical_analyser.acceptKeyword("procedure")	#	(procedure)
	ident = lexical_analyser.acceptIdentifier() #	(ident) On conserve dans ident l'identificateur de la procedure

	##Code Edern Rivoallan & Didier Fromont##
	global tableIdent
	tableIdent = TableIdent(ident)
	tableIdent.affichage()
	logger.debug("Name of program : "+ident) 	#	Debug
	return ident 								#	On retourne l'identificateur de la procedure principale


#corpsProgPrinc
def  corpsProgPrinc(lexical_analyser):
	global tableIdent
	codeGenerator.beginProgPrinc()									#	Generation du code du debut de programme
	codeGenerator.debutDeclaLocVars()		#	Reservation de l'espace pour les variables locales du programme principal

	if not lexical_analyser.isKeyword("begin"):
		logger.debug("Parsing declarations")
		partieDecla(lexical_analyser)
		logger.debug("End of declarations")
	lexical_analyser.acceptKeyword("begin")

	codeGenerator.debutProc()
	tableIdent._set_procActu(tableIdent._get_procPrinc())

	if not lexical_analyser.isKeyword("end"):	#	Flag de direction (!end)
		logger.debug("Parsing instructions")	#	Debug
		suiteInstr(lexical_analyser)			#	[suiteInstr]
		logger.debug("End of instructions")		#	Debug

	lexical_analyser.acceptKeyword("end")		#	(end)

	codeGenerator.endCompil(tableIdent.get_Total_Adresse(tableIdent._get_procActu()))			#	Generation du code pour la fin du programme

	lexical_analyser.acceptFel()				#	(.)
	logger.debug("End of program")				#	Debug



#partieDecla
def partieDecla(lexical_analyser):
### [listeDeclaOp] [listeDeclaVar] ###
###	[listedeclaOp] --------------- ###
### [listeDeclaVar] -------------- ###
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :	#	Flag de directions (procedure||function)
		listeDeclaOp(lexical_analyser)														#	[listeDeclaOp]
		if not lexical_analyser.isKeyword("begin"):											#	Flag de dircetion (!begin)
			listeDeclaVar(lexical_analyser)													#	[listeDeclaVar]

	else:
		listeDeclaVar(lexical_analyser)														#	[listeDeclaVar]



#listeDeclaOp
def listeDeclaOp(lexical_analyser):
###	[declaOp] (;) [listeDeclaOp] ###
###	[declaOp] (;) -------------- ###
	declaOp(lexical_analyser)																#	[declaOp]
	lexical_analyser.acceptCharacter(";")													#	(;)
	if lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function") :	#	Flag de direction (procedure||function)
		listeDeclaOp(lexical_analyser)														#	[listeDeclaOp]



#declaOp
def declaOp(lexical_analyser):
### [function]  ###
### [procedure] ###
	if lexical_analyser.isKeyword("procedure"):		#	Flag de direction (procedure)
		procedure(lexical_analyser)					#	[procedure]
	if lexical_analyser.isKeyword("function"):		#	Flag de direction (function)
		fonction(lexical_analyser)					#	[fonction]


#procedure
### (procedure) (ident) [partieFormelle] (is) [corpsProc] ###
def procedure(lexical_analyser):
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()

	##Code Edern Rivoallan & Didier Fromont##
    global tableIdent
    tableIdent._set_ligne(4,"Procedure")
    tableIdent._set_ligne(3,tableIdent._get_procPrinc())
    tableIdent._set_ligne(2,tableIdent._get_varProcGlobal())
    tableIdent._incrVarProcGlobal()
    tableIdent._set_procActu(ident)
    tableIdent._set_ligne(0,ident)
    tableIdent._set_ligne(1,None)
    tableIdent._ajouterLigne()
	#########################################

    labelXXX = codeGenerator.saveIdent(ident)

    logger.debug("Name of procedure : "+ident)

    partieFormelle(lexical_analyser)

    lexical_analyser.acceptKeyword("is")
    corpsProc(lexical_analyser)

    codeGenerator.retour(labelXXX, tableIdent.is_Fonction(ident, tableIdent._get_procPrinc()))

	##Code Edern Rivoallan & Didier Fromont##
    tableIdent._set_procActu(tableIdent._get_procPrinc())
	#########################################

#fonction
def fonction(lexical_analyser):
    lexical_analyser.acceptKeyword("function")
    ident = lexical_analyser.acceptIdentifier()
    logger.debug("Name of function : "+ident)

	##Code Edern Rivoallan & Didier Fromont##
    global tableIdent
    tableIdent._set_procActu(ident)
	#########################################

    labelXXX = codeGenerator.saveIdent(ident)


    partieFormelle(lexical_analyser)

    lexical_analyser.acceptKeyword("return")
    vtype1=nnpType(lexical_analyser)

	##Code Edern Rivoallan & Didier Fromont##

    tableIdent._set_ligne(4,"Fonction")
    tableIdent._set_ligne(3,tableIdent._get_procPrinc())
    tableIdent._set_ligne(2,tableIdent._get_varProcGlobal())
    tableIdent._incrVarProcGlobal()
    tableIdent._set_ligne(0,tableIdent._get_procActu())
    tableIdent._ajouterLigne()
	#########################################

    lexical_analyser.acceptKeyword("is")
    vtype2=corpsFonct(lexical_analyser)

    if vtype2==None:
        ErreurSemantique(lexical_analyser,"La fonction doit avoir au moins retourner quelque chose")
    elif vtype1 != vtype2:
        ErreurSemantique(lexical_analyser,"La fonction doit retourner le bon type")

    codeGenerator.retour(labelXXX, tableIdent.is_Fonction(ident, tableIdent._get_procPrinc()))

	##Code Edern Rivoallan & Didier Fromont##
    tableIdent._set_procActu(tableIdent._get_procPrinc()) #	On retourne dans la procedure principale => elle deviens la procedure actuelle
	#########################################


#corpsProc
def corpsProc(lexical_analyser):
### [partieDeclaProc] (begin) [suiteInstr] (end) ###
### ----------------- (begin) [suiteInstr] (end) ###
	codeGenerator.debutDeclaLocVars()
	if not lexical_analyser.isKeyword("begin"):		#	Flag de direction (!begin)
		partieDeclaProc(lexical_analyser)			#	[partieDeclaProc]
	lexical_analyser.acceptKeyword("begin")			#	(begin)
	codeGenerator.debutProc()
	suiteInstr(lexical_analyser)					#	[suiteInstr]
	lexical_analyser.acceptKeyword("end")			#	(end)

#corpsFonct
def corpsFonct(lexical_analyser):
###	[partieDeclaProc] (begin) [suiteinstrNonVide] (end) ###
### ----------------- (begin) [suiteinstrNonVide] (end) ###
	codeGenerator.debutDeclaLocVars()
	if not lexical_analyser.isKeyword("begin"):		#	Flag de direction (!begin)
		partieDeclaProc(lexical_analyser)			#	[partieDeclProc]
	lexical_analyser.acceptKeyword("begin")			# 	(begin)
	codeGenerator.debutProc()
	vtype=suiteInstrNonVide(lexical_analyser)		#	[suiteInstrNonVide]
	lexical_analyser.acceptKeyword("end")			#	(end)
	return vtype 									#	on retourne le type de retour de la suite d'instruction


#partieFormelle
def partieFormelle(lexical_analyser):
### (() [listeSpecifFormelles] ()) ###
### (() ---------------------- ()) ###
	##Code Edern Rivoallan & Didier Fromont##
	global tableIdent
	tableIdent._initCptVar() #	Compteur de variable locale
	#########################################
	lexical_analyser.acceptCharacter("(")			#	(()
	if not lexical_analyser.isCharacter(")"):		#	Flag de direction (!))
		listeSpecifFormelles(lexical_analyser)		#	[listeSpecifFormelles]
	lexical_analyser.acceptCharacter(")")			#	())


#listeSpecifFormelles
def listeSpecifFormelles(lexical_analyser):
###	[specif] (;) [listeSpecifFormelles] ###
###	[specif] --- ---------------------- ###
	specif(lexical_analyser)						#	[specif]
	if not lexical_analyser.isCharacter(")"):		#	Flag de direction (!))
		lexical_analyser.acceptCharacter(";")		#	(;)
		listeSpecifFormelles(lexical_analyser)		#	[listeSpecifFormelles]


#specif
def specif(lexical_analyser):
###	[listeIndent] (:) [mode] [type] ###
###	[listeIndent] (:) ------ ------ ###
	##Code Edern Rivoallan & Didier Fromont##
    global tableIdent
    tableIdent._initCptVarSpecif()
	#########################################

    listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")

    tableIdent._set_ligne(5,"in")
	#########################################

    if lexical_analyser.isKeyword("in"):
        mode(lexical_analyser)

    nnpType(lexical_analyser)

	##Code Edern Rivoallan & Didier Fromont##
    for i in range(0,tableIdent._get_CptVarSpecif()):
        tableIdent._setElemLigne(tableIdent._get_ligne(1),(tableIdent._get_tailleTable()-i-1),1)
        tableIdent._setElemLigne(tableIdent._get_ligne(5),(tableIdent._get_tailleTable()-i-1),5)
        tableIdent._setElemLigne("Parametre",(tableIdent._get_tailleTable()-i-1),4)
    tableIdent._init_ligne()
	#########################################


#mode
def mode(lexical_analyser):
### (in) (out) ###
### (in) ----- ###
	lexical_analyser.acceptKeyword("in")			#	(in)
	if lexical_analyser.isKeyword("out"):			#	Flag de redirection (out)
		lexical_analyser.acceptKeyword("out")		#	(out)
	##Code Edern Rivoallan & Didier Fromont##
		global tableIdent
		tableIdent._set_ligne(5,"inout")
	#########################################
		logger.debug("in out parameter")			#	Debug
	else:
	##Code Edern Rivoallan & Didier Fromont##
		tableIdent._set_ligne(5,"in")
	#########################################
		logger.debug("in parameter")				#	Debug


#nnpType
def nnpType(lexical_analyser):
### (integer) ###
### (boolean) ###
	#Importation
	global ligne

	if lexical_analyser.isKeyword("integer"):		#	Flag de redirection (integer)
		lexical_analyser.acceptKeyword("integer")	#	(integer)
	##Code Edern Rivoallan & Didier Fromont##
		global tableIdent
		tableIdent._set_ligne(1,"integer")
	#########################################
		logger.debug("integer type")				#	Debug
		return "integer"							#	Retourne le type

	elif lexical_analyser.isKeyword("boolean"):		#	Flag de redirection (boolean)
		lexical_analyser.acceptKeyword("boolean")	#	(boolean)
	##Code Edern Rivoallan & Didier Fromont##
		tableIdent._set_ligne(1,"boolean")
	#########################################
		logger.debug("boolean type")				#	Debug
		return "boolean"							#	Retourne le type
	## Erreurs
	else:
		logger.error("Unknown type found <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown type found <"+ lexical_analyser.get_value() +">!")


#partieDeclaProc
def partieDeclaProc(lexical_analyser):
### [listeDecVar] ###
	listeDeclaVar(lexical_analyser)					#	[listeDeclaVar]


#listeDeclaVar
def listeDeclaVar(lexical_analyser):
###	[declaVar] [listeDecalVar] ###
###	[declaVar] --------------- ###
	declaVar(lexical_analyser)						#	[declaVar]
	if lexical_analyser.isIdentifier():				#	Flag de redirection (identificateur)
		listeDeclaVar(lexical_analyser)				#	[listeDeclaVar]


#declaVar
def declaVar(lexical_analyser):
### [listeIdent] (:) [type] (;) ###
	##Code Edern Rivoallan & Didier Fromont##
	global tableIdent
	tableIdent._initCptVar()
	#########################################

	nVar = listeIdent(lexical_analyser)				#

	codeGenerator.declaNLocVar(nVar)				#	//Pt de Gen\\ instruction "nVar" nombre de variable ?

	lexical_analyser.acceptCharacter(":")
	logger.debug("now parsing type...")
	nnpType(lexical_analyser)
	##Code Edern Rivoallan & Didier Fromont##
	for i in range(0,tableIdent._get_CptVar()):
		tableIdent._setElemLigne(tableIdent._get_ligne(1),(tableIdent._get_tailleTable()-i-1),1)

	lexical_analyser.acceptCharacter(";")
	tableIdent._init_ligne()
	#########################################


#listeIdent
def listeIdent(lexical_analyser):
	global tableIdent
	procPrinc = tableIdent._get_procPrinc()
	procActu = tableIdent._get_procActu()
	ident = lexical_analyser.acceptIdentifier()
	if (tableIdent.is_Ident(ident,procActu)) or (tableIdent.is_Ident(ident,procPrinc)):
		ErreurSemantique(lexical_analyser,"Double declaration de variable")

	##Code Edern Rivoallan & Didier Fromont##
	if (ident,tableIdent._get_procActu())==(ident,tableIdent._get_procPrinc()) :
		tableIdent._set_ligne(0,ident)
		tableIdent._set_ligne(2,tableIdent._get_varProcGlobal())
		tableIdent._incrCptVarProcGlobal()
		tableIdent._set_ligne(3,tableIdent._get_procPrinc())
		tableIdent._set_ligne(4,"Variable")
		tableIdent._ajouterLigne()
	else :
		tableIdent._set_ligne(0,ident)
		tableIdent._set_ligne(2,tableIdent._get_CptVar())
		tableIdent._set_ligne(3,tableIdent._get_procActu())
		tableIdent._set_ligne(4,"Variable")
		tableIdent._ajouterLigne()

	tableIdent._incrCptVar()
	tableIdent._incrCptVarSpecif()
		#########################################

	logger.debug("identifier found: "+str(ident))		#	Debug

	if lexical_analyser.isCharacter(","):
		lexical_analyser.acceptCharacter(",")
		return listeIdent(lexical_analyser) + 1
	else:
		return 1


#suiteInstrNonVide
def suiteInstrNonVide(lexical_analyser):
### [instr]	(;) [suiteInstrNonVide] ###
### [instr]	--- ------------------- ###
	vtype1=instr(lexical_analyser)						#	[instr]
	if lexical_analyser.isCharacter(";"):				#	Flag de redirection (;)
		lexical_analyser.acceptCharacter(";")			#	(;)
		vtype2=suiteInstrNonVide(lexical_analyser)		#	[suiteInstrNonVide]
		if vtype1!=None and vtype2!=None: 				# Les 2 instructions sont des returns
			if vtype1!=vtype2:
				ErreurSemantique(lexical_analyser,"Les returns doivent etre du meme type 1")
			return vtype2
		elif vtype1!= None:
			return vtype1
		elif vtype2!= None:
			return vtype2
	return vtype1


#suiteInstr
def suiteInstr(lexical_analyser):
### [suiteinstrNonVide] ###
### ------------------- ###
	if not lexical_analyser.isKeyword("end"):			#	Flag de redirection (!end)
		vtype1=suiteInstrNonVide(lexical_analyser)		#	[suiteInstrNonVide]
		return vtype1									#	Retourne le type de la suite


#instr
def instr(lexical_analyser):
### [boucle] ###
### [altern] ###
### [es] ###
### [retour] ###
###	[ident] (:=) [expression] ###
###	[ident] ---- ------------ ###
###	[ident] (() [listePe] ()) ###
##########Edern & Didier###############################
	global tableIdent
	parent = tableIdent._get_procActu()
#########################################

	if lexical_analyser.isKeyword("while"):
		vtype1=boucle(lexical_analyser)
		return vtype1
	elif lexical_analyser.isKeyword("if"):
		vtype2=altern(lexical_analyser)
		return vtype2
	elif lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
		es(lexical_analyser)
	elif lexical_analyser.isKeyword("return"):
		vtype3=retour(lexical_analyser)
		return vtype3
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()

		if lexical_analyser.isSymbol(":="):
			if tableIdent.is_Ident(ident,parent):
				# affectation
				lexical_analyser.acceptSymbol(":=")
				vtype2=expression(lexical_analyser)
				logger.debug("parsed affectation")
				if (tableIdent.get_Ident_Type(ident,parent)) !=vtype2:
					ErreurSemantique(lexical_analyser,"Les variables doivent etre du meme type")
				if tableIdent.is_Parametre(ident,parent):
					if tableIdent.get_Ident_Mode(ident,parent) !="inout":
						ErreurSemantique(lexical_analyser,"Le parametre doit etre du type in out")
					else:
						codeGenerator.affectInstrInOut(tableIdent.get_Ident_Adresse(ident, parent), tableIdent.get_Total_Adresse(parent))
				else:
					codeGenerator.affectInstr(tableIdent.get_Ident_Adresse(ident, parent), tableIdent.get_Total_Adresse(parent))
			else:
				ErreurSemantique(lexical_analyser,"La variable n'est pas bien declare")

		elif lexical_analyser.isCharacter("("):
			parent = tableIdent._get_procPrinc()
			if tableIdent.is_Procedure(ident,parent):
				lexical_analyser.acceptCharacter("(")
				tableIdent._debutremplirListParam()
				codeGenerator.setOnCall(1, ident)
				if not lexical_analyser.isCharacter(")"):
					listePe(lexical_analyser)
				tableIdent._finremplirListParam()
				if len(tableIdent._getListTemp())!=tableIdent.get_Total_Param(ident):
					ErreurSemantique(lexical_analyser,"Nombre de parametre incorrete")
				for i in range(0,len(tableIdent._getListTemp())):
					if tableIdent.get_Table_FP(ident)[i][1] !=tableIdent._getListTemp()[i][1]:
						ErreurSemantique(lexical_analyser,"Type de l'argument "+str(i+1)+" incorrect")
					if tableIdent.get_Table_FP(ident)[i][5] == "inout" and tableIdent._getListTemp()[i][3] != "inout" and tableIdent._getListTemp()[i][2]=="Parametre" :
						ErreurSemantique(lexical_analyser,"Mode de l'argument "+str(i+1)+" incorrect")
				tableIdent._supprimerListParam()
				lexical_analyser.acceptCharacter(")")
				logger.debug("parsed procedure call")
				codeGenerator.setOnCall(0, "")

				codeGenerator.callIdent(ident, tableIdent.is_Fonction(ident, parent), tableIdent.get_Total_Param(ident))
			else:
				ErreurSemantique(lexical_analyser,"Cet identifiant ne correspond pas a une procedure")
		else:
			logger.error("Expecting procedure call or affectation!")
			raise AnaSynException("Expecting procedure call or affectation!")

	else:
		logger.error("Unknown Instruction <"+ lexical_analyser.get_value() +">!")
		raise AnaSynException("Unknown Instruction <"+ lexical_analyser.get_value() +">!")


#listePe
def listePe(lexical_analyser):
### [expression] (,) [listePe] ###
### [expression] --- --------- ###
	if tableIdent._getExpression() :
		tableIdent._finexpression()
	expression(lexical_analyser)						#	[expression]
	if lexical_analyser.isCharacter(","):				#	Flag de redirection (,)
		lexical_analyser.acceptCharacter(",")			#	(,)
		listePe(lexical_analyser)						#	[listePe]


#expression
def expression(lexical_analyser):
### [exp1] (or) [exp1] ###
### [exp1] --- ------- ###
	logger.debug("parsing expression: " + str(lexical_analyser.get_value()))	#	Debug
	vtype1=exp1(lexical_analyser)						#	[exp1]
	if lexical_analyser.isKeyword("or"):				#	Flag de redirection	(or)
		lexical_analyser.acceptKeyword("or")			#	(or)
		tableIdent._debutexpression()
		vtype2=exp1(lexical_analyser)					#	[exp1]

		codeGenerator.orInstr()							#	//Pt de Gen\\ instruction "OU"
		#	Erreurs
		if vtype1!="boolean"!=vtype2:
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre des booleens")
	return vtype1										#	Retourne le type de l'exp1


#exp1
def exp1(lexical_analyser):
### [exp2] (and) [exp2] ###
### [exp2] ----- ------ ###
	logger.debug("parsing exp1")						#	Debug
	vtype1=exp2(lexical_analyser)						#	[exp2]
	if lexical_analyser.isKeyword("and"):				# 	Flag de redirection (and)
		lexical_analyser.acceptKeyword("and")			#	(and)
		tableIdent._debutexpression()
		vtype2=exp2(lexical_analyser)					#	[exp2]

		codeGenerator.andInstr()						#	//Pt de Gen\\ instruction "ET"
		#	Erreur
		if vtype1!="boolean"!=vtype2:
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre des booleens")
	return vtype1										#	Retourne le type de l'exp2


#exp2
def exp2(lexical_analyser):
### [exp3] [opRel] [exp3] ###
### [exp3] ------- ------ ###
	logger.debug("parsing exp2")						#	Debug
	vtype1=exp3(lexical_analyser)						#	[exp3]
	if	lexical_analyser.isSymbol("<") or \
		lexical_analyser.isSymbol("<=") or \
		lexical_analyser.isSymbol(">") or \
		lexical_analyser.isSymbol(">="):				#	Flag de redirection (<||<=||>||>=)
		curOperator = opRel(lexical_analyser)			#	[opRel]
		tableIdent._debutexpression()
		vtype2=exp3(lexical_analyser)					#	[exp3]
		#	Erreurs
		if vtype1!="integer"!=vtype2:
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre des entiers")
		vtype1="boolean"								#	On modifie le type en booelan car l'expression a ete evaluer, et c'est donc le resulat de la condition que l'on obtient
		codeGenerator.opRelInstr(curOperator)			#	//Pt de Gen\\ instruction relationnelle

	elif lexical_analyser.isSymbol("=") or \
		lexical_analyser.isSymbol("/="):				#	Flag de redirection (=||/=)
		curOperator = opRel(lexical_analyser)			#	[opRel]
		tableIdent._debutexpression()
		vtype2=exp3(lexical_analyser)					#	[exp3]
		#	Erreurs
		if vtype1!=vtype2:
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre du meme types")
		vtype1="boolean"								#	Idem que dessus
		codeGenerator.opRelInstr(curOperator)			#	//Pt de Gen\\ instruction "relationelle"
	return vtype1										# 	Retourne le type de exp3


#opRel
def opRel(lexical_analyser):
### (=) ###
### (/=) ###
### (<) ###
### (<=) ###
### (>) ###
### (>=) ###
	logger.debug("parsing relationnal operator: " + lexical_analyser.get_value())	#	Debug
	if	lexical_analyser.isSymbol("<"):					#	Flag de redirection (<)
		lexical_analyser.acceptSymbol("<")				#	(<)
		return "l"										#	Retourne un code correspondant a <

	elif lexical_analyser.isSymbol("<="):				#	Flag de redirection (<=)
		lexical_analyser.acceptSymbol("<=")				#	(<=)
		return "le"										#	Retourne un code correspondant a <=

	elif lexical_analyser.isSymbol(">"):				#	Flag de redirection (>)
		lexical_analyser.acceptSymbol(">")				#	(>)
		return "g"										#	Retourne un code correspondant a >

	elif lexical_analyser.isSymbol(">="):				#	Flag de redirection (>=)
		lexical_analyser.acceptSymbol(">=")				#	(>=)
		return "ge"										#	Retourne un code correspondant a >=

	elif lexical_analyser.isSymbol("="):				#	Flag de redirection (=)
		lexical_analyser.acceptSymbol("=")				#	(=)
		return "e"										#	Retourne un code correspondant a =

	elif lexical_analyser.isSymbol("/="):				#	Flag de redirection (/=)
		lexical_analyser.acceptSymbol("/=")				#	(/=)
		return "ne"										#	Retourne un code correspondant a /=
	#	Erreurs
	else:
		msg = "Unknown relationnal operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)


#exp3
def exp3(lexical_analyser):
### [exp4] [opAd] [exp4] ###
### [exp4] ------ ------ ###
	logger.debug("parsing exp3")						#	Debug
	vtype1=exp4(lexical_analyser)						#	[exp4]
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):	#	Flag de redirection (+||-)
		curOpAdd = opAdd(lexical_analyser)				#	[opAd]
		tableIdent._debutexpression()
		vtype3=exp4(lexical_analyser)					#	[exp4]
		#	Erreurs
		if vtype1!=vtype3:
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre des entiers")

		codeGenerator.opArithAddInstr(curOpAdd)				#//Pt de Gen\\ instruction arithmetique
	return vtype1

#opAdd
def opAdd(lexical_analyser):
### (+) ###
###	(-) ###
	logger.debug("parsing additive operator: " + lexical_analyser.get_value())	#	debug
	if lexical_analyser.isCharacter("+"):				#	Flad de redirection (+)
		lexical_analyser.acceptCharacter("+")			#	(+)
		return "add"									#	retour du code "add"

	elif lexical_analyser.isCharacter("-"):				#	Flag de redirection (-)
		lexical_analyser.acceptCharacter("-")			#	(-)
		return "sub"									# 	retour du code "sub"
	else:												#	Autrement erreur
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

#exp4
def exp4(lexical_analyser):
###	[prim] [opMult] [prim] ###
### [prim] -------- ------ ###
	logger.debug("parsing exp4")						#	debug
	vtype1=prim(lexical_analyser)						#	[prim]
	if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"): 	#	Flag de redirection (*||/)
 		curOpMult = opMult(lexical_analyser)			#	[opMult]
		tableIdent._debutexpression()
		vtype3=prim(lexical_analyser)					#	[prim]
		if vtype1!=vtype3:								#	verif semantique des operandes
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre des entiers")
		codeGenerator.opArithMulInstr(curOpMult)						#//Pt de Gen\\	Generation d'une instruction multiplicative
	return vtype1

#opMult
def opMult(lexical_analyser):
###	(*) ###
###	(/) ###
	logger.debug("parsing multiplicative operator: " + lexical_analyser.get_value())	#	debug
	if lexical_analyser.isCharacter("*"):				#	Flag de redirection (*)
		lexical_analyser.acceptCharacter("*")			#	(*)
		return "mul"									# 	retour du code "mul" pour la multiplication

	elif lexical_analyser.isCharacter("/"):				#	Flag de redirection (/)
		lexical_analyser.acceptCharacter("/")			#	(/)
		return "div"									# 	retour du code "div" pour la division 

	else:												#	Erreur
		msg = "Unknown multiplicative operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)

#prim
def prim(lexical_analyser):
###	(opUnaire) [elemPrim] ###
### ---------- [elemPrim] ###
	logger.debug("parsing prim")						#	debug
	curOpUn = "nop"								
	if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-") or lexical_analyser.isKeyword("not"):		#	Flag de redirection (+||-||not)
		vtypeUnaire=opUnaire(lexical_analyser)			#	[opUnaire]	
		curOpUn = vtypeUnaire[0]
		vtype1 = vtypeUnaire[1]
		vtype2=elemPrim(lexical_analyser)				#	[elemPrim]
		if vtype1!=vtype2:								#	Erreur: opUnaire ne correspondant pas a un elemUnaire
			ErreurSemantique(lexical_analyser,"Les operandes doivent etre du meme types")
		if curOpUn == "neg" or curOpUn == "not":		
			codeGenerator.opUnaireInstr(curOpUn)		#//Pt de Gen\\ 	Generation d'une instruction unaire
	else:
		vtype2=elemPrim(lexical_analyser)				#	[elemPrim]
	return vtype2

#opUnaire
def opUnaire(lexical_analyser):
###	(+)   ###
###	(-)   ###
###	(not) ###
	logger.debug("parsing unary operator: " + lexical_analyser.get_value())		#
	if lexical_analyser.isCharacter("+"):				#	Flag de redirection (+)
		lexical_analyser.acceptCharacter("+")			#	(+)
		vtype = ("nop", "integer")						

	elif lexical_analyser.isCharacter("-"):				#	Flag de redirection (-)
		lexical_analyser.acceptCharacter("-")			#	(-)
		vtype = ("neg", "integer")

	elif lexical_analyser.isKeyword("not"):				#	Flag de redirection (not)
		lexical_analyser.acceptKeyword("not")			#	(not)
		vtype = ("not", "boolean")

	else:					#	Erreur
		msg = "Unknown additive operator <"+ lexical_analyser.get_value() +">!"
		logger.error(msg)
		raise AnaSynException(msg)
	return vtype

#elemPrim
def elemPrim(lexical_analyser):
###	[valeur] ###
### (() [expression] ()) ###
### [ident] (() [listePe] ()) ###
### [ident] --- --------- --- ###
	global tableIdent
	parent = tableIdent._get_procActu()
	logger.debug("parsing elemPrim: " + str(lexical_analyser.get_value()))
	if lexical_analyser.isCharacter("("):
		lexical_analyser.acceptCharacter("(")
		tableIdent._debutexpression()
		vtype=expression(lexical_analyser)
		lexical_analyser.acceptCharacter(")")
	elif lexical_analyser.isInteger() or lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
		value=lexical_analyser.get_value()
		vtype=valeur(lexical_analyser)
		tableIdent._remplir([value,vtype,"Constante","None"])
	elif lexical_analyser.isIdentifier():
		ident = lexical_analyser.acceptIdentifier()
		if(tableIdent.is_Fonction(ident,tableIdent._get_procPrinc()) or tableIdent.is_Procedure(ident,tableIdent._get_procPrinc())):	#	type de l'identifiant pour verification
			parent=tableIdent._get_procPrinc()
			vtype= tableIdent.get_Ident_Type(ident,parent)
			value= ident+"()"
			mode = tableIdent.get_Ident_Mode(ident,parent)
		else:
			parent=tableIdent._get_procActu()
			vtype= tableIdent.get_Ident_Type(ident,parent)
			value= ident
			mode = tableIdent.get_Ident_Mode(ident,parent)
		struct=tableIdent.get_Ident_Structure(ident,parent)
		tableIdent._remplir([value,vtype,struct,mode])
		if vtype!=None:
			if lexical_analyser.isCharacter("("):			# Appel fonct
				lexical_analyser.acceptCharacter("(")
				tableIdent._debutremplirListParam()
				codeGenerator.setOnCall(1, ident)
				if not lexical_analyser.isCharacter(")"):
					listePe(lexical_analyser)
				tableIdent._finremplirListParam()
				if len(tableIdent._getListTemp())!=tableIdent.get_Total_Param(ident):
					ErreurSemantique(lexical_analyser,"Nombre de parametre incorrete")
				for i in range(0,len(tableIdent._getListTemp())):
					if tableIdent.get_Table_FP(ident)[i][1] !=tableIdent._getListTemp()[i][1]:
						ErreurSemantique(lexical_analyser,"Type de l'argument "+str(i+1)+" incorrect")
					if tableIdent.get_Table_FP(ident)[i][5] == "inout" and tableIdent._getListTemp()[i][3] != "inout" and tableIdent._getListTemp()[i][2]=="Parametre" :
						ErreurSemantique(lexical_analyser,"Mode de l'argument "+str(i+1)+" incorrect")
				tableIdent._supprimerListParam()
				lexical_analyser.acceptCharacter(")")
				logger.debug("parsed procedure call")
				codeGenerator.setOnCall(0, "")

				logger.debug("Call to function: " + ident)
				codeGenerator.callIdent(ident, tableIdent.is_Fonction(ident, tableIdent._get_procPrinc()), tableIdent.get_Total_Param(ident))
			else:
				logger.debug("Use of an identifier as an expression: " + ident)
				if tableIdent.get_Ident_Mode(ident,parent) == "inout":
					codeGenerator.identInstrInOut(tableIdent.get_Ident_Adresse(ident,parent),tableIdent.get_Total_Adresse(parent), tableIdent.get_Ident_Target_Mode(codeGenerator.getNextCallAddr(),codeGenerator.getCalling()))						#Generation d'une instruction de recuperation d'identifiant
				else:
					codeGenerator.identInstrIn(tableIdent.get_Ident_Adresse(ident,parent),tableIdent.get_Total_Adresse(parent), tableIdent.get_Ident_Target_Mode(codeGenerator.getNextCallAddr(),codeGenerator.getCalling()))					#Generation d'une instruction de recuperation d'identifiant
		else:
			ErreurSemantique(lexical_analyser,"La variable n'a pas ete declare")	
	else:
		logger.error("Unknown Value!")
		raise AnaSynException("Unknown Value!")
	return vtype

#valeur
def valeur(lexical_analyser):
### [entier]  ###
### [valBool] ###
	if lexical_analyser.isInteger():					#	Flag de redirection (entier)
		entier = lexical_analyser.acceptInteger()		#	[entier]
		codeGenerator.entierInstr(entier)				#//Pt de Gen\\ 	Generation d'un entier
		if codeGenerator.onCall == 1:
			codeGenerator.getNextCallAddr()
		logger.debug("integer value: " + str(entier))	#	debug
		return "integer"								#	retour du code "integer" pour signifier le type entier
	elif lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):	#	Flag de redirection (true||false)
		vtype = valBool(lexical_analyser)				#	[valBool]
		return vtype 									# 	retour du code "bool" pour signifier que c'est un boolean
	else:												#	Erreurs
		logger.error("Unknown Value! Expecting an integer or a boolean value!")
		raise AnaSynException("Unknown Value ! Expecting an integer or a boolean value!")

#valBool
def valBool(lexical_analyser):
### (true)  ###
### (false) ###	
	if lexical_analyser.isKeyword("true"):				#	Flag de redirection (true)
		lexical_analyser.acceptKeyword("true")			#	(true)
		logger.debug("boolean true value")				#	debug
		codeGenerator.boolInstr("true")					#//Pt de Gen\\ Generation d'un boolean "true"
		if codeGenerator.onCall == 1:
			codeGenerator.getNextCallAddr()

	else:												#	Autrement direction vers false
		logger.debug("boolean false value")				#	debug
		lexical_analyser.acceptKeyword("false")			#	(false)
		codeGenerator.boolInstr("false")				#//Pt de Gen\\ Generation d'un boolean "false"

	return "boolean"									#	retour du code "boolean" pour boolean

#es
def es(lexical_analyser):
###	(get) (() [ident] ()) ###
### (put) (() [expression] ()) ###
	global tableIdent
	parent = tableIdent._get_procActu()					#	recuperation du parent
	logger.debug("parsing E/S instruction: " + lexical_analyser.get_value())	#	debug
	if lexical_analyser.isKeyword("get"):				#	Flag de redirection (get)
		lexical_analyser.acceptKeyword("get")			#	(get)
		lexical_analyser.acceptCharacter("(")			#	(()
		ident = lexical_analyser.acceptIdentifier()		#	[ident]
		#<---------------------------------------------------
		if tableIdent.is_Ident(ident,parent):			## zone de verification du parametre
			if tableIdent.is_Parametre(ident,parent):		
				if tableIdent.get_Ident_Type(ident,parent)!="integer" and tableIdent.get_Ident_Mode(ident,parent)!="inout":
					ErreurSemantique(lexical_analyser,"Le parametre doit etre un entier et en mode in out")
			elif tableIdent.is_Variable(ident,parent):
				if tableIdent.get_Ident_Type(ident,parent)!="integer":
					ErreurSemantique(lexical_analyser,"La variable doit etre un entier") 	##		Fin de verif
			lexical_analyser.acceptCharacter(")")		#	())
			logger.debug("Call to get "+ident)			#	debug
			codeGenerator.esGetInstr(tableIdent.get_Ident_Adresse(ident,parent),tableIdent.get_Total_Adresse(parent))	#//Pt de Gen\\ Generation de l'instruction get					#G??n??ration d'une instruction "GET"
		else:	#	Erreur
			ErreurSemantique(lexical_analyser,"La variable n'a pas ete declare")
		#---------------------------------------------------/>
	elif lexical_analyser.isKeyword("put"):				#	Flag de redirection (put)
		lexical_analyser.acceptKeyword("put")			#	(put)
		lexical_analyser.acceptCharacter("(")			#	(()
		vtype=expression(lexical_analyser)				#	[expression]
		#<---------------------------------------------------
		if vtype!="integer":							#	Verification du put
			ErreurSemantique(lexical_analyser,"L'expression doit etre un entier")
		#---------------------------------------------------/>
		lexical_analyser.acceptCharacter(")")			#	())
		logger.debug("Call to put")						#	debug
		codeGenerator.esPutInstr()						#//Pt de Gen\\ Generation d'une instruction "PUT"

	else:												#	Erreur
		logger.error("Unknown E/S instruction!")		
		raise AnaSynException("Unknown E/S instruction!")

#boucle
def boucle(lexical_analyser):
### (while) [expression] (loop) [suiteInstr] (end) ###
	logger.debug("parsing while loop: ")				#	debug
	lexical_analyser.acceptKeyword("while")				#	(while)
	labelXXX = codeGenerator.whileInit()				#//Pt de Gen\\ Generation du debut d'une boucle
	#<---------------------------------------------------
	vtype=expression(lexical_analyser)					#	[expression]
	if vtype!="boolean":								#	verification du type
		ErreurSemantique(lexical_analyser,"L'expression doit etre booleenne")
	#--------------------------------------------------/>
	labelYYY = codeGenerator.whileCond()				#//Pt de Gen\\ Generation d'une condition de boucle

	lexical_analyser.acceptKeyword("loop")				#	(loop)
	vtype2=suiteInstr(lexical_analyser)					#	[suiteInstr]

	codeGenerator.whileEnd(labelXXX, labelYYY)			#//Pt de Gen\\ Generation d'une fin de boucle
	lexical_analyser.acceptKeyword("end")				#	(end)
	logger.debug("end of while loop ")					#	debug
	return vtype2										#	type de la boucle == type de la suiteInstr 

#altern
def altern(lexical_analyser):
### (if) [expression] (then) [suiteInstr] (else) [suiteInstr] (end) ###
### (if) [expression] (then) [suiteInstr] ------ ------------ ----- ###
	logger.debug("parsing if: ")						#	debug
	lexical_analyser.acceptKeyword("if")				#	(if)
	#<---------------------------------------------------
	vtype=expression(lexical_analyser)					#	[expression]
	if vtype!="boolean":								#	verification du type (boolean)
		ErreurSemantique(lexical_analyser,"L'expression doit etre booleenne")
	#--------------------------------------------------/>
	labelXXX = codeGenerator.ifInit()					#//Pt de Gen\\ Generation d'un d??but de condition
	lexical_analyser.acceptKeyword("then")				#	(then)
	vtype2=suiteInstr(lexical_analyser)					#	[suiteInstr]
	vtype3=None
	if lexical_analyser.isKeyword("else"):				#	Flagde redirection (else)
		labelYYY = codeGenerator.ifCondElse(labelXXX)	#//Pt de Gen\\ Generation d'un second bloc de condition
		lexical_analyser.acceptKeyword("else")			#	(else)
		vtype3=suiteInstr(lexical_analyser)				#	[suiteInstr]
		codeGenerator.ifEnd(labelYYY)					#//Pt de Gen\\ Generation d'une fin de bloc de condition
	else:												#	Autrement ()rien
		codeGenerator.ifEnd(labelXXX)					#//Pt de Gen\\ Generation d'une fin de bloc de condition
	lexical_analyser.acceptKeyword("end")				#	(end)
	logger.debug("end of if")							#	debug
	if vtype2!=None and vtype3!=None: 					# Les 2 instructions sont des returns
		if vtype2!=vtype3:
			ErreurSemantique(lexical_analyser,"Les returns doivent etre du meme type 4")
		return vtype2
	elif vtype2!= None:
		return vtype2
	elif vtype3!= None:
		return vtype3

#retour
def retour(lexical_analyser):
### (return) [expression] ###
	logger.debug("parsing return instruction")			#	debug
	lexical_analyser.acceptKeyword("return")			#	(return)
	vtype=expression(lexical_analyser)					#	[expression]
	return vtype 										#	retour du type de retour uu"


########################################################################
# main #
def main():
## Le parser
	parser = argparse.ArgumentParser(description='Do the syntactical analysis of a NNP program.')
	parser.add_argument('inputfile', type=str, nargs=1, help='name of the input source file')
	parser.add_argument('-o', '--outputfile', dest='outputfile', action='store', \
				default="", help='name of the output file (default: stdout)')
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
	parser.add_argument('-d', '--debug', action='store_const', const=logging.DEBUG, \
				default=logging.INFO, help='show debugging info on output')
	parser.add_argument('-p', '--pseudo-code', action='store_const', const=True, default=False, \
				help='enables output of pseudo-code instead of assembly code')
	parser.add_argument('--show-ident-table', action='store_true', \
				help='shows the final identifiers table')
	args = parser.parse_args()
## Fin du parser
#Recuperation et test du nom du fichier
	filename = args.inputfile[0]
	f = None
	try:
		f = open(filename, 'r')
	except:
		print "Error: can\'t open input file!"
		return
#Fin du test/recup du nom du fichier
	outputFilename = args.outputfile

	  # create logger
	LOGGING_LEVEL = args.debug
	logger.setLevel(LOGGING_LEVEL)
	ch = logging.StreamHandler()
	ch.setLevel(LOGGING_LEVEL)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)

	if args.pseudo_code:
		True#
	else:
		True#

#Creation de l'analiseur lexical
	lexical_analyser = analex.LexicalAnalyser()

	lineIndex = 0
	for line in f:
		line = line.rstrip('\r\n')
		lexical_analyser.analyse_line(lineIndex, line)
		lineIndex = lineIndex + 1
	f.close()
# launch the analysis of the program
	lexical_analyser.init_analyser()
	program(lexical_analyser)
	if args.show_ident_table:
		print "------ IDENTIFIER TABLE ------"
		#print str(identifierTable)
		print "------ END OF IDENTIFIER TABLE ------"
	if outputFilename != "":
		try:
			output_file = open(outputFilename, 'w')
		except:
			print "Error: can\'t open output file!"
			return
	else:
		output_file = sys.stdout
# Outputs the generated code to a file
	instrIndex = 0
	while instrIndex < codeGenerator.get_instruction_counter():
		output_file.write("%s\n" % str(codeGenerator.get_instruction_at_index(instrIndex)))
		instrIndex += 1
	if outputFilename != "":
		output_file.close()

########################################################################

if __name__ == "__main__":
	main()
