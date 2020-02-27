# packagereader
Python script to create a static html page structure that
provides information (description, dependencies and reverse dependencies)
about installed packages on Debian/Ubuntu systems.

Requires Python 3.

Usage instructions: Run and follow the on-screen instructions (if any);
Creates the following files and directories (deleting any existing in
'packages' directory and overwriting others):
index.htm
style.css
packages/
packages/*.htm (one for each package installed)
packages/style.css
