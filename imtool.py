def imresize(im,sz):
    #resize
    pil_im = Image.fromarray(uint8(im))
    return numpy.array(pil_im.resize(sz))

def histep(im,nbr_bins = 256):
    #直方图均衡化
    imhist,bins = numpy.histogram(im.flatten(),nbr_bins,normed=True)
    cdf = imhist.cumsum()
    cdf = 255 * cdf /cdf[-1]
    im2 = np.interp(im.flatten,bins[:-1],cdf)
    return im2.reshape(im.shape),cdf

def compute_average(imlist):
    averageim = numpy.array(Image.open(imlist[0]),'f')
    for imname in imlist[1:]:
        try:
            averageim += array(Image.open(imname))
        except:
            print(imname+'...skipped')
    averageim /= len(imlist)
    return numpy.array(averageim,'uint8')


