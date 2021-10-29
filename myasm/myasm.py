import re
import sys, getopt
from dataclasses import dataclass
import pprint
import coden


adrMap = {
	"ALU":	0x00,
	"A":	0x00,
	"B":	0x01,
	"E":	0x02,
	"RAND":	0x03,
	"ADD":	0x04,
	"INC":	0x05,
	"SUB":	0x06,
	"DEC":	0x07,
	"UMUL":	0x08,
	"SMUL":	0x09,
	"DIVa":	0x0a,
	"0x0b":	0x0b,
	"0x0c":	0x0c,
	"0x0d":	0x0d,
	"0x0e":	0x0e,
	"0x0f":	0x0f,
	"FHO":	0x10,
	"FLO":	0x11,
	"FHZ":	0x12,
	"FLZ":	0x13,
	"ROTL":	0x14,
	"ROTR":	0x15,
	"LSL":	0x16,
	"LSR":	0x17,
	"ASR":	0x18,
	"COUNT":	0x19,
	"COMP":	0x1a,
	"BCDa":	0x1b,
	"AND":	0x1c,
	"OR":	0x1d,
	"XOR":	0x1e,
	"NOT":	0x1f,

	"PC":	0x20,
	"PC0":	0x20,
	"PC1":	0x21,
	"PC2":	0x22,
	"PC3":	0x23,
	"RJR":	0x24,
	"BNZw":	0x25,
	"RESETr":	0x25,
	"RJUMPw":	0x26,
	"PCSr":	0x26,
	"JNZw":	0x27,
	"JMPr":	0x27,

	"IO":	0x28,
	"TTY":	0x28,
	"LOAD":	0x29,
	"PAUSE":	0x30,

	"S":	0x80,
}

adrDesc = {
	"0x00":	"A register",
	"0x01":	"B register",
	"0x02":	"E register",
	"0x03":	"Random number generator",
	"0x04":	"A + B carry(E) (updates E reminder)",
	"0x05":	"A + 1 carry(E) (updates E reminder)",
	"0x06":	"A - B carry(E) (updates E reminder)",
	"0x07":	"A - 1 carry(E) (updates E reminder)",
	"0x08":	"A * B carry(E) unsigned (updates E unsigned reminder)",
	"0x09":	"A * B carry(E) 2compliment (updates E 2compliment reminder)",
	"0x0a":	"step of A / B carry(E) unsigned (updates E reminder) run eight times save E run one more time for result	",
	"0x0b":	"",
	"0x0c":	"",
	"0x0d":	"",
	"0x0e":	"",
	"0x0f":	"",
	"0x10":	"Find high 1 in A",
	"0x11":	"Find low 1 in A",
	"0x12":	"Find high 0 in A",
	"0x13":	"Find low 0 in A",
	"0x14":	"Rotate A left B steps ",
	"0x15":	"Rotate A right B steps",
	"0x16":	"Logical AE left B steps (updates E with bit shifted off)",
	"0x17":	"Logical EA right B steps (updates E with bit shifted off)",
	"0x18":	"Arithmetic A right B steps",
	"0x19":	"Count bits set in A",
	"0x1a":	"comparison result anded with E\n	0b(s A<B)(s A>B)(u A<B)(u A>B)(0 unused)(A has set bits)(A has clear bits)(A=B)",
	"0x1b":	"BCDaccelerator A is 2 packed BCD digits E has a carry eatch nibble is compaired to the high byte of B and the lower nibble of B is added to it if it is larger than B result is shifted up with carry in E",
	"0x1c":	"A and B",
	"0x1d":	"A or B",
	"0x1e":	"A xor B",
	"0x1f":	"Not A",

	"0x20":	"PCtmp low byte",
	"0x21":	"PCtmp 2 byte",
	"0x22":	"PCtmp 3 byte",
	"0x23":	"PCtmp high byte",
	"0x24":	"Relative jump amount",
	"0x25W":	"Conditional relative jump on non zero",
	"0x25R":	"Reset PC to 0x00000000",
	"0x26W":	"Unconditional relative jump with value",
	"0x26R":	"Copy PC to PCtmp",
	"0x27W":	"Conditional long jump to PCtmp on non zero",
	"0x27R":	"Unconditional long jump to PCtmp",

	"0x28":	"TTY",
	"0x29":	"Read immediate literarl in to B",
	"0x30":	"Halt/Pause with code",
	"0x80":	"0x80 - 0xff scratch pad ram"

}



@dataclass
class Line:
	n: int = 0
	b: int = 0
	line: str = None
	comment: str = None
	code: list = None
	byte: list = None
	asm: str = ''
	label: str = None

@dataclass
class Label:
	n: int = 0
	name: str = None
	addr: int = 0

@dataclass
class Assignment:
	n: int = 0
	name: str = None
	code: str = 0
	value: int = 0

def decodeCode(str, n, byteCount, labeles, assignments):
	str = re.sub("\n$", "", str)
	l = Line()
	split = re.split("#", str, 1)
	l.n = n
	l.b = byteCount
	l.line = str
	l.comment = None if len(split) != 2 else split[1]
	l.code = []
	i = 0
	str = split[0]
	print("\n--------------------\nreading line", n)
	pprint.pprint(l, indent=4)
	TMP = re.search("^[^\s]+:", str)
	if not TMP is None:
		label = Label(n, TMP.group()[:-1], byteCount)
		print("added label", label)
		l.label = label.name
		labeles[label.name] = label
		i += TMP.span()[1]
	
	TMP = re.search("^\s*:", str[i:])#remove leading whitespace
	if not TMP is None:
		i += TMP.span()[1]
	
	assignment = None
	while i < len(str):
		print("starting loop at", i, str[i:])
		
		TMP = re.search("^\s*", str[i:])#remove leading whitespace
		print(TMP)
		if not TMP is None:
			print("removing whitespace")
			i += TMP.span()[1]
			if i >= len(str):
				break
		
		TMP = re.search("^[^\s]+\s*=", str[i:])#value assignment
		if not TMP is None:
			assignment = Assignment(n, re.sub("\s*$", "", TMP.group()[:-1]), None)
			print("started value assignment", assignment)
			i += TMP.span()[1]
			if i >= len(str):
				break
		TMP = re.search("^[^\s]*[\(\[\{]", str[i:])#save expression as one chunk
		if not TMP is None:
			#if str[i] in ["(", "{", "["]:#save expression as one chunk
			print("is expression")
			depth = 1
			TMP = i + TMP.span()[1]
			if TMP >= len(str):
				break
			while depth != 0:
				print(depth, str[TMP])
				if str[TMP] in ["(", "{", "["]:
					depth+= 1
				if str[TMP] in [")", "}", "]"]:
					depth-= 1
				
				TMP+= 1
				if TMP >= len(str):
					print("unmatched pareentacis", str)
					break
			TMP += 1
			print("extracted line", str[:i], "\n",  str[i:TMP], "\n", str[TMP:])
			if assignment is None:
				l.code.append(str[i:TMP])
				byteCount+= 1
				
			else:
				assignment.code = str[i:TMP]
				assignments.append(assignment)
				assignment = None
			i = TMP
				
		else:
			print("is literal or string'", str[i:], "'")
			TMP = re.search("^[^\s]+", str[i:])#save litteral
			print(TMP)
			if not TMP is None:
				print("decoding segment")
				if assignment is None:
					l.code.append(TMP.group())
					byteCount+= 1
				else:
					assignment.code = TMP.group()
					assignments.append(assignment)
					assignment = None
				i += TMP.span()[1]
	return l, byteCount, labeles, assignments

def readFile(inputfile):
	n = 0
	byteCount = 0
	labeles = {}
	assignments = []
	file = [inputfile]
	with open(inputfile) as f:
		for line in f:
			n+=1
			l, byteCount, labeles, assignments = decodeCode(line, n, byteCount, labeles, assignments)
			file.append(l)
	#pprint.pprint(file, indent=4)
	#pprint.pprint(labeles, indent=4)
	return(file, labeles, assignments)

def addLabels(file, labeles, assignments):
	#pprint.pprint(adrMap, indent=4)
	#pprint.pprint(adrDesc, indent=4)
	for k in labeles:
		l = labeles[k]
		print(l.name, l, l.addr)
		adrMap[l.name] = l.addr
		tmp = l.name
		if not file[l.n].comment is None:
			tmp += '\t' + file[l.n].comment
		print(tmp)
		adrDesc["$" + str(l.addr)] = tmp
	
	for a in assignments:
		print("Decoding assignment", a)
		a.value = int(eval(a.code, adrMap))
		print(a.name, a.value)
		adrMap[a.name] = a.value
		
		tmp = a.name + "\t= " + str(a.value) + "\teval(" + a.code + ")"
		if not file[a.n].comment is None:
			tmp += '\t' + file[a.n].comment
		print(tmp)
		adrDesc[a.name] = tmp
	#pprint.pprint(adrMap, indent=4)
	#pprint.pprint(adrDesc, indent=4)

def assemble(file):
	for line in file[1:]:
		line.byte = []
		print(line)
		for segment in line.code:
			val = eval(segment, adrMap)
			print(val, type(val))
			line.byte.append(val&0xff)

def saveASM(file, outputfile, includeComents):
	for line in file[1:]:
		lbuf = ""
		if includeComents:
			lbuf +=	str(line.n).zfill(4) + " " + hex(line.b)[2:].zfill(6) + "\t"
			lbuf += line.line + "\n\t\t"
		if includeComents and not line.label is None:
			lbuf += line.label + ":"
		for segment in line.byte:
			lbuf += "\t" + hex(segment)[2:].zfill(2)
		if includeComents and not line.comment is None:
			lbuf += "\t#" + line.comment + "\t"
		print(lbuf)

def main(argv):
	inputfile = ''
	outputfile = ''
	includeComents = False
	try:
		opts, args = getopt.getopt(argv[1:],"hi:o:c",["ifile=","ofile="])
	except getopt.GetoptError:
		print('test.py -i <inputfile> -o <outputfile>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('test.py -i <inputfile> -o <outputfile>')
			sys.exit()
		elif opt in ("-i", "--ifile"):
			inputfile = arg
		elif opt in ("-o", "--ofile"):
			outputfile = arg
		elif opt in ("-c"):
			includeComents = True
	if outputfile == '':
		print("using default output file")
		outputfile = re.sub("\.[A-Za-z0-9]*$", "", inputfile) + ".asm"
	print('Input file is "', inputfile)
	print('Output file is "', outputfile)
	file, labeles, assignments = readFile(inputfile)
	#pprint.pprint(adrMap, indent=4)
	addLabels(file, labeles, assignments)
	
	assemble(file)
	del adrMap["__builtins__"]
	pprint.pprint(file, indent=4)
	pprint.pprint(labeles, indent=4)
	pprint.pprint(assignments, indent=4)
	
	pprint.pprint(adrMap, indent=4)
	pprint.pprint(adrDesc, indent=4)
	
	saveASM(file, outputfile, includeComents)
if __name__ == "__main__":
   main(sys.argv)
