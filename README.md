# Hello

A simple Android application using VOC, created from [beeware-android-template](https://github.com/eliasdorneles/beeware-android-template).

**This document describes a long and convoluted build process. It uses Java to build the VOC support library and the `dx` tool from the Android SDK. The normal process to build applications using VOC is a lot more streamlined than this, but I wanted to use my own tools for part of it.**

## Prerequisites

You will need to install the Android SDK (or Studio), Python, Java, [DUCK](https://gitlab.com/dboddie/DUCK) and the OpenSSL tools.

## Notes about Building

To build the application, we will do four things:

* Build VOC and a support library using Python and Java.
* Compile the application to class files.
* Convert the class files to a DEX file.
* Package the DEX file with some resources in an APK file.

### Building VOC

Build VOC, as [described in the documentation](https://voc.readthedocs.io/en/latest/background/install.html) but, instead of building the Java support library as suggested, build the Android support library.

To do this, set the `ANDROID_HOME` environment variable to the location of the Android SDK, append the location of the build tools inside the SDK to the `PATH` environment variable, and run `ant`:
```
export ANDROID_HOME=<SDK directory>
export PATH=<SDK directory>/build-tools/<version>:$PATH
ant android
```

The precise locations of the build tools inside the SDK may vary from release to release.

The build process should result in an Android support library being generated and placed in the `dist` directory. This will have a file name like `Python-3.4-Android-support.b7.jar` depending on the version of Python in use and the version of VOC.

Ideally, the support library would only include the files needed to run the application. Some versions of VOC will not compile the support library correctly, so you may need to exclude many modules in order to get it to build.

Copy the support library into the application directory.

### Compile the Application

In the application directory (containing this file), run the compiler like this:
```
voc -v hello
```

This should produce output like this following:
```
Compiling hello/app.py ...
Compiling hello/__init__.py ...
Compiling hello/__main__.py ...
Writing ./python/hello/app.class ...
Writing ./python/hello/app/MainApp.class ...
Writing ./python/hello/__init__.class ...
Writing ./python/hello/__main__.class ...
```

These files will need to be processed before they can be used.

### Converting the Class Files

Make a temporary directory called `temp`:
```
mkdir temp
```

Use the `dx` tool from the Android SDK to convert the class files to a single `classes.dex` file:
```
dx --dex --output=temp/classes.dex --verbose \
    Python-3.4-Android-support.b7.jar \
    python/hello/app.class \
    python/hello/app/MainApp.class \
    python/hello/__init__.class \
    python/hello/__main__.class
```

If this succeeds then we can package the DEX file for deployment.

If it fails then there is a good chance that the compiler is not generating code suitable for conversion to DEX. One solution to this is to remove as many modules from the support library and recompile it. See the troubleshooting section below for guidance.

### Make a Package

Before we can actually make a package, we need to create a key and a signing certificate:
```
openssl genpkey -algorithm RSA -out key.pem -pkeyopt rsa_keygen_bits:2048 -pkeyopt rsa_keygen_pubexp:3
openssl req -new -x509 -days 365 -sha1 -key key.pem -out cert.pem
```

Run the `build.py` script, passing the temporary directory, key and certificate:
```
build.py temp key.pem cert.pem hello.apk
```

If successful, the `hello.apk` file should be created. It can be installed to a connected Android device with the `adb` tool:
```
adb install hello.apk
```

## Troubleshooting

If the support library cannot be converted from a JAR file to part of a DEX file then it may need to be cut down, removing modules that the compiler processes incorrectly. In the VOC distribution, edit the `tools/compile_stdlib.py` file to append problematic modules to the `IGNORE_MODULES` set.

Excluding the following set of modules has been found to help produce a working support library:
```
IGNORE_MODULES = set([
    '__builtins__',
    '__init__',
    '__phello__.foo',
    '_bootlocale',
    '_compat_pickle',   # broken
    '_csv',
    '_dummy_thread',
    '_io',
    '_osx_support',
    '_sre',             # broken
    'antigravity',
    'asynchat',
    'asyncore',         # broken
    'ast',              # broken
    'bdb',
    'bisect',
    'cProfile',
    'calendar',         # broken
    'cgi',
    'cgitb',
    'cmath',
    'cmd',
    'code',
    'codeop',
    'colorsys',
    'configparser',
    'copy',
    'copyreg',          # broken
    'crypt',
    'csv',
    'dis',
    'dummy_threading',
    'ensurepip',
    'fileinput',
    'fnmatch',
    'formatter',
    'fractions',
    'genericpath',
    'getopt',
    'gzip',
    'hashlib',
    'hmac',
    'html',
    'imghdr',
    'imp',
    'importlib',
    'keyword',
    'linecache',
    'locale',
    'macurl2path',
    'mailcap',
    'nntplib',
    'ntpath',
    'nturl2path',
    'opcode',
    'os',
    'pdb',
    'pickletools',
    'pipes',
    'plat-aix4',
    'plat-darwin',
    'plat-freebsd4',
    'plat-freebsd5',
    'plat-freebsd6',
    'plat-freebsd7',
    'plat-freebsd8',
    'plat-generic',
    'plat-linux',
    'plat-netbsd1',
    'plat-next3',
    'plat-sunos5',
    'plat-unixware7',
    'platform',
    'PlatformInterface',
    'poplib',
    'posixpath',
    'pprint',
    'pyclbr',
    'py_compile',
    'queue',
    'random',
    're',
    'reprlib',
    'rlcompleter',
    'runpy',
    'sched',
    'shelve',
    'shlex',
    'site',
    'site-packages',
    'socket',
    'sre_constants',
    'sre_parse',
    'ssl',
    'stat',
    'statistics',
    'stringprep',
    'struct',
    'subprocess',
    'sunau',
    'symbol',
    'symtable',
    'sys',
    'sysconfig',
    'telnetlib',
    'tempfile',
    'textwrap',
    'this',
    'threading',
    'time',
    'tkinter',
    'token',
    'tokenize',
    'tracemalloc',
    'tty',
    'turtle',
    'turtledemo',
    'types',
    'venv',
    'warnings',
    'wave'
])
```
