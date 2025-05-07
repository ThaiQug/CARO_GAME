class Board:
    """Quản lý bàn cờ và luật chơi của cờ Caro."""
    
    def __init__(self, size=15):
        """Khởi tạo bàn cờ với kích thước cho trước.
        
        Args:
            size: Kích thước bàn cờ (size x size)
        """
        self.size = size
        self.board = [[' ' for _ in range(size)] for _ in range(size)]
        self.last_move = None
        self.moves_count = 0
        self.move_history = []  # Lưu lịch sử các nước đi
        self.threat_cache = {}  # Cache để lưu trữ các mối đe dọa
        
    def is_valid_move(self, row, col):
        """Kiểm tra nước đi có hợp lệ không.
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
        
        Returns:
            bool: True nếu nước đi hợp lệ, False nếu không
        """
        # Kiểm tra tọa độ có nằm trong bàn cờ không
        if not (0 <= row < self.size and 0 <= col < self.size):
            return False
        
        # Kiểm tra ô đã có quân cờ chưa
        return self.board[row][col] == ' '
    
    def make_move(self, row, col, player):
        """Thực hiện nước đi trên bàn cờ.
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            bool: True nếu nước đi thành công, False nếu không
        """
        if not self.is_valid_move(row, col):
            return False
        
        self.board[row][col] = player
        self.last_move = (row, col)
        self.moves_count += 1
        self.move_history.append((row, col, player))
        
        # Reset threat cache khi có nước đi mới
        self.threat_cache = {}
        
        return True
    
    def check_winner(self):
        """Kiểm tra xem có người thắng cuộc không.
        
        Returns:
            str: 'X' hoặc 'O' nếu có người thắng, None nếu chưa có người thắng
        """
        if self.last_move is None:
            return None
            
        row, col = self.last_move
        player = self.board[row][col]
        
        # Kiểm tra hàng ngang
        if self._check_line(row, col, 0, 1, player):
            return player
            
        # Kiểm tra hàng dọc
        if self._check_line(row, col, 1, 0, player):
            return player
            
        # Kiểm tra đường chéo chính (từ trên trái xuống dưới phải)
        if self._check_line(row, col, 1, 1, player):
            return player
            
        # Kiểm tra đường chéo phụ (từ trên phải xuống dưới trái)
        if self._check_line(row, col, 1, -1, player):
            return player
            
        return None
    
    def _check_line(self, row, col, row_dir, col_dir, player):
        """Kiểm tra 5 quân cờ liên tiếp theo một hướng.
        
        Args:
            row: Hàng bắt đầu
            col: Cột bắt đầu
            row_dir: Hướng dịch chuyển hàng (0, 1, hoặc -1)
            col_dir: Hướng dịch chuyển cột (0, 1, hoặc -1)
            player: Người chơi ('X' hoặc 'O')
        
        Returns:
            bool: True nếu có 5 quân cờ liên tiếp, False nếu không
        """
        # Đếm số quân cờ liên tiếp về trước
        count_backward = 0
        r, c = row, col
        
        while (0 <= r < self.size and 0 <= c < self.size and 
               self.board[r][c] == player):
            count_backward += 1
            r -= row_dir
            c -= col_dir
            
        # Đếm số quân cờ liên tiếp về sau
        count_forward = 0
        r, c = row + row_dir, col + col_dir
        
        while (0 <= r < self.size and 0 <= c < self.size and 
               self.board[r][c] == player):
            count_forward += 1
            r += row_dir
            c += col_dir
            
        # Có thắng không (5 quân cờ liên tiếp)
        return count_backward + count_forward >= 5  # Do đã đếm quân cờ hiện tại 2 lần
    
    def is_full(self):
        """Kiểm tra xem bàn cờ đã đầy chưa.
        
        Returns:
            bool: True nếu bàn cờ đầy, False nếu không
        """
        return self.moves_count == self.size * self.size
    
    def get_valid_moves(self):
        """Lấy danh sách các nước đi hợp lệ.
        
        Returns:
            list: Danh sách các tọa độ (row, col) hợp lệ
        """
        valid_moves = []
        
        # Chỉ xem xét các ô nằm gần các quân cờ đã đặt
        if self.moves_count == 0:
            # Nước đi đầu tiên ở giữa bàn cờ
            mid = self.size // 2
            return [(mid, mid)]
        
        # Kiểm tra các ô trống trong phạm vi 3 ô từ quân cờ đã đặt
        checked_cells = set()
        
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] != ' ':
                    # Kiểm tra các ô xung quanh
                    for dr in range(-3, 4):
                        for dc in range(-3, 4):
                            r, c = row + dr, col + dc
                            
                            if (0 <= r < self.size and 0 <= c < self.size and 
                                self.board[r][c] == ' ' and (r, c) not in checked_cells):
                                valid_moves.append((r, c))
                                checked_cells.add((r, c))
        
        # Nếu không có ô nào thỏa mãn, xem xét tất cả các ô trống
        if not valid_moves:
            for row in range(self.size):
                for col in range(self.size):
                    if self.board[row][col] == ' ':
                        valid_moves.append((row, col))
        
        return valid_moves
    
    def get_smart_moves(self, max_moves=None):
        """Lấy danh sách các nước đi hợp lệ được sắp xếp theo mức độ quan trọng.
        
        Args:
            max_moves: Số nước đi tối đa trả về, nếu None sẽ trả về tất cả
            
        Returns:
            list: Danh sách các tọa độ (row, col) hợp lệ đã sắp xếp
        """
        # Nếu là nước đi đầu tiên, đi giữa bàn cờ
        if self.moves_count == 0:
            mid = self.size // 2
            return [(mid, mid)]
        
        valid_moves = self.get_valid_moves()
        move_scores = []
        
        for row, col in valid_moves:
            # Đánh giá mức độ quan trọng của nước đi
            importance = self._evaluate_move_importance(row, col)
            move_scores.append(((row, col), importance))
        
        # Sắp xếp theo mức độ quan trọng giảm dần
        move_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Trả về tất cả hoặc giới hạn số nước đi
        if max_moves is None:
            return [move for move, _ in move_scores]
        else:
            return [move for move, _ in move_scores[:max_moves]]
    
    def _evaluate_move_importance(self, row, col):
        """Đánh giá mức độ quan trọng của một nước đi.
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            
        Returns:
            int: Điểm quan trọng của nước đi
        """
        importance = 0
        
        # Xem xét tất cả các ô xung quanh trong phạm vi 2 ô
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = row + dr, col + dc
                if 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] != ' ':
                    # Ô càng gần càng quan trọng
                    distance = abs(dr) + abs(dc)
                    if distance == 1:
                        importance += 5  # Ô liền kề
                    elif distance == 2:
                        importance += 2  # Ô cách 2
                    elif distance == 3:
                        importance += 1  # Ô cách 3
                    elif distance == 4:
                        importance += 0.5  # Ô cách 4
        
        # Ưu tiên các ô ở trung tâm bàn cờ
        center = self.size // 2
        distance_to_center = abs(row - center) + abs(col - center)
        center_importance = max(0, self.size // 2 - distance_to_center)
        importance += center_importance
        
        # Kiểm tra các mẫu đe dọa
        for player in ['X', 'O']:
            # Kiểm tra nếu nước đi này tạo thành 5 liên tiếp
            self.board[row][col] = player
            if self._check_win_at(row, col, player):
                importance += 1000  # Nước đi chiến thắng hoặc chặn chiến thắng
            
            # Kiểm tra các mẫu đe dọa
            threat_level = self._check_threat_patterns(row, col, player)
            importance += threat_level * 20
            
            # Hoàn trả lại bàn cờ
            self.board[row][col] = ' '
        
        return importance
    
    def _check_win_at(self, row, col, player):
        """Kiểm tra nếu đặt quân tại vị trí này sẽ tạo thành 5 liên tiếp.
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            bool: True nếu sẽ thắng, False nếu không
        """
        # Kiểm tra 4 hướng
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row_dir, col_dir in directions:
            consecutive = 1  # Quân hiện tại
            
            # Kiểm tra về trước
            r, c = row - row_dir, col - col_dir
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                consecutive += 1
                r -= row_dir
                c -= col_dir
            
            # Kiểm tra về sau
            r, c = row + row_dir, col + col_dir
            while 0 <= r < self.size and 0 <= c < self.size and self.board[r][c] == player:
                consecutive += 1
                r += row_dir
                c += col_dir
            
            if consecutive >= 5:
                return True
        
        return False
    
    def _check_threat_patterns(self, row, col, player):
        """Kiểm tra các mẫu đe dọa khi đặt quân tại vị trí này.
        
        Args:
            row: Chỉ số hàng
            col: Chỉ số cột
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            int: Mức độ đe dọa
        """
        # Dùng cache nếu đã tính toán trước đó
        cache_key = (row, col, player)
        if cache_key in self.threat_cache:
            return self.threat_cache[cache_key]
        
        threat_level = 0
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row_dir, col_dir in directions:
            # Kiểm tra mẫu "bốn mở" (4 quân liên tiếp với 2 đầu mở)
            open_four = self._check_open_four(row, col, row_dir, col_dir, player)
            if open_four:
                threat_level += 100
            
            # Kiểm tra mẫu "bốn nửa mở" (4 quân liên tiếp với 1 đầu mở)
            half_open_four = self._check_half_open_four(row, col, row_dir, col_dir, player)
            if half_open_four:
                threat_level += 50
            
            # Kiểm tra mẫu "ba mở" (3 quân liên tiếp với 2 đầu mở)
            open_three = self._check_open_three(row, col, row_dir, col_dir, player)
            if open_three:
                threat_level += 20
        
        # Lưu vào cache
        self.threat_cache[cache_key] = threat_level
        return threat_level
    
    def _check_open_four(self, row, col, row_dir, col_dir, player):
        """Kiểm tra mẫu "bốn mở" (4 quân liên tiếp với 2 đầu mở).
        
        Args:
            row, col: Vị trí đặt quân
            row_dir, col_dir: Hướng kiểm tra
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            bool: True nếu tạo thành mẫu bốn mở, False nếu không
        """
        # 4 quân liên tiếp với 2 đầu mở: _XXXX_
        consecutive = 1  # Quân hiện tại
        open_ends = 0
        
        # Kiểm tra về trước
        r, c = row - row_dir, col - col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r -= row_dir
                c -= col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        # Kiểm tra về sau
        r, c = row + row_dir, col + col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r += row_dir
                c += col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        return consecutive == 4 and open_ends == 2
    
    def _check_half_open_four(self, row, col, row_dir, col_dir, player):
        """Kiểm tra mẫu "bốn nửa mở" (4 quân liên tiếp với 1 đầu mở).
        
        Args:
            row, col: Vị trí đặt quân
            row_dir, col_dir: Hướng kiểm tra
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            bool: True nếu tạo thành mẫu bốn nửa mở, False nếu không
        """
        # 4 quân liên tiếp với 1 đầu mở: _XXXX hoặc XXXX_
        consecutive = 1  # Quân hiện tại
        open_ends = 0
        
        # Kiểm tra về trước
        r, c = row - row_dir, col - col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r -= row_dir
                c -= col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        # Kiểm tra về sau
        r, c = row + row_dir, col + col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r += row_dir
                c += col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        return consecutive == 4 and open_ends == 1
    
    def _check_open_three(self, row, col, row_dir, col_dir, player):
        """Kiểm tra mẫu "ba mở" (3 quân liên tiếp với 2 đầu mở).
        
        Args:
            row, col: Vị trí đặt quân
            row_dir, col_dir: Hướng kiểm tra
            player: Người chơi ('X' hoặc 'O')
            
        Returns:
            bool: True nếu tạo thành mẫu ba mở, False nếu không
        """
        # 3 quân liên tiếp với 2 đầu mở: _XXX_
        consecutive = 1  # Quân hiện tại
        open_ends = 0
        
        # Kiểm tra về trước
        r, c = row - row_dir, col - col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r -= row_dir
                c -= col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        # Kiểm tra về sau
        r, c = row + row_dir, col + col_dir
        while 0 <= r < self.size and 0 <= c < self.size:
            if self.board[r][c] == player:
                consecutive += 1
                r += row_dir
                c += col_dir
            elif self.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
        
        return consecutive == 3 and open_ends == 2
    
    def evaluate(self, player):
        """Đánh giá trạng thái bàn cờ đối với người chơi.
        
        Args:
            player: Người chơi đang đánh giá ('X' hoặc 'O')
            
        Returns:
            int: Điểm đánh giá
        """
        opponent = 'O' if player == 'X' else 'X'
        
        # Nếu người chơi thắng
        if self.check_winner() == player:
            return 10000
        
        # Nếu đối thủ thắng
        if self.check_winner() == opponent:
            return -10000
            
        # Đánh giá các dãy quân cờ
        score = 0
        
        # Đánh giá hàng ngang
        for row in range(self.size):
            score += self._evaluate_line_improved(self.board[row], player)
        
        # Đánh giá hàng dọc
        for col in range(self.size):
            column = [self.board[row][col] for row in range(self.size)]
            score += self._evaluate_line_improved(column, player)
        
        # Đánh giá đường chéo chính
        for offset in range(-self.size + 5, self.size - 4):
            diagonal = []
            for i in range(max(0, offset), min(self.size, self.size + offset)):
                diagonal.append(self.board[i][i - offset])
            if len(diagonal) >= 5:
                score += self._evaluate_line_improved(diagonal, player)
        
        # Đánh giá đường chéo phụ
        for offset in range(4, 2 * self.size - 5):
            diagonal = []
            for i in range(max(0, offset - self.size + 1), min(self.size, offset + 1)):
                diagonal.append(self.board[i][offset - i])
            if len(diagonal) >= 5:
                score += self._evaluate_line_improved(diagonal, player)
        
        # Đánh giá kiểm soát trung tâm
        center_score = self._evaluate_center_control(player)
        score += center_score
        
        return score
    
    def _evaluate_line_improved(self, line, player):
        """Đánh giá một dòng (hàng, cột, đường chéo) với hàm đánh giá cải tiến.
        
        Args:
            line: Danh sách các ô trong dòng
            player: Người chơi đang đánh giá ('X' hoặc 'O')
            
        Returns:
            int: Điểm đánh giá cho dòng
        """
        score = 0
        opponent = 'O' if player == 'X' else 'X'
        
        # Tìm các mẫu cửa sổ kích thước 6 để xem xét các trường hợp đặc biệt
        for i in range(len(line) - 5):
            window = line[i:i+6]
            
            # Đếm số quân của mỗi người chơi trong cửa sổ
            player_count = window.count(player)
            opponent_count = window.count(opponent)
            empty_count = window.count(' ')
            
            # Đánh giá cửa sổ dựa trên các mẫu
            
            # Mẫu "năm liên tiếp" (chiến thắng)
            if player_count == 5 and empty_count == 1:
                score += 10000
            
            # Mẫu "bốn mở" (4 quân liên tiếp với 2 đầu mở)
            # _XXXX_
            if player_count == 4 and empty_count == 2:
                if window[0] == ' ' and window[5] == ' ':
                    score += 5000
                else:
                    score += 500
            
            # Mẫu "bốn nửa mở" (4 quân liên tiếp với 1 đầu mở)
            # XXXX_ hoặc _XXXX
            if player_count == 4 and empty_count == 1:
                score += 100
            
            # Mẫu "ba mở" (3 quân liên tiếp với 2 đầu mở)
            # _XXX__
            if player_count == 3 and empty_count == 3:
                if window[0] == ' ' and window[4] == ' ':
                    score += 50
                else:
                    score += 10
            
            # Mẫu "ba nửa mở" (3 quân liên tiếp với 1 đầu mở)
            if player_count == 3 and empty_count == 2 and opponent_count == 1:
                score += 5
            
            # Mẫu "hai mở" (2 quân liên tiếp với 2 đầu mở)
            if player_count == 2 and empty_count == 4:
                score += 2
            
            # Đánh giá phòng thủ
            
            # Mẫu đối thủ "bốn mở"
            if opponent_count == 4 and empty_count == 2:
                if window[0] == ' ' and window[5] == ' ':
                    score -= 4500
                else:
                    score -= 400
            
            # Mẫu đối thủ "bốn nửa mở"
            if opponent_count == 4 and empty_count == 1:
                score -= 90
            
            # Mẫu đối thủ "ba mở"
            if opponent_count == 3 and empty_count == 3:
                if window[0] == ' ' and window[4] == ' ':
                    score -= 40
                else:
                    score -= 8
            
            # Mẫu đối thủ "ba nửa mở"
            if opponent_count == 3 and empty_count == 2 and player_count == 1:
                score -= 4
        
        return score
    
    def _evaluate_center_control(self, player):
        """Đánh giá mức độ kiểm soát trung tâm bàn cờ.
        
        Args:
            player: Người chơi đang đánh giá ('X' hoặc 'O')
            
        Returns:
            int: Điểm kiểm soát trung tâm
        """
        score = 0
        opponent = 'O' if player == 'X' else 'X'
        center = self.size // 2
        
        # Chia bàn cờ thành các vùng
        regions = [
            (0, center // 2),    # Vùng góc
            (center // 2, center * 3 // 4),  # Vùng biên
            (center * 3 // 4, center * 5 // 4),  # Vùng gần trung tâm
            (center * 5 // 4, center * 3 // 2),  # Vùng biên
            (center * 3 // 2, self.size)  # Vùng góc
        ]
        
        # Trọng số cho các vùng
        weights = [1, 2, 3, 2, 1]
        
        # Đánh giá kiểm soát mỗi vùng
        for region_idx, (start, end) in enumerate(regions):
            weight = weights[region_idx]
            
            for row in range(start, end):
                for col in range(start, end):
                    if row < self.size and col < self.size:
                        if self.board[row][col] == player:
                            score += weight
                        elif self.board[row][col] == opponent:
                            score -= weight
        
        return score
    
    def display(self):
        """Hiển thị bàn cờ."""
        print("   " + " ".join(f"{i:2d}" for i in range(self.size)))
        print("  +" + "-" * (self.size * 3) + "+")
        
        for i in range(self.size):
            print(f"{i:2d}|", end=" ")
            for j in range(self.size):
                print(f"{self.board[i][j]} ", end=" ")
            print("|")
            
        print("  +" + "-" * (self.size * 3) + "+")
    
    def copy(self):
        """Tạo một bản sao của bàn cờ.
        
        Returns:
            Board: Bản sao của bàn cờ
        """
        new_board = Board(self.size)
        new_board.board = [row[:] for row in self.board]
        new_board.last_move = self.last_move
        new_board.moves_count = self.moves_count
        new_board.move_history = self.move_history.copy()
        # Không sao chép threat_cache vì nó là bộ đệm
        return new_board