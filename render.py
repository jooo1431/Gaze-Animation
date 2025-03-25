#!/usr/bin/python
# coding=utf-8
import blenderproc as bproc
import sys
import os
import cv2
sys.path.append('./')
import eyemodel
import numpy as np
import matplotlib.pyplot as plt


#   ^
#   |    .-.
#   |   |   | <- Head
#   |   `^u^'
# Y |      ¦V <- Camera    (As seen from above)
#   |      ¦
#   |      ¦
#   |      o <- Target
#
#     ----------> X
#
# +X = left
# +Y = back
# +Z = up
        
def render_imgs(output_dir):
    with eyemodel.Renderer() as r:
        '''
        Eye Setting
        Options:
            eye_position = [0,0,0]
            eye_target
            eye_closedness  = 0.0
            iris = light or dark
            eye_radius = 24/2
            pupil_radius = 4/2, Max: 3.58
            eye_up = [0,0,1]
        ''' 
        r.iris = "dark"  
        r.pupil_radius = 2.0  

        # Camera Setting
        # Options: ["camera_position", "camera_target", "image_size", "focal_length", "camera_up", "focus_distance", "fstop", "camera_up"]
        r.camera_position = [20, -70, -10]  
        r.camera_target = [0, -r.eye_radius, 0]

        # Light Setting
        # Options: ["location", "target", "type", "size", "strength", "view_angle"]
        r.lights = [
            eyemodel.Light(
                type="spot", # spot or sun available
                location = [10, -10, 50],
                strength = 10,
                target = [0,0,0]),
            eyemodel.Light(
                strength = 1,
                location = [15, -50, -10],
                target = r.camera_target),
            eyemodel.Light(
                strength = 1,
                location = [20, -50, -10],
                target = r.camera_target)
        ]

        # Render single sample
        # r.eye_target = [-18.826,-0.9169 ,0]
        # r.render(output_dir +"/test.png")

        # Render all samples in data
        for i in range(data.shape[0]):
            target = data[i].tolist()
            target.append(0) # target has to be [, ,]
            target = [ round(elem,8) for elem in target ]  
            r.eye_target = target
            r.render(output_dir + "/sample" + str(i) +".png")

def plot_data(timesteps=None):
    hor_max = data[:,0][np.argmax(data[:,0])] 
    hor_min = data[:,0][np.argmin(data[:,0])]
    vert_max = data[:,1][np.argmax(data[:,1])] 
    vert_min = data[:,1][np.argmin(data[:,1])]

    max_val = max(hor_max,vert_max)
    min_val = min(hor_min, vert_min)

    plt.plot(data[:,0], label='horizontal')
    plt.plot(data[:,1], label='vertical')
    plt.legend(loc="upper left")
    plt.xlabel("Time (ms)")
    plt.ylabel("Gaze Direction (°)")

    if timesteps is not None:
        for t in timesteps:
            plt.axvline(x=t, lw=0.75,c="black") 

    plt.savefig(os.path.join(main_dir,'fig.png'))

def render_video(inp_dir):
    width = 640
    height = 480
    fps = 1000 # 1000Hz
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') #cv2.VideoWriter_fourcc(*'DIVX') 
    out_file = os.path.join(main_dir,'video_sample.mp4')

    video = cv2.VideoWriter(out_file,fourcc,fps,(width,height))
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]]) 
        
    for filename in sorted(os.listdir(inp_dir), key=len): 
        print(filename)
        img = cv2.imread(os.path.join(inp_dir,filename))
        #upscaled = sr.upsample(img)
        #sharpened_img = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
        #sharpened_img = cv2.filter2D(img, -1, kernel) 
        video.write(img)

    video.release()
    cv2.destroyAllWindows()


if __name__=="__main__":

    # Load data
    data_dir = "gaze_data_sample"
    load_data = np.load(os.path.join(data_dir,'siggraph_video_gaze_7_sample.npy')) # (5000,2) in degrees (horizontal, vertical)

    for idx in range(len(load_data)-6):
        main_dir = 'Samples/Sample'+ str(idx+1) 
        img_dir = main_dir + '/imgs'

        if not os.path.exists(img_dir):
            os.makedirs(img_dir) 

        data = np.insert(load_data[idx],0,np.zeros((2,), dtype=float), axis=0) # add start pos [0,0] to data (5001,2)

        # Render images
        render_imgs(output_dir=img_dir)

        # Plot data graph
        plot_data(timesteps=[537, 1780,2561,3459,4657])

        # Render video
        render_video(inp_dir=img_dir)

    

