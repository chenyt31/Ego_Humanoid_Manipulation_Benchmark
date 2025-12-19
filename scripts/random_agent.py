import importlib
import sys
if "isaaclab" not in sys.modules:
    sys.modules["isaaclab"] = importlib.import_module("isaaclab")
    
import argparse
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Random agent for Ego_Humanoid_Manipulation_Benchmark environments.")
parser.add_argument("--disable_fabric", action="store_true", default=False, help="Disable fabric and use USD I/O operations.")
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to simulate.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch
import isaaclab_tasks  # noqa: F401
import humanoid.tasks
from isaaclab_tasks.utils import parse_env_cfg

import numpy as np
from PIL import Image
import cv2  # 用来生成视频

def get_rgb_image(obs: dict) -> np.ndarray:
    print(obs.keys()) 
    """获取固定相机的 RGB 图像"""
    rgb_tensor = obs["fixed_rgb"][0]
    # if "fixed_rgb" in obs:
    #     rgb_tensor = obs["fixed_rgb"][0]  # 取第一个环境
    # else:
    #     rgb_tensor = obs["rgb"][0]
    rgb_numpy = rgb_tensor.cpu().numpy().astype(np.uint8)
    return rgb_numpy

def main():
    env_cfg = parse_env_cfg(
        args_cli.task, device=args_cli.device, num_envs=args_cli.num_envs, use_fabric=not args_cli.disable_fabric,
    )
    env = gym.make(args_cli.task, cfg=env_cfg)
    
    # env.reset() 可能返回 tuple (obs, info)
    obs_tuple = env.reset()
    obs = obs_tuple[0] if isinstance(obs_tuple, tuple) else obs_tuple

    # 保存第一帧
    first_frame = get_rgb_image(obs)
    Image.fromarray(first_frame).save("first_frame.png")
    print("Saved first_frame.png")

    # 视频设置
    h, w, _ = first_frame.shape
    video_filename = "simulation.mp4"
    video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*"mp4v"), 30, (w, h))

    # 保存第一帧到视频
    video_writer.write(cv2.cvtColor(first_frame, cv2.COLOR_RGB2BGR))

    max_steps = 100
    step_count = 0

    while simulation_app.is_running() and step_count < max_steps:
        with torch.inference_mode():
            actions = 2 * torch.rand(env.action_space.shape, device=env.unwrapped.device) - 1
            step_result = env.step(actions)
            obs = step_result[0] if isinstance(step_result, tuple) else step_result

            rgb_numpy = get_rgb_image(obs)
            # OpenCV 需要 BGR 格式
            video_writer.write(cv2.cvtColor(rgb_numpy, cv2.COLOR_RGB2BGR))

            step_count += 1
            print(f"Step {step_count}: actions={actions}")

    video_writer.release()
    print(f"Saved video {video_filename}")
    env.close()
    simulation_app.close()

if __name__ == "__main__":
    main()