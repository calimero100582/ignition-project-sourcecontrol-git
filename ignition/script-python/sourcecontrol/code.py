def runGitCommand(folder, submodule, callback): 
	from org.eclipse.jgit.api.errors import TransportException
	
	git = Git(folder, submodule)
	
	try:
		return callback(git)
	except TransportException as e:
		system.perspective.print(system.util.jsonEncode(e))
		#system.perspective.sendMessage("git-request-login", {"method": method, "folder": folder, "submodule": submodule, "payload": payload})
	#	raise e
	#except:
	#	raise
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

	try:
		return runGitCommand(folder, submodule, callback)
	except:
		return False
	
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
	# 4 - Rename current branch and checkout master/main??

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

def AddSubmodule(folder, submodule, uri, payload):
	from org.eclipse.jgit.transport import URIish
	def callback(git):
		import os
		import shutil
		project_exists = os.path.exists(os.path.join(folder, submodule))
		
		if project_exists:
			os.rename(os.path.join(folder, submodule), os.path.join(folder, submodule+'.temporary'))

		try:
			submoduleAddCommand = git.submoduleAdd();
			submoduleAddCommand.setPath(submodule);
			submoduleAddCommand.setURI(uri);
			addLogin(submoduleAddCommand, payload)

			return submoduleAddCommand.call();
		finally:
			if project_exists:
				# gather all files
				source = os.path.join(folder, submodule+'.temporary')
				destination = os.path.join(folder, submodule)
				allfiles = os.listdir(source)
				 
				# iterate on all files to move them to destination folder
				for f in allfiles:
					src_path = os.path.join(source, f)
					dst_path = os.path.join(destination, f)
					if os.path.exists(dst_path):
						if os.path.isfile(dst_path):
							os.remove(dst_path)
						else:
							shutil.rmtree(dst_path)
					os.rename(src_path, dst_path)
				
				os.rmdir(source)
			
	return runGitCommand(folder, "", callback)

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

def getRemoteHostFromUri(uri):
	from java.net import URI
	return URI(uri).getHost()

def getRemoteHost(folder, submodule):
	def callback(git):
		remoteUri = git.getRepository().getConfig().getString("remote", "origin", "url")
	
		return getRemoteHostFromUri(remoteUri)
	
	return runGitCommand(folder, submodule, callback)

def requireLoginForUri(uri):
	from org.eclipse.jgit.transport import NetRC

	netrc = NetRC()
	return netrc.getEntry(getRemoteHostFromUri(uri)) == None
	
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
