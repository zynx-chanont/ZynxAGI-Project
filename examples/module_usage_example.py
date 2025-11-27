"""
ZynxAGI Modules - Usage Examples
=================================

This script demonstrates how to use the three core ZynxAGI modules:
1. Zynx Module - Universal AI Orchestration
2. Deeja Module - Emotional AI & Cultural Intelligence  
3. Zynx-Metadata Module - Autonomous IP Tracking

Run with: python examples/module_usage_example.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from zynx_agi.modules import ZynxModule, DeejaModule, ZynxMetadataModule
from zynx_agi.modules.zynx import ZynxRequest
from zynx_agi.modules.deeja import DeejaRequest


async def example_zynx_module():
    """Example: Using Zynx Module for AI orchestration"""
    print("\n" + "="*60)
    print("Example 1: Zynx Module - AI Orchestration")
    print("="*60)
    
    # Initialize Zynx module
    zynx = ZynxModule(config={
        "orchestration_rules": {
            "cultural_context_threshold": 0.7,
            "ip_guardrails_enabled": True
        }
    })
    
    await zynx.initialize()
    print(f"✓ Zynx module initialized: {zynx.module_id}")
    
    # Process English request
    print("\n--- Processing English request ---")
    request = ZynxRequest(message="Hello! How can you help me?")
    response = await zynx.process(request)
    
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Platform used: {response.platform_used}")
    print(f"Processing time: {response.processing_time_ms}ms")
    
    # Process Thai request (triggers cultural routing)
    print("\n--- Processing Thai request ---")
    request = ZynxRequest(message="สวัสดีครับ ผมต้องการความช่วยเหลือครับ")
    response = await zynx.process(request)
    
    print(f"Success: {response.success}")
    print(f"Message: {response.message}")
    print(f"Requires cultural intelligence: {response.routing_decision['requires_cultural_intelligence']}")
    print(f"Recommended platform: {response.routing_decision['recommended_platform']}")
    
    await zynx.shutdown()
    print("\n✓ Zynx module shutdown complete")


async def example_deeja_module():
    """Example: Using Deeja Module for emotional AI"""
    print("\n" + "="*60)
    print("Example 2: Deeja Module - Emotional AI & Cultural Intelligence")
    print("="*60)
    
    # Initialize Deeja module
    deeja = DeejaModule(config={
        "cultural_sensitivity_weight": 0.3,
        "thai_context_boost": 0.3
    })
    
    await deeja.initialize()
    print(f"✓ Deeja module initialized: {deeja.module_id}")
    
    # Process Thai message with cultural analysis
    print("\n--- Processing Thai cultural message ---")
    request = DeejaRequest(message="สวัสดีค่ะ ยินดีที่ได้รู้จักค่ะ ขอบคุณค่ะ")
    response = await deeja.process(request)
    
    print(f"Success: {response.success}")
    print(f"Response: {response.message}")
    print(f"Language detected: {response.cultural_analysis.language_detected}")
    print(f"Formality level: {response.cultural_analysis.formality_level:.2f}")
    print(f"Empathy score: {response.empathy_score:.3f}")
    print(f"Thai markers found: {len(response.cultural_analysis.thai_markers)}")
    
    # Process emotional message
    print("\n--- Processing emotional message ---")
    request = DeejaRequest(message="I'm feeling sad and lonely today")
    response = await deeja.process(request)
    
    print(f"Success: {response.success}")
    print(f"Response: {response.message}")
    print(f"Sentiment: {response.emotional_analysis.sentiment}")
    print(f"Emotions detected: {response.emotional_analysis.detected_emotions}")
    print(f"Empathy required: {response.emotional_analysis.empathy_required}")
    print(f"Empathy score: {response.empathy_score:.3f}")
    
    # Process positive message
    print("\n--- Processing positive message ---")
    request = DeejaRequest(message="I'm so happy! Thank you for everything!")
    response = await deeja.process(request)
    
    print(f"Success: {response.success}")
    print(f"Response: {response.message}")
    print(f"Sentiment: {response.emotional_analysis.sentiment}")
    print(f"Emotions detected: {response.emotional_analysis.detected_emotions}")
    
    await deeja.shutdown()
    print("\n✓ Deeja module shutdown complete")


async def example_metadata_module():
    """Example: Using Zynx-Metadata Module for IP tracking"""
    print("\n" + "="*60)
    print("Example 3: Zynx-Metadata Module - IP Tracking")
    print("="*60)
    
    # Initialize Zynx-Metadata module with temporary storage
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="zynx_demo_")
    
    metadata = ZynxMetadataModule(
        storage_path=Path(temp_dir),
        config={
            "auto_detect_intent": True,
            "generate_json": True,
            "generate_markdown": True
        }
    )
    
    await metadata.initialize()
    print(f"✓ Zynx-Metadata module initialized: {metadata.module_id}")
    print(f"  Storage path: {metadata.storage_path}")
    
    # Observe interaction with discovery intent
    print("\n--- Observing interaction with 'discover' intent ---")
    observation = await metadata.observe_interaction(
        agent_name="deeja",
        user_input="I discovered a new pattern in Thai language processing",
        agent_response="That's an interesting discovery! Tell me more."
    )
    
    print(f"Tracked: {observation.tracked}")
    if observation.tracked:
        print(f"Intent detected: {observation.intent_detected}")
        print(f"UUID: {observation.metadata.uuid}")
        print(f"SHA-256: {observation.metadata.sha256}")
        print(f"Created at: {observation.metadata.created_at}")
        print(f"License: {observation.metadata.license}")
        print(f"Files generated:")
        for format_type, path in observation.storage_paths.items():
            print(f"  - {format_type}: {path}")
    
    # Observe interaction without intent
    print("\n--- Observing interaction without intent ---")
    observation = await metadata.observe_interaction(
        agent_name="deeja",
        user_input="Hello, how are you?",
        agent_response="I'm doing well, thank you!"
    )
    
    print(f"Tracked: {observation.tracked}")
    print(f"Intent detected: {observation.intent_detected}")
    
    # Observe interaction with 'create' intent
    print("\n--- Observing interaction with 'create' intent ---")
    observation = await metadata.observe_interaction(
        agent_name="zynx",
        user_input="I want to create a new AI agent for Thai education",
        agent_response="That's a great idea! Let's design it together."
    )
    
    print(f"Tracked: {observation.tracked}")
    if observation.tracked:
        print(f"Intent detected: {observation.intent_detected}")
        print(f"UUID: {observation.metadata.uuid}")
    
    # List active sessions
    sessions = await metadata.list_active_sessions()
    print(f"\n--- Active tracking sessions ---")
    print(f"Total sessions: {len(sessions)}")
    for uuid, meta in sessions.items():
        print(f"  - {uuid[:8]}... : {meta.intent_detected}")
    
    await metadata.shutdown()
    print("\n✓ Zynx-Metadata module shutdown complete")
    print(f"  Demo logs saved to: {temp_dir}")


async def example_combined_usage():
    """Example: Using all three modules together"""
    print("\n" + "="*60)
    print("Example 4: Combined Module Usage")
    print("="*60)
    
    # Initialize all modules
    print("\n--- Initializing all modules ---")
    zynx = ZynxModule()
    deeja = DeejaModule()
    
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="zynx_combined_")
    metadata = ZynxMetadataModule(storage_path=Path(temp_dir))
    
    await zynx.initialize()
    await deeja.initialize()
    await metadata.initialize()
    
    print("✓ All modules initialized")
    
    # Process a message through the full pipeline
    print("\n--- Processing through full pipeline ---")
    user_message = "I discovered that Thai cultural AI needs more empathy"
    
    # 1. Route through Zynx
    print("\n1. Zynx orchestration:")
    zynx_response = await zynx.process(ZynxRequest(message=user_message))
    print(f"   Platform: {zynx_response.platform_used}")
    
    # 2. Analyze with Deeja
    print("\n2. Deeja cultural analysis:")
    deeja_response = await deeja.process(DeejaRequest(message=user_message))
    print(f"   Language: {deeja_response.cultural_analysis.language_detected}")
    print(f"   Empathy score: {deeja_response.empathy_score:.3f}")
    
    # 3. Track with Metadata
    print("\n3. Zynx-Metadata IP tracking:")
    observation = await metadata.observe_interaction(
        agent_name="combined_pipeline",
        user_input=user_message,
        agent_response=deeja_response.message
    )
    
    if observation.tracked:
        print(f"   Intent: {observation.intent_detected}")
        print(f"   UUID: {observation.metadata.uuid}")
    
    # Get status of all modules
    print("\n--- Module Status ---")
    zynx_status = await zynx.get_status()
    deeja_status = await deeja.get_status()
    metadata_status = await metadata.get_status()
    
    print(f"Zynx: Active={zynx_status['active']}, Platforms={len(zynx_status['platforms'])}")
    print(f"Deeja: Active={deeja_status['active']}, Contexts={len(deeja_status['cultural_contexts'])}")
    print(f"Metadata: Active={metadata_status['active']}, Sessions={metadata_status['active_sessions_count']}")
    
    # Cleanup
    await zynx.shutdown()
    await deeja.shutdown()
    await metadata.shutdown()
    
    print("\n✓ All modules shutdown complete")


async def main():
    """Run all examples"""
    print("\n" + "="*60)
    print("ZynxAGI Modules - Usage Examples")
    print("="*60)
    print("\nDemonstrating the three core ZynxAGI modules:")
    print("1. Zynx Module - Universal AI Orchestration")
    print("2. Deeja Module - Emotional AI & Cultural Intelligence")
    print("3. Zynx-Metadata Module - Autonomous IP Tracking")
    print("4. Combined Usage - All modules working together")
    
    try:
        # Run each example
        await example_zynx_module()
        await example_deeja_module()
        await example_metadata_module()
        await example_combined_usage()
        
        print("\n" + "="*60)
        print("All examples completed successfully! ✓")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
