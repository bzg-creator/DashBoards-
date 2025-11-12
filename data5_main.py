import open3d as o3d
import numpy as np
import copy


def print_info(geometry, step_name):
    """Print information about geometry"""
    print(f"\n=== {step_name} ===")

    if hasattr(geometry, 'vertices'):
        print(f"Number of vertices: {len(geometry.vertices)}")
    elif hasattr(geometry, 'points'):
        print(f"Number of points: {len(geometry.points)}")

    if hasattr(geometry, 'triangles'):
        print(f"Number of triangles: {len(geometry.triangles)}")

    # Handle voxel grid
    if str(type(geometry)).find('VoxelGrid') != -10000000:
        try:
            voxels = geometry.get_voxels()
            print(f"Number of voxels: {len(voxels)}")
        except:
            print("Number of voxels: Available (cannot access count)")

    if hasattr(geometry, 'vertex_colors') and len(geometry.vertex_colors) > 0:
        print("Has vertex colors: Yes")
    elif hasattr(geometry, 'colors') and len(geometry.colors) > 0:
        print("Has colors: Yes")
    else:
        print("Has colors: No")

    if hasattr(geometry, 'vertex_normals') and len(geometry.vertex_normals) > 0:
        print("Has normals: Yes")
    elif hasattr(geometry, 'normals') and len(geometry.normals) > 0:
        print("Has normals: Yes")
    else:
        print("Has normals: No")


def main():
    # Task 1: Loading and Visualization
    print("\n" + "=" * 50)
    print("TASK 1: LOADING AND VISUALIZATION")
    print("=" * 50)

    mesh = o3d.io.read_triangle_mesh("finn.obj")

    if len(mesh.vertices) == 0:
        print("Failed to load mesh, creating sample mesh...")
        mesh = o3d.geometry.TriangleMesh.create_box(width=1.0, height=1.0, depth=1.0)
        mesh.translate([-0.5, -0.5, -0.5])  # Center it

    print_info(mesh, "Original Model")

    print("Displaying original model...")
    o3d.visualization.draw_geometries([mesh], window_name="Task 1: Original Model")

    # Task 2: Conversion to Point Cloud
    print("\n" + "=" * 50)
    print("TASK 2: CONVERSION TO POINT CLOUD")
    print("=" * 50)

    print("Sampling points from mesh...")
    point_cloud = mesh.sample_points_uniformly(number_of_points=15000)
    print_info(point_cloud, "Point Cloud")

    print("Displaying point cloud...")
    o3d.visualization.draw_geometries([point_cloud], window_name="Task 2: Point Cloud")

    # Task 3: Surface Reconstruction from Point Cloud
    print("\n" + "=" * 50)
    print("TASK 3: SURFACE RECONSTRUCTION FROM POINT CLOUD")
    print("=" * 50)

    point_cloud.estimate_normals(
        search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30)
    )
    point_cloud.orient_normals_consistent_tangent_plane(k=30)

    print("Performing Poisson surface reconstruction...")
    mesh_reconstructed, densities = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        point_cloud, depth=6, width=0, scale=1.1, linear_fit=False)

    densities = np.asarray(densities)
    density_threshold = np.quantile(densities, 0.2)
    vertices_to_remove = densities < density_threshold
    mesh_reconstructed.remove_vertices_by_mask(vertices_to_remove)

    mesh_reconstructed.remove_degenerate_triangles()
    mesh_reconstructed.remove_duplicated_triangles()
    mesh_reconstructed.remove_duplicated_vertices()
    mesh_reconstructed.remove_non_manifold_edges()

    print_info(mesh_reconstructed, "Reconstructed Mesh")

    print("Displaying reconstructed mesh...")
    o3d.visualization.draw_geometries([mesh_reconstructed], window_name="Task 3: Reconstructed Mesh")

    # =========================
    # ✅ UPDATED TASK 4: VOXELIZATION
    # =========================
    print("\n" + "=" * 50)
    print("TASK 4: VOXELIZATION")
    print("=" * 50)

    bbox = point_cloud.get_axis_aligned_bounding_box()
    extent = np.linalg.norm(np.asarray(bbox.get_extent()))
    voxel_size = extent / 50  # adaptive voxel size
    voxel_grid = o3d.geometry.VoxelGrid.create_from_point_cloud(point_cloud, voxel_size=voxel_size)

    print(f"Voxel count (approx): {len(voxel_grid.get_voxels())}, voxel_size={voxel_size:.3f}")
    print_info(voxel_grid, f"Voxel Grid (size={voxel_size:.3f})")

    print("Displaying voxel grid...")
    o3d.visualization.draw([voxel_grid], title="Task 4 — Voxelized Model")

    # Task 5: Adding a Plane
    print("\n" + "=" * 50)
    print("TASK 5: ADDING A PLANE")
    print("=" * 50)

    points = np.asarray(point_cloud.points)
    y_min, y_max = np.min(points[:, 1]), np.max(points[:, 1])
    z_min, z_max = np.min(points[:, 2]), np.max(points[:, 2])

    padding = 0.2
    height = (y_max - y_min) + 2 * padding
    depth = (z_max - z_min) + 2 * padding

    plane_mesh = o3d.geometry.TriangleMesh.create_box(width=0.02, height=height, depth=depth)
    center_y = (y_min + y_max) / 2
    center_z = (z_min + z_max) / 2
    plane_mesh.translate([-0.01, center_y - height / 2, center_z - depth / 2])
    plane_mesh.paint_uniform_color([0.6, 0.6, 0.6])

    print("Created vertical clipping plane at x=0")
    print(f"Plane vertices: {len(plane_mesh.vertices)}")
    print(f"Plane triangles: {len(plane_mesh.triangles)}")
    print(f"Plane dimensions: {0.02:.3f} x {height:.3f} x {depth:.3f}")

    print("Displaying object with clipping plane...")
    o3d.visualization.draw_geometries([point_cloud, plane_mesh], window_name="Task 5: Object with Clipping Plane")

    # Task 6: Surface Clipping
    print("\n" + "=" * 50)
    print("TASK 6: SURFACE CLIPPING")
    print("=" * 50)

    points = np.asarray(point_cloud.points)
    mask = points[:, 0] <= 0
    clipped_points = points[mask]

    clipped_cloud = o3d.geometry.PointCloud()
    clipped_cloud.points = o3d.utility.Vector3dVector(clipped_points)

    if len(point_cloud.colors) > 0:
        colors = np.asarray(point_cloud.colors)
        clipped_cloud.colors = o3d.utility.Vector3dVector(colors[mask])

    if len(point_cloud.normals) > 0:
        normals = np.asarray(point_cloud.normals)
        clipped_cloud.normals = o3d.utility.Vector3dVector(normals[mask])

    print_info(clipped_cloud, "Clipped Point Cloud")
    print(f"Original points: {len(points)}")
    print(f"Remaining points after clipping: {len(clipped_points)}")

    print("Displaying clipped model...")
    o3d.visualization.draw_geometries([clipped_cloud], window_name="Task 6: Clipped Model")

    # Task 7: Working with Color and Extremes
    print("\n" + "=" * 50)
    print("TASK 7: WORKING WITH COLOR AND EXTREMES — WIREFRAME CUBES")
    print("=" * 50)

    points = np.asarray(point_cloud.points)
    z_values = points[:, 2]
    z_min, z_max = np.min(z_values), np.max(z_values)
    normalized_z = (z_values - z_min) / (z_max - z_min) if z_max != z_min else np.zeros_like(z_values)

    colors = np.zeros((len(points), 3))
    colors[:, 0] = normalized_z
    colors[:, 1] = 1 - np.abs(normalized_z - 0.5) * 2
    colors[:, 2] = 1 - normalized_z

    colored_cloud = copy.deepcopy(point_cloud)
    colored_cloud.colors = o3d.utility.Vector3dVector(colors)

    z_min_idx = np.argmin(z_values)
    z_max_idx = np.argmax(z_values)
    min_point = points[z_min_idx]
    max_point = points[z_max_idx]

    print(f"Z-axis extremes:")
    print(f"  Minimum Z point: {min_point} (Z = {z_min:.3f})")
    print(f"  Maximum Z point: {max_point} (Z = {z_max:.3f})")

    bbox = colored_cloud.get_axis_aligned_bounding_box()
    cube_size = max(bbox.get_extent()) * 0.2

    def create_wire_cube(center, color):
        cube = o3d.geometry.TriangleMesh.create_box(width=cube_size,
                                                    height=cube_size,
                                                    depth=cube_size)
        cube.translate(center - np.array([cube_size / 2] * 3))
        wire = o3d.geometry.LineSet.create_from_triangle_mesh(cube)
        wire.paint_uniform_color(color)
        return wire

    min_wire = create_wire_cube(min_point, [0, 0, 1])
    max_wire = create_wire_cube(max_point, [1, 0, 0])
    axes = o3d.geometry.TriangleMesh.create_coordinate_frame(size=cube_size * 0.5)

    o3d.visualization.draw_geometries(
        [colored_cloud, min_wire, max_wire, axes],
        window_name="Task 7: Extremes with Wireframe Cubes",
        width=1200,
        height=800
    )


if __name__ == "__main__":
    main()
