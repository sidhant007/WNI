# We Not I (wni) : Cheapest distributed computing solution, utilising other people's pc power

A CLI based application
- Allows users to run distributed codes on other peoples pc(via internet)
- Easier to use than other cluster based solutions
- Uses a virtual currency that is earned by lending own pc power & spent by using others pc power

See https://devpost.com/software/we-not-i-wni for a more detailed description

How to install wni:
1. Download this wni/ directory
2. Ensure ```setuptools``` is installed on your PC for ```Python3```
3. Run ```python3 setup.py install```

Now you can simply type ```wni --help``` to check.

How to run the host as local machine:
1. Download the ../server/ directory on your local pc.
2. Run ```python3 main.py``` in ../server/ directory.
3. Now use all the commands of ```wni``` with the flag ```-dev``` to connect to the localhost:8080 instead of the the prod version
