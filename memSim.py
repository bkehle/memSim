# Questions
# What to do if page is already in table when updating?
# Do we update the TLB upon Page Table hit?
# When to update present bit/take things out of physical memory?
# Do we load the entire frame into physical memory?
import sys

TLB_SIZE = 16
PAGE_TABLE_SIZE = 256
PAGE_SIZE = 256

class PTEntry:
	def __init__(self, frame):
		self.frame = frame
		self.present = True

class PageTable:
	def __init__(self):
		self.table = [None] * PAGE_TABLE_SIZE
	
	def addEntry(self, page, frame):
		for entry in self.table:
			if entry != None and entry.frame == frame:
				entry.present = False
		
		if self.table[page] == None:
			self.table[page] = PTEntry(frame)
		else:
			self.table[page].present = True

class MemorySimulator:
	def __init__(self, frames, algorithm):
		self.physicalMemory = globals()[algorithm + "Memory"](frames)
		self.TLB = globals()[algorithm + "TLB"]()
		self.pageTable = PageTable()
		
		self.pageFaults = 0
		self.translatedNum = 0
		self.TLBHits = 0
		self.TLBMisses = 0
	
	def processAddress(self, address):
		pageNum, offset = self.getNumbers(int(address))
		self.translatedNum += 1
		frame = None
      
		frameNum = self.TLB.getFrame(pageNum)
		if frameNum == None:
			self.TLBMisses += 1
			frameNum, frame = self.checkPageTable(pageNum)
		else:
			self.TLBHits += 1
		
		if frame == None:
			frame = self.physicalMemory.getFrame[frameNum]

		self.printRequest(address, frame[offset], frameNum, frame)
	
	def getNumbers(self, num):
		pageNum = (num & 0xFF00) >> 8
		offset = num & 0xFF
		return (pageNum, offset)
	
	def checkPageTable(self, page):
		if self.pageTable.table[page] == None or self.pageTable.table[page].present == False:
			self.pageFaults += 1
			frame = self.getFromDisk(page)
			frameNum = self.physicalMemory.addValue(frame)
			self.TLB.addEntry(page, frameNum)
			self.pageTable.addEntry(page, frameNum)
			return (frameNum, frame)
		
		self.TLB.addEntry(page, self.pageTable.table[page].frame)
		return (self.pageTable.table[page].frame, None)

	def getFromDisk(self, frame):
		file = open("BACKING_STORE.bin", 'rb')
		file.seek(PAGE_SIZE * frame)
		return file.read(PAGE_SIZE)
	
	def printRequest(self, address, value, frameNum, frame):
		string_frame = [str(num) for num in frame]
		print(address + ", " + str(value) + ", " + str(frameNum) + "\n" + ''.join(string_frame) + "\n")
		
	def printStats(self):
		print("Number of Translated Addresses = %d" % self.translatedNum)
		print("Page Faults = %d" % self.pageFaults)
		print("Page Fault Rate = %f" % (self.pageFaults / self.translatedNum))
		print("TLB Hits = %d" % self.TLBHits)
		print("TLB Misses = %d" % self.TLBMisses)
		print("TLB Hit Rate = %f" % (self.TLBHits/self.translatedNum))

class LRUMemory:
	def __init__(self, frames):
		self.memory = [[0] * PAGE_SIZE] * frames
		self.frameQueue = []
		for i in range(frames):
			self.frameQueue.append(i)
	
	def addValue(self, frame):
		temp = self.frameQueue.pop(0)
		self.frameQueue.append(temp)

		for i in range(PAGE_SIZE):
			self.memory[temp][i] = frame[i]

		return temp
	
	def getFrame(self, frameNum):
		self.memory[frameNum]


class LRUTLB:
	def __init__(self):
		self.table = {}
		self.numQueue = []

	def getFrame(self, page):
		if page in self.numQueue:
			return self.table[page]
		return None

	def addEntry(self, page, frame):
		delLst = []
		
		for key, value in self.table.items():
			if value == frame:
				delLst.append(key)
		
		for key in delLst:
			del self.table[key]
			self.numQueue.remove(key)

		if len(self.numQueue) == TLB_SIZE:
			del self.table[self.numQueue.pop(0)]
		
		self.numQueue.append(page)
		self.table[page] = frame


class FIFOMemory:
	def __init__(self, frames):
		self.memory = [[0] * PAGE_SIZE] * frames
		self.frameNum = 0
	
	def addValue(self, frame):
		temp = self.frameNum
		if temp == len(self.memory):
			temp = 0
		
		for i in range(PAGE_SIZE):
			self.memory[temp][i] = frame[i]

		self.frameNum = temp + 1
		return temp
	
	def getFrame(self, frameNum):
		self.memory[frameNum]

class FIFOTLB:
	def __init__(self):
		self.numQueue = []
		self.table = {}

	def getFrame(self, page):
		if page in self.numQueue:
			return self.table[page]
		return None

	def addEntry(self, page, frame):
		delLst = []
		
		for key, value in self.table.items():
			if value == frame:
				delLst.append(key)
		
		for key in delLst:
			del self.table[key]
			self.numQueue.remove(key)

		if len(self.numQueue) == TLB_SIZE:
			del self.table[self.numQueue.pop(0)]
		
		self.numQueue.append(page)
		self.table[page] = frame

def checkArgs():
	if(len(sys.argv) == 1):
		print("Usage: memSim <reference-sequence-file.txt> <FRAMES> <PRA>")
		sys.exit(1)
	
	file = sys.argv[1]
	frames = 256
	algs = ["FIFO", "LRU"]
	alg = "FIFO"
	
	if(len(sys.argv) > 2):
		arg = sys.argv[2]
		if arg.isnumeric():
			frames = int(arg)
			if frames > 256 or frames < 1:
				frames = 256
	
	if(len(sys.argv) > 3):
		alg = sys.argv[3].upper()
		if alg not in algs:
			alg = "FIFO"
	
	return (file, frames, alg)

def main():
	file, frames, alg = checkArgs()
	memSim = MemorySimulator(frames, alg)

	lines = open(file, "r").readlines()
	for line in lines:
		memSim.processAddress(line.strip())

	memSim.printStats()


main()



