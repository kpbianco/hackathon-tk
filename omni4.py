import numpy as np
from pxr import Usd, UsdGeom, Sdf, Gf
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
    def __init__(self, stage_path="./tire_models/Formula1_Tire.usd", wear_rate=0.01, integrator: IntegratorType = IntegratorType.EULER):
        self.stage_path = stage_path
        self.wear_rate = wear_rate

        self.integrator_type = integrator

        fps = 60
        self.sim_substeps = 32
        self.frame_dt = 1.0 / fps
        self.sim_dt = self.frame_dt / self.sim_substeps
        self.sim_time = 0.0
        self.profiler = {"step": []}

        self.init_simulation()

    def create_cylinder_mesh(self, height, radius, num_segments):
        vertices = []
        indices = []

        # Top and bottom center points
        vertices.append([0, height / 2, 0])  # Top center
        vertices.append([0, -height / 2, 0])  # Bottom center

        # Create vertices along the top and bottom edge
        for i in range(num_segments):
            angle = 2 * np.pi * i / num_segments
            x = radius * np.cos(angle)
            z = radius * np.sin(angle)
            vertices.append([x, height / 2, z])  # Top edge
            vertices.append([x, -height / 2, z])  # Bottom edge

        # Create indices for top and bottom faces
        for i in range(num_segments):
            top_center_index = 0
            bottom_center_index = 1
            top_edge_start = 2 + i * 2
            bottom_edge_start = 3 + i * 2
            next_top_edge = 2 + ((i + 1) % num_segments) * 2
            next_bottom_edge = 3 + ((i + 1) % num_segments) * 2

            indices.append([top_center_index, next_top_edge, top_edge_start])
            indices.append([bottom_center_index, bottom_edge_start, next_bottom_edge])

        # Create indices for side faces
        for i in range(num_segments):
            top_edge_start = 2 + i * 2
            bottom_edge_start = 3 + i * 2
            next_top_edge = 2 + ((i + 1) % num_segments) * 2
            next_bottom_edge = 3 + ((i + 1) % num_segments) * 2

            indices.append([top_edge_start, next_top_edge, bottom_edge_start])
            indices.append([next_top_edge, next_bottom_edge, bottom_edge_start])

        return np.array(vertices), np.array(indices)

    def generate_particles_on_cylinder(self, builder, vertices, num_particles_per_segment):
        num_vertices = len(vertices)
        self.active_particles = []
        self.marker_indices = []

        for i in range(num_vertices):
            particle = builder.add_particle(vertices[i], wp.vec3(0.0, 0.0, 0.0), 0.0, 0.1)
            self.active_particles.append(particle)

        # Add particles along the curved surface
        for i in range(2, num_vertices, 2):
            top_vertex = vertices[i]
            bottom_vertex = vertices[i + 1]
            for j in range(num_particles_per_segment):
                t = j / num_particles_per_segment
                point = top_vertex * (1 - t) + bottom_vertex * t
                particle = builder.add_particle(point, wp.vec3(0.0, 0.0, 0.0), 0.0, 0.1)
                self.active_particles.append(particle)
                # Add condition for markers
                if i % 10 == 0 and j % 10 == 0:  # Adjust this value for the spacing of the markers
                    self.marker_indices.append(len(self.active_particles) - 1)

        self.num_particles = len(self.active_particles)
        self.particle_active = np.ones(self.num_particles, dtype=bool)  # Initialize all particles as active

    def init_simulation(self):
        builder = wp.sim.ModelBuilder()

        # Create cylinder mesh
        height = 0.305  # Approximate height of an F1 tire (in meters)
        radius = 0.165  # Approximate radius of an F1 tire (in meters)
        num_segments = 100  # Increased detail
        vertices, indices = self.create_cylinder_mesh(height, radius, num_segments)

        # Rotate the cylinder to be horizontal
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, 0, 1],
            [0, -1, 0]
        ])
        vertices = np.dot(vertices, rotation_matrix.T)

        # Generate particles on the cylinder
        self.generate_particles_on_cylinder(builder, vertices, num_particles_per_segment=20)

        if self.integrator_type == IntegratorType.EULER:
            self.integrator = wp.sim.SemiImplicitIntegrator()
        else:
            self.integrator = wp.sim.XPBDIntegrator(iterations=1)

        self.model = builder.finalize()
        self.model.ground = False

        self.state_0 = self.model.state()
        self.state_1 = self.model.state()

        self.stage = Usd.Stage.CreateNew(self.stage_path)
        root_layer = self.stage.GetRootLayer()
        self.renderer = wp.sim.render.SimRenderer(self.model, self.stage, scaling=40.0)

        self.use_cuda_graph = wp.get_device().is_cuda
        if self.use_cuda_graph:
            with wp.ScopedCapture() as capture:
                self.simulate()
            self.graph = capture.graph

    def simulate(self):
        for _ in range(self.sim_substeps):
            self.state_0.clear_forces()
            self.integrator.simulate(self.model, self.state_0, self.state_1, self.sim_dt)
            self.apply_rotation()
            (self.state_0, self.state_1) = (self.state_1, self.state_0)

    def apply_rotation(self):
        # Apply rotation to the tire
        rotation_angle = self.sim_dt * 10  # Adjust the rotation speed as needed
        rotation_matrix = np.array([
            [np.cos(rotation_angle), 0, -np.sin(rotation_angle)],
            [0, 1, 0],
            [np.sin(rotation_angle), 0, np.cos(rotation_angle)]
        ])
        particle_positions = self.state_0.particle_q.numpy()
        rotated_positions = np.dot(particle_positions, rotation_matrix.T)
        self.state_0.particle_q = wp.array(rotated_positions, dtype=wp.vec3)

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
            colors = np.array([[0.8, 0.3, 0.2]] * len(self.state_0.particle_q))
            for idx in self.marker_indices:
                colors[idx] = [1.0, 1.0, 0.0]  # Color the markers yellow
            self.renderer.begin_frame(self.sim_time)
            self.renderer.render_points(
                points=self.state_0.particle_q.numpy(), radius=0.1, name="points", colors=colors
            )
            self.renderer.end_frame()

    def save(self, save_path):
        if self.renderer:
            stage = self.renderer.stage
            stage.GetRootLayer().Export(save_path)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--device", type=str, default=None, help="Override the default Warp device.")
    parser.add_argument("--wear_rate", type=float, default=0.01, help="Rate of tire wear per simulation step.")
    parser.add_argument("--num_frames", type=int, default=300, help="Total number of frames.")
    parser.add_argument("--integrator", help="Type of integrator", type=IntegratorType, choices=list(IntegratorType), default=IntegratorType.EULER)
    parser.add_argument("--save_path", type=str, default="./tire_models/Formula1_Tire_wear.usd", help="Path to save the output USD file.")

    args = parser.parse_known_args()[0]

    with wp.ScopedDevice(args.device):
        simulator = TireWearSimulator(wear_rate=args.wear_rate, integrator=args.integrator)

        for _i in range(args.num_frames):
            simulator.step()
            simulator.render()

        frame_times = simulator.profiler["step"]
        print("\nAverage frame sim time: {:.2f} ms".format(sum(frame_times) / len(frame_times)))

        if simulator.renderer:
            simulator.save(args.save_path)