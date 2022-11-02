# JLang
A Python based programming language!

## What is JLang
JLang is a programming language written in python and which can be transpiled into python. However JLang adds support for many common programming features such as 
static typing, the use of {} over indentation, and many other unique features.

JLang does however support native python code via the use of python.<module | method> which allows for the execution of python directly within JLang!
```c#
// This loads the Python print method directly into JLang
load python.print
load python.module.sys

print("Hello from JLang!")

// Demonstrating the use of a python module in JLang
sys.stdout.write("Test\n")

// This is a JLang string
String test = "test"

for i in range(5){
  // A JLang formatted string
  print(f"Number: ${i}")
}
```
