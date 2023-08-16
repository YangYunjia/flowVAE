from collections import Counter
import numpy as np
import os
from torch.utils.data import Subset
import torch

from .base_model import convEncoder, convDecoder, convEncoder_Unet, convDecoder_Unet
from .vae import frameVAE, Unet, Md_Unet

class MDCounter(dict):
    '''
    Remark: if a number added to counter is zero, then it won't be added to it. So we re-write it
    '''
    def __init__(self, *args, **kwargs):
        super(MDCounter, self).__init__(*args, **kwargs)
        self._cktensor()
        
    def __add__(self, other):
        if not isinstance(other, MDCounter):
            return NotImplemented
        result = MDCounter()
        for elem, count in self.items():
            result[elem] = count + other[elem]

        for elem, count in other.items():
            if elem not in self:
                result[elem] = count
        return result

    def __sub__(self, other):
        if not isinstance(other, MDCounter):
            return NotImplemented
        result = MDCounter()
        for elem, count in self.items():
            result[elem] = count - other[elem]

        for elem, count in other.items():
            if elem not in self:
                result[elem] = -count
        return result

    def __mul__(self, number):
        for k in self.keys():
            self[k] *= number
        return self
    
    def __truediv__(self, number):
        for k in self.keys():
            self[k] /= number
        return self

    def append(self, item):
        for k, v in item.items():
            if k in self.keys(): 
                self[k].append(v)
            else:
                self[k] = [v]
        return self
    
    def _cktensor(self):
        for k in self.keys():
            if torch.is_tensor(self[k]):
                self[k] = self[k].item()


def warmup_lr(epoch):

    if epoch < 20:
        lr =  1 + 0.5 * epoch
    else:
        lr =  10 * 0.95**(epoch - 20)
    
    print(epoch, 'lr set to ', lr)

    return lr

def warmup_plt_lr(epoch):

    if epoch < 20:
        lr =  1 + 0.5 * epoch
    elif epoch < 50:
        lr = 10
    elif epoch < 100:
        lr = 1
    elif epoch < 150:
        lr = 0.1
    elif epoch < 200:
        lr = 0.01
    elif epoch < 250:
        lr = 0.001
    else:
        lr = 0.0001
    
    print(epoch, 'lr set to ', lr)

    return lr

def load_encoder_decoder(_id):

    # if _id == 0:
    #     _encoder = bm.mlpEncoder(in_channels=802, hidden_dims=[256, 128, 64])
    #     _decoder = bm.mlpDecoder(in_channels=latent_dim, out_channels=401, hidden_dims=[64, 128, 256])
    if _id == 1:
        _encoder = convEncoder(in_channels=2, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[256, 512, 256, 128], sizes=[26, 101, 401])
    elif _id == 2:
        _encoder = convEncoder(in_channels=2, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[256, 256, 128, 64], sizes=[26, 101, 401])
    elif _id == 3:
        _encoder = convEncoder(in_channels=2, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[512, 256, 256, 128], sizes=[26, 101, 401])
    elif _id == 33:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = [convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[512, 256, 128, 128], 
                                        sizes=[24, 100, 401], encoder_hidden_dims=[256, 128, 64, 3]),
                    convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[512, 256, 128, 128], 
                                        sizes=[24, 100, 401], encoder_hidden_dims=[256, 128, 64, 3])]
    elif _id == 4:
        _encoder = convEncoder(in_channels=2, last_size=[6], hidden_dims=[64, 128, 128, 256], pool_kernels=[3,0,3,0], pool_strides=[2,0,2,0])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[512, 256, 256, 128], sizes=[26, 101, 401])
    elif _id == 5:
        _encoder = convEncoder(in_channels=2, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[256, 128, 64, 64], sizes=[26, 101, 401])
    elif _id == 51:
        _encoder = convEncoder_Unet(in_channels=2, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[256, 128, 64, 64], 
                                            sizes = (24, 100, 401), encoder_hidden_dims=[256, 128, 64, 2])
    elif _id == 52:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = convDecoder_Unet(out_channels=2, last_size=[5], hidden_dims=[256, 128, 64, 64], 
                                            sizes = (24, 100, 401), encoder_hidden_dims=[256, 128, 64, 3])
    elif _id == 53:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[5], hidden_dims=[64, 128, 256])
        _decoder = [convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[256, 128, 64, 64], 
                                            sizes = [24, 100, 401], encoder_hidden_dims=[256, 128, 64, 3]),
                    convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[256, 128, 64, 64], 
                                            sizes = [24, 100, 401], encoder_hidden_dims=[256, 128, 64, 3])]
    elif _id == 82:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[6], hidden_dims=[64, 128, 128, 256], pool_kernels=[3, 3, 0, 0])
        _decoder = convDecoder_Unet(out_channels=2, last_size=[6], hidden_dims=[256, 128, 128, 64, 64], 
                                            sizes = (12, 24, 100, 401), encoder_hidden_dims=[256, 128, 128, 64, 3])
    elif _id == 92:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[7], hidden_dims=[64, 128, 128, 256, 256], pool_kernels=[3, 0, 0, 0, 0])
        _decoder = convDecoder_Unet(out_channels=2, last_size=[7], hidden_dims=[256, 256, 128, 128, 64, 64], 
                                            sizes = (13, 25, 50, 100, 401), encoder_hidden_dims=[256, 256, 128, 128, 64, 3])
    
    elif _id == 6:
        _encoder = convEncoder(in_channels=2, last_size=[5], hidden_dims=[32, 64, 128])
        _decoder = convDecoder(out_channels=1, last_size=[5], hidden_dims=[128, 64, 32, 32], sizes=[26, 101, 401])
    elif _id == 61:
        _encoder = convEncoder_Unet(in_channels=2, last_size=[5], hidden_dims=[32, 64, 128])
        _decoder = convDecoder_Unet(out_channels=1, last_size=[5], hidden_dims=[128, 64, 32, 32],
                                            sizes = (24, 100, 401), encoder_hidden_dims=[128, 64, 32, 2])
    elif _id == 72:
        _encoder = convEncoder_Unet(in_channels=3, last_size=[5], hidden_dims=[128, 256, 512])
        _decoder = convDecoder_Unet(out_channels=2, last_size=[5], hidden_dims=[512, 256, 128, 128], 
                                            sizes = (24, 100, 401), encoder_hidden_dims=[512, 256, 128, 3])

    if _id < 20:
        _model_type = frameVAE
    elif _id in [33, 53]:
        print('model is Md_Unet')
        _model_type = Md_Unet
    else:
        _model_type = Unet

    return _encoder, _decoder, _model_type
    