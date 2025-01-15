import multiprocessing
from basic_pipelines.detection_pipeline import GStreamerDetectionApp
from Locomotion.bounding_box_target_select import cautious_approach
from basic_pipelines.detection_copy_2 import app_callback, user_app_callback_class
import argparse

if __name__ == "__main__":
    bbox_queue = multiprocessing.Queue()


    # Start the GStreamer app process
    gstreamer_proc = multiprocessing.Process(target=lambda: GStreamerDetectionApp(app_callback, user_app_callback_class(), bbox_queue).run())

    # Start the locomotion process
    locomotion_proc = multiprocessing.Process(target=cautious_approach, args=(bbox_queue,))

    gstreamer_proc.start()
    locomotion_proc.start()

    try:
        gstreamer_proc.join()
        locomotion_proc.join()
    except KeyboardInterrupt:
        print("Shutting down...")
        gstreamer_proc.terminate()
        locomotion_proc.terminate()