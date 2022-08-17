import tifffile
import numpy as np
from pathlib import Path

def imread(filename):
    ext = Path(filename).suffix
    if ext== '.tif' or ext=='.tiff':
        return tifffile.imread(filename)
        
def imwrite(filename, arr):
    ext = Path(filename).suffix
    if ext== '.tif' or ext=='.tiff':
        tifffile.imsave(filename, arr) 
        
def get_image_file_names(file_path):
    file_path = Path(file_path)
    ext = file_path.suffix
    img_file_path = []
    if file_path.is_dir():
        img_file_path.extend(file_path.glob('*.tif'))
        img_file_path.extend(file_path.glob('*.tiff'))
    elif ext=='.tif' or ext=='.tiff':
        img_file_path = [file_path]
    else:
        raise ValueError('Input file format not recognized. Currently only tif files can be processed (.tif or .tiff)')
    return img_file_path        


def read_filter_radii_parameters_from_txt(file_path):
    #opening the file --- it sends an error message if file is not found
    file_id = open(file_path, 'r')
    Lines = file_id.readlines()
    
    valid_filters_one_radius = ["low_pass", 
                                 "high_pass", 
                                 "laplacian", ]

    valid_filters_several_radii = ["band_pass", 
                                 "laplacian_multiscale"]    
    
    output ={}
    for identifier in valid_filters_one_radius+valid_filters_several_radii:
        output[identifier] =  []
    
    current_filter = ''
    for line in Lines:                
        if any(x == current_filter.lower() for x in valid_filters_several_radii) and not(output[current_filter][-1]==[]):
            #append new line of paramters
            output[current_filter].append([])        
        
        x = line.split()
        for string in x:
            if string.isnumeric() and any(x == current_filter.lower() for x in valid_filters_one_radius):
                output[current_filter].append(float(string))
            elif string.isnumeric() and any(x == current_filter.lower() for x in valid_filters_several_radii):
                output[current_filter][-1] = np.append(output[current_filter][-1], float(string))
            else:
                current_filter = string.lower()
                if any(x == current_filter.lower() for x in valid_filters_several_radii):
                    output[current_filter].append([])                 
                    
    #remove empty variable
    for identifier in valid_filters_several_radii:
        if len(output[identifier])>0:
            if output[identifier][-1] == []:
                del output[identifier][-1]
    
    for radii in output["band_pass"]:
        if not(len(radii)==2):
            raise ValueError('Parameters for band_pass filter incorrectly given. It requires 2 radii per line, the lower and higher radii for the filter')
    
    return output


def get_file_name_output(prefix, filter_identifier, radius):
    file_name_output = ''
    if not(prefix == ''):
        file_name_output = file_name_output + prefix + '_'
    
    file_name_output = file_name_output + filter_identifier
    
    if np.array(radius).size ==1:
        radius = [radius]
        
    radius_str = '_radius_'
    for r in np.array(radius):
        radius_str = radius_str + str(r) + '_'
    radius_str = radius_str[1:-1]
    
    file_name_output = file_name_output + '_' + radius_str
    
    return file_name_output