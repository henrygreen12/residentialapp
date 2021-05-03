import os

absolute_path = os.path.dirname(os.path.abspath(__file__)) 

def dir_last_updated():
	folder = absolute_path + '/static'

	return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))
