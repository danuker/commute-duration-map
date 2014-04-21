import urllib2
import json

import numpy
import matplotlib.pyplot as plt
from matplotlib.mlab import griddata
from matplotlib import cm, colors
import matplotlib.image as mpimg

from time import sleep

def get_time(src='46.7746416,23.6215208',
             dest='46.76817,23.579759',
             arrival_time='1399356000'):
    """
    Gets the travel time in seconds, from src to dest, with given arrival_time
    """
    
    url = 'http://maps.googleapis.com/maps/api/directions/json?'+ \
        'origin=' + src + \
        '&destination=' + dest + \
        '&sensor=false&mode=transit' + \
        '&arrival_time=' + arrival_time
    
    response = urllib2.urlopen(url)
    data = json.load(response)
    routes = data['routes']
    
    # Return the minimum time of all routes
    try:
        return min(r['legs'][0]['duration']['value'] for r in routes)
    except:
        if data['status'] == u'ZERO_RESULTS':
            return numpy.NaN
        
        raise Exception(str(data))

def read_points(A, B, D, n=9):
    """
    Reads n points of the parallelogram defined by A, B, and D
    Loads data from points.txt, and only requests if the point is new
    """
    
    cache = {}
    with open('points.txt', 'r') as f:
        for line in f:
            x, y, z = line.strip().split('\t')
            cache[(x, y)] = z

    # The sides (differences of vectors)
    a, b, d = map(numpy.array, [A, B, D])
    ab = b-a
    ad = d-a
    
    us = numpy.linspace(0, 1, int(numpy.sqrt(n)))
    vs = us
    print 'Actual n:', len(us)*len(vs)
    
    i = 0
    for u in us:
        for v in vs:
            point = a + (u*ab) + (v*ad)
            x = '%0.6f'%point[0]
            y = '%0.6f'%point[1]
            print i
            if (x, y) in cache:
                pass
            else:
                
                cache[(x, y)] = get_time( '%f,%f'%(float(x),float(y)) )
                sleep(2.5)
                with open('points.txt', 'a') as g:
                    g.write("%s\t%s\t%0.6f\n"%(x, y, cache[(x, y)]))
            i += 1
                
    with open('points.txt', 'w') as h:
        for (x, y) in cache:
            h.write("%s\t%s\t%s\n"%(x, y, cache[(x, y)]))
    
    return cache

if __name__=='__main__':
    """
    Prepare the points and perform the plotting
    """
    
    ig, ax = plt.subplots()
    
    pt_map = read_points(
        (46.749179,23.50137),   # A - somewhere in Floresti
        (46.73889,23.602771),   # B - south side of Cluj
        (46.803504,23.579748),  # D - north side
        n=1000)                  # I want this many points
    
    X, Y, Z = [], [], []
    
    for k in pt_map:
        y, x = map(float, k)  # Convert them to floats
        z = float(pt_map[k])
        
        for l, e in zip([X, Y, Z], [x, y, z]):
            l.append(e)
    
    # Compute the interpolation
    xi = numpy.linspace(min(X), max(X), 500)
    yi = numpy.linspace(min(Y), max(Y), 500)
    zi = griddata(X,Y,Z,xi,yi,interp='nn')
    
    # Load the image (whose coordinates were found 
    # using Wikimedia's GeoLocator)
    img=mpimg.imread('staticmap.png')

    plt.imshow(img,
               extent=[ 23.506622, 23.690128, 46.731558,46.814797],
               aspect=1.333)
    
    # Prepare colormap
    r,g,b,a = [numpy.abs(numpy.linspace (-1, 1, 10)),
               numpy.abs(numpy.linspace(0, 0, 10)),
               numpy.abs(numpy.linspace(-1, 1, 10)),
               numpy.abs(numpy.linspace(-1, 1, 3))]
    
    CM = colors.LinearSegmentedColormap.from_list('blackwhite', zip(r,g,b,a))
    
    # See the estimated duration
    plt.contourf(xi,yi,zi,30,cmap=CM,
                  vmax=abs(zi).max(), vmin=-abs(zi).max())
    plt.colorbar()
    
    # And the actual points it's based on
    plt.scatter(X, Y,marker='o',c='b',s=1,alpha=0.5, zorder=1)
    
    plt.title('Seconds to Spyhce')
    plt.show()
    