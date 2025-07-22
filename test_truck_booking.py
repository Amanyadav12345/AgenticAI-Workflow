
#!/usr/bin/env python
"""
Test script for truck booking workflow
"""
import sys
import os

# Add the amanfirstagent src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'amanfirstagent', 'src'))

from amanfirstagent.tools.workflow_tools import (
    TruckSearchTool, 
    TripDetailCollectorTool, 
    TruckOwnerContactTool
)

def test_truck_search():
    """Test truck search functionality"""
    print("Testing Truck Search...")
    tool = TruckSearchTool()
    result = tool._run("Mumbai", "Delhi", "2025-07-25")
    print(f"Truck Search Result: {result}")
    return result

def test_trip_detail_collection():
    """Test trip detail collection"""
    print("\nTesting Trip Detail Collection...")
    tool = TripDetailCollectorTool()
    result = tool._run(
        truck_id="TRK001",
        consigner_name="John Doe",
        consignee_name="Jane Smith", 
        pickup_address="123 Main St, Mumbai",
        delivery_address="456 Oak Ave, Delhi",
        parcel_size="2m x 1m x 1m",
        parcel_weight="500kg",
        parcel_value="50000"
    )
    print(f"Trip Detail Collection Result: {result}")
    return result

def test_truck_owner_contact():
    """Test truck owner contact"""
    print("\nTesting Truck Owner Contact...")
    tool = TruckOwnerContactTool()
    result = tool._run(
        truck_id="TRK001",
        owner_contact="+91-9876543210",
        trip_details={
            "pickup": "Mumbai",
            "delivery": "Delhi", 
            "date": "2025-07-25"
        }
    )
    print(f"Truck Owner Contact Result: {result}")
    return result

def main():
    """Run all tests"""
    print("Testing Truck Booking Workflow Components\n")
    print("=" * 50)
    
    try:
        # Test individual components
        test_truck_search()
        test_trip_detail_collection()
        test_truck_owner_contact()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()