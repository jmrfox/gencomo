"""
Test script for mesh functionality.
"""

import sys
import os

# Add the parent directory to path for importing gencomo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest
import trimesh

from gencomo.demos import create_cylinder_mesh, create_torus_mesh
from gencomo.mesh import MeshManager


class TestCreateCylinderMesh:
    """Test the create_cylinder_mesh function."""
    
    def test_create_cylinder_basic(self):
        """Test basic cylinder creation with default parameters."""
        mesh = create_cylinder_mesh()
        
        # Check that we get a trimesh object
        assert isinstance(mesh, trimesh.Trimesh)
        
        # Check that mesh has vertices and faces
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
        
        # Check metadata
        assert mesh.metadata["morphology_type"] == "cylinder"
        assert mesh.metadata["length"] == 100.0  # default
        assert mesh.metadata["radius"] == 5.0    # default
        
    def test_create_cylinder_custom_params(self):
        """Test cylinder creation with custom parameters."""
        length = 50.0
        radius = 3.0
        resolution = 32
        center = (1.0, 2.0, 3.0)
        axis = "x"
        
        mesh = create_cylinder_mesh(
            length=length,
            radius=radius,
            resolution=resolution,
            center=center,
            axis=axis
        )
        
        # Check metadata reflects custom parameters
        assert mesh.metadata["length"] == length
        assert mesh.metadata["radius"] == radius
        assert mesh.metadata["center"] == center
        assert mesh.metadata["axis"] == axis
        
        # Check theoretical volume calculation
        expected_volume = np.pi * radius**2 * length
        assert abs(mesh.metadata["volume_theoretical"] - expected_volume) < 1e-10
        
    def test_create_cylinder_different_axes(self):
        """Test cylinder creation along different axes."""
        for axis in ["x", "y", "z"]:
            mesh = create_cylinder_mesh(axis=axis)
            assert mesh.metadata["axis"] == axis
            assert isinstance(mesh, trimesh.Trimesh)


class TestCreateTorusMesh:
    """Test the create_torus_mesh function."""
    
    def test_create_torus_basic(self):
        """Test basic torus creation with default parameters."""
        mesh = create_torus_mesh()
        
        # Check that we get a trimesh object
        assert isinstance(mesh, trimesh.Trimesh)
        
        # Check that mesh has vertices and faces
        assert len(mesh.vertices) > 0
        assert len(mesh.faces) > 0
        
        # Check metadata
        assert mesh.metadata["morphology_type"] == "torus"
        assert mesh.metadata["major_radius"] == 20.0  # default
        assert mesh.metadata["minor_radius"] == 5.0   # default
        
    def test_create_torus_custom_params(self):
        """Test torus creation with custom parameters."""
        major_radius = 15.0
        minor_radius = 3.0
        major_segments = 24
        minor_segments = 16
        center = (1.0, 2.0, 3.0)
        axis = "y"
        
        mesh = create_torus_mesh(
            major_radius=major_radius,
            minor_radius=minor_radius,
            major_segments=major_segments,
            minor_segments=minor_segments,
            center=center,
            axis=axis
        )
        
        # Check metadata reflects custom parameters
        assert mesh.metadata["major_radius"] == major_radius
        assert mesh.metadata["minor_radius"] == minor_radius
        assert mesh.metadata["center"] == center
        assert mesh.metadata["axis"] == axis
        
        # Check theoretical volume calculation
        expected_volume = 2 * np.pi**2 * major_radius * minor_radius**2
        assert abs(mesh.metadata["volume_theoretical"] - expected_volume) < 1e-10
        
        # Check theoretical surface area calculation
        expected_surface_area = 4 * np.pi**2 * major_radius * minor_radius
        assert abs(mesh.metadata["surface_area_theoretical"] - expected_surface_area) < 1e-10
        
    def test_create_torus_different_axes(self):
        """Test torus creation along different axes."""
        for axis in ["x", "y", "z"]:
            mesh = create_torus_mesh(axis=axis)
            assert mesh.metadata["axis"] == axis
            assert isinstance(mesh, trimesh.Trimesh)
            
    def test_create_torus_different_segments(self):
        """Test torus creation with different segment counts."""
        segment_configs = [
            {"major_segments": 12, "minor_segments": 8},
            {"major_segments": 20, "minor_segments": 12},
            {"major_segments": 32, "minor_segments": 16},
        ]
        
        for config in segment_configs:
            mesh = create_torus_mesh(**config)
            assert isinstance(mesh, trimesh.Trimesh)
            # More segments should generally result in more vertices
            assert len(mesh.vertices) > 0
            assert len(mesh.faces) > 0


class TestMeshManager:
    """Test the MeshManager class."""
    
    @pytest.fixture
    def simple_cylinder(self):
        """Create a simple cylinder mesh for testing."""
        return create_cylinder_mesh(length=20.0, radius=2.0, resolution=16)
    
    @pytest.fixture
    def simple_torus(self):
        """Create a simple torus mesh for testing."""
        return create_torus_mesh(major_radius=10.0, minor_radius=2.0, major_segments=20, minor_segments=12)
    
    @pytest.fixture
    def mesh_manager(self, simple_cylinder):
        """Create a MeshManager instance with a simple cylinder."""
        return MeshManager(simple_cylinder, verbose=False)
        
    @pytest.fixture
    def torus_manager(self, simple_torus):
        """Create a MeshManager instance with a simple torus."""
        return MeshManager(simple_torus, verbose=False)
    
    def test_mesh_manager_init(self, simple_cylinder):
        """Test MeshManager initialization."""
        manager = MeshManager(simple_cylinder, verbose=True)
        
        assert manager.mesh is not None
        assert manager.original_mesh is not None
        assert manager.verbose is True
        assert manager.bounds is not None
        assert isinstance(manager.stats, dict)
        
    def test_mesh_manager_init_no_mesh(self):
        """Test MeshManager initialization without a mesh."""
        manager = MeshManager(verbose=False)
        
        assert manager.mesh is None
        assert manager.original_mesh is None
        assert manager.bounds is None
        
    def test_copy(self, mesh_manager):
        """Test mesh manager copy functionality."""
        copied = mesh_manager.copy()
        
        assert isinstance(copied, MeshManager)
        assert copied.mesh is not mesh_manager.mesh  # Different objects
        assert np.array_equal(copied.mesh.vertices, mesh_manager.mesh.vertices)
        
    def test_to_trimesh(self, mesh_manager):
        """Test conversion to trimesh object."""
        trimesh_obj = mesh_manager.to_trimesh()
        
        assert isinstance(trimesh_obj, trimesh.Trimesh)
        assert trimesh_obj is mesh_manager.mesh
        
    def test_compute_bounds(self, mesh_manager):
        """Test bounds computation."""
        bounds = mesh_manager.bounds
        
        assert bounds is not None
        assert "x" in bounds
        assert "y" in bounds
        assert "z" in bounds
        
        # Each bound should be a tuple of (min, max)
        for axis in ["x", "y", "z"]:
            assert isinstance(bounds[axis], tuple)
            assert len(bounds[axis]) == 2
            assert bounds[axis][0] <= bounds[axis][1]  # min <= max
            
    def test_get_z_range(self, mesh_manager):
        """Test z-range retrieval."""
        z_range = mesh_manager.get_z_range()
        
        assert isinstance(z_range, tuple)
        assert len(z_range) == 2
        assert z_range[0] <= z_range[1]  # min <= max
        
    def test_get_z_range_no_mesh(self):
        """Test z-range retrieval with no mesh loaded."""
        manager = MeshManager()
        
        with pytest.raises(ValueError, match="No mesh loaded"):
            manager.get_z_range()
            
    def test_center_mesh_centroid(self, mesh_manager):
        """Test mesh centering on centroid."""
        original_centroid = mesh_manager.mesh.centroid.copy()
        
        centered_mesh = mesh_manager.center_mesh(center_on="centroid")
        
        assert isinstance(centered_mesh, trimesh.Trimesh)
        # After centering on centroid, the centroid should be close to origin
        new_centroid = centered_mesh.centroid
        assert np.allclose(new_centroid, [0, 0, 0], atol=1e-10)
        
    def test_center_mesh_bounds(self, mesh_manager):
        """Test mesh centering on bounds center."""
        centered_mesh = mesh_manager.center_mesh(center_on="bounds_center")
        
        assert isinstance(centered_mesh, trimesh.Trimesh)
        # Check that bounds center is close to origin
        bounds_center = centered_mesh.bounds.mean(axis=0)
        assert np.allclose(bounds_center, [0, 0, 0], atol=1e-10)
        
    def test_center_mesh_no_mesh(self):
        """Test centering with no mesh loaded."""
        manager = MeshManager()
        
        with pytest.raises(ValueError, match="No mesh loaded"):
            manager.center_mesh()
            
    def test_scale_mesh(self, mesh_manager):
        """Test mesh scaling."""
        scale_factor = 2.0
        original_volume = mesh_manager.mesh.volume
        
        scaled_mesh = mesh_manager.scale_mesh(scale_factor)
        
        assert isinstance(scaled_mesh, trimesh.Trimesh)
        # Volume should scale by factor^3
        expected_volume = original_volume * (scale_factor ** 3)
        # Use relative tolerance since mesh scaling modifies in-place
        assert abs(scaled_mesh.volume - expected_volume) / expected_volume < 0.01
        
    def test_analyze_mesh(self, mesh_manager):
        """Test mesh analysis functionality."""
        analysis = mesh_manager.analyze_mesh()
        
        assert isinstance(analysis, dict)
        
        # Check for expected keys in analysis (based on actual implementation)
        expected_keys = [
            "volume", "is_watertight", "is_winding_consistent",
            "face_count", "vertex_count", "bounds", "issues"
        ]
        
        for key in expected_keys:
            assert key in analysis
            
        # Check data types
        assert isinstance(analysis["volume"], (int, float, type(None)))
        assert isinstance(analysis["is_watertight"], bool)
        assert isinstance(analysis["face_count"], int)
        assert isinstance(analysis["vertex_count"], int)
        assert isinstance(analysis["bounds"], (list, type(None)))
        assert isinstance(analysis["issues"], list)
        
    def test_analyze_mesh_no_mesh(self):
        """Test analysis with no mesh loaded."""
        manager = MeshManager()
        
        with pytest.raises(AttributeError):
            manager.analyze_mesh()


class TestMeshManagerIntegration:
    """Integration tests combining create_cylinder_mesh, create_torus_mesh, and MeshManager."""
    
    def test_cylinder_to_manager_workflow(self):
        """Test complete workflow from cylinder creation to mesh management."""
        # Create cylinder
        cylinder = create_cylinder_mesh(length=30.0, radius=4.0, resolution=20)
        
        # Create manager
        manager = MeshManager(cylinder, verbose=False)
        
        # Test analysis
        analysis = manager.analyze_mesh()
        assert analysis["volume"] > 0
        assert analysis["face_count"] > 0
        assert analysis["vertex_count"] > 0
        
        # Test centering
        centered = manager.center_mesh()
        assert np.allclose(centered.centroid, [0, 0, 0], atol=1e-10)
        
        # Test scaling (note: scale_mesh modifies in-place)
        original_volume = cylinder.volume
        scaled = manager.scale_mesh(0.5)
        # Volume should be reduced by factor^3 = 0.5^3 = 0.125
        expected_volume = original_volume * (0.5 ** 3)
        assert abs(scaled.volume - expected_volume) / expected_volume < 0.01
        
    def test_torus_to_manager_workflow(self):
        """Test complete workflow from torus creation to mesh management."""
        # Create torus
        torus = create_torus_mesh(major_radius=15.0, minor_radius=3.0, major_segments=24, minor_segments=16)
        
        # Create manager
        manager = MeshManager(torus, verbose=False)
        
        # Test analysis
        analysis = manager.analyze_mesh()
        assert analysis["volume"] > 0
        assert analysis["face_count"] > 0
        assert analysis["vertex_count"] > 0
        
        # Test centering
        centered = manager.center_mesh()
        assert np.allclose(centered.centroid, [0, 0, 0], atol=1e-10)
        
        # Test scaling (note: scale_mesh modifies in-place)
        original_volume = torus.volume
        scaled = manager.scale_mesh(0.5)
        # Volume should be reduced by factor^3 = 0.5^3 = 0.125
        expected_volume = original_volume * (0.5 ** 3)
        assert abs(scaled.volume - expected_volume) / expected_volume < 0.01
        
    def test_multiple_cylinders_comparison(self):
        """Test creating and comparing multiple cylinders."""
        cylinders = []
        managers = []
        
        # Create cylinders with different parameters
        params = [
            {"length": 10.0, "radius": 1.0},
            {"length": 20.0, "radius": 2.0},
            {"length": 30.0, "radius": 3.0},
        ]
        
        for param in params:
            cylinder = create_cylinder_mesh(**param)
            manager = MeshManager(cylinder, verbose=False)
            
            cylinders.append(cylinder)
            managers.append(manager)
            
        # Verify volumes increase as expected
        volumes = [m.analyze_mesh()["volume"] for m in managers]
        
        # Each subsequent cylinder should have larger volume
        assert volumes[0] < volumes[1] < volumes[2]
        
        # Verify theoretical vs actual volumes are close
        for i, (cylinder, manager) in enumerate(zip(cylinders, managers)):
            theoretical = cylinder.metadata["volume_theoretical"]
            actual = manager.analyze_mesh()["volume"]
            # Allow some tolerance for mesh discretization
            assert abs(theoretical - actual) / theoretical < 0.1  # Within 10%
            
    def test_multiple_tori_comparison(self):
        """Test creating and comparing multiple tori."""
        tori = []
        managers = []
        
        # Create tori with different parameters
        params = [
            {"major_radius": 10.0, "minor_radius": 1.0},
            {"major_radius": 20.0, "minor_radius": 2.0},
            {"major_radius": 30.0, "minor_radius": 3.0},
        ]
        
        for param in params:
            torus = create_torus_mesh(**param)
            manager = MeshManager(torus, verbose=False)
            
            tori.append(torus)
            managers.append(manager)
            
        # Verify volumes increase as expected
        volumes = [m.analyze_mesh()["volume"] for m in managers]
        
        # Each subsequent torus should have larger volume
        assert volumes[0] < volumes[1] < volumes[2]
        
        # Verify theoretical vs actual volumes are close
        for i, (torus, manager) in enumerate(zip(tori, managers)):
            theoretical = torus.metadata["volume_theoretical"]
            actual = manager.analyze_mesh()["volume"]
            # Allow some tolerance for mesh discretization
            assert abs(theoretical - actual) / theoretical < 0.1  # Within 10%
            
    def test_mixed_mesh_types_comparison(self):
        """Test comparing different mesh types (cylinder vs torus)."""
        # Create meshes with similar volumes for comparison
        cylinder = create_cylinder_mesh(length=20.0, radius=3.0, resolution=20)
        torus = create_torus_mesh(major_radius=8.0, minor_radius=2.0, major_segments=20, minor_segments=12)
        
        # Create managers
        cyl_manager = MeshManager(cylinder, verbose=False)
        tor_manager = MeshManager(torus, verbose=False)
        
        # Both should analyze successfully
        cyl_analysis = cyl_manager.analyze_mesh()
        tor_analysis = tor_manager.analyze_mesh()
        
        # Both should have positive volumes
        assert cyl_analysis["volume"] > 0
        assert tor_analysis["volume"] > 0
        
        # Both should be watertight (for well-formed meshes)
        assert cyl_analysis["is_watertight"]
        assert tor_analysis["is_watertight"]
        
        # Torus should have genus 1, cylinder should have genus 0
        if cyl_analysis.get("genus") is not None:
            assert cyl_analysis["genus"] == 0
        if tor_analysis.get("genus") is not None:
            assert tor_analysis["genus"] == 1


if __name__ == "__main__":
    # Run tests when script is executed directly
    pytest.main([__file__, "-v"])
