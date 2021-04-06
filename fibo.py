import subprocess
import math
import argparse
import platform

parser = argparse.ArgumentParser(description="Generate a Fibonacci spiral")

parser.add_argument('-l','--lua',help="Use lualatex to compile document", action="store_true")
parser.add_argument('-x','--xe',help="Use xelatex to compile document", action="store_true")
parser.add_argument('-v','--view',help="View PDF afterwards", action="store_true")

args = parser.parse_args()

SCALE = 1
PHI = 0.5*(5**0.5-1) # scale factor
LEN = 8 # how many iterations
D = 144 # angle (in degrees) for each arc
R = 5. # radius of largest circle
SA = 30 # start angle

# Set TeX engine
TEX = "pdflatex"
if args.lua:
    TEX = "lualatex"
if args.xe:
    TEX = "xelatex"

# If requested, how to view the PDF afterwards
SHOW = args.view

if platform.system() == "Linux":
    OPEN = "xdg-open" # Linux
elif platform.system() == "Darwin":
    OPEN = "open" # Mac OS
else:
    OPEN = "" # Dunno what to do for Windows
    SHOW = False

# this is a bit wasteful, but I think a simple thing that works is probably better than a complicated calculation. 
def curve(n):
    """Plot a curve that goes in different directions depending on the binary expansion of the argument"""
    r = R
    a = SA
    direction = +1 
    out = "\draw[color=black] "
    x = 0
    y = 0
    if n == 0:
        out += "(0,0) "
    
    for i in range(LEN):
        if n%2 == 1:
            direction *= -1
            a = (a+180) % 360 # switch direction and reduce radius
            r *= PHI
        if n == 1: # are we ready to start drawing?
            out += f"({x},{y}) "
        if n <= 1: # are we drawing?
            out += f"arc[radius={r}, start angle={a}, delta angle={D*direction}] "
        else: # update starting point of next maybe-arc
            x += -r*math.cos(a * math.pi/180) + r*math.cos( (a + D*direction) * math.pi/180)
            y += -r*math.sin(a * math.pi/180) + r*math.sin( (a + D*direction) * math.pi/180)
            
        a = (a+direction*D) % 360
        r *= PHI # reduce radius
        n >>= 1
    return out + ";"

def curves():
    """plot all of the possible curves"""
    return "\n".join([curve(i) for i in range(2**LEN)])

def full_file():
    """Use standalone class for single-image documents."""
    out = r"""\documentclass[border=10pt,tikz]{standalone}
\begin{document}

"""

    for f in [curves]:
        out += "\\begin{tikzpicture}[x=" +  f"{SCALE}cm, y={SCALE}cm]\n" + f() + "\n\\end{tikzpicture}\n\n"
    out += r"\end{document}"
    return out
    
fn = "fibo"
tfn =   fn + ".tex"
ofn = fn + ".pdf"
with open(tfn,'w') as f:
    f.write(full_file())

# compile it

subprocess.call(f"{TEX} {tfn} -o {ofn}", shell =True, executable = '/bin/zsh')
if SHOW:
    subprocess.call(f"{OPEN} {ofn}",shell =True, executable = '/bin/zsh')
