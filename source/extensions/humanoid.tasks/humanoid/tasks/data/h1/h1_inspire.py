import os
from isaaclab.managers.scene_entity_cfg import SceneEntityCfg
import isaaclab.sim as sim_utils
from isaaclab.assets.articulation.articulation_cfg import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
current_file_path = os.path.abspath(__file__)
parent_dir_path = os.path.dirname(current_file_path)

# ------------------------------------------------------------
# Tuned control parameters (PhysX-stable)
# ------------------------------------------------------------
# Shoulder / elbow
SHOULDER_KP = 1500
SHOULDER_KD = 60
ELBOW_KP = 1200
ELBOW_KD = 50

# Wrist (critical)
WRIST_KP = 300
WRIST_KD = 12

# Hand (very soft)
HAND_KP = 80
HAND_KD = 5

# Effort limits
ARM_EFFORT_LIMIT = 500
HAND_EFFORT_LIMIT = 5

# ------------------------------------------------------------
# Articulation configuration
# ------------------------------------------------------------
H1_INSPIRE_CFG = ArticulationCfg(
    prim_path="{ENV_REGEX_NS}/Robot",
    spawn=sim_utils.UsdFileCfg(
        usd_path=f"{parent_dir_path}/h1_inspire_convex_decomp.usd",
        activate_contact_sensors=True,
        rigid_props=sim_utils.RigidBodyPropertiesCfg(
            max_depenetration_velocity=10.0,
            solver_position_iteration_count=32,
            solver_velocity_iteration_count=2,
            max_contact_impulse=5.0,
        ),
        articulation_props=sim_utils.ArticulationRootPropertiesCfg(
            enabled_self_collisions=False,
            solver_position_iteration_count=16,
            solver_velocity_iteration_count=2,
        ),
        semantic_tags=[("focus", "true"), ("category", "robot")],
    ),

    # --------------------------------------------------------
    # Initial state
    # --------------------------------------------------------
    init_state=ArticulationCfg.InitialStateCfg(
        pos=(0.0, 0.0, 1.05),
        joint_pos={
            ".*_hip_.*_joint": 0.0,
            ".*_knee_joint": 0.0,
            ".*_ankle_.*_joint": 0.0,
            ".*_shoulder_pitch_joint": 0.5,
            ".*_shoulder_roll_joint": 0.0,
            ".*_shoulder_yaw_joint": 0.0,
            ".*_elbow_pitch_joint": -1.0,
            ".*_elbow_roll_joint": 0.0,
            ".*_wrist_pitch_joint": 0.0,
            ".*_wrist_yaw_joint": 0.0,
            ".*_index_.*_joint": 0.0,
            ".*_middle_.*_joint": 0.0,
            ".*_ring_.*_joint": 0.0,
            ".*_pinky_.*_joint": 0.0,
            ".*_thumb_.*_joint": 0.0,
        },
        joint_vel={".*": 0.0},
    ),

    soft_joint_pos_limit_factor=1.0,

    # --------------------------------------------------------
    # Actuators
    # --------------------------------------------------------
    actuators={
        "arms": ImplicitActuatorCfg(
            joint_names_expr=[
                ".*_shoulder_pitch_joint",
                ".*_shoulder_roll_joint",
                ".*_shoulder_yaw_joint",
                ".*_elbow_pitch_joint",
                ".*_elbow_roll_joint",
                ".*_wrist_pitch_joint",
                ".*_wrist_yaw_joint",
            ],
            velocity_limit=4.0,
            effort_limit=ARM_EFFORT_LIMIT,
            stiffness={
                ".*_shoulder_pitch_joint": SHOULDER_KP,
                ".*_shoulder_roll_joint": SHOULDER_KP,
                ".*_shoulder_yaw_joint": SHOULDER_KP,
                ".*_elbow_pitch_joint": ELBOW_KP,
                ".*_elbow_roll_joint": ELBOW_KP,
                ".*_wrist_pitch_joint": WRIST_KP,
                ".*_wrist_yaw_joint": WRIST_KP,
            },
            damping={
                ".*_shoulder_pitch_joint": SHOULDER_KD,
                ".*_shoulder_roll_joint": SHOULDER_KD,
                ".*_shoulder_yaw_joint": SHOULDER_KD,
                ".*_elbow_pitch_joint": ELBOW_KD,
                ".*_elbow_roll_joint": ELBOW_KD,
                ".*_wrist_pitch_joint": WRIST_KD,
                ".*_wrist_yaw_joint": WRIST_KD,
            },
        ),

        "hands": ImplicitActuatorCfg(
            joint_names_expr=[
                ".*_index_.*_joint",
                ".*_middle_.*_joint",
                ".*_ring_.*_joint",
                ".*_pinky_.*_joint",
                ".*_thumb_.*_joint",
            ],
            velocity_limit=2.0,
            effort_limit=HAND_EFFORT_LIMIT,
            stiffness={".*": HAND_KP},
            damping={".*": HAND_KD},
        ),
    },
)

# ------------------------------------------------------------
# Scene entity configs (for controllers / observations)
# ------------------------------------------------------------
H1_INSPIRE_LEFT_ARM_CFG = SceneEntityCfg(
    "robot",
    joint_names=[
        "left_shoulder_pitch_joint",
        "left_shoulder_roll_joint",
        "left_shoulder_yaw_joint",
        "left_elbow_pitch_joint",
        "left_elbow_roll_joint",
        "left_wrist_pitch_joint",
        "left_wrist_yaw_joint",
    ],
    body_names=["L_hand_base_link"],
    preserve_order=True,
)

H1_INSPIRE_RIGHT_ARM_CFG = SceneEntityCfg(
    "robot",
    joint_names=[
        "right_shoulder_pitch_joint",
        "right_shoulder_roll_joint",
        "right_shoulder_yaw_joint",
        "right_elbow_pitch_joint",
        "right_elbow_roll_joint",
        "right_wrist_pitch_joint",
        "right_wrist_yaw_joint",
    ],
    body_names=["R_hand_base_link"],
    preserve_order=True,
)

H1_INSPIRE_LEFT_HAND_CFG = SceneEntityCfg(
    "robot",
    joint_names=[
        "L_index_proximal_joint",
        "L_index_intermediate_joint",
        "L_middle_proximal_joint",
        "L_middle_intermediate_joint",
        "L_pinky_proximal_joint",
        "L_pinky_intermediate_joint",
        "L_ring_proximal_joint",
        "L_ring_intermediate_joint",
        "L_thumb_proximal_yaw_joint",
        "L_thumb_proximal_pitch_joint",
        "L_thumb_intermediate_joint",
        "L_thumb_distal_joint",
    ],
    body_names=[
        "L_thumb_tip",
        "L_index_tip",
        "L_middle_tip",
        "L_ring_tip",
        "L_pinky_tip",
    ],
    preserve_order=True,
)

H1_INSPIRE_RIGHT_HAND_CFG = SceneEntityCfg(
    "robot",
    joint_names=[
        "R_index_proximal_joint",
        "R_index_intermediate_joint",
        "R_middle_proximal_joint",
        "R_middle_intermediate_joint",
        "R_pinky_proximal_joint",
        "R_pinky_intermediate_joint",
        "R_ring_proximal_joint",
        "R_ring_intermediate_joint",
        "R_thumb_proximal_yaw_joint",
        "R_thumb_proximal_pitch_joint",
        "R_thumb_intermediate_joint",
        "R_thumb_distal_joint",
    ],
    body_names=[
        "R_thumb_tip",
        "R_index_tip",
        "R_middle_tip",
        "R_ring_tip",
        "R_pinky_tip",
    ],
    preserve_order=True,
)

"""
Stable Isaac Lab configuration for Unitree H1 + Inspire Hands.
- Wrist large-angle rotation stable
- Hand manipulation without solver lock-up
- No USD modification required
"""
