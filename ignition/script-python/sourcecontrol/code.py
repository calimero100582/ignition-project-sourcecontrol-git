def runGitCommand(folder, submodule, callback):
	
	git = Git(folder, submodule)
	try:
		return callback(git)
	except:
		pass # do some logging eventually?
	finally:
		git.close()

def Git(folder, submodule):
	from java.io import File
	from org.eclipse.jgit.api import Git
	from org.eclipse.jgit.submodule import SubmoduleWalk
	
	path = File(folder)
	return Git.open(path) if not submodule else Git.wrap(SubmoduleWalk.getSubmoduleRepository(path, submodule))

def isRepositoryValid(folder):
	def callback(git):
		try:
			return git.getRepository().getObjectDatabase().exists()
		except:
			return False

	return runGitCommand(folder, "", callback)
	
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
	
def Fetch(folder, submodule):
	def callback(git):
		fetchCommand = git.fetch()
		
		return fetchCommand.call()
	
	return runGitCommand(folder, submodule, callback)
	
def Pull(folder, submodule):
	def callback(git):
		pullCommand = git.pull()
		
		return pullCommand.call()

	return runGitCommand(folder, submodule, callback)

def Push(folder, submodule):
	def callback(git):
		pushCommand = git.push()
		
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
