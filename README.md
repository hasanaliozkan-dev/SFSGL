![Badge](https://img.shields.io/pypi/v/SFSGL.svg)
[![License - MIT 3-Clause](https://img.shields.io/pypi/l/sfsgl.svg)](https://github.com/hasanaliozkan-dev/sfsgl/blob/main/LICENSE)
[![PyPI - Downloads](https://static.pepy.tech/badge/sfsgl)](https://pepy.tech/projects/sfsgl)
# **SFSGL (Simple File Sharing Gathering Library)**

### Description
This is a simple file-sharing and gathering library. It provides a simple interface to share and gather files. The library is implemented using Flask and Flask-RESTful. The library provides two interfaces, one for sharing files and the other for gathering files. The library is implemented in a way that it can be used as a standalone application. This library's main purpose is to apply programming course assignments and quizzes safely and securely (without using ChatGPT, Copilot, etc.). For example, in your lab, if you have an intranet you can share your programming assignments with your students and gather their solutions without using any other tools. They only reach your server and they can't connect outside of the lab network.

### Installation
You can install the library using pip.

```bash
pip install sfsgl
```

### Docker installation and running
You can run this docker command to build and run the application using the docker container.
```bash
docker build -t my-python-app .
docker run -p 5001:5001 -p 5002:5002 my-python-app
```



### Usage
You can use the library as a standalone application. You can run the following command to start the application.

```bash
python -m sfsgl
```

### Example Usage
```python 
    from SFSGL.sfsgl import SFSGL

    if __name__ == '__main__':
        session = SFSGL(shared_folder_path= "exact_path_to_shared_folder")
        session.start()
```

!!! You'll need to specify the the exact path of the shared folder otherwise the library cannot find your folder path. 



### Configuration Parameters

- shared_folder_path : path to the folder where the files will be shared, default is "shared"

- gathered_folder_path : path to the folder where the files will be gathered, default is "gathered"

- allowed_extension_to_gather : list of allowed file extensions to gather, default is ```["py","zip"]```

- allowed_extension_to_share : list of allowed file extensions to share, default is ```["py","zip","txt"]```

- allow_multiple_upload : boolean value to allow multiple file upload per user, default is ```"True"```

- add_ip_to_file : boolean value to add the IP address of the user to the file name, default is ```"True"```

- shared_port : port number to file sharing interface, default is ```5001```

- gathered_port : port number to file gathering interface, default is ```5002```






### Contribution
You can contribute to the library by forking the repository and sending a pull request. 
You can also report bugs and feature requests by creating an issue. Btw. the author has
no idea about the security of the library. If you find a security issue do not hesitate 
to fix it  and send a pull request. 



### License

MIT License

Copyright (c) 2025 Hasan Ali ÖZKAN

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
