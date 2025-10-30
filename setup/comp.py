#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Firewall Application Compilation Script
Builds the firewall application using PyInstaller for distribution
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
import argparse
from importlib import metadata as importlib_metadata

class AppCompiler:
    """Handle application compilation with PyInstaller"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.script_dir = self.project_root / "firewall/script"
        self.lang_dir = self.project_root / "firewall/lang"
        self.config_dir = self.project_root / "firewall/config"
        self.ui_dir = self.project_root / "firewall/UI"
        self.assets_dir = self.project_root / "firewall/assets"
        self.dist_dir = self.project_root / "dist"
        self.build_dir = self.project_root / "build"

        # Application details
        self.app_name = "TuxFw"
        self.main_script = "main.py"
        self.version_file = self.assets_dir / "version_info.txt"
        self.icon_file = "icon.ico"
        self.logo_file = "logo.png"
        
        # Ensure version file exists
        if not self.version_file.exists():
            version_info = """
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(0, 0, 1, 0),
    prodvers=(0, 0, 1, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          '040904B0',
          [StringStruct('CompanyName', 'Tuxxle'),
          StringStruct('FileDescription', 'TuxFw - Firewall Manager'),
          StringStruct('FileVersion', '0.1.0'),
          StringStruct('InternalName', 'TuxFw'),
          StringStruct('LegalCopyright', '© 2025 Nsfr750. All rights reserved.'),
          StringStruct('OriginalFilename', 'TuxFw.exe'),
          StringStruct('ProductName', 'TuxFw'),
          StringStruct('ProductVersion', '0.1.0')])
      ]
    ),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)"""
            with open(self.version_file, 'w', encoding='utf-8') as f:
                f.write(version_info.strip())

        # Ensure directories exist
        self.dist_dir.mkdir(exist_ok=True)
        self.build_dir.mkdir(exist_ok=True)

    def check_dependencies(self):
        """Check if required dependencies are installed"""
        required_packages = [
            'PyInstaller',
            'PySide6',
            'wand',
            'qrcode',
            'pip-nftables'
        ]

        # Map distribution names to potential importable modules
        import_candidates_map = {
            'PyInstaller': ['PyInstaller'],
            'PySide6': ['PySide6'],
            'wand': ['wand'],
            'qrcode': ['qrcode'],
            'pip-nftables': ['pip_nftables', 'nftables'],
        }

        missing_packages = []

        for package in required_packages:
            present = False
            # First, try to detect by distribution name
            try:
                _ = importlib_metadata.version(package)
                present = True
            except Exception:
                present = False

            # If not found by distribution, try import candidates
            if not present:
                candidates = import_candidates_map.get(
                    package, [package.replace('-', '_').split('[')[0]]
                )
                for mod in candidates:
                    try:
                        __import__(mod)
                        present = True
                        break
                    except ImportError:
                        continue

            if present:
                print(f"✅ {package}")
            else:
                missing_packages.append(package)
                print(f"❌ {package} - MISSING")

        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("Install with: pip install -r requirements.txt")
            return False

        print("\n✅ All dependencies are installed!")
        return True

    def clean_build(self):
        """Clean previous build files"""
        print("🧹 Cleaning previous builds...")

        dirs_to_clean = [
            self.dist_dir,
            self.build_dir,
            self.project_root / "dist",
            self.project_root / "build"
        ]

        for dir_path in dirs_to_clean:
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"  Removed: {dir_path}")

        # Clean .spec files
        for spec_file in self.project_root.glob("*.spec"):
            spec_file.unlink()
            print(f"  Removed: {spec_file}")

        print("✅ Clean completed!")

    def get_pyinstaller_args(self, build_type="onefile", console=False, debug=False):
        """Get PyInstaller arguments based on build type"""

        # Base arguments
        args = [
            '--name', self.app_name,
            '--version-file', str(self.version_file),
            '--distpath', str(self.dist_dir),
            '--workpath', str(self.build_dir),
            '--clean'
        ]

        # Icon (if exists)
        icon_path = self.assets_dir / self.icon_file if not self.icon_file.startswith('assets/') else self.project_root / self.icon_file
        if icon_path.exists():
            args.extend(['--icon', str(icon_path)])

        # Build type
        if build_type == "onefile":
            args.append('--onefile')
        elif build_type == "onedir":
            args.append('--onedir')

        # Console vs windowed
        if not console:
            args.append('--noconsole')

        # Debug mode
        if debug:
            args.append('--debug')

        # Additional options
        # Conditionally include data directories if they exist to prevent build failures
        data_pairs = []
        if self.config_dir.exists():
            data_pairs += ['--add-data', f'{self.config_dir};firewall/config']
        else:
            print(f"ℹ️  Skipping missing data dir: {self.config_dir}")
        if self.lang_dir.exists():
            data_pairs += ['--add-data', f'{self.lang_dir};firewall/lang']
        else:
            print(f"ℹ️  Skipping missing data dir: {self.lang_dir}")
        if self.assets_dir.exists():
            data_pairs += ['--add-data', f'{self.assets_dir};firewall/assets']
        else:
            print(f"ℹ️  Skipping missing data dir: {self.assets_dir}")

        args.extend(data_pairs + [
            '--hidden-import', 'PySide6.QtCore',
            '--hidden-import', 'PySide6.QtWidgets',
            '--hidden-import', 'PySide6.QtGui',
            '--hidden-import', 'wand',
            '--hidden-import', 'qrcode',
            '--hidden-import', 'psutil',
            '--hidden-import', 'pyrewall',
            '--hidden-import', 'pip_nftables',
            # Ensure Requests has a character detection backend available in the EXE
            '--hidden-import', 'charset_normalizer',
            '--hidden-import', 'chardet',
            # Collect package data/resources to be safe
            '--collect-all', 'charset_normalizer',
            '--collect-all', 'chardet',
        ])

        # Main script
        args.append(str(self.script_dir / self.main_script))

        return args

    def build_onefile(self, console=False, debug=False):
        """Build single executable file"""
        print(f"🔨 Building onefile executable (console={console}, debug={debug})...")

        # Remove stale spec to avoid reusing old datas configuration
        spec_file = self.project_root / f"{self.app_name}.spec"
        if spec_file.exists():
            try:
                spec_file.unlink()
            except Exception:
                pass

        args = self.get_pyinstaller_args("onefile", console, debug)

        try:
            result = subprocess.run([sys.executable, '-m', 'PyInstaller'] + args,
                                  cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Onefile build completed successfully!")

                # Show output file
                exe_path = self.dist_dir / f"{self.app_name}.exe"
                if exe_path.exists():
                    size = exe_path.stat().st_size / (1024 * 1024)  # MB
                    print(f"📦 Output: {exe_path} ({size:.1f} MB)")

                return True
            else:
                print("❌ Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except Exception as e:
            print(f"❌ Build error: {e}")
            return False

    def build_onedir(self, console=False, debug=False):
        """Build directory with all files"""
        print(f"🔨 Building onedir package (console={console}, debug={debug})...")

        # Remove stale spec to avoid reusing old datas configuration
        spec_file = self.project_root / f"{self.app_name}.spec"
        if spec_file.exists():
            try:
                spec_file.unlink()
            except Exception:
                pass

        args = self.get_pyinstaller_args("onedir", console, debug)

        try:
            result = subprocess.run([sys.executable, '-m', 'PyInstaller'] + args,
                                  cwd=self.project_root, capture_output=True, text=True)

            if result.returncode == 0:
                print("✅ Onedir build completed successfully!")

                # Show output directory
                dist_path = self.dist_dir / self.app_name
                if dist_path.exists():
                    total_size = sum(f.stat().st_size for f in dist_path.rglob('*') if f.is_file())
                    size_mb = total_size / (1024 * 1024)
                    print(f"📁 Output: {dist_path} ({size_mb:.1f} MB)")

                return True
            else:
                print("❌ Build failed!")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                return False

        except Exception as e:
            print(f"❌ Build error: {e}")
            return False

    def create_installer(self):
        """Create Windows installer (placeholder for future implementation)"""
        print("📦 Creating installer...")
        print("ℹ️  Installer creation not implemented yet")
        print("   For now, use the executable from dist/ directory")

    def run_tests(self):
        """Run application tests before building"""
        print("🧪 Running tests...")

        try:
            # Import and run basic tests
            test_result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'],
                                       cwd=self.project_root, capture_output=True, text=True)

            if test_result.returncode == 0:
                print("✅ Tests passed!")
                return True
            else:
                print("❌ Tests failed!")
                print("STDOUT:", test_result.stdout)
                print("STDERR:", test_result.stderr)
                return False

        except FileNotFoundError:
            print("ℹ️  pytest not found, skipping tests")
            return True
        except Exception as e:
            print(f"❌ Test error: {e}")
            return False

    def create_build_info(self):
        """Create build information file"""
        build_info = {
            'app_name': self.app_name,
            'version': '0.1.0',
            'build_time': str(__import__('datetime').datetime.now()),
            'python_version': sys.version,
            'platform': sys.platform,
            'dependencies': [
                'PySide6',
                'wand',
                'qrcode',
                'python-iptables'
            ]
        }

        info_file = self.dist_dir / 'build_info.json'
        import json
        with open(info_file, 'w') as f:
            json.dump(build_info, f, indent=2)

        print(f"📝 Build info saved: {info_file}")


def main():
    """Main compilation function"""
    parser = argparse.ArgumentParser(description='Compile Firewall Application')
    parser.add_argument('--type', choices=['onefile', 'onedir', 'installer'],
                       default='onefile', help='Build type')
    parser.add_argument('--console', action='store_true',
                       help='Show console window (debug mode)')
    parser.add_argument('--debug', action='store_true',
                       help='Build in debug mode')
    parser.add_argument('--clean', action='store_true',
                       help='Clean previous builds')
    parser.add_argument('--no-test', action='store_true',
                       help='Skip tests before building')

    args = parser.parse_args()

    compiler = AppCompiler()

    print("🚀 Firewall Application Compiler")
    print("=" * 40)

    # Check dependencies
    if not compiler.check_dependencies():
        print("❌ Missing dependencies. Please install requirements first.")
        return 1

    # Clean if requested
    if args.clean:
        compiler.clean_build()

    # Run tests (unless disabled)
    if not args.no_test:
        if not compiler.run_tests():
            print("❌ Tests failed. Build cancelled.")
            return 1

    # Build application
    success = False
    if args.type == "onefile":
        success = compiler.build_onefile(console=args.console, debug=args.debug)
    elif args.type == "onedir":
        success = compiler.build_onedir(console=args.console, debug=args.debug)
    elif args.type == "installer":
        success = compiler.build_onefile(console=args.console, debug=args.debug)
        if success:
            compiler.create_installer()

    # Create build info
    if success:
        compiler.create_build_info()

        print("\n🎉 Build completed successfully!")
        print(f"📦 Check the {compiler.dist_dir} directory for output files")

        # Show summary
        if (compiler.dist_dir / f"{compiler.app_name}.exe").exists():
            exe_size = (compiler.dist_dir / f"{compiler.app_name}.exe").stat().st_size
            print(f"📊 Executable size: {exe_size / (1024*1024):.1f} MB")

        return 0
    else:
        print("\n❌ Build failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
