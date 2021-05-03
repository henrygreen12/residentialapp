from furnace_detect import *
from pvc_steel_detect import *



#importing what we need
image_path = '/home/murray/Desktop/example3.jpg' #define this as the path in which we save the furnace image
model_detect = 'furnace_not_furnace.model'
model_eff = 'pvc_steel.model'
furnace_detect = is_furnace(image,model_detect)





if furance_detect[0] == 'Furnace':
    if furnace_detect[1] > 0.4:
        print('furnace_found,take a better photo')




#confidence greater than 0.8 is sure of furnace, we will detect effciency based upon model parameters
    if furance_detect[1] >= 0.8:
        print('furnace found')
        eff_detect = is_pvc(image,model_eff)
        eff_detect = eff_detect[0]




#furnace not found , confidence is low, take another photo
    else:
        print('furnace_not_found')




if eff_detect == 'pvc':
    effciency = [0.9,0.96]

if eff_detect == 'steel':
    effciency = [0.75,0.80]
