"""
Basic test for Sentinel-AI 2.0 project structure
Tests the project setup without external dependencies
"""

import os
import sys

def test_project_structure():
    """Test that the project structure is correct."""
    print("📁 Testing project structure...")
    
    required_files = [
        "app/__init__.py",
        "app/models/__init__.py",
        "app/models/requests.py",
        "app/models/budget.py",
        "app/models/cache.py",
        "app/models/complexity.py",
        "app/models/providers.py",
        "app/core/__init__.py",
        "app/core/router.py",
        "app/core/complexity.py",
        "app/core/cache.py",
        "app/core/budget.py",
        "app/core/prompt_opt.py",
        "app/core/providers.py",
        "app/main.py",
        "requirements.txt"
    ]
    
    # Check README in parent directory
    if not os.path.exists("../README.md"):
        required_files.append("README.md (missing in parent directory)")
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist")
        return True

def test_file_contents():
    """Test that key files have content."""
    print("\n📄 Testing file contents...")
    
    files_to_check = [
        "app/models/requests.py",
        "app/core/router.py",
        "app/main.py",
        "requirements.txt"
    ]
    
    empty_files = []
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if not content:
                    empty_files.append(file_path)
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}")
            return False
    
    # Check README in parent directory
    try:
        with open("../README.md", 'r') as f:
            content = f.read().strip()
            if not content:
                empty_files.append("README.md (empty)")
    except Exception as e:
        print(f"❌ Error reading README.md: {e}")
        return False
    
    if empty_files:
        print(f"❌ Empty files: {empty_files}")
        return False
    else:
        print("✅ All key files have content")
        return True

def test_python_syntax():
    """Test that Python files have valid syntax."""
    print("\n🐍 Testing Python syntax...")
    
    python_files = [
        "app/models/requests.py",
        "app/models/budget.py",
        "app/models/cache.py",
        "app/models/complexity.py",
        "app/models/providers.py",
        "app/core/router.py",
        "app/core/complexity.py",
        "app/core/cache.py",
        "app/core/budget.py",
        "app/core/prompt_opt.py",
        "app/core/providers.py",
        "app/main.py"
    ]
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                compile(content, file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            print(f"❌ Error checking {file_path}: {e}")
            return False
    
    if syntax_errors:
        print(f"❌ Syntax errors: {syntax_errors}")
        return False
    else:
        print("✅ All Python files have valid syntax")
        return True

def test_import_structure():
    """Test that the import structure is correct."""
    print("\n📦 Testing import structure...")
    
    # Check that __init__.py files exist
    init_files = [
        "app/__init__.py",
        "app/models/__init__.py",
        "app/core/__init__.py"
    ]
    
    missing_inits = []
    for init_file in init_files:
        if not os.path.exists(init_file):
            missing_inits.append(init_file)
    
    if missing_inits:
        print(f"❌ Missing __init__.py files: {missing_inits}")
        return False
    else:
        print("✅ All __init__.py files exist")
        return True

def test_requirements():
    """Test that requirements.txt has necessary packages."""
    print("\n📦 Testing requirements.txt...")
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read()
            
        required_packages = [
            "fastapi",
            "uvicorn",
            "pydantic"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in content:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages in requirements.txt: {missing_packages}")
            return False
        else:
            print("✅ All required packages listed in requirements.txt")
            return True
            
    except Exception as e:
        print(f"❌ Error reading requirements.txt: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Sentinel-AI 2.0 Project Tests")
    print("=" * 50)
    
    tests = [
        test_project_structure,
        test_file_contents,
        test_python_syntax,
        test_import_structure,
        test_requirements
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All project tests passed!")
        print("\n✅ Project structure is correct")
        print("✅ All required files exist")
        print("✅ Python syntax is valid")
        print("✅ Import structure is correct")
        print("✅ Requirements are properly specified")
        
        print("\n🚀 Next steps to run the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: uvicorn app.main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
        print("4. Test the API endpoints using the interactive Swagger UI")
        
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()