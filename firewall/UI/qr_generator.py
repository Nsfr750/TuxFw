"""
Pure Python QR code generator using Qt for rendering
"""
from typing import List
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter, QColor, QPixmap

def generate_qr_code_data(text: str, version: int = 1) -> List[List[bool]]:
    """
    Generate QR code matrix as a 2D list of booleans (True = black, False = white)
    This is a simplified implementation that creates a basic QR code pattern
    """
    # Calculate size based on version (simplified)
    size = 41 + (version - 1) * 4
    qr = [[False] * size for _ in range(size)]
    
    # Add position markers (squares in corners)
    for i in range(7):
        for j in range(7):
            # Top-left
            qr[i][j] = (i == 0 or i == 6 or j == 0 or j == 6 or 
                        (2 <= i <= 4 and 2 <= j <= 4))
            # Top-right
            if i < 7 and (size - 1 - j) >= size - 7:
                qr[i][-j-1] = qr[i][j]
            # Bottom-left
            if (size - 1 - i) >= size - 7 and j < 7:
                qr[-i-1][j] = qr[i][j]
    
    # Add timing patterns
    for i in range(8, size-8):
        if 0 <= i < size:
            qr[6][i] = i % 2 == 0
            qr[i][6] = i % 2 == 0
    
    # Add dark module
    if 4 * version + 9 < size and 8 < size:
        qr[4 * version + 9][8] = True
    
    # Add some sample data (in a real implementation, this would be the actual encoded data)
    for i in range(4, size-4):
        for j in range(4, size-4):
            if (i + j) % 3 == 0:
                qr[i][j] = not qr[i][j]
    
    return qr

def qr_to_qimage(qr_data: List[List[bool]], scale: int = 10, border: int = 4) -> QImage:
    """
    Convert QR code matrix to QImage
    """
    if not qr_data or not qr_data[0]:
        raise ValueError("Invalid QR code data")
        
    size = len(qr_data)
    width = (size + 2 * border) * scale
    height = (size + 2 * border) * scale
    
    # Create image with dark background
    image = QImage(width, height, QImage.Format_RGB32)
    if image.isNull():
        raise RuntimeError("Failed to create QImage")
    
    # Fill with dark background
    image.fill(QColor(0x2D, 0x2D, 0x2D))
    
    # Set up painter
    painter = QPainter()
    if not painter.begin(image):
        raise RuntimeError("Failed to initialize QPainter")
    
    try:
        # Draw white modules
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0xFF, 0xFF, 0xFF))  # White
        
        for y in range(size):
            for x in range(size):
                if qr_data[y][x]:
                    painter.drawRect(
                        (x + border) * scale,
                        (y + border) * scale,
                        scale, scale
                    )
    finally:
        painter.end()
    
    return image