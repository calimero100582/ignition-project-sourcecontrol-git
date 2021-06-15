# Ignition Source Control Management Project
The goal of this project is to be able to manage and version Ignition's projects source files

## Task
- [x]  Find Ignition data directory
- [x]  Display changed files
- [x]  Custom commit message
- [x]  Commit by project
- [x]  Ignition Project Readme.md creator/editor
- [x]  Projects folder remote setup
- [x]  Fetch, Pull and Push
- [ ]  Branch management
- [ ]  Commit history view
- [ ]  Rollback/Reset/Revert
- [ ]  Add project as Submodule
- [ ]  Submodule management
- [ ]  Default Commit message
- [ ]  Link to Azure DevOps
  - Work items
  - Pull requests
  - etc...


### Code to add submodule
	import java.io.File as File;
	from org.eclipse.jgit.api import Git
	import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider as UsernamePasswordCredentialsProvider
	import os

	path = File(self.session.custom.projectsFolder)
	git = Git.open(path)
	addSubmoduleCommand = git.submoduleAdd()
	
	addSubmoduleCommand.setURI("<remove repo uri>")
	addSubmoduleCommand.setPath("<submodule name / project folder>")
	addSubmoduleCommand.setCredentialsProvider( UsernamePasswordCredentialsProvider("<username or github token>", "<password or azure devops token>"));
	
	addSubmoduleCommand.call()
	git.close()


### Code to push submodule
The following code works, but return "not authorized" on Github, with token, even if the push succeed

	import java.io.File as File;
	from org.eclipse.jgit.api import Git
	from org.eclipse.jgit.submodule import SubmoduleWalk
	import org.eclipse.jgit.transport.UsernamePasswordCredentialsProvider as UsernamePasswordCredentialsProvider
	import os

	path = File(self.session.custom.projectsFolder)
	git = Git.wrap(SubmoduleWalk.getSubmoduleRepository(path, "<submodule name / project folder>"))

	pushCommand = git.push()
	pushCommand = pushCommand.setCredentialsProvider( UsernamePasswordCredentialsProvider("<username or github token>", "<password or azure devops token>"));
	pushCommand.call()
	git.close()