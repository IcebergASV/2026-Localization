import numpy as np
import math

def deg_to_rad(degrees: float) -> float:
    return degrees * (math.pi / 180.0)

def build_c2w_matrix(pitch_deg: float, roll_deg: float, yaw_deg: float, cam_world_pos: tuple) -> np.ndarray:
    pitch = deg_to_rad(pitch_deg)
    roll = deg_to_rad(roll_deg)
    yaw = deg_to_rad(yaw_deg)
    
    Xc, Yc, Zc = cam_world_pos

    cp, sp = np.cos(pitch), np.sin(pitch)
    cr, sr = np.cos(roll), np.sin(roll)
    cy, sy = np.cos(yaw), np.sin(yaw)

    mworld = np.array([
        [cy*cp, cy*sp*sr - sy*cr, cy*sp*cr + sy*sr, Xc],
        [sy*cp, sy*sp*sr + cy*cr, sy*sp*cr - cy*sr, Yc],
        [-sp,    cp*sr,          cp*cr,          Zc],
        [0,      0,              0,              1]
    ])
    return mworld

def cam_to_world(p_cam: tuple, mworld: np.ndarray) -> np.ndarray:
    pc = np.array([p_cam[0], p_cam[1], p_cam[2], 1.0])
    p_world = np.dot(mworld, pc)
    return p_world[:3]

def pixel_to_world(u: float, v: float, dist: float, K: np.ndarray, mworld: np.ndarray, is_straight_line_dist: bool = True) -> tuple:
    fx, fy = K[0, 0], K[1, 1]
    cx, cy = K[0, 2], K[1, 2]

    xn = (u - cx) / fx
    yn = (v - cy) / fy

    if is_straight_line_dist:
        norm = math.sqrt(xn**2 + yn**2 + 1.0)
        Xc = dist * (xn / norm)
        Yc = dist * (yn / norm)
        Zc = dist * (1.0 / norm)
    else:
        Xc = xn * dist
        Yc = yn * dist
        Zc = dist

    p_cam = (Xc, Yc, Zc)
    p_world = cam_to_world(p_cam, mworld)
    return p_cam, p_world

def main():
    print("=== CAMERA & WORLD TRANSFORMATION SETUP ===")
    
    use_default_k = input("Use default 1080p camera intrinsics? (y/n): ").strip().lower() == 'y'
    if use_default_k:
        K = np.array([
            [1662.7,    0.0, 960.0],
            [   0.0, 1662.7, 540.0],
            [   0.0,    0.0,   1.0]
        ])
    else:
        fx = float(input("Enter focal length fx (pixels): "))
        fy = float(input("Enter focal length fy (pixels): "))
        cx = float(input("Enter optical center cx (pixels): "))
        cy = float(input("Enter optical center cy (pixels): "))
        K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    print("\n--- Enter Camera Pose in World Space ---")
    cam_x = float(input("Camera World X position: "))
    cam_y = float(input("Camera World Y position: "))
    cam_z = float(input("Camera World Z position: "))
    
    pitch = float(input("Camera Pitch (degrees): "))
    roll = float(input("Camera Roll (degrees): "))
    yaw = float(input("Camera Yaw (degrees): "))

    mworld = build_c2w_matrix(pitch, roll, yaw, (cam_x, cam_y, cam_z))
    
    dist_type_input = input("\nIs your distance value (1) Straight-line distance d OR (2) Planar depth Zc? Enter 1 or 2 [default=1]: ").strip()
    is_straight_line = dist_type_input != '2'

    print("\n==================================================")
    print("  Setup complete! Entering interactive mode.     ")
    print("  Type 'q' or 'exit' at any prompt to quit.     ")
    print("==================================================\n")

    while True:
        try:
            u_str = input("\nEnter Pixel u (X coordinate): ").strip()
            if u_str.lower() in ['q', 'exit']:
                break
            u = float(u_str)

            v_str = input("Enter Pixel v (Y coordinate): ").strip()
            if v_str.lower() in ['q', 'exit']:
                break
            v = float(v_str)

            d_str = input("Enter Distance (d or Zc): ").strip()
            if d_str.lower() in ['q', 'exit']:
                break
            d = float(d_str)

            p_cam, p_world = pixel_to_world(u, v, d, K, mworld, is_straight_line_dist=is_straight_line)

            print("\n--- RESULTS ---")
            print(f"3D Camera Frame (Xc, Yc, Zc) : [{p_cam[0]:.4f}, {p_cam[1]:.4f}, {p_cam[2]:.4f}]")
            print(f"3D World Frame  (Xw, Yw, Zw) : [{p_world[0]:.4f}, {p_world[1]:.4f}, {p_world[2]:.4f}]")

        except ValueError:
            print("Invalid numerical input. Please enter valid numbers or 'q' to quit.")
        except KeyboardInterrupt:
            break

    print("\nExited loop. Program finished.")

if __name__ == "__main__":
    main()