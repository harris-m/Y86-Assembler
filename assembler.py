#Y86 Assembler 1.0 by Harris M.
#Please forgive me for the awful code,
#I hacked this together really quickly
#and I'm not a python expert

#But hey, it works!

import sys, struct

#Write the value as one byte, big endian
def write1(outFile, value):
	outFile.write(struct.pack(">B", value))

#Write the value as two bytes, big endian
def write2(outFile, value):
	outFile.write(struct.pack(">H", value))

#Write the value as four bytes, little endian
def write4(outFile, value):
	outFile.write(struct.pack("<i", value))

#Write out a block from the buffer
def flushBuf(outFile, startAddr, byteCount, outBuf):
	write2(outFile, startAddr)
	write2(outFile, byteCount)
	for i in outBuf:
		if i[0] == 1:
			write1(outFile, i[1])
		elif i[0] == 2:
			write2(outFile, i[1])
		elif i[0] == 4:
			write4(outFile, i[1])

regs = {
	'eax': 0,
	'ecx': 1,
	'edx': 2,
	'ebx': 3,
	'esp': 4,
	'ebp': 5,
	'esi': 6,
	'edi': 7
}

def main():
	# Check arguments
	if len(sys.argv) == 2:
		inFileName = sys.argv[1]
		outFileName = "out.yb"
	elif len(sys.argv) == 3:
		inFileName = sys.argv[1]
		outFileName = sys.argv[2]
	else:
		print "Usage: " + sys.argv[0] + " INPUT_FILE [OUTPUT_FILE]"
		sys.exit()

	#Open files
	try:
		inFile = open(inFileName, "r")
	except IOError:
		print "Failed to open " + inFileName
		sys.exit()

	try:
		outFile = open(outFileName, "wb")
	except IOError:
		print "Failed to open " + outFileName
		sys.exit()

	#Write magic number
	write2(outFile, 0x7962);

	#Begin reading file
	outBuf = [] # A list of tuples that contain the number of bits to write and the value
	byteCount = 0 # How many bytes have been written since the last flush
	startAddr = 0 # The address at which this block started

	line = inFile.readline()
	while line:
		line = line.strip()
		if line.startswith(":"):
			if len(outBuf) > 0:
				flushBuf(outFile, startAddr, byteCount, outBuf)
			startAddr = int(line[1:], 16)
			outBuf = []
			byteCount = 0
		else:
			tokens = line.split(' ')
			if tokens[0] == "halt":
				outBuf.append((1, 0x00))
				byteCount += 1
			elif tokens[0] == "nop":
				outBuf.append((1, 0x10))
				byteCount += 1
			elif tokens[0] == "rrmovl":
				outBuf.append((1, 0x20))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "irmovl":
				outBuf.append((1, 0x30))
				outBuf.append((1, 0xF0 + regs[tokens[2]]))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 6
			elif tokens[0] == "rmmovl":
				outBuf.append((1, 0x40))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[3]]))
				outBuf.append((4, int(tokens[2], 16)))
				byteCount += 6
			elif tokens[0] == "mrmovl":
				outBuf.append((1, 0x50))
				outBuf.append((1, (regs[tokens[3]] << 4) + regs[tokens[2]]))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 6
			elif tokens[0] == "add":
				outBuf.append((1, 0x60))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]));
				byteCount += 2
			elif tokens[0] == "sub":
				outBuf.append((1, 0x61))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]));
				byteCount += 2
			elif tokens[0] == "and":
				outBuf.append((1, 0x62))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]));
				byteCount += 2
			elif tokens[0] == "xor":
				outBuf.append((1, 0x63))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]));
				byteCount += 2
			elif tokens[0] == "jmp":
				outBuf.append((1, 0x70))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "jle":
				outBuf.append((1, 0x71))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "jl":
				outBuf.append((1, 0x72))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "je":
				outBuf.append((1, 0x73))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "jne":
				outBuf.append((1, 0x74))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "jge":
				outBuf.append((1, 0x75))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "jg":
				outBuf.append((1, 0x76))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "cmovle":
				outBuf.append((1, 0x21))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "cmovl":
				outBuf.append((1, 0x22))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "cmove":
				outBuf.append((1, 0x23))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "cmovne":
				outBuf.append((1, 0x24))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "cmovge":
				outBuf.append((1, 0x25))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "cmovg":
				outBuf.append((1, 0x26))
				outBuf.append((1, (regs[tokens[1]] << 4) + regs[tokens[2]]))
				byteCount += 2
			elif tokens[0] == "call":
				outBuf.append((1, 0x80))
				outBuf.append((4, int(tokens[1], 16)))
				byteCount += 5
			elif tokens[0] == "ret":
				outBuf.append((1, 0x90))
				byteCount += 1
			elif tokens[0] == "push":
				outBuf.append((1, 0xA0))
				outBuf.append((1, (regs[tokens[1]] << 4) + 0xF))
				byteCount += 2
			elif tokens[0] == "pop":
				outBuf.append((1, 0xB0))
				outBuf.append((1, (regs[tokens[1]] << 4) + 0xF))
				byteCount += 2

		line = inFile.readline()

	if len(outBuf) > 0:
		flushBuf(outFile, startAddr, byteCount, outBuf)


	inFile.close()
	outFile.close()

if __name__ == '__main__':
   main()