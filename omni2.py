import os
import numpy as np
from pxr import Usd, UsdGeom
import warp as wp
import warp.sim
import warp.sim.render
from enum import Enum

class IntegratorType(Enum):
    EULER = "euler"
    XPBD = "xpbd"

    def __str__(self):
        return self.value

class TireWearSimulator:
    def __init__(self, stage_path="./tire_models/Single_L_Front.usd", mesh_path="/root/Single_L_Front", wear_rate=0.01, integrator: IntegratorType = IntegratorType.EULER):
        self.stage_path = stage_path
        self.mesh_path = mesh_path
        self.wear_rate = wear_rate

        # Load USD stage
        self.stage = Usd.Stage.Open(self.stage_path)
        assert self.stage, f"Failed to open stage {self.stage_path}"

        # Load tire mesh
        self.mesh_prim = self.stage.GetPrimAtPath(self.mesh_path)
        assert self.mesh_prim, f"Mesh not found at path {self.mesh_path}"
        
        self.mesh_geom = UsdGeom.Mesh(self.mesh_prim)
        self.mesh_points = np.array(self.mesh_geom.GetPointsAttr().Get())
        self.mesh_indices = np.array(self.mesh_geom.GetFaceVertexIndicesAttr().Get())

        self.integrator_type = integrator

        fps = 60
        self.sim_substeps = 32
        self.frame_dt = 1.0 / fps
        self.sim_dt = self.frame_dt / self.sim_substeps
        self.sim_time = 0.0
        self.profiler = {"step": []}

        self.init_simulation()

    def add_particles_in_triangle(self, builder, v0, v1, v2, num_subdivisions):
        for i in range(num_subdivisions + 1):
            for j in range(num_subdivisions - i + 1):
                # Barycentric coordinates
                b0 = i / num_subdivisions
                b1 = j / num_subdivisions
                b2 = 1 - b0 - b1

                # Compute the position of the particle
                point = b0 * v0 + b1 * v1 + b2 * v2

                # Check if the point lies within the triangle bounds
                builder.add_particle(point, wp.vec3(0.0, 0.0, 0.0), 0.0, 0.1)
        

    def init_simulation(self):
        builder = wp.sim.ModelBuilder()

        # self.tire_mesh = wp.sim.Mesh(self.mesh_points, self.mesh_indices)
        # builder.add_shape_mesh(
        #     body=-1,
        #     mesh=self.tire_mesh,
        #     pos=wp.vec3(0.0, 0.0, 0.0),
        #     rot=wp.quat_identity(),
        #     scale=wp.vec3(1.0, 1.0, 1.0),
        #     ke=1.0e2,
        #     kd=1.0e2,
        #     kf=1.0e1,
        # )

        # Interpolate particles over the surface area of the mesh
        for triangle in self.mesh_indices.reshape(-1, 3):
            v0, v1, v2 = self.mesh_points[triangle]
            self.add_particles_in_triangle(builder, v0, v1, v2, num_subdivisions=10)  # Adjust num_particles as needed

        if self.integrator_type == IntegratorType.EULER:
            self.integrator = wp.sim.SemiImplicitIntegrator()
        else:
            self.integrator = wp.sim.XPBDIntegrator(iterations=1)

        self.model = builder.finalize()
        self.model.ground = False

        self.state_0 = self.model.state()
        self.state_1 = self.model.state()

        self.renderer = wp.sim.render.SimRenderer(self.model, self.stage, scaling=40.0)
        self.use_cuda_graph = wp.get_device().is_cuda
        if self.use_cuda_graph:
            with wp.ScopedCapture() as capture:
                self.simulate()
            self.graph = capture.graph

    def simulate(self):
        #wp.sim.collide(self.model, self.state_0)

        for _ in range(self.sim_substeps):
            self.state_0.clear_forces()
            self.integrator.simulate(self.model, self.state_0, self.state_1, self.sim_dt)
            self.apply_wear()
            (self.state_0, self.state_1) = (self.state_1, self.state_0)

    def apply_wear(self):
        for i in range(len(self.mesh_points)):
            self.mesh_points[i] -= self.wear_rate * np.array([0, 1, 0]) # Assuming wear occurs downward
        self.mesh_geom.GetPointsAttr().Set(self.mesh_points)

    def step(self):
        with wp.ScopedTimer("step", dict(self.profiler)):
            if self.use_cuda_graph:
                wp.capture_launch(self.graph)
            else:
                self.simulate()
        self.sim_time += self.frame_dt
        self.profiler["step"].append(self.sim_time)

    def render(self):
        if self.renderer is None:
            return

        with wp.ScopedTimer("render"):
            self.renderer.begin_frame(self.sim_time)
            self.renderer.render(self.state_0)
            self.renderer.end_frame()

    def save(self, save_path):
        if self.renderer:
            stage = self.renderer.stage
            stage.GetRootLayer().Export(save_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--device", type=str, default=None, help="Override the default Warp device.")
    parser.add_argument("--stage_path", type=lambda x: None if x == "None" else str(x), default="./tire_models/Single_L_Front.usd", help="Path to the input USD file.")
    parser.add_argument("--mesh_path", type=str, default="/root/Single_L_Front/Object066", help="Path to the tire mesh in the USD file.")
    parser.add_argument("--wear_rate", type=float, default=0.01, help="Rate of tire wear per simulation step.")
    parser.add_argument("--num_frames", type=int, default=300, help="Total number of frames.")
    parser.add_argument("--integrator", help="Type of integrator", type=IntegratorType, choices=list(IntegratorType), default=IntegratorType.EULER)
    parser.add_argument("--save_path", type=str, default="./tire_models/Single_L_Front_wear.usd", help="Path to save the output USD file.")

    args = parser.parse_known_args()[0]

    with wp.ScopedDevice(args.device):
        simulator = TireWearSimulator(stage_path=args.stage_path, mesh_path=args.mesh_path, wear_rate=args.wear_rate, integrator=args.integrator)

        for _i in range(args.num_frames):
            simulator.step()
            simulator.render()

        frame_times = simulator.profiler["step"]
        print("\nAverage frame sim time: {:.2f} ms".format(sum(frame_times) / len(frame_times)))

        if simulator.renderer:
            simulator.save(args.save_path)
