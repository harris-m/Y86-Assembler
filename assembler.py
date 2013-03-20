#Y86 Assembler 1.1 by Harris M.

import sys, struct, collections

#Register constants
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

#We'll store our buffered data in this type
BufferedItem = collections.namedtuple("BufferedVal", ["size", "value"])

#Handles output buffering and writing
class OutputBuffer(object):
	def __init__(self, outFile):
		#A list of tuples to be written out
		#first value is the number of bytes
		#second value is the value to write
		self.buffer = [];
		self.outFile = outFile;
		#How many bytes since the last flush
		self.byteCount = 0;
		#Starting address to write for the current block
		self.startAddr = 0;

	#Write the value as one byte, big endian
	def write1(self, value):
		self.outFile.write(struct.pack(">B", value))

	#Write the value as two bytes, big endian
	def write2(self, value):
		self.outFile.write(struct.pack(">H", value))

	#Write the value as four bytes, little endian
	def write4(self, value):
		self.outFile.write(struct.pack("<i", value))

	#Buffer a new item in the block
	def buf(self, size, value):
		self.buffer.append(BufferedItem(size, value))
		self.byteCount += size

	#Write out a block from the buffer
	def flushBuf(self):
		self.write2(self.startAddr)
		self.write2(self.byteCount)
		for item in self.buffer:
			if item.size == 1:
				self.write1(item.value)
			elif item.size == 2:
				self.write2(item.value)
			elif item.size == 4:
				self.write4(item.value)

	def flushIfBufIsNotEmpty(self):
		if len(self.buffer) > 0:
			self.flushBuf();

	def resetBuffer(self, newStartAddr):
		self.startAddr = newStartAddr
		self.buffer = []
		self.byteCount = 0

def main():
	# Check arguments
	if len(sys.argv) == 2:
		inFileName = sys.argv[1]
		outFileName = "out.yb" #Default ouput filename
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

	#Create output buffer
	ob = OutputBuffer(outFile);

	#Write magic number
	ob.write2(0x7962);

	#Begin reading file
	line = inFile.readline()
	while line:
		line = line.strip() #Toss extra spaces/newlines
		tokens = line.split() #Split line on whitespace
		if line.startswith(":"): #New starting address
			ob.flushIfBufIsNotEmpty()
			ob.resetBuffer(int(line[1:], 16))
		elif len(tokens) > 0:
			if tokens[0] == "halt":
				ob.buf(1, 0x00)
			elif tokens[0] == "nop":
				ob.buf(1, 0x10)
			elif tokens[0] == "rrmovl":
				ob.buf(1, 0x20)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "irmovl":
				ob.buf(1, 0x30)
				ob.buf(1, 0xF0 + regs[tokens[2]])
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "rmmovl":
				ob.buf(1, 0x40)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[3]])
				ob.buf(4, int(tokens[2], 16))
			elif tokens[0] == "mrmovl":
				ob.buf(1, 0x50)
				ob.buf(1, (regs[tokens[3]] << 4) + regs[tokens[2]])
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "add":
				ob.buf(1, 0x60)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "sub":
				ob.buf(1, 0x61)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "and":
				ob.buf(1, 0x62)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "xor":
				ob.buf(1, 0x63)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "jmp":
				ob.buf(1, 0x70)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "jle":
				ob.buf(1, 0x71)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "jl":
				ob.buf(1, 0x72)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "je":
				ob.buf(1, 0x73)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "jne":
				ob.buf(1, 0x74)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "jge":
				ob.buf(1, 0x75)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "jg":
				ob.buf(1, 0x76)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "cmovle":
				ob.buf(1, 0x21)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "cmovl":
				ob.buf(1, 0x22)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "cmove":
				ob.buf(1, 0x23)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "cmovne":
				ob.buf(1, 0x24)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "cmovge":
				ob.buf(1, 0x25)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "cmovg":
				ob.buf(1, 0x26)
				ob.buf(1, (regs[tokens[1]] << 4) + regs[tokens[2]])
			elif tokens[0] == "call":
				ob.buf(1, 0x80)
				ob.buf(4, int(tokens[1], 16))
			elif tokens[0] == "ret":
				ob.buf(1, 0x90)
			elif tokens[0] == "push":
				ob.buf(1, 0xA0)
				ob.buf(1, (regs[tokens[1]] << 4) + 0xF)
			elif tokens[0] == "pop":
				ob.buf(1, 0xB0)
				ob.buf(1, (regs[tokens[1]] << 4) + 0xF)

		line = inFile.readline() #grab the next line

	ob.flushIfBufIsNotEmpty() #write out the last block

	#Cleanup
	inFile.close()
	outFile.close()

if __name__ == '__main__':
   main()