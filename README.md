Assignment 2
Due date: August 6th
Introduction
In this assignment, you will create software that can model mazes, both two-dimensional and three-dimensional. You will also write code to solve these mazes. You will see that with the correct setup, the exact same algorithm can solve both 2d and 3d mazes!
Consider the following 2-dimensional maze with 7 rows and 7 columns:
+--+--+--+--+--+--+--+

|S |              |  |

+  +  +  +--+--+  +  +

|  |  |        |     |

+  +--+--+--+  +--+  +

|     |        |     |

+--+  +  +--+--+--+--+

|  |  |  |           |

+  +  +  +  +--+--+  +

|  |  |           |  |

+  +  +--+--+--+--+  +

|  |     |           |

+  +--+  +  +--+--+  +

|           |      F |

+--+--+--+--+--+--+--+ 
What makes this a good maze? There's two key properties that it satisfies:
1. Connectedness. Every cell is reachable from any other cell. This is what makes a maze feel like a maze; it's always possible for you to go in the wrong direction.
2. Unique Paths. There is never more than one way to get from one cell to another (without backctracking). In particular, this means there is exactly one way to solve the maze.
These properties are two sides of the same coin: the first says that between any two cells there is _at least_ one simple path, and the second says that between any two cells there is at most one simple path. Simple means you never visit the same cell twice. Together, these properties make the maze a tree.
In this assignment, you will model a maze as a tree where the nodes are the cells of the grid. The root node is the starting cell, and the subtrees of a cell are the cells directly connected to it in the maze (i.e. there's no wall between them). You will write code to construct this tree given a flat description of the maze and then write functions that operate on the tree structure.
General Guidelines
Please read this handout carefully and ask questions if there are any tasks you do not understand.
Generally, if there are certain method behaviours that were not specified, we leave it up to your interpretations, but please do ask on Piazza first to make sure you are not making unreasonable assumptions that you will be deducted marks for.
The tasks are not designed to be equally difficult, or even in increasing order of difficulty. They are just laid out in logical order.
Although implementing a complex application can be challenging at first, we will guide you through a progression of tasks, in order to gradually build pieces of your implementation. Your responsibility includes reading through this handout and the starter code we provide, carefully, and understanding how the classes work together in the context of the application.
Coding Guidelines 
These guidelines are designed to help you write well-designed code that will adhere to the interfaces we have defined (and thus will be able to pass our test cases).
You must:
write each method in such a way that the docstrings you have been given in the starter code accurately describe the body of the method.
write test methods where indicated. These will not be graded, but will be required for any remark requests.
We recommend that you go farther and write tests for all methods that you implement, even private ones.
You do NOT need to write doctests for the functions and methods in this assignment. The setup required to do the testing would create disruptively long docstrings.
incorporate inheritance into your code, as described in the Your Task section.
avoid writing duplicate code.
  
You must NOT:
modify any code that you are given. In particular, you must not:
change the parameters, parameter type annotations, or return types in any of the methods you have been given in the starter code.
add or remove any parameters in any of the methods you have been given in the starter code.
change the type annotations of any public or private attributes you have been given in the starter code.
create any new public attributes.
create any new public methods that do not override or extend a method of the same name in a parent class.
create any new top-level functions, that is, functions defined outside any class.
write code that mutates objects unnecessarily.
add any more import statements to your code.
create an alias between an attribute (that is of a mutable type) of a class and a parameter to a method; this could lead to nasty side effects. 
You may need to:
create new private methods for the classes you have been given.
if you create new private methods you must provide type annotations for every parameter and return value. You must also write a full docstring for this method as described in the function design recipeLinks to an external site., except that you do not need to write any doctests, as noted above.
create new private attributes for the classes you have been given.
if you create new private attributes you must give them a type annotation and include a description of them in the class's docstring as described in the class design recipe
import more objects from the typing module
      
While writing your code you can assume that all arguments passed to the methods you have been given in the starter code will respect the preconditions outlined in the methods' docstrings.
Your Task
Complete the classes and methods given to you in the starter code to create a piece of software that can model and solve both 2d and 3d mazes. 
You are encouraged to complete this assignment in the order outlined in the tasks below but you may choose a different order if you wish.
Make sure you complete each "Test your code!" section before moving on to the next task to make sure that your code works as expected.
In each of the tasks below you are encouraged to read questions in the "Something to think about" sections. You are not required to answer these questions for this assignment but thinking about them might help you write better code!
Task 1: Get the starter code and read the documentation
Download the zip file that contains the starter code [hereDownload here].
Unzip the file and place the contents in pycharm in your a2 folder (remember to set your a2 folder as a sources root)
You should see the following files:
maze_2d.py

maze_3d.py

maze_node.py

tests.py

example_tests.py

visualizer.py

a folder called samples containing several .json files named like maze2d-HxW.json or maze3d-HxWxF.json.
For this assignment, you will be required to edit and submit all Python files except for visualizer.py and example_tests.py.
If you look at these files you will notice that you have been given the headers and docstrings for many classes and methods, which describe how you are expected to implement them. You will complete them in the rest of this assignment's tasks.
The visualizer.py file is given to you but will not work until you finish some of the initial tasks (tasks 1-5). It will render a 2d or 3d maze in an interactive pygame window. To run it, use the command
# to visualize the sample 7x7 2d maze

python3 visualizer.py 2d samples/maze2d-7x7.json

# to visualize the sample 7x7x2 3d maze

python3 visualizer.py 3d samples/maze3d-7x7x2.json

Again, these commands will not work until you finish tasks 1-5.
A picture!
To help you test your code, we've included some pictures of what the visualizer should render for samples/maze2d-7x7.json and samples/maze3d-7x7x2.json.
If you've correctly implemented the build tree logic for 2d mazes (tasks 2,3,4), the command python3 visualizer.py 2d samples/maze2d-7x7.json should result in a pygame window like this.
visualizer-maze2d-7x7.png
If you've correctly implemented the build tree logic for 3d mazes (tasks 2,3,5), the command python3 visualizer.py 3d samples/maze3d-7x7x2.json should result in a pygame window like this.
visualizer-maze3d-7x7x2.png
Test your code!
Each task has a section about testing your code. 
In the tests.py file, you will write your own tests for your code as you work through the assignment. You will submit this file, but it's empty right now!
The file example_tests.py contains some tests we have written for you. This is not a complete set of tests, but will help you a little. Right now all of the tests should fail because you haven't written any code yet!
Something to think about!
You will be submitting code split across multiple files. Open up each of the files and look at which functions and classes are defined in each file. Why do you think the files were organized in this way?  Is there a different way we could have organized these files?
Task 2: Write the initializer for MazeNode
In maze_node.py, you will find a class MazeNode with a number of methods and attributes. Read the docstring for the class and the initializer carefully, and then implement __init__.
Task 3: Write the initializers for MazeNode2D and MazeNode3D
In maze_2d.py, you will find a class MazeNode2D. In maze_3d.py, you will find a class MazeNode3D. Both classes inherit from MazeNode. Read the docstrings for both classes carefully and implement their initializers.
Task 4: Implement build_maze_tree_2d
In maze_2d.py, implement the build_maze_tree_2d function, which takes a flat description of a 2d maze and returns a MazeNode2D object which is the root of a tree representing the maze.
The input to this function is a list of lists of strings. Each string represents a single cell in the maze and describes which walls it has as well as whether it is the starting cell, the finishing cell, or just a regular cell. Each string consists of 4 binary digits that indicate whether there is a wall above the cell, below it, to the left, and to the right respectively. The string might optionally be followed by a single character describing the kind of the cell: "S" for "start", "F" for "finish", and no character for "regular".
See any of the maze2d-* files in the samples/ folder for examples of what this list of list of strings looks like.
Hints and Reminders
See the parse_cell function in maze_node.py. Use it!
The x coordinate of a MazeNode2D represents its row. When x = 0, the cell is at the top and as x increases, the cell moves downwards. Thus, the cell "above" (x, y) is the cell (x - 1, y). 
Similarly, the y coordinate represents its column. When y = 0, the cell is at the left and as y increases, the cell moves to the right. Thus, the cell "to the left of" (x, y) is the cell (x, y - 1).
Be very careful here! It is important that you interpret these cell-strings correctly. Getting this wrong will lead you astray the rest of the assignment. To make sure things are working correctly, reference your implementation against the pictures given at the beginning of the handout.
Note. Once you have completed this task, the visualizer should work for 2d mazes.
Task 5: Implement build_maze_tree_3d
In maze_3d.py, implement the build_maze_tree_3d function, which takes a flat description of a 3d maze and returns a MazeNode3D object which is the root of a tree representing the maze.
The input to this function is a list of lists of lists of strings. Each string represents a single cell in the maze and describes which walls it has as well as whether it is the starting cell, the finishing cell, or just a regular cell. Each string consists of 6 binary digits that indicate whether there is a wall in the (x+1), (x-1), (y+1), (y-1), (z+1), and (z-1) directions respectively. The string might optionally be followed by a single character describing the kind of the cell: "S" for "start", "F" for "finish", and no character for "regular".
See any of the maze3d-* files in the samples/ folder for examples of what this list of list of strings looks like.
Hints and Reminders
See the parse_cell function in maze_node.py. Use it!
Be very careful here! It is important that you interpret these cell-strings correctly. Getting this wrong will lead you astray the rest of the assignment. To make sure things are working correctly, reference your implementation against the pictures given at the beginning of the handout.
Note. Once you have completed this task, the visualizer should work for 3d mazes.
Task 6: Implement MazeNode.get_root
Implement the get_root method of MazeNode in maze_node.py.
Task 7: Implement MazeNode.make_start
Implement the make_start method of MazeNode in maze_node.py.
Task 8: Implement MazeNode.make_finish
Implement the make_finish method of MazeNode in maze_node.py.
Task 9: Implement MazeNode.preorder_solve
Implement the preorder_solve method of MazeNode in maze_node.py.
Task 10: Implement MazeNode.levelorder_solve
Implement the levelorder_solve method of MazeNode in maze_node.py.
Something to think about 
In tasks 9 and 10, you wrote code to automatically solve a maze. Notice how the same algorithm works for MazeNode2D and MazeNode3D. Do you think the algorithm could work for any maze? What's really going on here?
Marking Scheme
5% A2 Quercus quiz
90% A2 submission on MarkUs
5% example tests
75% hidden tests
10% PyTA (there must be no errors at all, see related piazza post)
Final Task! Submit your work
You've almost finished and now it is time to hand in your work!
BUT BEFORE YOU SUBMIT:
Take some time to polish up your code This not only will improve your mark, but  it also feels good to make your code look its best! Here are some things you can do:
Pay attention to any violations of the Python style guidelines that PyCharm points out. Fix them!
In each file you will submit, run the provided python_ta.check_all(...) code to check for errors. Fix them!
Make sure the tests.py file contains at least the recommended tests from the tasks above.
Check any docstrings that you have written to make sure they are precise and complete and that they follow the conventions of the Function Design Recipe and the Class Design Recipe (but as noted above, you do NOT need to write docstring examples on this assignment, as they would be disruptively long).
Remove any code you added just for debugging, such as print function calls.
Remove any TODO comments where you have added the necessary code.
Take pride in your gorgeous code! This assignment is a significant piece of software, and you should be proud of the work you’ve done!
Submission Guidelines:
Login to MarkUs, find your A2 entry and click on it.
DOUBLE CHECK AGAIN THAT YOUR CODE RUNS!!
Submit the following files only:
maze_node.py
maze_2d.py
maze_3d.py
tests.py
Run the self-test provided on MarkUs. Are there any tests that fail? Are there any python-ta errors that you should fix? Your code will be tested on MarkUs, so it must run in that environment!
Download the files you submitted and make sure you're submitting the right version of your code!
If you make any changes to your code, make sure to submit the updated files to MarkUs before the deadline -- and run the self-test again!
Regrades:
In order to submit a valid remark request, you must also have submitted tests that cover the scenario in which you are submitting a remark request for. More details will be given after the assignment grades are released.
Appendix 1: An explanation of some pieces of the starter code (OPTIONAL).
There are parts of the starter code that involve Python features that not been explained in class. It is not absolutely necessary to understand them to complete this assignment but a brief explanation of each will be provided below for those of you who are interested: 
if TYPE_CHECKING: :
Pycharm does a lot of work in order to highlight problematic code and give us hints as to how to improve the code we are writing as we are writing it. In order to do this, Pycharm constantly analyzes your code by running it through a program called a type checker. The TYPE_CHECKING variable is True only when a type checker is analyzing our code and False when we run our code normally. This lets us define a block of code that we normally don't want to run but is useful for the type checker.

Extra Reading:
- https://docs.python.org/3/library/typing.html#typing.TYPE_CHECKINGLinks to an external site.

- https://stackabuse.com/python-circular-imports/Links to an external site.
@pytest.fixture

This is a part of the pytest library that lets us mark that a function should be treated as a "fixture". In testing, a fixture is an object that can be used in multiple tests. Before each test runs, a fixture object is created if needed by running the fixture function and getting its return value. That fixture object is then passed as a parameter to the test. A test can indicate which fixtures it needs by including a parameter that has the same name as the fixture function.
You do NOT need to use fixtures when writing your tests in the tests.py file.

Extra Reading:
- https://docs.pytest.org/en/latest/fixture.htmlLinks to an external site.
Classes in pytest:
You might have noticed that the tests in example_tests.py are organized into classes. This is simply a way to keep your tests organized and make it clear which groups of tests logically go together. You are not required to write your tests in tests.py in this way but you may if you wish.
Extra Reading:
- https://docs.pytest.org/en/latest/getting-started.html#group-multiple-tests-in-a-classLinks to an external site.
