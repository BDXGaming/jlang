# JLang
A Python based programming language!

## What is JLang
JLang is a programming language written in python and which can be transpiled into python. However JLang adds support for many common programming features such as 
static typing, the use of {} over indentation, and many other unique features.

JLang does however support native python code via the use of python.<module | method> which allows for the execution of python directly within JLang!
```c#
// This loads the Python print method directly into JLang
load python.print

print("Hello from JLang!")
```
