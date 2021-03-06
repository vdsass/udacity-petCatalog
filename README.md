#Pet Catalog

**Note:** If you already have a vagrant machine installed skip to the 'Fetch the Source Code and VM Configuration'

You need to use a virtual machine (VM) to run a web server and a web app that uses it. The VM is a Linux system that runs on top of your own machine.  You can share files easily between your computer and the VM.

### VirtualBox

VirtualBox is the software that runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

#Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program.

From the terminal, run:

    git clone https://github.com/vdsass/udacity-petCatalog.git

This will create and populate a directory named **Pet_Catalog** complete with source code.

## Run the virtual machine!

Using the terminal, change directory to Pet_Catalog (**cd Pet_Catalog**), then type **vagrant up** to launch your virtual machine.

# Run the Pet_Catalog Application

When the virtual machine is running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.

Navigate to the appropriate directory by typing **cd /vagrant/Pet_Catalog**. This will take you to the folder shared between the virtual and host machines.

Type **ls** to ensure that you are inside the directory that contains pet_catalog_creator.py, pet_catalog_loader.py, pet_catalog_server.py, and two directories named 'templates' and 'static'

Type **python pet_catalog_creator.py** to initialize a 'sqlite' database.

The following step is **optional**. The application allows you to create your own Pet Families and individual Pets. If you want a pre-defined set of Pet Families and Pets type **python pet_catalog_loader.py** to populate the sqlite database with a few entries.

Type **python pet_catalog_server.py** to run the Flask web server. In your browser visit **http://localhost:8000** to view the Pet Catalog list of Pet Families.  You should be able to view, add, edit, and delete Pet Families and Pets.

## Third Party Login

Pet Catalog will allow create, update, and delete operations on the database only when a user is logged in (signed on). Google Plus (G+) and Facebook are used by Pet Catalog for third-party verification, authentication, and login.

See the developer's pages on Google and Facebook for credetials setup (https://developers.google.com/api-client-library/python/auth/web-app#overview).

pet_catalog_server.py uses two files to acquire verification information. One file for Google Plus **(gplus_client_secrets.json)** and one file for Facebook verification and authentication **(fb_client_secrets.json)**. The two files are in the application's root directory and contain placeholders for the respective values.

Update the **gplus_client_secrets.json** file with your 'client_id' and 'client_secret.' Also, note the project_id name, the redirect_uris, and javascript_origins paths.

Update the **fb_client_secrets.json** file with your 'app_id' and 'app_secret.'


Google Plus - Example gplus_client_secrets.json file

```
{"web": { "client_id":"YOUR GOOGLE CLIENT ID",
		  "project_id":"petcatalog",
		  "auth_uri":"https://accounts.google.com/o/oauth2/auth",
		  "token_uri":"https://accounts.google.com/o/oauth2/token",
		  "auth_provider_x509cert_url":"https://www.googleapis.com/oauth2/v1/certs",
		  "client_secret":"YOUR GOOGLE CLIENT SECRET",
		  "redirect_uris":["http://localhost:8000/gconnect"],
		  "javascript_origins":["http://localhost:8000"]
		}
}
```

Facebook - Example fb_client_secrets.json file
```
{"app": {
            "app_id":"YOUR FACEBOOK APP ID",
            "app_secret":"YOUR FACEBOOK APP SECRET"
        }
}
```
## json end points

Verify json end points by navigating to the following URLs:
```
    http://localhost:8000/families/json/
    http://localhost:8000/family/n/pets/json/
        Where 'n' is the family id of the Pet Family
```
# Known Issues:
1. Navigation bar:
    a. Figure out how to write messages to the navigation bar.
    b. Clear the login buttons on child pages, or
        i. the buttons should indicate 'Log off', 'Log out', ...

2. Login:
    a. Can login only from home page.
    b. Child pages imply you can login, but there's no action.

3. All Child pages:
    a. 'row' width is too wide.

4. Family of Pet <Family Name> (i.e., Cats, Dogs, ...)
    a. Edit, Remove, Add buttons need to be justified consistently
        i. and change color appropriately


