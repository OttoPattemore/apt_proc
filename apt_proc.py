from PIL import Image
import sys
import os

def split(img):
    return (img.crop([86,0,995,img.height]),img.crop([1126,0,2035,img.height]))

# Replaces static with black lines
def noise_remove(img):
    apply  = img.copy()
    for y in range(0,img.height):
        for x in range(0,img.width):
            value = img.getpixel((x,y))
            just_left_value = img.getpixel((x-1,y))
            grey_scale = int((float(value[0])+float(value[1])+float(value[2]))/3.0)
            just_left_grey_scale = int((float(just_left_value[0])+float(just_left_value[1])+float(just_left_value[2]))/3.0)
            dif = just_left_grey_scale-grey_scale
            if dif < -240 or dif >240:
                for j in range(0,apply.width):
                    apply.putpixel((j,y),(0,0,0))
                break
    return apply

def noise_patch(img):
    apply  = img.copy()
    for y in range(0,img.height):
        for x in range(0,img.width):
            value = img.getpixel((x,y))
            if((value == (0,0,0,255)) or (value == 0)):
                apply.putpixel((x,y),apply.getpixel((x,max(y-1,0))))
    return apply

# Jet color scheme adapted from https://stackoverflow.com/questions/7706339/grayscale-to-red-green-blue-matlab-jet-color-scale
def interpolate( val, y0, x0, y1, x1 ):
  return (val-x0)*(y1-y0)/(x1-x0) + y0

def blue( grayscale ):
  if ( grayscale < -0.33 ): return 1.0
  elif ( grayscale < 0.33 ): return interpolate( grayscale, 1.0, -0.33, 0.0, 0.33 );
  else: return 0.0

def green( grayscale ): 
  if ( grayscale < -1.0 ): return 0.0
  if  ( grayscale < -0.33 ): return interpolate( grayscale, 0.0, -1.0, 1.0, -0.33 );
  elif ( grayscale < 0.33 ): return 1.0
  elif ( grayscale <= 1.0 ): return interpolate( grayscale, 1.0, 0.33, 0.0, 1.0 );
  else: return 1.0

def red( grayscale ):
  if ( grayscale < -0.33 ):
    return 0.0
  elif ( grayscale < 0.33 ):
    return interpolate( grayscale, 0.0, -0.33, 1.0, 0.33 )
  else:
      return 1.0


def rain_fall(visible,thermal_image):
    apply  = visible.copy()
    for x in range(0,thermal_image.width):
        for y in range(0,thermal_image.height):
            min_thermal = 200
            value = thermal_image.getpixel((x,y))
            if type(value)==int:
                grey_scale  = value
            else:
                grey_scale = int((float(value[0])+float(value[1])+float(value[2]))/3.0)
            if(grey_scale > min_thermal):
                v  = (grey_scale-min_thermal)/(255-min_thermal)
                apply.putpixel((x,y),(int(red((v-0.5)*2)*255),int(green((v-0.5)*2)*255),int(blue((v-0.5)*2)*255)))
    return apply

def apt_proc(image):
    vis, therm = split(image)
    noise_removed_visible = noise_patch(noise_remove(vis))
    noise_removed_thermal = noise_patch(noise_remove(therm))
    return (noise_removed_visible, noise_removed_thermal, rain_fall(noise_removed_visible,noise_removed_thermal))
def main():
    if(len(sys.argv) < 3):
        print("Usage: ./apt_proc <input> <output directory>")
        exit(-1)
    input_image = sys.argv[1]
    output_directory = sys.argv[2]
    if not os.path.isdir(output_directory):
        os.mkdir(output_directory)
    
    visible, thermal, rainfall = apt_proc(Image.open(input_image))

    thermal.save(output_directory+"/thermal.png")
    visible.save(output_directory+"/visible.png")
    rainfall.save(output_directory+"/rainfall.png")
if __name__ == "__main__":
    main()