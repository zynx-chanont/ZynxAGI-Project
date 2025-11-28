"""
Tests for Metadata Schema Lock + Attribution System
"""

import pytest
import json
from zynx_agi.core.schema_lock import (
    MetadataSchemaLock,
    AttributionManager,
    AttributionInfo,
    SchemaDefinition,
    SchemaLockStatus,
    get_schema_lock,
    get_attribution_manager,
    register_standard_schemas
)


class TestMetadataSchemaLock:
    """Tests for MetadataSchemaLock class"""
    
    def test_register_schema(self):
        """Test schema registration"""
        lock_manager = MetadataSchemaLock()
        
        schema = lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1", "field2"],
            optional_fields=["field3"],
            description="Test schema"
        )
        
        assert schema.name == "test_schema"
        assert schema.version == "1.0.0"
        assert schema.required_fields == ["field1", "field2"]
        assert schema.optional_fields == ["field3"]
        assert schema.status == SchemaLockStatus.UNLOCKED
        assert schema.attribution is not None  # Auto-attributed
    
    def test_lock_schema(self):
        """Test schema locking"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"]
        )
        
        result = lock_manager.lock_schema("test_schema")
        
        assert result["schema_name"] == "test_schema"
        assert result["lock_hash"] is not None
        assert result["lock_timestamp"] is not None
        assert result["status"] == "locked"
        assert result["immutable"] is False
        
        # Verify schema is now locked
        schema = lock_manager.get_schema("test_schema")
        assert schema.status == SchemaLockStatus.LOCKED
    
    def test_lock_schema_immutable(self):
        """Test making schema immutable"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"]
        )
        
        result = lock_manager.lock_schema("test_schema", make_immutable=True)
        
        assert result["status"] == "immutable"
        assert result["immutable"] is True
        
        # Cannot relock immutable schema
        with pytest.raises(ValueError, match="immutable"):
            lock_manager.lock_schema("test_schema")
    
    def test_cannot_modify_locked_schema(self):
        """Test that locked schemas cannot be modified"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"]
        )
        lock_manager.lock_schema("test_schema")
        
        # Attempting to re-register should fail
        with pytest.raises(ValueError, match="locked"):
            lock_manager.register_schema(
                name="test_schema",
                version="2.0.0",
                required_fields=["field1", "field2"]
            )
    
    def test_verify_integrity_valid(self):
        """Test integrity verification with valid schema"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"]
        )
        lock_manager.lock_schema("test_schema")
        
        result = lock_manager.verify_integrity("test_schema")
        
        assert result["verified"] is True
        assert result["schema_name"] == "test_schema"
        assert result["expected_hash"] == result["computed_hash"]
    
    def test_verify_integrity_unlocked(self):
        """Test integrity verification with unlocked schema"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"]
        )
        
        result = lock_manager.verify_integrity("test_schema")
        
        assert result["verified"] is False
        assert "not locked" in result["reason"]
    
    def test_validate_metadata_valid(self):
        """Test metadata validation with valid data"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1", "field2"],
            optional_fields=["field3"]
        )
        
        result = lock_manager.validate_metadata(
            "test_schema",
            {"field1": "value1", "field2": "value2"}
        )
        
        assert result["valid"] is True
        assert result["missing_fields"] == []
    
    def test_validate_metadata_missing_fields(self):
        """Test metadata validation with missing required fields"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1", "field2"]
        )
        
        result = lock_manager.validate_metadata(
            "test_schema",
            {"field1": "value1"}  # Missing field2
        )
        
        assert result["valid"] is False
        assert "field2" in result["missing_fields"]
    
    def test_validate_metadata_type_checking(self):
        """Test metadata validation with type checking"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="test_schema",
            version="1.0.0",
            required_fields=["field1"],
            field_types={"field1": "str"}
        )
        
        # Valid type
        result = lock_manager.validate_metadata(
            "test_schema",
            {"field1": "string_value"}
        )
        assert result["valid"] is True
        
        # Invalid type
        result = lock_manager.validate_metadata(
            "test_schema",
            {"field1": 123}  # Should be str, is int
        )
        assert result["valid"] is False
        assert len(result["invalid_types"]) == 1
    
    def test_list_schemas(self):
        """Test listing registered schemas"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="schema1",
            version="1.0.0",
            required_fields=["f1"]
        )
        lock_manager.register_schema(
            name="schema2",
            version="1.0.0",
            required_fields=["f1", "f2"]
        )
        lock_manager.lock_schema("schema1")
        
        schemas = lock_manager.list_schemas()
        
        assert len(schemas) == 2
        
        schema1 = next(s for s in schemas if s["name"] == "schema1")
        assert schema1["locked"] is True
        
        schema2 = next(s for s in schemas if s["name"] == "schema2")
        assert schema2["locked"] is False
    
    def test_lock_history(self):
        """Test lock history tracking"""
        lock_manager = MetadataSchemaLock()
        
        lock_manager.register_schema(
            name="schema1",
            version="1.0.0",
            required_fields=["f1"]
        )
        lock_manager.lock_schema("schema1")
        
        history = lock_manager.get_lock_history()
        
        assert len(history) == 1
        assert history[0]["schema_name"] == "schema1"
        assert history[0]["action"] == "lock"


class TestAttributionManager:
    """Tests for AttributionManager class"""
    
    def test_create_attribution(self):
        """Test creating attribution"""
        manager = AttributionManager()
        
        attribution = manager.create_attribution()
        
        assert attribution.author == "Chanont Wankaew"
        assert attribution.organization == "Zynx Thailand"
        assert attribution.license == "ZPDL v1.0 © Chanont Wankaew"
        assert attribution.uuid is not None
        assert attribution.created_at is not None
    
    def test_create_attribution_custom(self):
        """Test creating attribution with custom values"""
        manager = AttributionManager()
        
        attribution = manager.create_attribution(
            author="Custom Author",
            organization="Custom Org"
        )
        
        assert attribution.author == "Custom Author"
        assert attribution.organization == "Custom Org"
    
    def test_embed_attribution(self):
        """Test embedding attribution in content"""
        manager = AttributionManager()
        
        content = {"key": "value", "data": [1, 2, 3]}
        attributed = manager.embed_attribution(content)
        
        assert "_attribution" in attributed
        assert attributed["_attribution"]["author"] == "Chanont Wankaew"
        assert attributed["_attribution"]["content_hash"] is not None
        assert attributed["key"] == "value"  # Original content preserved
    
    def test_verify_attribution_valid(self):
        """Test verifying valid attribution"""
        manager = AttributionManager()
        
        content = {"key": "value"}
        attributed = manager.embed_attribution(content)
        
        result = manager.verify_attribution(attributed)
        
        assert result["verified"] is True
        assert result["has_attribution"] is True
        assert result["author"] == "Chanont Wankaew"
    
    def test_verify_attribution_modified_content(self):
        """Test verifying attribution after content modification"""
        manager = AttributionManager()
        
        content = {"key": "value"}
        attributed = manager.embed_attribution(content)
        
        # Modify content after attribution
        attributed["key"] = "modified_value"
        
        result = manager.verify_attribution(attributed)
        
        assert result["verified"] is False
        assert "modified" in result["reason"]
    
    def test_verify_attribution_no_attribution(self):
        """Test verifying content without attribution"""
        manager = AttributionManager()
        
        content = {"key": "value"}  # No attribution
        
        result = manager.verify_attribution(content)
        
        assert result["verified"] is False
        assert result["has_attribution"] is False
    
    def test_attribution_report(self):
        """Test generating attribution report"""
        manager = AttributionManager()
        
        # Create some attributions
        manager.embed_attribution({"data": 1})
        manager.embed_attribution({"data": 2})
        
        report = manager.generate_attribution_report()
        
        assert report["total_attributions"] == 2
        assert report["default_author"] == "Chanont Wankaew"
        assert len(report["attribution_log"]) == 2
    
    def test_get_attribution_by_uuid(self):
        """Test retrieving attribution by UUID"""
        manager = AttributionManager()
        
        attribution = manager.create_attribution()
        manager.embed_attribution({"data": 1}, attribution)
        
        retrieved = manager.get_attribution_by_uuid(attribution.uuid)
        
        assert retrieved is not None
        assert retrieved["uuid"] == attribution.uuid


class TestGlobalInstances:
    """Tests for global instance accessors"""
    
    def test_get_schema_lock(self):
        """Test getting default schema lock instance"""
        lock1 = get_schema_lock()
        lock2 = get_schema_lock()
        
        # Should return the same instance
        assert lock1 is lock2
    
    def test_get_attribution_manager(self):
        """Test getting default attribution manager instance"""
        manager1 = get_attribution_manager()
        manager2 = get_attribution_manager()
        
        # Should return the same instance
        assert manager1 is manager2


class TestStandardSchemas:
    """Tests for standard schema registration"""
    
    def test_register_standard_schemas(self):
        """Test registering standard schemas"""
        lock_manager = MetadataSchemaLock()
        register_standard_schemas(lock_manager)
        
        schemas = lock_manager.list_schemas()
        schema_names = [s["name"] for s in schemas]
        
        assert "session_metadata" in schema_names
        assert "artifact_metadata" in schema_names
        assert "attribution_metadata" in schema_names
        
        # All should be locked
        for schema in schemas:
            assert schema["locked"] is True
        
        # Attribution metadata should be immutable
        attribution_schema = next(s for s in schemas if s["name"] == "attribution_metadata")
        assert attribution_schema["immutable"] is True
    
    def test_standard_schema_integrity(self):
        """Test integrity of standard schemas"""
        lock_manager = MetadataSchemaLock()
        register_standard_schemas(lock_manager)
        
        for schema_name in ["session_metadata", "artifact_metadata", "attribution_metadata"]:
            result = lock_manager.verify_integrity(schema_name)
            assert result["verified"] is True, f"Schema {schema_name} failed integrity check"


class TestAttributionInfo:
    """Tests for AttributionInfo model"""
    
    def test_default_values(self):
        """Test AttributionInfo default values"""
        info = AttributionInfo()
        
        assert info.author == "Chanont Wankaew"
        assert info.organization == "Zynx Thailand"
        assert info.license == "ZPDL v1.0 © Chanont Wankaew"
        assert "First discovered" in info.ip_notice
        assert info.uuid is not None
        assert info.created_at is not None
    
    def test_custom_values(self):
        """Test AttributionInfo with custom values"""
        info = AttributionInfo(
            author="Test Author",
            organization="Test Org"
        )
        
        assert info.author == "Test Author"
        assert info.organization == "Test Org"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
