#!/usr/bin/python
# coding: utf-8
#
# Packagereader v0.001
# Python script to create a static html page structure that
# provides information (description, dependencies and reverse dependencies)
# about installed packages on Debian/Ubuntu systems.
#
# Requires Python 3.
#
# Usage instructions: Run and follow the on-screen instructions (if any);
# Creates the following files and directories (deleting any existing in
# 'packages' directory and overwriting others):
# index.htm
# style.css
# packages/
# packages/*.htm (one for each package installed)
# packages/style.css
#
import re, os, sys, shutil


# MAIN
def main():
    
    path_to_data = "/var/lib/dpkg/status"

    print("Debian/Ubuntu Packagereader v0.001")
    while not (os.path.isfile(path_to_data)):
        print("File '" + path_to_data + "' not found.")
        path_to_data = input("Please enter filename with full path"
                             "(or Ctrl+C to quit): ")

    data = open(path_to_data, 'r', encoding='utf-8').read()

    packages_count = data.count("Package: ")
    print("Number of packages installed: %d" % packages_count)

    packages = []
    dependencies = [[] for i in range(packages_count)]
    descriptions = ["" for i in range(packages_count)]

    for i in range(packages_count):
        # Let's split the data into package-by-package chunks
        # on each iteration
        data_for_this_run = ((data.split("Package: ", i+2)[i+1]).
                             split("Package:",1)[0])
        # Let's get the package name
        p_name = data_for_this_run.split("\n",1)[0]
    
        # As there can be various types of fields following
        # Description, let's eliminate them from the actual
        # description field
        p_desc = data_for_this_run.split("Description: ",1)[1]
        p_desc = p_desc.replace("Homepage:", "SPLIT_HERE")
        p_desc = p_desc.replace("Original-Maintainer:", "SPLIT_HERE")
        p_desc = p_desc.split("SPLIT_HERE",1)[0]
    
        p_dep = ['NONE']
        if (data_for_this_run.count("\nDepends:") == 1):
            p_dep = (data_for_this_run.split("\nDepends: ",1)[1]).split("\n",1)[0]       
            # Let's remove the version information in parentheses
            # to get just the dependency package names
            p_dep = re.sub("\([a-zA-Z0-9<>= \.].*?\)", "", p_dep)
            p_dep = p_dep.replace(" ", "")
            p_dep = p_dep.split(",")        
            # Let's remove package name duplicates that were created
            # due to the version number removal
            p_dep = list(set(p_dep))        
    
        packages.append(p_name)
        descriptions[i] = p_desc
        dependencies[i] = p_dep

    create_html(packages, dependencies, descriptions)


def create_html(packages, dependencies, descriptions):
    n = len(packages)
    html_boilerplate = ("<!doctype html>\n<html>\n<meta charset='utf-8'>\n"
                "<head>\n<link rel='stylesheet' href='style.css'>\n</head>\n"
                "<body>\n")
    # css minified.
    css_style = ("body{background-color:#b0bdcb;color:#000;font-family:"
        "'Courier New',monospace;font-size:14px;padding:16px}div{width:720px;"
        "padding:16px;margin:5;background-color:#d5dbe3;box-shadow:5px 5px "
        "#758699}.div_title{font-weight:700}a:link{color:#976cb8}"
        "a:visited{color:#5f3c7b}a:hover{color:#c09ddc}")
    
    if os.path.isdir('packages'):
        print("Folder 'packages' already exists. ")
        a = ""
        while not (a == "N" or a == "n" or a == "Y" or a == "y"):
            a = input("Do you wish to delete existing folder and re-create "
                      "all content? (Y/N) ")

        if (a == "Y" or a == "y"):
            print("Deleting existing folder and contents.")
            shutil.rmtree('packages')
        else:
            sys.exit()
    
    try:
        os.mkdir('packages')
    except:
        print("Cannot create folder 'packages'. Please check access rights.")
        sys.exit()
        
        
    print("Creating files...")
    # Individual .htm files for packages:
    for i in range(n):
        # Let's do some preformatting for any multiline
        # descriptions:
        descriptions[i] = descriptions[i].replace("\n", "<br>")
        
        f = open('packages/' + packages[i] + '.htm', 'w+')
        
        f.write(html_boilerplate)
        
        
        # Package title + description
        f.write("<div id='pkg_name'><span class='div_title'>Package:</span> "
                + packages[i] + "</div>\n")
        
        f.write("\n<br><br><div id='descr'>\n<span class='div_title'>"
                "Description: </span><br>\n" + descriptions[i] + "</div>\n")
        
        
        # Dependencies
        if not (dependencies[i][0] == "NONE"):
            dependencies[i].sort()
            f.write("\n<br><br><div id='deps'><span class='div_title'>"
                    "Dependencies:</span><br>\n")
            for j in range(len(dependencies[i])):
                
                # Let's check if the dependency string contains
                # alternatives.
                dep_alts = dependencies[i][j].count("|")
                if (dep_alts > 0):
                    alts = dependencies[i][j].split("|",-1)
                    
                    for k in range(dep_alts+1):
                        alt_delimiter = " | "
                        
                        if (alts[k] in packages):
                            f.write("<a href='" + alts[k] + ".htm'>"
                                   + alts[k] + "</a>" + alt_delimiter)
                        else:
                            f.write(alts[k] + alt_delimiter)
                
                
                # Simple case for non-alternative-containing deps.
                else:
                    if (dependencies[i][j] in packages):
                        f.write("<a href='" + dependencies[i][j] + ".htm'>"
                                + dependencies[i][j] + "</a><br>")
                    else:
                        f.write(dependencies[i][j] + "<br>")
            f.write("</div>")
            
            
        # Reverse dependencies
        rev_deps = []
        for j in range(n):
            temp_deps = []
            for k in dependencies[j]:
                temp_deps.extend(k.split("|",-1))
            
            if packages[i] in temp_deps:
                rev_deps.append(packages[j])
                
        if not (len(rev_deps) == 0):
            rev_deps.sort()
            f.write("\n<br><br><div id='rev_deps'><span class='div_title'>"
                    "Reverse Dependencies:</span><br>\n")
            for j in range(len(rev_deps)):
                f.write("<a href='" + rev_deps[j] + ".htm'>"
                       + rev_deps[j] + "</a><br>")
                
            f.write("</div>")
        
        f.write("\n</body>\n</html>")
        f.close()
        
        
    # Index:
    pkgs_sorted = sorted(packages)
    f = open('index.htm', 'w+')
    f.write(html_boilerplate)
    f.write("<div><span class='div_title'>Packages Index:</span><br><br>\n")
    for i in range(n):
        f.write("<a href='packages/" + pkgs_sorted[i] + ".htm'>" +
                pkgs_sorted[i] + "</a><br>\n")
    f.write("\n</div>\n</body>\n</html>")
    f.close()
    
    # Style sheets for both packages/ and rootdir
    f = open('packages/style.css', 'w+')
    f.write(css_style)
    f.close()
    f = open('style.css', 'w+')
    f.write(css_style)
    f.close()
    print("Done!")

if __name__ == '__main__':
    main()