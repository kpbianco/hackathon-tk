class Tire:
    def __init__(self, 
                 tire_pressure=0.0, 
                 tire_temp=0.0, 
                 tire_wear=0.0, 
                 tire_speed=0.0, 
                 tire_grip=0.0, 
                 tire_load=0.0, 
                 tire_wear_percent=0.0, 
                 tire_slip_ratio=0.0, 
                 tire_slip_angle=0.0, 
                 tire_vert_defl=0.0, 
                 tire_surf_temp=0.0, 
                 tire_carcass_temp=0.0, 
                 tire_inner_temp=0.0, 
                 tire_middle_temp=0.0, 
                 tire_outer_temp=0.0, 
                 tire_type="", 
                 tire_compound="", 
                 patch_load=0.0, 
                 tire_air_pressure=0.0, 
                 patch_temp=0.0, 
                 friction_coef=0.0, 
                 rotational_speed=0.0, 
                 corner_stiffness=0.0, 
                 long_stiffness=0.0, 
                 aligning_torque=0.0, 
                 drag_force=0.0, 
                 overheat=False, 
                 flat_spot=False, 
                 speed_diff=0.0, 
                 load_sensitivity=0.0):
        
        self.tire_pressure = tire_pressure
        self.tire_temp = tire_temp
        self.tire_wear = tire_wear
        self.tire_speed = tire_speed
        self.tire_grip = tire_grip
        self.tire_load = tire_load
        self.tire_wear_percent = tire_wear_percent
        self.tire_slip_ratio = tire_slip_ratio
        self.tire_slip_angle = tire_slip_angle
        self.tire_vert_defl = tire_vert_defl
        self.tire_surf_temp = tire_surf_temp
        self.tire_carcass_temp = tire_carcass_temp
        self.tire_inner_temp = tire_inner_temp
        self.tire_middle_temp = tire_middle_temp
        self.tire_outer_temp = tire_outer_temp
        self.tire_type = tire_type
        self.tire_compound = tire_compound
        self.patch_load = patch_load
        self.tire_air_pressure = tire_air_pressure
        self.patch_temp = patch_temp
        self.friction_coef = friction_coef
        self.rotational_speed = rotational_speed
        self.corner_stiffness = corner_stiffness
        self.long_stiffness = long_stiffness
        self.aligning_torque = aligning_torque
        self.drag_force = drag_force
        self.overheat = overheat
        self.flat_spot = flat_spot
        self.speed_diff = speed_diff
        self.load_sensitivity = load_sensitivity

    def __repr__(self):
        return (f"Tire(tire_pressure={self.tire_pressure}, tire_temp={self.tire_temp}, tire_wear={self.tire_wear}, "
                f"tire_speed={self.tire_speed}, tire_grip={self.tire_grip}, tire_load={self.tire_load}, "
                f"tire_wear_percent={self.tire_wear_percent}, tire_slip_ratio={self.tire_slip_ratio}, "
                f"tire_slip_angle={self.tire_slip_angle}, tire_vert_defl={self.tire_vert_defl}, "
                f"tire_surf_temp={self.tire_surf_temp}, tire_carcass_temp={self.tire_carcass_temp}, "
                f"tire_inner_temp={self.tire_inner_temp}, tire_middle_temp={self.tire_middle_temp}, "
                f"tire_outer_temp={self.tire_outer_temp}, tire_type={self.tire_type}, tire_compound={self.tire_compound}, "
                f"patch_load={self.patch_load}, tire_air_pressure={self.tire_air_pressure}, patch_temp={self.patch_temp}, "
                f"friction_coef={self.friction_coef}, rotational_speed={self.rotational_speed}, corner_stiffness={self.corner_stiffness}, "
                f"long_stiffness={self.long_stiffness}, aligning_torque={self.aligning_torque}, drag_force={self.drag_force}, "
                f"overheat={self.overheat}, flat_spot={self.flat_spot}, speed_diff={self.speed_diff}, load_sensitivity={self.load_sensitivity})")
