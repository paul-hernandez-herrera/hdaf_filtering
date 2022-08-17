# -*- coding: utf-8 -*-
"""
Created on Sun Jul 31 20:09:21 2022

@author: jalip
"""
import argparse 
import numpy as np
import hdaf_filter
from . import input_output as io


def main():
    parser = argparse.ArgumentParser(description='Hermite Distributed Approximation Functional (hdaf) low-pass, high-pass, band-pass and laplacian fourier filters parameters')
    parser.add_argument('--parameters_file', default=[], type=str, help='Path to the file containing the information of the filters to apply.', required = True)
    parser.add_argument('--input_file', default=[], type=str, help='Path to the folder or file containing the images to be processed.', required = True)
    parser.add_argument('--save_output', action='store_true', help='Save the output images as tif file')
    parser.add_argument('--save_plot', action='store_true', help='Save a plot of the input and output images as png file')
    parser.add_argument('--folder_output', default=[], type=str, help='Path to save the output tif file and png plot')
    parser.add_argument('--no_use_prefix', action='store_true', help='Do not use input file name as prefix name for saving outputs')
    args = parser.parse_args()
    
    #reading the parameters for each filter
    filter_par = io.read_filter_radii_parameters_from_txt(args.parameters_file)
    
    #creating the object hdaf_filter
    obj = hdaf_filter.filt(np.random.rand(1,1,1))
    obj.set_save_output(args.save_output)
    obj.set_save_plot(args.save_plot)
    if not(args.folder_output==[]):
        obj.set_folder_output(args.folder_output)
    
    
    img_file_path = io.get_image_file_names(args.input_file)
    
    for file in img_file_path:
        obj = apply_filters_to_img(file, filter_par, obj, args)

    
    
def apply_filters_to_img(file, filters, obj, args):
    #creating a folder to save the output
    if not(args.no_use_prefix):
        obj.set_save_prefix(file.stem)

    #update the image
    obj.set_image(io.imread(file))
    
    valid_keys = ['low_pass', 'high_pass', 'laplacian', 'band_pass', 'laplacian_multiscale']
    
    for key in filters.keys():
        if  any(x == key for x in valid_keys):
            for radius in filters[key]:
                obj.apply_filter(key, radius)
                
    return obj        
    
    
if __name__ == '__main__':
    main()