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
        if args.format == "maplab":
            if not args.input_dir:
                print(f"Error: Loading from directory but 'input_dir' is empty!")
                return False
            elif not Path(args.input_dir).is_dir():
                print(f"Error: Loading from directory {args.input_dir} not possible!")
                return False
        else:
            if not args.input_file:
                print(f"Error: Importing from file but 'input_file' is empty!")
                return False
            elif not Path(args.input_file).is_file():
                print(f"Error: Importing from file {args.input_file} not possible!")
                return False
    elif args.mode == "to_file":
        if args.format == "maplab":
            if not args.output_dir:
                print(f"Error: Exporting to directory but 'output_dir' is empty!")
                return False
            elif not Path(args.output_dir).is_dir():
                print(f"Error: Exporting to directory {args.output_dir} not possible!")
                return False
        else:
            if not args.output_file:
                print(f"Error: Exporting to file but 'output_file' is empty!")
                return False
            elif not Path(args.output_file).parent.is_dir():
                print(f"Error: {args.output_file} is no valid directory!")
                return False
    return True

def find_index(list, condition):
    return [i for i, elem in enumerate(list) if condition(elem)]