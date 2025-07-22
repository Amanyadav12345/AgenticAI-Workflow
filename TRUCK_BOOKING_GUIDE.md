# 🚛 Truck Booking Agent System

Your two-agent truck booking system has been successfully implemented! This system handles the complete workflow from truck search to booking confirmation.

## System Overview

### Agent 1: Trip Planning Agent
**Role**: Trip Planning Specialist  
**Responsibilities**:
- Search for available trucks from point A to B
- Present truck options to users
- Collect detailed trip information
- Validate all required details

**Tools Available**:
- `TruckSearchTool`: Finds available trucks by location
- `TripDetailCollectorTool`: Collects consigner, consignee, and parcel details
- `NotificationTool`: Sends notifications to users

### Agent 2: Availability Verification Agent
**Role**: Truck Availability Verification Specialist  
**Responsibilities**:
- Contact truck owners to verify availability
- Confirm or decline bookings
- Notify users of booking status
- Handle alternative truck selection if needed

**Tools Available**:
- `TruckOwnerContactTool`: Contacts truck owners for verification
- `NotificationTool`: Sends booking confirmations or rejections

## Complete Workflow

### Step 1: User Request
User says: *"I need a truck from Mumbai to Delhi"*

### Step 2: Agent 1 - Truck Search
1. **TruckSearchTool** searches for available trucks
2. Returns list of trucks with details:
   - Truck ID, Owner Name, Contact
   - Truck Type, Capacity, Price
   - Rating and Availability Status

### Step 3: User Selection
User selects a truck from the presented options

### Step 4: Agent 1 - Detail Collection
**TripDetailCollectorTool** collects:
- **Consigner Details**: Name and information
- **Consignee Details**: Name and information  
- **Addresses**: Pickup and delivery locations
- **Parcel Info**: Size, weight, value
- **Special Instructions**: Any handling requirements

### Step 5: Agent 2 - Availability Verification
1. **TruckOwnerContactTool** contacts the truck owner
2. Verifies availability for requested dates/route
3. Returns one of:
   - ✅ **Available**: Booking confirmed with reference number
   - ❌ **Not Available**: User needs to select another truck

### Step 6: Completion
- If available: Booking confirmed with reference number
- If not available: Agent 1 asks user to select another truck

## Sample Truck Search Results

```json
{
  "available_trucks": [
    {
      "truck_id": "TRK001",
      "owner_name": "ABC Transport", 
      "contact": "+91-9876543210",
      "truck_type": "Medium Truck",
      "capacity": "5 tons",
      "price_per_km": 25,
      "estimated_total": 2500,
      "rating": 4.5
    },
    {
      "truck_id": "TRK002",
      "owner_name": "XYZ Logistics",
      "contact": "+91-9876543211", 
      "truck_type": "Large Truck",
      "capacity": "10 tons",
      "price_per_km": 35,
      "estimated_total": 3500,
      "rating": 4.2
    }
  ]
}
```

## Required Trip Details

When a user selects a truck, these details are collected:

### Required Fields:
- ✅ **Consigner Name**: Person sending the parcel
- ✅ **Consignee Name**: Person receiving the parcel
- ✅ **Pickup Address**: Complete pickup location
- ✅ **Delivery Address**: Complete delivery location  
- ✅ **Parcel Size**: Dimensions (e.g., "2m x 1m x 1m")
- ✅ **Parcel Weight**: Weight (e.g., "500kg")

### Optional Fields:
- **Parcel Value**: Declared value for insurance
- **Special Instructions**: Fragile, urgent, etc.

## Testing the System

Run the test to see the workflow in action:

```bash
# Test individual components
python simple_test.py

# Test with CrewAI integration (if dependencies are installed)
cd amanfirstagent/src
python -m amanfirstagent.main truck_booking
```

## Integration Points

### API Endpoints (for real implementation):
1. **Truck Search API**: `GET /api/trucks/search?from={pickup}&to={delivery}`
2. **Booking API**: `POST /api/bookings`
3. **Owner Contact API**: `POST /api/owners/contact`

### Database Tables Needed:
- `trucks` (id, owner_id, type, capacity, location, status)
- `owners` (id, name, contact, rating)
- `bookings` (id, truck_id, user_id, details, status)
- `trip_details` (booking_id, consigner, consignee, addresses, parcel_info)

## Security Features

- Input validation for all user inputs
- Phone number and email masking in logs
- Dangerous pattern detection
- SQL injection prevention
- Rate limiting for API calls

## Next Steps

1. **Integration with Telegram Bot**: Connect to your existing telegram_bot.py
2. **Real API Connections**: Replace simulated responses with actual API calls
3. **Database Integration**: Store bookings and truck information
4. **Payment Integration**: Add payment processing
5. **Real-time Tracking**: GPS tracking for booked trucks
6. **SMS/Email Notifications**: Send booking confirmations

Your truck booking system is ready to handle the complete user journey from "I need a truck" to "Booking confirmed"! 🎉