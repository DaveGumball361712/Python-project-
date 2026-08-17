import sys
sys.stdout.reconfigure(encoding='utf-8')
def map(rows=12, collums=12, width=3):
    middle_line="─"*width
    top_borders=("┌"+"┬".join([middle_line]*collums)+"┐")
    bottom_borders=("└" +"┴".join([middle_line]*collums)+"┘")
    middle_borders=("├"+"┼".join([middle_line]*collums)+"┤")
    inside_line=("│"+"│".join([" "*width]*collums)+"│")
    print (top_borders)
    for i in range(rows):
        print (inside_line)
        if i < rows - 1:
            print (middle_borders)
    print (bottom_borders)

map()