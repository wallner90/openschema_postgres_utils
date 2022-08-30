from math import sin, cos, atan2, asin
from pathlib import Path

def euler_to_quaternion(roll, pitch, yaw):
    cy = cos(yaw * 0.5)
    sy = sin(yaw * 0.5)
    cp = cos(pitch * 0.5)
    sp = sin(pitch * 0.5)
    cr = cos(roll * 0.5)
    sr = sin(roll * 0.5)

    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy
    return [qw, qx, qy, qz]

def quaternion_to_euler(qw, qx, qy, qz):
    roll = atan2(2*(qw*qx + qy*qz), 1-2*(qx*qx + qy*qy))
    pitch = asin(2*(qw*qy - qz*qx))
    yaw = atan2(2*(qw*qz + qx*qy), 1-2*(qy*qy + qz*qz))
    return [roll, pitch, yaw]

def args_sanity_check(args) -> bool:
    # Sanity checks
    if args.mode == "to_db":
        if args.input_file == None:
            print(f"Error: Loading from file but 'input_file' is empty!")
            return False
        elif not Path(args.input_file).is_file():
            print(f"Error: Loading from file {args.input_file} not possible!")
            return False
    elif args.mode == "to_file":
        if args.output_file == None:
            print(f"Error: Store to file but 'output_file' is empty!")
            return False
        elif not Path(args.output_file).parent.is_dir():
            print(f"Error: {args.output_file} is no valid directory!")
            return False
    return True