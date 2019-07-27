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
