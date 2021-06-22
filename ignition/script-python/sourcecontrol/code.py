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

def Clone(folder, uri, payload):
	import os
	from java.io import File
	from org.eclipse.jgit.api import Git
	from org.eclipse.jgit.transport import UsernamePasswordCredentialsProvider

	# In this case, cloning is not really a good idea as it requires an empty folder
	# 1 - Init
	Init(folder)
	# 2 - Add remote as origin
	AddRemote(folder, "", "origin", uri)
	# 3 - Pull
	Pull(folder, "", payload)
	# 4 - Rename current branch and checkout master??

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
			
		addLogin(fetchCommand, payload)
		
		return fetchCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def Pull(folder, submodule, payload):
	def callback(git):
		pullCommand = git.pull()
			
		addLogin(pullCommand, payload)
		
		return pullCommand.call()

	return runGitCommand(folder, submodule, callback)

def Push(folder, submodule, payload):
	def callback(git):
		pushCommand = git.push()
		
		addLogin(pushCommand, payload)
		
		return pushCommand.call()
	
	return runGitCommand(folder, submodule, callback)

def Diff(folder, submodule, file):
	def callback(git):
		from java.io import ByteArrayOutputStream
		from java.nio.charset import StandardCharsets
		from org.eclipse.jgit.treewalk.filter import PathFilter

		diffCommand = git.diff()
		
		patchStream = ByteArrayOutputStream()
		diffCommand.setOutputStream(patchStream)
		
		fileFilter = PathFilter.create(file)
		diffCommand.setPathFilter(fileFilter)

		diffCommand.call()
		
		return patchStream.toString(StandardCharsets.UTF_8)

	return runGitCommand(folder, submodule, callback)

def AddRemote(folder, submodule, name, uri):
	from org.eclipse.jgit.transport import URIish
	def callback(git):
		remoteAddCommand = git.remoteAdd()
		
		remoteAddCommand.setName(name)
		remoteAddCommand.setUri(URIish(uri))
		
		return remoteAddCommand.call()
	
	return runGitCommand(folder, submodule, callback)

def CheckoutBranch(folder, submodule, branch):
	def callback(git):
		checkoutCommand = git.checkout()
		
		checkoutCommand.setName(branch.replace("refs/heads/", ""))
		
		return checkoutCommand.call()

	return runGitCommand(folder, submodule, callback)
	
def CreateBranch(folder, submodule, branch, payload):
	from org.eclipse.jgit.api import CreateBranchCommand
	def callback(git):
		checkoutCommand = git.checkout()
	
		splitBranch = branch.split("/")
		checkoutCommand.setName(branch.replace("refs/heads/", ""))
				
		checkoutCommand.setCreateBranch(true)
		checkoutCommand.setName("stable")
		checkoutCommand.setUpstreamMode(CreateBranchCommand.SetupUpstreamMode.SET_UPSTREAM)
		checkoutCommand.setStartPoint("origin/stable").call();
	
		return checkoutCommand.call()

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