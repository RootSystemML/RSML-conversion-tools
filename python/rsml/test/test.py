from openalea.deploy import shared_data

N = 2

from time import sleep
from openalea.deploy.shared_data import shared_data
import rsml

img_dir = shared_data(rsml)
data = shared_data(rsml)/'rsml'

files = [fn for fn in data.glob('*.rsml') if 'old' not in fn]
#print files

fn= files[N]

print "read ", fn 



def rw(fn, display=False):
	gs = rsml.rsml2mtg(fn)
	if display:
		dump = rsml.Dumper()
		s = dump.dump(gs)
		print s
	rsml.plot3d(gs, img_dir='.')
	return gs

#gs = rw(fn)

def plot(n=N):
	fn= files[n]

	print "read ", fn 

	gs = rw(fn)

def test_rootnav(n=0):
	rootnav_data = data/'rootnav'
	files = [fn for fn in rootnav_data.glob('*.rsml') if 'old' not in fn]

	print 'nb files: ', len(files)
	if  n < 0 or n >= len(files):
		n = 0

	fn = files[n]
	gs = rw(fn)
	return gs

def test_rsa(id=1):
	rsa_data = data/'rootsystemanalyser'
	files = [fn for fn in rsa_data.glob('lupine*/lupine*_%d/*.rsml'%id) if 'old' not in fn]

	gs = []
	for fn in files:
		gs.append(rw(fn))
		sleep(0.3)
	return gs

def f2():
	rsml.plot3d(gs, img_dir='.')

	# OK

	data = shared_data(rsml)/'rsml'/'rootnav'

	files = [fn for fn in data.glob('*.rsml') if 'old' not in fn]
	fn= files[0]

	print "read ", fn 

	def get_file(f, ext='.png'):
		return f.splitext()[0]+ext

	gs = rsml.rsml2mtg(fn)
	rsml.plot2d(gs, img_file=get_file(fn))
