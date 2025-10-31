# Pandora coding style

A very brief introduction to Pandora coding conventions. LArContent does have a .clang-format file to enforce conventions, but here's an outline.

## Class, function and variable naming conventions

Pandora uses camel case for naming classes, functions and variables. [Camel case](https://en.wikipedia.org/wiki/Camel_case) is the convention by which words or abbreviations in the middle of a phrase begin with a capital letter. Classes and functions use **upper camel case** and so also start with a capital letter:

```C++
void MyClassName::MyFunctionName();
```

Non-class member variables use **lower camel case**, starting with a lower case letter:

```C++
int myVariableName{};
```

For member variables in classes, the camel case convention is followed, but with a `m_` prefix to denote the member variable status:

```C++
int m_myMemberVariableName;
```

The use of underscores between (lowercase) words and abbreviations in phrases is known as [snake case](https://en.wikipedia.org/wiki/Snake_case) (which is the preferred coding style for Python variables and functions, with upper camel case used for class names).

More generally, names should be as descriptive as reasonably possible. So a Monte Carlo particle list might be called `mcParticleList`. Variables that are pointers are prefixed with a lowercase `p` to indicate that they are pointer types, so a pointer to a Monte Carlo particle list might take the name `pMCParticleList`.

## Variable initialisation

Local variables should be initialised at the time of declaration (i.e. when you state the variable name and its type), while class member variables should be initialised in the constructor initialisation list. Historically direct initialisation has been preferred over copy initialisation, as it is more efficient:

```C++
int myVariableName = 0;   // Copy initialisation
int myVariableName(0);    // Direct initialisation
```

Unfortunately, direct initialisation is not always syntactically correct - it can't be used for arrays for example. A solution to this is to use brace initialisation, which is functionally equivalent to direct initialisation:

```C++
int myVariableName{0};    // Brace initialisation
```

This allows for a consistent form of initialisation across variable types.

Constructor initialisation lists are defined for each constructor of a class and have the form:

```C++
MyClassName::MyClassName() :
    m_myVariable1{0},
    m_myVariable2{0},
    m_myVariable3{0}
{
    ...
}
```

with each variable initialised in the order in which it was declared in the class.

## Formatting

Tab indentations should be 4 spaces wide (and should be converted to spaces - any half-way decent editor will have settings to do this for you). White space should be used sparingly and to aid code readability. When starting code blocks (e.g. functions, for loops), the curly braces should reside on a line on their own, for example:

```
for (const auto element : list)
{
    ...
}
```

Note also the space between `for` and the opening parenthesis (do not include a space between the end of a function name and the opening parenthesis for the argument list).

It's also useful to add new lines around variable declaration blocks (no leading newline is required if the preceding line contains a curly brace):

```
...
{
    int myVariable1{0};
    int myVariable2{0};

    // Next code block starts here
    ...
```

One exception to this is for loop variables requiring declaration prior to a loop, where a newline between the variable declaration block and the `for` loop is unnecessary.

If code blocks related to `for` loops or conditional statements are only a single line long, the curly braces should be omitted around the associated block, for example:

```
if (condition)
    return;
```

## Scope

In general, declare variables where you need them, don't simply declare all variables at the beginning of a function (for example). If a variable is only to be used within a particular loop, declare it there (or immediately before it, if it has to be initialised only once prior to the loop). By limiting the scope you reduce the risk of errors, you'll get useful error messages if you do use the variable outside of its intended scope and the compiler will be better able to optimise your code.
