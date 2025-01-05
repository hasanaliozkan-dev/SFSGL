
# **SFSGL (Simple File Sharing Gathering Library)**

### Description
This is a simple file sharing and gathering library. It provides a simple interface to share and gather files. The library is implemented using Flask and Flask-RESTful. The library provides two interfaces, one for sharing files and the other for gathering files. The library is implemented in a way that it can be used as a standalone application. The main purpose of this library is applying programming course assignments and quizes in a safe and secure way (without using of ChatGPT, Copilot, etc.). For example in your lab if you have an intranet you can share your programming assignments with your students and gather their solutions without using any other tools. They only reach your server they can't connect outside of the lab network.

### Installation
You can install the library using pip.

```bash
pip install sfsgl
```

### Docker installation and running
You can run this docker command to build and run the application using docker container.
```bash
docker build -t my-python-app .
docker run -p 5001:5001 -p 5002:5002 my-python-app
```



### Usage
You can use the library as a standalone application. You can run the following command to start the application.

```bash
python -m sfsgl
```




### Configuration Parameters

- shared_folder_path : path to the folder where the files will be shared, default is "shared"

- gathered_folder_path : path to the folder where the files will be gathered, default is "gathered"

- allowed_extension_to_gather : list of allowed file extensions to gather, default is ```["py","zip"]```

- allowed_extension_to_share : list of allowed file extensions to share, default is ```["py","zip","txt"]```

- allow_multiple_upload : boolean value to allow multiple file upload per user, default is ```"True"```

- add_ip_to_file : boolean value to add the ip address of the user to the file name, default is ```"True"```

- shared_port : port number to file sharing interface, default is ```5001```
- gathered_port : port number to file gathering interface, default is ```5002```





### Contrubution
You can contribute to the library by forking the repository and sending a pull request. You can also report bugs and feature requests by creating an issue.
Btw. the author has no idea about the security of the library. If you find a security issue do not hesitate to fix is  and send a pull request. 



### License

