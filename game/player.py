class Player:
    """Lớp cơ sở cho tất cả người chơi."""
    
    def __init__(self, symbol):
        """Khởi tạo người chơi với ký hiệu cho trước.
        
        Args:
            symbol: Ký hiệu của người chơi ('X' hoặc 'O')
        """
        self.symbol = symbol
        self.name = "Player"
    
    def get_move(self, board):
        """Lấy nước đi tiếp theo.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            tuple: Tọa độ (row, col) của nước đi
        """
        raise NotImplementedError("Phương thức này phải được triển khai ở lớp con")


class HumanPlayer(Player):
    """Người chơi là con người."""
    
    def __init__(self, symbol):
        """Khởi tạo người chơi là con người.
        
        Args:
            symbol: Ký hiệu của người chơi ('X' hoặc 'O')
        """
        super().__init__(symbol)
        self.name = f"Human ({symbol})"
    
    def get_move(self, board):
        """Lấy nước đi tiếp theo từ người chơi.
        
        Args:
            board: Bàn cờ hiện tại
            
        Returns:
            tuple: Tọa độ (row, col) của nước đi
        """
        while True:
            try:
                move = input(f"Người chơi {self.symbol}, nhập nước đi (hàng cột): ")
                row, col = map(int, move.split())
                
                if board.is_valid_move(row, col):
                    return row, col
                else:
                    print("Nước đi không hợp lệ. Vui lòng thử lại.")
            except ValueError:
                print("Định dạng không hợp lệ. Vui lòng nhập hai số nguyên cách nhau bởi khoảng trắng.")


class Game:
    """Quản lý trò chơi cờ Caro."""
    
    def __init__(self, board, player1, player2):
        """Khởi tạo trò chơi với bàn cờ và hai người chơi.
        
        Args:
            board: Bàn cờ
            player1: Người chơi thứ nhất (X)
            player2: Người chơi thứ hai (O)
        """
        self.board = board
        self.players = [player1, player2]
        self.current_player_idx = 0
        
    def play(self, verbose=True):
        """Chạy trò chơi.
        
        Args:
            verbose: Nếu True, in thông tin chi tiết của trò chơi
            
        Returns:
            str hoặc None: Ký hiệu của người thắng hoặc None nếu hòa
        """
        if verbose:
            print("\nTrò chơi Cờ Caro bắt đầu!")
            print(f"{self.players[0].name} vs {self.players[1].name}")
        
        while True:
            # Hiển thị bàn cờ
            if verbose:
                self.board.display()
            
            # Lấy người chơi hiện tại
            current_player = self.players[self.current_player_idx]
            if verbose:
                print(f"\nLượt của {current_player.name}")
            
            # Lấy nước đi
            row, col = current_player.get_move(self.board)
            
            # Thực hiện nước đi
            self.board.make_move(row, col, current_player.symbol)
            if verbose:
                print(f"{current_player.name} đặt quân tại ({row}, {col})")
            
            # Kiểm tra người thắng
            winner = self.board.check_winner()
            if winner:
                if verbose:
                    self.board.display()
                    print(f"\nNgười chơi {winner} thắng!")
                return winner
            
            # Kiểm tra hòa
            if self.board.is_full():
                if verbose:
                    self.board.display()
                    print("\nTrò chơi kết thúc với kết quả hòa!")
                return None
            
            # Chuyển lượt người chơi
            self.current_player_idx = 1 - self.current_player_idx