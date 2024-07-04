import cv2
import pykinect_azure as pykinect

def main():
    pykinect.initialize_libraries(track_body=True)

    device_config = pykinect.default_configuration
    device_config.color_resolution = pykinect.K4A_COLOR_RESOLUTION_OFF
    device_config.depth_mode = pykinect.K4A_DEPTH_MODE_WFOV_2X2BINNED

    # Start the device and body tracker
    device = pykinect.start_device(config=device_config)
    body_tracker = pykinect.start_body_tracker()

    cv2.namedWindow('Depth image with skeleton', cv2.WINDOW_NORMAL)

    while True:
        # Get capture and body tracker frame
        capture = device.update()
        body_frame = body_tracker.update()

        # Get the color depth image and body segmentation
        ret_depth, depth_color_image = capture.get_colored_depth_image()
        ret_color, body_image_color = body_frame.get_segmentation_image()

        if not ret_depth or not ret_color:
            continue

        # Combine images and draw skeletons
        combined_image = cv2.addWeighted(depth_color_image, 0.6, body_image_color, 0.4, 0)
        combined_image = body_frame.draw_bodies(combined_image)

        cv2.imshow('Depth image with skeleton', combined_image)

        # Press 'q' key to stop
        if cv2.waitKey(1) == ord('q'):
            break

if __name__ == "__main__":
    main()
