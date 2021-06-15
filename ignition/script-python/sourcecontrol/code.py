def runGitCommand(folder, submodule, callback):
	from org.eclipse.jgit.api.errors import TransportException
	
	git = Git(folder, submodule)
	try:
		return callback(git)
	except TransportException as e:
		system.perspective.print(system.util.jsonEncode(e))
		#system.perspective.sendMessage("git-request-login", {"method": method, "folder": folder, "submodule": submodule, "payload": payload})
	#except:
	#	pass # do some logging eventually?
	finally:
		git.close()

def Git(folder, submodule):
	from java.io import File
	from org.eclipse.jgit.api import Git
	from org.eclipse.jgit.submodule import SubmoduleWalk
	
	path = File(folder)
	return Git.open(path) if not submodule else Git.wrap(SubmoduleWalk.getSubmoduleRepository(path, submodule))

def isRepositoryValid(folder, submodule = "", payload = {}):
	def callback(git):
		try:
			return git.getRepository().getObjectDatabase().exists()
		except:
			return False

	return runGitCommand(folder, submodule, callback)
	
def Init(folder):
	from java.io import File
	from org.eclipse.jgit.api import Git
	
	path = File(folder)
	git = Git.init().setDirectory(path).call()
	git.close()

def Clone(folder, uri, username, password):
	import os
	from java.io import File
	from org.eclipse.jgit.api import Git
	from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider

	path = File(folder)
	cloneCommand = Git.cloneRepository()
	
	cloneCommand.setURI(uri)
	cloneCommand.setDirectory(path)
	
	if username or password:
		cloneCommand.setCredentialsProvider(UsernamePasswordCredentialsProvider(username, password))
	
	git = cloneCommand.call()
	git.close()

def Status(folder, submodule, subfolder):
	def callback(git):
		statusCommand = git.status()

		if subfolder:
			statusCommand.addPath(subfolder)

		return statusCommand.call()
		
	return runGitCommand(folder, submodule, callback)
	
def Fetch(folder, submodule, payload):
	def callback(git):
		fetchCommand = git.fetch()
			
		addLogin(pushCommand, payload)
		
		return fetchCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def Pull(folder, submodule, payload):
	def callback(git):
		pullCommand = git.pull()
			
		addLogin(pushCommand, payload)
		
		return pullCommand.call()

	return runGitCommand(folder, submodule, callback)

def Push(folder, submodule, payload):
	from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider
	
	def callback(git):
		pushCommand = git.push()
		
		addLogin(pushCommand, payload)
		
		return pushCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def getListBranch(folder, submodule):
	from org.eclipse.jgit.api.ListBranchCommand import ListMode
	def callback(git):
		listBranchCommand = git.branchList()
		listBranchCommand.setListMode(ListMode.ALL)
		
		return listBranchCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def getCurrentBranch(folder, submodule):
	def callback(git):
		return git.getRepository().getBranch()

	return runGitCommand(folder, submodule, callback)
	
def getListSubmodule(folder, submodule):
	def callback(git):
		submoduleStatusCommand = git.submoduleStatus()

		return submoduleStatusCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def Commit(folder, submodule, files, removedFiles, authorName, authorEmail, message):
	def callback(git):
		if len(files) > 0:
			addCommand = git.add()
	
			for file in files:
				addCommand = addCommand.addFilepattern(file)
		
			addCommand.call()
	
		if len(removedFiles) > 0:
			removeCommand = git.rm()
	
			for file in removedFiles:
				removeCommand.addFilepattern(file)
	
			removeCommand.call()
	
		return git.commit().setAuthor(authorName, authorEmail).setMessage(message).call();
	
	return runGitCommand(folder, submodule, callback)

def getRemoteHost(folder, submodule):
	def callback(git):
		from java.net import URI
		
		remoteUri = git.getRepository().getConfig().getString("remote", "origin", "url")
	
		return URI(remoteUri).getHost()
	
	return runGitCommand(folder, submodule, callback)

def requireLogin(folder, submodule):
	from org.eclipse.jgit.transport import NetRC

	netrc = NetRC()
	return netrc.getEntry(getRemoteHost(folder, submodule)) == None

def addLogin(command, payload):
	from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider
	from org.eclipse.jgit.transport import NetRCCredentialsProvider
	
	if hasattr(payload, "username") or hasattr(payload, "password"):
		return command.setCredentialsProvider(UsernamePasswordCredentialsProvider(payload.username, payload.password))
	
	return command.setCredentialsProvider(NetRCCredentialsProvider())