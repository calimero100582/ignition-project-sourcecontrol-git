# netrc lib parse and input 
# machine host1.austin.century.com login fred password bluebonnet
def LoadFile(netrcFilepath):
	if system.file.fileExists(netrcFilepath):
		return system.file.readFileAsString(netrcFilepath)
		
	return ""
		
def SaveFile(netrcFilepath, entries):
	if entries:
		netrcFileContent = ""
		
		for entry in entries:
			entryContent = entries[entry].toFileEntry()
			
			if entryContent:
				netrcFileContent += entryContent + "\n"
				
		system.file.writeFile(netrcFilepath, netrcFileContent)

def Parse(netrcFilepath):
	filecontent = LoadFile(netrcFilepath)
	
	words = filecontent.split()
	entries = {}
	entry = NetRcEntry()
	set = None
	
	for word in words:
		if set:
			set(word)
			set = None
		elif word == "default":
			entry.setMachine("default")
		elif word == "machine":
			set = entry.setMachine
		elif word == "login":
			set = entry.setLogin
		elif word == "password":
			set = entry.setPassword
			
		if entry.isComplete():
			entries[entry.machine] = entry
			entry = NetRcEntry()

	return entries

def AddOrUpdateEntry(netrcFilepath, host, username, password):
	entries = Parse(netrcFilepath)
	
	entry = NetRcEntry()
	entry.setMachine(host)
	entry.setLogin(username)
	entry.setPassword(password)
	entries[host] = entry
	
	SaveFile(netrcFilepath, entries)

def DeleteEntry(netrcFilepath, host):
	entries = Parse(netrcFilepath)

	entry = NetRcEntry()
	entries[host] = entry
	
	SaveFile(netrcFilepath, entries)

class NetRcEntry:
	# login netrc entry
	login = ""
	# password netrc entry
	password = ""
	# machine netrc entry
	machine = ""

	def setMachine(self, machine):
		self.machine = machine

	def setLogin(self, login):
		self.login = login

	def setPassword(self, password):
		self.password = password

	def isComplete(self):
		return self.login and self.password and self.machine
		
	def toFileEntry(self):
		if not self.isComplete():
			return ""

		entry = ""

		entry += self.machine if self.machine == "default" else ("machine " + self.machine)
		entry += " "

		entry += "login " + self.login
		entry += " "

		entry += "password " + self.password
		entry += "\n"

		return entry