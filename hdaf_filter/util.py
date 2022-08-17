# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 20:16:18 2022

@author: jalip
"""
import numpy as np

from pathlib import Path
import matplotlib.pyplot as plt
from . import input_output as io


        
def plot_filter_output(input_img, output_img, filter_identifier, radius, folder_output, file_prefix):
    fig, axs = plt.subplots(1, 2, constrained_layout=True,figsize=(8,8))
    
    input_img = np.amax(input_img,axis=0)
    img1 = axs[0].imshow(input_img, cmap='gray')
    axs[0].set_title('Input Image')
    plt.colorbar(img1, ax=axs[0])
    
    output_img = np.amax(output_img,axis=0)
    img_output = axs[1].imshow(output_img, cmap='jet')
    axs[1].set_title('Output')
    plt.colorbar(img_output, ax=axs[1])
    
    fig.savefig(Path(folder_output, io.get_file_name_output(file_prefix, filter_identifier, radius)  + ".png"))        
    plt.close('all')
    
                
    

    