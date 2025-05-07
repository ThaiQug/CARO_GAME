import random
from game.player import Player

class RandomAgent(Player):
    """Agent đánh cờ ngẫu nhiên."""
    
    def __init__(self, symbol):
        """Khởi tạo agent ngẫu nhiên.
        
        Args:
            symbol: Ký hiệu của agent ('X' hoặc 'O')
        """
        super().__init__(symbol)
        self.name = f"Random Agent ({symbol})"
    
    def get_move(self, board):
        """Lấy nước đi ngẫu nhiên từ các nước đi hợp lệ.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            tuple: Tọa độ (row, col) của nước đi
        """
        valid_moves = board.get_valid_moves()
        return random.choice(valid_moves)