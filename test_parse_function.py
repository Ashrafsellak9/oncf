#!/usr/bin/env python3
"""
Test the parse_wkt_linestring function directly
"""

import sys
import os

# Add the current directory to Python path to import from app.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_parse_function():
    """Test the parse_wkt_linestring function"""
    
    try:
        # Import the function from app.py
        from app import parse_wkt_linestring
        
        print("🔍 Testing parse_wkt_linestring function...")
        print("=" * 50)
        
        # Test cases with real geometry data
        test_cases = [
            "SRID=3857;LINESTRING(-851596.7498882831 3967357.0515490603, -851607.6731740611 3967365.8083651373)",
            "SRID=3857;LINESTRING(-931422.4866921209 3930584.980286067, -931429.4264905186 3930592.180230386)",
            "SRID=3857;LINESTRING(-1029530.063811 3800062.28159, -1029530.8978848121 3800062.833242858)",
            "SRID=3857;LINESTRING(-659278.0092749159 4065090.1958290054, -659277.8015850194 4065082.198525403)",
            "SRID=3857;LINESTRING(-758674.9530974822 4033951.939492329, -758693.5136594393 4033959.3896963424)"
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\nTest {i}:")
            print(f"   Input: {test_case}")
            
            result = parse_wkt_linestring(test_case)
            
            if result:
                print(f"   ✅ Success: {result}")
            else:
                print(f"   ❌ Failed: returned None")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the oncf-ems directory")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    test_parse_function()
