
import numpy as np

def is_edge(x_or_y,w_or_h):
    return x_or_y==0 or x_or_y==(w_or_h-1)

#get lbph. param image: grayscale np.ndarray image with shape (w,h)
#return  lbp histogram as a list of number
def lbph(image):
    # if (len(image.shape)>2):
    #     image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = []
    h,w = image.shape
    for y in range(h):
        if is_edge(y,h):#we wouldn't want edge of face image anyway, sometimes it's not part of human face
            continue
        for x in range(w):
            if is_edge(x,w):
                continue
            #p8 r1 lbph
            central = image[y,x]
            biner = ''
            biner += str( int(image[y-1,x-1]>central) ) #int casts True/False to 1/0
            biner += str( int(image[y-1,x+0]>central) )
            biner += str( int(image[y-1,x+1]>central) )
            biner += str( int(image[y+0,x-1]>central) )
            biner += str( int(image[y+0,x+1]>central) )
            biner += str( int(image[y+1,x-1]>central) )
            biner += str( int(image[y+1,x+0]>central) )
            biner += str( int(image[y+1,x+1]>central) )
            dec = int(biner,2)
            result.append(dec)
    return result
