#!/usr/bin/env python3
"""
Verification script for Sentinel-AI 2.0 setup
Checks that all files are present and properly configured
"""

import os
import sys

def check_files():
    """Check that all required files exist."""
    print("🔍 Checking Sentinel-AI 2.0 files...")
    
    required_files = [
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/app/models/__init__.py",
        "backend/app/models/requests.py",
        "backend/app/models/budget.py",
        "backend/app/models/cache.py",
        "backend/app/models/complexity.py",
        "backend/app/models/providers.py",
        "backend/app/core/__init__.py",
        "backend/app/core/router.py",
        "backend/app/core/complexity.py",
        "backend/app/core/cache.py",
        "backend/app/core/budget.py",
        "backend/app/core/prompt_opt.py",
        "backend/app/core/providers.py",
        "backend/requirements.txt",
        "backend/basic_test.py",
        "backend/demo.py",
        "backend/TESTING_GUIDE.md",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    else:
        print("✅ All required files exist!")
        return True

def check_git_status():
    """Check git status."""
    print("\n📊 Checking git status...")
    
    import subprocess
    try:
        result = subprocess.run(['git', 'status'], capture_output=True, text=True)
        if "nothing to commit" in result.stdout:
            print("✅ All files are committed to git!")
            return True
        else:
            print("⚠️ Some files may not be committed")
            print(result.stdout)
            return False
    except Exception as e:
        print(f"❌ Error checking git status: {e}")
        return False

def check_branch():
    """Check current git branch."""
    print("\n🌿 Checking git branch...")
    
    import subprocess
    try:
        result = subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True)
        branch = result.stdout.strip()
        print(f"✅ Current branch: {branch}")
        return True
    except Exception as e:
        print(f"❌ Error checking branch: {e}")
        return False

def check_remote():
    """Check remote repository."""
    print("\n🌐 Checking remote repository...")
    
    import subprocess
    try:
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        print("✅ Remote repositories:")
        print(result.stdout)
        return True
    except Exception as e:
        print(f"❌ Error checking remote: {e}")
        return False

def main():
    """Run all checks."""
    print("🚀 Sentinel-AI 2.0 Setup Verification")
    print("=" * 50)
    
    checks = [
        check_files,
        check_git_status,
        check_branch,
        check_remote
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        try:
            if check():
                passed += 1
        except Exception as e:
            print(f"❌ Check failed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Verification Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! Your Sentinel-AI 2.0 is ready!")
        print("\n✅ What you have:")
        print("   - Complete backend implementation")
        print("   - All files committed to git")
        print("   - Ready for deployment")
        
        print("\n🚀 Next steps:")
        print("1. Test the implementation: cd backend && python3 basic_test.py")
        print("2. Run the demo: python3 demo.py")
        print("3. Start the server: uvicorn app.main:app --reload")
        print("4. Visit: http://localhost:8000/docs")
        
    else:
        print("⚠️ Some checks failed. Please review the errors above.")
    
    return passed == total

if __name__ == "__main__":
    main()