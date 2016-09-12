import sys
import os
import pylab
import math

def create_dir(dir_name):

    # create results directory if it doesn't already exist
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def transpose(m):

	"""
	Transpose the rectangular two-dimentional matrix m.
	"""
	return [[m[y][x] for y in range(len(m))]for x in range(len(m[0]))]


def get_mean(data):

    if len(data) > 0:
        return sum(data)/len(data)
    else:
        return 0


def get_mean_and_sum(data):

    """
    Takes a 2D array of data and calculates mean and sum of each sub-list.
    """

    return [get_mean(x) for x in data], [sum(x) for x in data]


def create_colour_dict(n=0):

    "Create a colour dictionary with an entry for each state."
    
    colour_dict = {}
    colour_dict['none']='white'    # nodes in no group
    index = 0
    keys = xrange(0, n)
    prev_colour=0
    for g_id in [x for x in keys]:
        cur_colour = (prev_colour+383)%n
        colour_dict[g_id] = '#%02x%02x%02x' \
                % hsl2rgb(float(cur_colour)/(len(keys)),1.0,0.5)
        prev_colour = cur_colour
        index += 1
    return colour_dict


def get_red_green_colour(x):

    """
    Get a colour in the red-green colour range corresponding to x.

    x in range [0.0, 1.0]
    0.0 -> red
    0.5 -> yellow
    1.0 -> green
    """

    return '#%02x%02x%02x' % hsl2rgb(x/4.0,1.0,0.5)


def create_plot_colour_dict():

    colour_dict = {}
    colour_dict['none'] = 'white'
    colour_dict[0] = 'teal'
    colour_dict[1] = 'limegreen'
    colour_dict[2] = 'indigo'
    colour_dict[3] = 'orange'
    colour_dict[4] = 'plum'
    colour_dict[5] = 'flerp'
    colour_dict[6] = 'derp'
    return colour_dict


def hsl2rgb(h,s,l):
    if (s == 0.0 ):                       # HSL values = [0-1]
        r = 255*l                       # RGB results = [0-1]
        g = 255*l
        b = 255*l
    else:
        if (l < 0.5):
            q = l * (1 + s)
        else:
            q = (l + s) - (l * s)
        p = 2 * l - q

        r = rounded(255*Hue_2_RGB(p, q, h + (1.0/3.0)))
        g = rounded(255*Hue_2_RGB(p, q, h))
        b = rounded(255*Hue_2_RGB(p, q, h - (1.0/3.0)))
    return (r,g,b)  

def Hue_2_RGB(p,q,t):             # Hue_2_RGB
    if (t<0):
        t += 1.0
    if (t>1):
        t -= 1.0
    if ((6 * t) < 1):
        return (p + ((q - p) * 6 * t))
    if ((2 * t) < 1):
        return q 
    if ((3 * t) < 2):
        return (p + ((q - p) * 6 * ((2.0/3.0) - t)))
    return p 
  
def rounded(float):
  return int(math.floor(float+0.5))
 

def write_plot(
        x_data, y_data, 
        outfile, 
        title_text, 
        xlabel_text, ylabel_text, 
        colours, 
        labels=None,
        ylim=None, 
        type='lin',
        marker='',
        keys=None,
        lw=2
        ):

    """
    A general x-y plotting function.
    """
    
    assert len(x_data) == len(y_data)
    
    pylab.clf()
    
    for d in range(len(x_data)):
        
        if type == 'lin':
            plot_string = 'pylab.plot(' 
        elif type == 'log':
            plot_string = 'pylab.loglog('
        elif type == 'semilogy':
            plot_string = 'pylab.semilogy('
        elif type == 'semilogx':
            plot_string = 'pylab.semilogx('
        else:
            print "NetIO_plots::write_plot - unknown plot type."
            sys.exit()

        if keys != None:
            colour = get_red_green_colour(keys[d])
        else:
            colour = colours[d]

        plot_string += "x_data["+str(d)+"], y_data["+str(d)+"], " +\
                "'" + colour + "'" + ", marker='"+marker+"'" +\
                ", linewidth=%d)" % (lw)
    
        #print plot_string

        exec plot_string 
    
    pylab.xlabel(xlabel_text)
    pylab.ylabel(ylabel_text)
    pylab.title(title_text)
    if labels != None:
        lgd = pylab.legend(labels, loc=9, bbox_to_anchor=(0.5, -0.1), ncol=len(labels))
    if ylim != None:
        pylab.ylim(ylim[0], ylim[1])
    if labels != None:
        pylab.savefig(outfile+".pdf", format='pdf', additional_artists=lgd, bbox_inches="tight")
        pylab.savefig(outfile+".png", format='png', additional_artists=lgd, bbox_inches="tight")
    else: 
        pylab.savefig(outfile+".pdf", format='pdf')
        pylab.savefig(outfile+".png", format='png')


def write_data(data, outfile, sep='\n'):

    out = open(outfile, 'w')
    for d in data:
        out.write(str(d) + sep)
    out.flush()
    out.close()


def write_data_2d(data, outfile, sep1=',', sep2='\n'):

    out = open(outfile, 'w')
    for d1 in data:
        for d2 in d1:
            out.write(str(d2) + sep1)
        out.write(sep2)
    out.flush()
    out.close()


