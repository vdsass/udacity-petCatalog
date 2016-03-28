# Pet_Catalog

**Note: If you already have a vagrant machine installed skip to the 'Fetch the Source Code and VM Configuration' section**

You need to use a virtual machine (VM) to run a web server and a web app that uses it. The VM is a Linux system that runs on top of your own machine.  You can share files easily between your computer and the VM.

### VirtualBox

VirtualBox is the software that runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

**Windows Note:** The Installer may ask you to grant network permissions to Vagrant or make a firewall exception. Be sure to allow this.

## Fetch the Source Code and VM Configuration

**Windows:** Use the Git Bash program (installed with Git) to get a Unix-style terminal.  
**Other systems:** Use your favorite terminal program.

From the terminal, run:

    git clone https://github.com/vdsass/udacity-petCatalog.git

This will create and populate a directory structure named **Pet_Catalog** complete with source code.

## Run the virtual machine!

Using the terminal, change directory to Pet_Catalog (**cd Pet_Catalog**), then type **vagrant up** to launch your virtual machine.

## Running the Pet_Catalog Application

When the virtual machine is running, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.

Navigate to the appropriate directory by typing **cd /vagrant/Pet_Catalog**. This will take you to the folder shared between the virtual and host machines.

Type **ls** to ensure that you are inside the directory that contains pet_catalog_creator.py, pet_catalog_loader.py, pet_catalog_server.py, and two directories named 'templates' and 'static'

Type **python pet_catalog_creator.py** to initialize a 'sqlite' database.

The following step is optional. The application allows you to create your own Pet Families and individual Pets. If you want a pre-defined set of Pet Families and Pets type **python pet_catalog_loader.py** to populate the sqlite database with a few entries.

Type **python pet_catalog_server.py** to run the Flask web server. In your browser visit **http://localhost:8000** to view the Pet Catalog list of Pet Families.  You should be able to view, add, edit, and delete Pet Families and Pets.

Issues:
1. Navigation bar:
    a. Figure out how to write messages to the navigation bar.
    b. Clear the login buttons on child pages.
        i. the buttons should indicate 'Log off', 'Log out', ...

2. Login:
    a. Can login only from home page.
    b. Child pages imply you can login, but there's no action.

3. All Child pages:
    a. 'row' width is too wide.

4. Family of Pet <Family Name> (i.e., Cats, Dogs, ...)
    a. Occassionally, 'None' is displayed after banner
    b. Edit, Remove, Add buttons need to be justified right
        i. and change color appropriately

    c. Add labeling that displays each pet's information
    d. Pet Families look OK. Need larger font and separation between rows
        i. length of 'row' is what I want

5. New Family - Add Pet to the Family of <>
    a. Add button needs space after description text block.
    b. Field Labels are not in-line with field

6. Add A Pet
    x. Supply all fields

6. Delete Pet
    x. deletes record on Cancel
    x. does not delete record on Remove

