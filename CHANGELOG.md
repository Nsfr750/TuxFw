# Changelog

All notable changes to this project will be documented in this file.

## [0.0.1] - 2025-10-28

### Added
- Initial project setup and structure
- Basic firewall management interface with PySide6
- Support for English and Italian languages
- Basic rule management (add, edit, delete, import/export)
- Log viewer with search and filtering capabilities
- Dark theme support for the UI with Wand integration
- Log export functionality (TXT, CSV, JSON)
- Error handling and logging system
- QR code generation for rule sharing
- Mock firewall for development and testing

### Changed
- Improved UI/UX with better organization and feedback
- Enhanced tabbed interface with consistent theming
- Optimized file handling and error reporting
- Updated dependencies to use Wand for image processing
- Improved cross-platform compatibility

### Fixed
- Fixed UI initialization issues
- Resolved QR code generation with dark theme support
- Addressed various UI layout and styling issues
- Fixed logger parameter passing in ViewLogsWindow
- Resolved indentation and syntax issues in view_logs.py
- Fixed exception handling in file loading operations
### Removed
- Unused imports and redundant code
- Deprecated functions and variables