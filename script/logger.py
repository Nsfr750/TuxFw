#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path


class FirewallLogger:
    """Advanced logger with daily rotation for the firewall application"""

    def __init__(self, name="firewall", log_level=logging.INFO, max_bytes=10*1024*1024, backup_count=30):
        """
        Initialize the logger

        Args:
            name (str): Logger name
            log_level: Logging level (default: INFO)
            max_bytes (int): Maximum size of each log file before rotation (default: 10MB)
            backup_count (int): Number of backup files to keep (default: 30)
        """
        self.name = name
        self.log_level = log_level
        self.max_bytes = max_bytes
        self.backup_count = backup_count

        # Create logs directory if it doesn't exist
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level)

        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()

        # Create formatters
        self.file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        self.console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )

        # Setup file handler with daily rotation
        self._setup_file_handler()

        # Setup console handler
        self._setup_console_handler()

    def _get_current_log_filename(self):
        """Get the current log filename based on date"""
        today = datetime.now().strftime('%Y-%m-%d')
        return f"{self.name}_{today}.log"

    def _setup_file_handler(self):
        """Setup file handler with rotation"""
        log_file = self.log_dir / self._get_current_log_filename()

        # Create a rotating file handler that rotates daily
        # The maxBytes and backupCount are for the RotatingFileHandler
        # but we'll also implement daily rotation logic
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.max_bytes,
            backupCount=self.backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(self.log_level)
        file_handler.setFormatter(self.file_formatter)

        # Custom filter to handle daily rotation
        file_handler.addFilter(self._DailyRotationFilter())

        self.logger.addHandler(file_handler)

    def _setup_console_handler(self):
        """Setup console handler for real-time monitoring"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(self.console_formatter)
        self.logger.addHandler(console_handler)

    def _DailyRotationFilter(self):
        """Custom filter to handle daily rotation"""
        class DailyRotationFilter(logging.Filter):
            def __init__(self, logger_instance):
                super().__init__()
                self.logger_instance = logger_instance
                self.current_date = datetime.now().strftime('%Y-%m-%d')

            def filter(self, record):
                # Check if date has changed
                new_date = datetime.now().strftime('%Y-%m-%d')
                if new_date != self.current_date:
                    # Date changed, need to rotate
                    self.current_date = new_date
                    self.logger_instance._rotate_log_file()
                return True

        return DailyRotationFilter(self)

    def _rotate_log_file(self):
        """Rotate log file when date changes"""
        # Remove old file handlers
        for handler in self.logger.handlers[:]:
            if isinstance(handler, logging.handlers.RotatingFileHandler):
                handler.close()
                self.logger.removeHandler(handler)

        # Setup new file handler with new date
        self._setup_file_handler()

    def log_firewall_event(self, event_type, message, **kwargs):
        """
        Log a firewall-specific event

        Args:
            event_type (str): Type of event (rule_added, rule_deleted, firewall_enabled, etc.)
            message (str): Event message
            **kwargs: Additional context data
        """
        context = f"[{event_type}]" + (f" {kwargs}" if kwargs else "")
        self.logger.info(f"{context} {message}")

    def log_error(self, error, context=""):
        """
        Log an error with context

        Args:
            error (Exception or str): Error to log
            context (str): Additional context about where the error occurred
        """
        if isinstance(error, Exception):
            error_msg = f"{type(error).__name__}: {str(error)}"
        else:
            error_msg = str(error)

        if context:
            self.logger.error(f"[{context}] {error_msg}")
        else:
            self.logger.error(error_msg)

    def log_security_event(self, event_type, source_ip=None, destination_ip=None, port=None, action="BLOCKED", **kwargs):
        """
        Log a security-related event

        Args:
            event_type (str): Type of security event (connection_attempt, rule_triggered, etc.)
            source_ip (str): Source IP address
            destination_ip (str): Destination IP address
            port (int): Port number
            action (str): Action taken (ALLOWED, BLOCKED, etc.)
            **kwargs: Additional security context
        """
        security_info = []
        if source_ip:
            security_info.append(f"src={source_ip}")
        if destination_ip:
            security_info.append(f"dst={destination_ip}")
        if port:
            security_info.append(f"port={port}")

        security_context = f"[{event_type}] {action} {' '.join(security_info)}"
        if kwargs:
            security_context += f" {kwargs}"

        self.logger.warning(security_context)

    def log_config_change(self, change_type, details=""):
        """
        Log configuration changes

        Args:
            change_type (str): Type of change (settings_updated, rule_added, rule_deleted, etc.)
            details (str): Details about the change
        """
        self.logger.info(f"[CONFIG_CHANGE] {change_type}: {details}")

    def log_performance(self, operation, duration_ms, **kwargs):
        """
        Log performance metrics

        Args:
            operation (str): Operation performed
            duration_ms (float): Duration in milliseconds
            **kwargs: Additional performance context
        """
        context = f"[{operation}] {duration_ms:.2f}ms"
        if kwargs:
            context += f" {kwargs}"

        self.logger.info(context)

    def get_log_files(self):
        """Get list of all log files"""
        return sorted(self.log_dir.glob(f"{self.name}_*.log"))

    def cleanup_old_logs(self, days_to_keep=30):
        """
        Clean up old log files

        Args:
            days_to_keep (int): Number of days of logs to keep
        """
        import time

        cutoff_time = time.time() - (days_to_keep * 24 * 60 * 60)

        for log_file in self.get_log_files():
            if log_file.is_file() and log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    self.logger.info(f"Cleaned up old log file: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to cleanup log file {log_file.name}: {e}")

    def get_logger(self):
        """Get the underlying logger instance"""
        return self.logger

    # Convenience methods for different log levels
    def debug(self, message):
        """Log debug message"""
        self.logger.debug(message)

    def info(self, message):
        """Log info message"""
        self.logger.info(message)

    def warning(self, message):
        """Log warning message"""
        self.logger.warning(message)

    def error(self, message):
        """Log error message"""
        self.logger.error(message)

    def critical(self, message):
        """Log critical message"""
        self.logger.critical(message)


# Global logger instance
_firewall_logger = None


def get_logger(name="firewall", log_level=logging.INFO):
    """
    Get or create a global logger instance

    Args:
        name (str): Logger name
        log_level: Logging level

    Returns:
        FirewallLogger: Configured logger instance
    """
    global _firewall_logger
    if _firewall_logger is None:
        _firewall_logger = FirewallLogger(name, log_level)
    return _firewall_logger


def log_firewall_event(event_type, message, **kwargs):
    """Convenience function to log firewall events"""
    logger = get_logger()
    logger.log_firewall_event(event_type, message, **kwargs)


def log_error(error, context=""):
    """Convenience function to log errors"""
    logger = get_logger()
    logger.log_error(error, context)


def log_security_event(event_type, source_ip=None, destination_ip=None, port=None, action="BLOCKED", **kwargs):
    """Convenience function to log security events"""
    logger = get_logger()
    logger.log_security_event(event_type, source_ip, destination_ip, port, action, **kwargs)


def log_config_change(change_type, details=""):
    """Convenience function to log configuration changes"""
    logger = get_logger()
    logger.log_config_change(change_type, details)


def log_performance(operation, duration_ms, **kwargs):
    """Convenience function to log performance metrics"""
    logger = get_logger()
    logger.log_performance(operation, duration_ms, **kwargs)


if __name__ == "__main__":
    # Example usage and testing
    logger = get_logger("firewall", logging.DEBUG)

    # Test different log types
    logger.info("Firewall logger initialized")
    logger.log_firewall_event("STARTUP", "Application started successfully")
    logger.log_security_event("CONNECTION_ATTEMPT", source_ip="192.168.1.100", destination_ip="10.0.0.1", port=80, action="ALLOWED")
    logger.log_config_change("RULE_ADDED", "Added rule for port 443")
    logger.log_performance("RULE_PROCESSING", 15.5, rule_count=10)
    logger.warning("High number of blocked connections detected")
    logger.error("Failed to save configuration file", context="ConfigTab.save_config")

    print("Logger test completed. Check logs/ directory for output files.")
