import numpy as np
from pathlib import Path
from . import input_output as io
from . import util

class filt():
    
    def __init__(self, input_img):
        np.set_printoptions(suppress=True)
        
        #constructor given an image
        self.set_n(60)
        
        self.img = np.random.rand(1,1,1)
        
        self.set_image(input_img)     
        
        self.set_save_plot(False)
        
        self.set_save_output(False)
        
        self.set_save_prefix('')
        
        self.set_folder_output(Path.cwd())

    def set_image(self, input_img):
        # constructor when a new image is given. This function allows to apply the filters to a new image
        temp_shape = self.img.shape
        
        # just in case we have a 2D image, convert it to 3D image with only 1 slice in z. 
        # necessary to allow the code to work with 2D and 3D images
        self.img = self.__create_3d_image(input_img)

        #if the shape is the same as the previous it is not necessary to recompute the filters
        if not(temp_shape==self.img.shape):
            #we need to re-compute the fixed variables/filter in case the shape of the new image is different from previous image shape
            self.freq_norm_square = self.__computer_norm_frequency_squared(self.img.shape)
            
            #index for filter
            self.nhalf = np.floor(np.array(self.img.shape)/2).astype('int')+1
            
            self.flip = np.mod(self.img.shape, 2).astype('int')
            
            #dictionary to save low_pass filters
            self.dict_low_pass_filters = dict()
            
            #laplacian in the fourier space
            self.laplacian_fourier_space = - self.__replicate_one_cuadrant(self.freq_norm_square)                   
            
        #compute fourier transform of image
        self.img_FT = np.fft.fftn(self.img)           
    
    def get_filter(self, filter_identifier, radius):
        filter_identifier = filter_identifier.lower()
        
        if filter_identifier == 'low_pass':
            filter_ = self.__get_low_pass_filter(radius)
        elif filter_identifier == 'high_pass':
            filter_ = 1 - self.__get_low_pass_filter(radius)
        elif filter_identifier == 'laplacian':
            filter_ = self.laplacian_fourier_space*self.__get_low_pass_filter(radius)
        elif filter_identifier == 'band_pass':
            filter_ = self.__get_low_pass_filter(radius[0]) - self.__get_low_pass_filter(radius[1])
            if radius[0]>radius[1]:
                #invert filter, because we require radius_2>radius_1 to construct band-pass
                filter_ = -filter_
        else:
            raise ValueError('filter_identifier ' + filter_identifier + ' not recognized')
        return filter_                
    
    def apply_filter(self, filter_identifier, radius):
        filter_identifier = filter_identifier.lower()
        
        if filter_identifier == 'laplacian_multiscale':
            #deactivate saving and writing images, since multiscale laplacian requires to apply the laplacian and this would save the laplacian for each radius
            temp_save_plot = self.flag_save_plot; temp_save_output = self.flag_save_output
            self.set_save_plot(False); self.set_save_output(False)
            img_spatial_domain = self.apply_laplacian_multiscale(radius)
            #activate the default values
            self.set_save_plot(temp_save_plot); self.set_save_output(temp_save_output)   
        else:
            #low_pass, high_pass, laplacian, and band_pass require the same steps to apply the filter
            filter_ = self.get_filter(filter_identifier,radius)            
            img_filtered = filter_ * self.img_FT
            img_spatial_domain = np.fft.ifftn(img_filtered)
            img_spatial_domain = np.real(img_spatial_domain)
        
        
        if self.flag_save_plot:
            util.plot_filter_output(self.img, img_spatial_domain, filter_identifier, radius, self.folder_output, self.prefix)
            
        #convert image to 2D in case it only has 1 slice// necesary to run the code with 2d and 3d images
        if img_spatial_domain.shape[0]==1:
            img_spatial_domain = img_spatial_domain.reshape(img_spatial_domain.shape[1],img_spatial_domain.shape[2])
            
        if self.flag_save_output:
            io.imwrite(Path(self.folder_output, io.get_file_name_output(self.prefix, filter_identifier, radius) + ".tif"), img_spatial_domain)
        return img_spatial_domain       
    
    def apply_laplacian_multiscale(self, radii):
        img_multiscale_lap = np.zeros(self.img.shape)
        for radius in radii:
            img_current_radius_lap = self.__create_3d_image(np.real(self.apply_filter('laplacian', radius)))
            I = np.abs(img_current_radius_lap) > np.abs(img_multiscale_lap)
            img_multiscale_lap[I] = img_current_radius_lap[I]
        return img_multiscale_lap    
    
    def set_n(self, n):
        self.n = n
        
    def set_folder_output(self, folder_output):
        self.folder_output = folder_output
        
    def set_save_prefix(self, prefix):
        self.prefix = prefix
        
    def set_save_output(self, option):
        self.flag_save_output = option

    def set_save_plot(self, option):
        self.flag_save_plot = option     
        
       
    ## PRIVATE METHODS
    def __construct_low_pass_filter(self, radius):
        # computes a low-pass filter belonging to the family of the Hermite Distributed Approximating functions (HDAF)
        # See https://doi.org/10.1016/j.jneumeth.2016.03.019 Sec. 4.1
        # See https://www.math.uh.edu/~mpapadak/BHKP06-final.pdf
        # n: degree of the polynomial for the app
        # sigma: scale of te parameter (size)
        # xi: values to evaluate the functional (distance/norm to the zero frequency elevatate at square)
        # xi is assumed to be elevate at square to speed up operations
        
        #cut-off frecuency
        cnk = self.__get_cnk(radius)
        
        #coefficients of the polynomial
        coefficients = []
        for i in range(self.n,-1,-1):
            coefficients.append(1/np.math.factorial(i))
            
        # changing values of x, according to the selected scale
        xi =  self.freq_norm_square * np.power(cnk,2)
        
        filt = np.polyval(coefficients, xi) * np.exp(-xi)        
        
        filt = self.__replicate_one_cuadrant(filt)
        
        return filt
    
    def __get_low_pass_filter(self, radius):
        #function to get the low pass filter using the given n and radius
        key = str(self.n)+"_"+str(radius)
        
        if not(self.dict_low_pass_filters.__contains__(key)):
            #construct low pass filter
            self.dict_low_pass_filters[key] = self.__construct_low_pass_filter(radius)
        return self.dict_low_pass_filters[key]    


    def __create_3d_image(self, img):
        #make sure to have 3 dimensions. Important to allow the code to work with 2d and 3d images
        if img.ndim == 2:
            img = img.reshape((1,img.shape[0],img.shape[1]))
        return img
    
    def __get_cnk(self, radius):
        #radius given in voxels/pixels/spatial domain. Change to cut-off frequency in fourier space
        # Tested for n=60
        radius = self.__convert_radius_to_cut_off_frequency(radius)
        cnk = np.sqrt(2*self.n +1)/(np.sqrt(2)*radius*np.pi)        
        return cnk    
    
        
    def __replicate_one_cuadrant(self, filt_one_cuadrant):
        #variable to save the filter
        filt = np.zeros(self.img.shape)
        size_crop = self.img.shape-self.nhalf
        end_pos = self.nhalf + self.flip-2
        
        filt[0:self.nhalf[0],0:self.nhalf[1],0:self.nhalf[2]] = filt_one_cuadrant
        
        #replicate low pass filter in X
        filt[self.nhalf[0]:self.img.shape[0],:,:] = filt[end_pos[0]:end_pos[0]-size_crop[0]:-1,:,:]

        #replicate low pass filter in Y
        filt[:,self.nhalf[1]:self.img.shape[1],:] = filt[:,end_pos[1]:end_pos[1]-size_crop[1]:-1,:]
        
        #replicate low pass filter in Z
        filt[:,:,self.nhalf[2]:self.img.shape[2]] = filt[:,:,end_pos[2]:end_pos[2]-size_crop[2]:-1]        
        return filt
    
    def __computer_norm_frequency_squared(self, img_shape):
        
        eps = np.finfo(np.float32).eps
        #step in each dimension 
        step_ = 2*np.pi/np.array(img_shape)

        
        #array in each direction, inclusive pi
        i = np.arange(0, np.pi + eps, step_[0]) 
        j = np.arange(0, np.pi + eps, step_[1]) 
        k = np.arange(0, np.pi + eps, step_[2]) 
        
        #create the nd array of coordinates
        I, J, K = np.meshgrid(i, j, k, indexing ='ij')
        
        freq_norm_square = I**2 + J**2 + K**2         
        return freq_norm_square 
    
    def __convert_radius_to_cut_off_frequency(self, radius):
        cut_off_freq = (0.542423208/radius) + (0.0957539421/(radius**2))
        return cut_off_freq 