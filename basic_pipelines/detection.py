import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GLib
import argparse
import multiprocessing
import numpy as np
import setproctitle
import cv2
import time

import hailo
from hailo_common_funcs import get_numpy_from_buffer, disable_qos
from hailo_rpi_common import get_default_parser, QUEUE, get_caps_from_pad, GStreamerApp, app_callback_class

from locomotion.bounding_box_target_select import *
import locomotion.bounding_box_motor_control 

from ImageEnhancement.ApplyImageEnhancement import apply_image_enhancement

from ImageEnhancement.ImageProcesses import *
import time

#Function to apply the enhancement algorithm with given hyperparameters
def apply_image_enhancement(image, params, vclahe, bgrclahe):

    times = []
    #enhanced_image = image
    #vclahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_Value"], tileGridSize=(8, 8)) #Adjusted clipLimit
    #bgrclahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_BGR"], tileGridSize=(8, 8))

    #print("Amogus")
    #print(image.shape)
    #print(params.items())
    ### Step 1: Dual-Channel Light Amplification in HSV
    
    times.append(time.time())
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv_image)
    s = (s*params["Saturation"]).astype(np.uint8)

    #Apply CLAHE to the VAlue channel with controlled limits
    #print(params["CLAHE_clipLimit_Value"])
    times.append(time.time())
    v_clahe = vclahe.apply(v)

    # Merge back the channels and convert to BGR
    times.append(time.time())
    hsv_amplified = cv2.merge([h, s, v_clahe])
    amplified_image = cv2.cvtColor(hsv_amplified, cv2.COLOR_HSV2BGR)

    ### Step 2: Color Contrast Enhancement with CLAHE on Each Channel
    #Split the amplified image into BGR channels
    b, g, r = cv2.split(amplified_image)

    # Apply CLAHE to each channel with a controlled clip limit
    times.append(time.time())
    b_clahe = bgrclahe.apply(b)
    g_clahe = bgrclahe.apply(g)
    r_clahe = bgrclahe.apply(r)

    # Merge enhanced channels back
    times.append(time.time())
    contrast_enhanced_image = cv2.merge([b_clahe, g_clahe, r_clahe])

    ### Step 3: Multi-Scale Retinex for Signal Integration
    #Make sure the retinex functions are defined
    # Apply multi-scale retinex on each channel separately
    times.append(time.time())
    """retinex_b = multi_scale_retinex(b_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])
    retinex_g = multi_scale_retinex(g_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])
    retinex_r = multi_scale_retinex(r_clahe, sigmas = [params["Retinex_sigma1"], params["Retinex_sigma2"], params["Retinex_sigma3"]], gain = params["Retinex_gain"])

    #Stack channels back together and clip values to the valid range
    times.append(time.time())
    retinex_image = cv2.merge([retinex_b, retinex_g, retinex_r])
    retinex_image = np.clip(retinex_image, 0, 255).astype(np.uint8)
    """
    retinex_image = contrast_enhanced_image

    ### Step 4: Noise Reduction with Edge Preservation
    # Apply bilateral filter for noise reduction with edge preservation
    times.append(time.time())
    denoised_image = cv2.bilateralFilter(retinex_image, d=9, sigmaColor=10, sigmaSpace=10) #Potentially three more hyperparameters

    ### Step 5: Blend the Amplified and Original Image for a Natural Look
    times.append(time.time())
    alpha = params["Blend_ratio"] # Blend ratio; adjust for stronger or weaker enhancement
    final_image = cv2.addWeighted(denoised_image, alpha, image, 1-alpha, 0)

    final_image = cv2.bilateralFilter(final_image, d=5, sigmaColor=10, sigmaSpace=10)
    times.append(time.time())

    def adjust_gamma(image, gamma=1.2):
        invGamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** invGamma * 255 for i in np.arange(0,256)]).astype("uint8")
        return cv2.LUT(image, table)

    #Apply gamma correction to final image
    times.append(time.time())
    final_image = adjust_gamma(final_image, gamma = params["gamma"])
    
    times.append(time.time())
    #Increase brightness by adding a fixed value
    brightness_boost = params["brightness_boost"] #Adjust from between 20-40
    enhanced_image = cv2.convertScaleAbs(final_image, alpha=1, beta=brightness_boost)
    
    times.append(time.time())
    #print(times)

    return enhanced_image

# -----------------------------------------------------------------------------------------------
# User defined class to be used in the callback function
# -----------------------------------------------------------------------------------------------
# iheritance from the app_callback_class
class user_app_callback_class(app_callback_class):
    def __init__(self):
        super().__init__()
        self.last_time = time.time()
        self.is_recording = False  # Flag to track recording state
        self.video_writer = None  # cv2.VideoWriter instance
        self.output_filename = None  # Default filename
        self.target_subjects = ['person', 'cat']  # List of target species
        self.confidence_threshold = 0.5  # Set confidence threshold for recording
        self.detection_start_time = None  # Track when the detection starts
        self.post_detection_duration = 4  # Continue recording for 5 seconds after detection
        self.target_detected = False
        self.target_label = None

    def start_recording(self, width, height):
        # Initialize the video writer when recording starts
        if self.video_writer is None:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec for MP4 format
            self.video_writer = cv2.VideoWriter(self.output_filename, fourcc, 15, (width, height))
            self.is_recording = True
            print(f"Started recording to {self.output_filename}")

    def stop_recording(self):
        # Release the video writer and stop recording
        if self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            print("Stopped recording")

    def update_filename(self, new_filename):
        # Update the video filename dynamically
        self.output_filename = os.path.join('/home/terrastride/terrastride_recordings/'+new_filename)
        print(f"Updated video filename to {self.output_filename}")

    def check_detection(self, detections):
        # Check if any detection matches the target subject and confidence threshold
        for detection in detections:
            label = detection.get_label()
            confidence = detection.get_confidence()
            
            if label in self.target_subjects and confidence >= self.confidence_threshold:
                return label, True  # Target detected with high confidence
        return None, False

    def handle_post_detection(self, current_time):
        # Continue recording if the target is still present or if enough time has passed
        if self.detection_start_time is not None:
            elapsed_time = current_time - self.detection_start_time
            if elapsed_time < self.post_detection_duration:
                # Still within the time window, continue recording
                return True
            else:
                # Stop recording after post-detection time
                self.stop_recording()
        return False


# Create an instance of the class
user_data = user_app_callback_class()

# -----------------------------------------------------------------------------------------------
# User defined callback function
# -----------------------------------------------------------------------------------------------

# This is the callback function that will be called when data is available from the pipeline
def app_callback(pad, info, user_data):
    # Parameters for preprocessing (optional)

    # Get the GstBuffer from the probe info
    buffer = info.get_buffer()
    if buffer is None:
        return Gst.PadProbeReturn.OK

    # Get the caps from the pad
    format, width, height = get_caps_from_pad(pad)

    # Get the video frame from the buffer
    frame = get_numpy_from_buffer(buffer, format, width, height)
    #frame = apply_image_enhancement(frame, params=params, vclahe=vclahe, bgrclahe=bgrclahe)

    # Get the detections from the buffer
    roi = hailo.get_roi_from_buffer(buffer)
    detections = roi.get_objects_typed(hailo.HAILO_DETECTION)

    # Check if the target subjects are detected and have high enough confidence
    label, user_data.target_detected = user_data.check_detection(detections)
    if label:
        user_data.target_label = label

    if user_data.target_detected and detections:
        locomotion.bounding_box_motor_control.stop_robot()
        
        # If a valid target subject is detected, start recording (if not already recording)
        if not user_data.is_recording:
            # Generate a new filename for the recording
            new_filename = f"terrastride_{user_data.target_label}_{time.strftime('%Y%m%d_%H%M%S')}.mp4"
            user_data.update_filename(new_filename)
            user_data.start_recording(width, height)

        # Save start time
        if user_data.is_recording:
            user_data.detection_start_time = time.time()

        # Handle cautious approach
        user_data.last_time = cautious_approach(detections, user_data.last_time, width, height)

    else:
        user_data.target_detected = False

        # If no target is detected, check if enough time has passed since the last valid detection
        if user_data.is_recording:
            # Check if we have passed the threshold time to stop recording after the last detection
            user_data.is_recording = user_data.handle_post_detection(time.time())
        else:
            user_data.last_time = random_exploration(user_data.last_time)


    # Draw the detection count on the frame
    cv2.putText(frame, f"Detecting: {user_data.target_label}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Convert the frame to BGR and save it if recording
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    #print(frame_bgr.shape)
    #print(frame_bgr.shape)
    #print("Image enhancement applied")
    if user_data.is_recording and user_data.video_writer is not None:
        user_data.video_writer.write(frame_bgr)

    # Return the frame to user_data
    user_data.set_frame(frame_bgr)

    return Gst.PadProbeReturn.OK
    

#-----------------------------------------------------------------------------------------------
# User Gstreamer Application
# -----------------------------------------------------------------------------------------------

# This class inherits from the hailo_rpi_common.GStreamerApp class

class GStreamerDetectionApp(GStreamerApp):
    def __init__(self, args, user_data):
        # Call the parent class constructor
        super().__init__(args, user_data)
        # Additional initialization code can be added here
        # Set Hailo parameters these parameters shuold be set based on the model used
        self.batch_size = 2
        self.network_width = 640
        self.network_height = 640
        self.network_format = "RGB"
        self.default_postprocess_so = os.path.join(self.postprocess_dir, 'libyolo_hailortpp_post.so')

        # Set the HEF file path based on the network
        if args.network == "yolov11s":
            self.hef_path = os.path.join(self.current_path, '../resources/yolov11s.hef')
        else:
            assert False, "Invalid network type"

        self.app_callback = app_callback
    
        nms_score_threshold = 0.3 
        nms_iou_threshold = 0.45
        self.thresholds_str = f"nms-score-threshold={nms_score_threshold} nms-iou-threshold={nms_iou_threshold} output-format-type=HAILO_FORMAT_TYPE_FLOAT32"

        # Set the process title
        setproctitle.setproctitle("TerraStride Tracking App")

        self.create_pipeline()


    def get_pipeline_string(self):
        if (self.source_type == "rpi"):
            source_element = f"libcamerasrc name=src_0 auto-focus-mode=AfModeManual ! "
            source_element += f"video/x-raw, format={self.network_format}, width=1536, height=864 ! "
            source_element += QUEUE("queue_src_scale")
            source_element += f"videoscale ! "
            source_element += f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, framerate=10/1 ! "
        
        elif (self.source_type == "usb"):
            source_element = f"v4l2src device={self.video_source} name=src_0 ! "
            source_element += f"video/x-raw, width=640, height=480, framerate=10/1 ! "
        else:  
            source_element = f"filesrc location={self.video_source} name=src_0 ! "
            source_element += QUEUE("queue_dec264")
            source_element += f" qtdemux ! h264parse ! avdec_h264 max-threads=2 ! "
            source_element += f" video/x-raw,format=I420 ! "
        source_element += QUEUE("queue_scale")
        source_element += f" videoscale n-threads=2 ! "
        source_element += QUEUE("queue_src_convert")
        source_element += f" videoconvert n-threads=3 name=src_convert qos=false ! "
        source_element += f"video/x-raw, format={self.network_format}, width={self.network_width}, height={self.network_height}, pixel-aspect-ratio=1/1 ! "
        
        
        pipeline_string = "hailomuxer name=hmux "
        pipeline_string += source_element
        pipeline_string += "tee name=t ! "
        pipeline_string += QUEUE("bypass_queue", max_size_buffers=20) + "hmux.sink_0 "
        pipeline_string += "t. ! " + QUEUE("queue_hailonet")
        pipeline_string += "videoconvert n-threads=3 ! "
        pipeline_string += f"hailonet hef-path={self.hef_path} batch-size={self.batch_size} {self.thresholds_str} force-writable=true ! "
        pipeline_string += QUEUE("queue_hailofilter")
        pipeline_string += f"hailofilter so-path={self.default_postprocess_so} qos=false ! "
        pipeline_string += QUEUE("queue_hmuc") + " hmux.sink_1 "
        pipeline_string += "hmux. ! " + QUEUE("queue_hailo_python")
        pipeline_string += QUEUE("queue_user_callback")
        pipeline_string += f"identity name=identity_callback ! "
        pipeline_string += QUEUE("queue_hailooverlay")
        pipeline_string += f"hailooverlay ! "
        pipeline_string += QUEUE("queue_videoconvert")
        pipeline_string += f"videoconvert n-threads=3 qos=false ! "
        pipeline_string += QUEUE("queue_hailo_display")
        pipeline_string += f"fpsdisplaysink video-sink={self.video_sink} name=hailo_display sync={self.sync} text-overlay={self.options_menu.show_fps} signal-fps-measurements=true "
        print(pipeline_string)
        return pipeline_string

if __name__ == "__main__":
    #Parameters for image enhancement
    params = {"Saturation": 0.05079967757819648,
              "CLAHE_clipLimit_Value": 2.525144052221287,
              "CLAHE_clipLimit_BGR": 3.6481905337323903,
              "Retinex_gain": 1.1856138179236042,
              "Retinex_sigma1": 12.602866099185661,
              "Retinex_sigma2": 78.29144514892346,
              "Retinex_sigma3": 169.00897570787157,
              "Blend_ratio": 0.07407034069082408,
              "gamma": 1.3266392904177562,
              "brightness_boost": 22.896780890614952}
    
    #Classes predefined for image enhancement
    vclahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_Value"], tileGridSize=(8, 8)) #Adjusted clipLimit
    bgrclahe = cv2.createCLAHE(clipLimit = params["CLAHE_clipLimit_BGR"], tileGridSize=(8, 8))

    parser = get_default_parser()
    # Add additional arguments here
    parser.add_argument("--network", default="yolov11s", choices=['yolov11s'], help="Which Network to use, default is yolov11s")
    args = parser.parse_args()
    app = GStreamerDetectionApp(args, user_data)
    app.run()