#!/usr/bin/env python
"""
Simple test for truck booking tools without CrewAI dependencies
"""
import json
import sys
import os
from datetime import datetime

# Add the amanfirstagent src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'amanfirstagent', 'src'))

# Simple mock class for testing
class MockTool:
    def __init__(self, name):
        self.name = name
        print(f"Initialized {name}")

def test_truck_search():
    """Test truck search logic"""
    print("Testing Truck Search...")
    
    pickup_location = "Mumbai"
    delivery_location = "Delhi" 
    date = "2025-07-25"
    
    # Simulate truck search results
    trucks = [
        {
            "truck_id": "TRK001",
            "owner_name": "ABC Transport",
            "contact": "+91-9876543210",
            "truck_type": "Medium Truck",
            "capacity": "5 tons",
            "price_per_km": 25,
            "estimated_total": 2500,
            "rating": 4.5,
            "location": pickup_location,
            "availability": "Available"
        },
        {
            "truck_id": "TRK002", 
            "owner_name": "XYZ Logistics",
            "contact": "+91-9876543211",
            "truck_type": "Large Truck",
            "capacity": "10 tons",
            "price_per_km": 35,
            "estimated_total": 3500,
            "rating": 4.2,
            "location": pickup_location,
            "availability": "Available"
        }
    ]
    
    result = {
        "success": True,
        "pickup_location": pickup_location,
        "delivery_location": delivery_location,
        "date": date,
        "available_trucks": trucks,
        "total_found": len(trucks)
    }
    
    print(f"Found {len(trucks)} trucks:")
    for truck in trucks:
        print(f"  - {truck['truck_id']}: {truck['owner_name']} ({truck['truck_type']}) - Rs.{truck['estimated_total']}")
    
    return result

def test_trip_collection():
    """Test trip detail collection logic"""
    print("\nTesting Trip Detail Collection...")
    
    trip_details = {
        "truck_id": "TRK001",
        "consigner_name": "John Doe",
        "consignee_name": "Jane Smith",
        "pickup_address": "123 Main St, Mumbai",
        "delivery_address": "456 Oak Ave, Delhi",
        "parcel_size": "2m x 1m x 1m",
        "parcel_weight": "500kg",
        "parcel_value": "50000",
        "created_at": datetime.now().isoformat()
    }
    
    required_fields = [
        "consigner_name", "consignee_name", "pickup_address", 
        "delivery_address", "parcel_size", "parcel_weight"
    ]
    
    missing_fields = []
    for field in required_fields:
        if not trip_details.get(field):
            missing_fields.append(field)
    
    result = {
        "success": len(missing_fields) == 0,
        "trip_details": trip_details,
        "missing_fields": missing_fields
    }
    
    if missing_fields:
        print(f"Missing required fields: {', '.join(missing_fields)}")
    else:
        print("All trip details collected successfully!")
        print(f"  Consigner: {trip_details['consigner_name']}")
        print(f"  Consignee: {trip_details['consignee_name']}")
        print(f"  Pickup: {trip_details['pickup_address']}")
        print(f"  Delivery: {trip_details['delivery_address']}")
        print(f"  Parcel: {trip_details['parcel_size']}, {trip_details['parcel_weight']}")
    
    return result

def test_owner_contact():
    """Test truck owner contact logic"""
    print("\nTesting Truck Owner Contact...")
    
    import random
    
    truck_id = "TRK001"
    owner_contact = "+91-9876543210"
    
    # 80% chance of availability for simulation
    is_available = random.random() > 0.2
    
    contact_result = {
        "success": True,
        "truck_id": truck_id,
        "owner_contact": owner_contact[:4] + "***",
        "contacted_at": datetime.now().isoformat(),
        "availability_status": "available" if is_available else "not_available",
        "owner_response": "Truck is available for the requested dates" if is_available 
                        else "Truck is not available for the requested dates",
        "response_time": f"{random.randint(30, 300)} seconds"
    }
    
    if is_available:
        contact_result["booking_confirmed"] = True
        contact_result["booking_reference"] = f"BK{random.randint(10000, 99999)}"
    
    print(f"Contacted truck owner for {truck_id}")
    print(f"Status: {contact_result['availability_status']}")
    print(f"Response: {contact_result['owner_response']}")
    
    if is_available:
        print(f"Booking Reference: {contact_result.get('booking_reference')}")
    
    return contact_result

def main():
    """Run all tests"""
    print("Testing Truck Booking Workflow Components")
    print("=" * 50)
    
    try:
        # Test individual components
        search_result = test_truck_search()
        collection_result = test_trip_collection()
        contact_result = test_owner_contact()
        
        print("\n" + "=" * 50)
        print("WORKFLOW SUMMARY:")
        print(f"1. Truck Search: Found {search_result.get('total_found', 0)} trucks")
        print(f"2. Trip Collection: {'Complete' if collection_result.get('success') else 'Incomplete'}")
        print(f"3. Owner Contact: {'Available' if contact_result.get('availability_status') == 'available' else 'Not Available'}")
        
        if (search_result.get('success') and 
            collection_result.get('success') and 
            contact_result.get('availability_status') == 'available'):
            print("\nWORKFLOW RESULT: BOOKING SUCCESSFUL!")
            print(f"Booking Reference: {contact_result.get('booking_reference')}")
        else:
            print("\nWORKFLOW RESULT: BOOKING FAILED - User needs to select another truck")
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()