import cv2
import numpy as np
from onvif import ONVIFCamera

# Function to get stream URI from the camera
def get_stream_uri(ip, port, user, password):
    mycam = ONVIFCamera(ip, port, user, password)
    media = mycam.create_media_service()
    profiles = media.GetProfiles()
    token = profiles[0].token

    # Corrected structure for the GetStreamUri call
    stream_setup = {
        'Stream': 'RTP-Unicast',
        'Transport': {'Protocol': 'RTSP'}
    }
    uri = media.GetStreamUri({'ProfileToken': token, 'StreamSetup': stream_setup})
    stream_uri = uri.Uri

    if 'username' not in stream_uri or 'password' not in stream_uri:
        credential = f'{user}:{password}@'
        stream_uri = stream_uri.replace('rtsp://', f'rtsp://{credential}')

    return stream_uri


# Replace with your cameras' IP, port, username, and password
camera_info = [
    ('192.168...', PORT, username, password),
    ('192.168...', PORT, username, password),
    ('192.168...', PORT, username, password),
    # Add more cameras as needed
]

# Create video capture objects for each camera
caps = [cv2.VideoCapture(get_stream_uri(*info)) for info in camera_info]

window_name = "Camera Grid"
cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

# Define a common size for all frames (width, height)
common_size = (640, 480)

# Initialize the full_screen_cam_index to None
full_screen_cam_index = None

# Mouse callback function to handle clicks
def mouse_callback(event, x, y, flags, param):
    global full_screen_cam_index
    if event == cv2.EVENT_LBUTTONDOWN:
        if full_screen_cam_index is None:
            # Calculate which camera feed was clicked
            cam_index = (y // common_size[1]) * 2 + (x // common_size[0])
            if cam_index < len(caps):
                full_screen_cam_index = cam_index
        else:
            # Return to grid view
            full_screen_cam_index = None

# Add mouse callback to the window
cv2.setMouseCallback(window_name, mouse_callback)

while True:
    frames = []
    for cap in caps:
        ret, frame = cap.read()
        if ret:
            resized_frame = cv2.resize(frame, common_size)
            frames.append(resized_frame)
        else:
            # Create a black frame if the camera did not return an image
            black_frame = np.zeros((common_size[1], common_size[0], 3), dtype=np.uint8)
            frames.append(black_frame)

    # Ensure that we have exactly 4 frames for the 2x2 grid
    while len(frames) < 4:
        black_frame = np.zeros((common_size[1], common_size[0], 3), dtype=np.uint8)
        frames.append(black_frame)

    if full_screen_cam_index is not None and frames[full_screen_cam_index] is not None:
        # Show only the selected camera in full screen
        cv2.imshow(window_name, frames[full_screen_cam_index])
    else:
        # Create a 2x2 grid
        grid_frame = cv2.vconcat([cv2.hconcat(frames[:2]), cv2.hconcat(frames[2:4])])
        cv2.imshow(window_name, grid_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# Release all capture objects and destroy all OpenCV windows
for cap in caps:
    cap.release()
cv2.destroyAllWindows()
