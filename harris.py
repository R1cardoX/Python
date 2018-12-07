from scipy.ndimage import filters
from PIL import Image
from pylab import *
from numpy import *

def compute_harris_respose(im,sigma = 3):
    #对每个像素计算Harris角点检测器相应函数
    #计算导数
    imx = zeros(im.shape)
    filters.gaussian_filter(im,(sigma,sigma),(0,1),imx)
    imy = zeros(im.shape)
    filters.gaussian_filter(im,(sigma,sigma),(1,0),imy)
    
    Wxx = filters.gaussian_filter(imx*imx,sigma)
    Wxy = filters.gaussian_filter(imx*imy,sigma)
    Wyy = filters.gaussian_filter(imy*imy,sigma)
    
    Wdet = Wxx*Wyy - Wxy**2
    Wtr = Wxx + Wyy

    return Wdet/Wtr

def get_harris_points(harrisim,min_dist = 10,threshold = 0.1):
    #从一幅Harris相应图像中返回角点，min_dict为分割角点和图像边界的最少像素数目
    #寻找高于阈值的候选角点
    corner_threshold = harrisim.max() * threshold
    harrisim_t = (harrisim > corner_threshold) * 1

    #得到候选点的坐标
    coords = array(harrisim_t.nonzero()).T

    #以及他们的Harris响应值
    candidate_values = [harrisim[c[0],c[1]] for c in coords]
    
    #对候选点按照Harris响应值进行排序
    index = argsort(candidate_values)
    
    #将可行点的位置保存到数组中
    allowed_locations = zeros(harrisim.shape)
    allowed_locations[min_dist:-min_dist,min_dist:-min_dist] = 1

    #按照min_distance原则，选择最佳Harris点
    filtered_corrds = []
    for i in index:
        if allowed_locations[coords[i,0],coords[i,1]] == 1:
            filtered_corrds.append(coords[i])
            allowed_locations[(coords[i,0]-min_dist):(coords[i,0]+min_dist),(coords[i,0]-min_dist):(coords[i,0]+min_dist)] = 0
    return filtered_corrds

def plot_harris_points(image,filtered_corrds):
    figure()
    gray()
    imshow(image)
    plot([p[1] for p in filtered_corrds],[p[0] for p in filtered_corrds],'*')
    axis('off')
    show()

im = array(Image.open('./res/1.jpg').convert('L'))
harrisim = compute_harris_respose(im)
filtered_corrds = get_harris_points(harrisim,6)
plot_harris_points(im,filtered_corrds)

