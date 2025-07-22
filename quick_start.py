#!/usr/bin/env python
"""
Quick Start Script for Truck Booking System
Simple ASCII-only version for Windows compatibility
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """Quick start the truck booking system"""
    print("=" * 50)
    print("TRUCK BOOKING SYSTEM - QUICK START")
    print("=" * 50)
    print()
    
    # Check if we're in the right directory
    if not Path('simple_test.py').exists():
        print("[ERROR] Run this from the AgenticAI-Workflow directory")
        return
    
    print("What would you like to do?")
    print("1. Run Simple Test (Basic workflow demo)")
    print("2. Run Extended Test (NEW! Complete system with billing & docs)")
    print("3. Run Agent Test (Full CrewAI system)")
    print("4. Exit")
    print()
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == '1':
        print("\nRunning Simple Test...")
        print("-" * 30)
        try:
            result = subprocess.run([sys.executable, 'simple_test.py'], 
                                  capture_output=False)
            if result.returncode == 0:
                print("\n[SUCCESS] Test completed!")
            else:
                print("\n[ERROR] Test failed")
        except Exception as e:
            print(f"\n[ERROR] {e}")
    
    elif choice == '2':
        print("\nRunning Extended Test (NEW!)...")
        print("-" * 35)
        print("This shows the complete system with billing & documentation")
        try:
            result = subprocess.run([sys.executable, 'test_extended_simple.py'], 
                                  capture_output=False)
            if result.returncode == 0:
                print("\n[SUCCESS] Extended test completed!")
                print("[INFO] All new features working: Bilty, Documents, Tracking")
            else:
                print("\n[ERROR] Extended test failed")
        except Exception as e:
            print(f"\n[ERROR] {e}")
    
    elif choice == '3':
        print("\nRunning Agent Test...")
        print("-" * 30)
        
        # Check if environment is set up
        if not Path('.env').exists():
            print("[INFO] Setting up environment...")
            if Path('.env.example').exists():
                import shutil
                shutil.copy('.env.example', '.env')
                print("[CREATED] .env file from template")
                print("[IMPORTANT] Edit .env file with your API keys!")
                return
        
        # Try running the CrewAI system
        try:
            agent_path = Path('amanfirstagent/src').absolute()
            env = os.environ.copy()
            env['PYTHONPATH'] = str(agent_path) + os.pathsep + env.get('PYTHONPATH', '')
            
            result = subprocess.run([
                sys.executable, '-m', 'amanfirstagent.main', 'truck_booking'
            ], cwd=agent_path, env=env)
            
            if result.returncode == 0:
                print("\n[SUCCESS] Agent test completed!")
            else:
                print("\n[INFO] Try the simple test first (option 1)")
        except Exception as e:
            print(f"\n[ERROR] {e}")
            print("[TIP] Try option 1 for basic test")
    
    elif choice == '4':
        print("Goodbye!")
    
    else:
        print("[ERROR] Invalid choice")

if __name__ == "__main__":
    main()