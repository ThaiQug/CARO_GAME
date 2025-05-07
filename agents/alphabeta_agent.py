import time
import random
from game.player import Player

class AlphaBetaAgent(Player):
    """Agent sử dụng thuật toán Alpha-Beta Pruning đã được tối ưu hóa."""
    
    def __init__(self, symbol, depth=3):
        """Khởi tạo agent Alpha-Beta."""
        super().__init__(symbol)
        self.depth = depth
        self.name = f"Alpha-Beta Agent (Level {depth}) ({symbol})"
        self.opponent_symbol = 'O' if symbol == 'X' else 'X'
        self.transposition_table = {}
        self.move_history = {}
        
        # Cân bằng giữa tấn công và phòng thủ
        self.defense_weight = 1.2  # Ưu tiên phòng thủ hơn
        
        # Trọng số khoảng cách cho sắp xếp nước đi
        self.distance_weights = {1: 10, 2: 5, 3: 1}
        
    def get_move(self, board):
        """Lấy nước đi tốt nhất sử dụng thuật toán Alpha-Beta Pruning."""
        start_time = time.time()
        self.transposition_table = {}  # Reset bộ nhớ đệm
        valid_moves = board.get_valid_moves()
        
        # Kiểm tra nhanh các trường hợp đặc biệt
        quick_move = self._check_quick_moves(board, valid_moves)
        if quick_move:
            return quick_move
        
        # Nếu là nước đi đầu tiên, ưu tiên đi giữa bàn cờ
        if board.moves_count == 0:
            mid = board.size // 2
            return (mid, mid)
        
        # Sắp xếp nước đi theo mức ưu tiên
        valid_moves = self._order_moves(board)
        
        best_score = float('-inf')
        best_moves = []
        alpha = float('-inf')
        beta = float('inf')
        
        # Iterative deepening: Tăng dần độ sâu
        for current_depth in range(1, self.depth + 1):
            # Kiểm tra thời gian
            if time.time() - start_time > 3.0 and current_depth > 1:
                break
                
            depth_best_score = float('-inf')
            depth_best_moves = []
            
            for move in valid_moves:
                row, col = move
                board_copy = board.copy()
                board_copy.make_move(row, col, self.symbol)
                
                score = self._alpha_beta(board_copy, current_depth - 1, alpha, beta, False)
                
                # Cập nhật lịch sử nước đi
                if (row, col) not in self.move_history:
                    self.move_history[(row, col)] = 0
                self.move_history[(row, col)] += 2 ** current_depth
                
                if score > depth_best_score:
                    depth_best_score = score
                    depth_best_moves = [move]
                elif score == depth_best_score:
                    depth_best_moves.append(move)
                
                alpha = max(alpha, depth_best_score)
            
            # Cập nhật nước đi tốt nhất
            best_score = depth_best_score
            best_moves = depth_best_moves.copy()
            
            # Tìm thấy nước đi thắng, dừng tìm kiếm
            if best_score >= 8000:
                break
        
        # Chọn một trong các nước đi tốt nhất
        if best_moves:
            return random.choice(best_moves)
        else:
            return random.choice(valid_moves)
    
    def _check_quick_moves(self, board, valid_moves):
        """Kiểm tra nhanh các nước đi chiến thắng hoặc phòng thủ quan trọng."""
        # Kiểm tra nước thắng ngay lập tức
        for move in valid_moves:
            row, col = move
            board_copy = board.copy()
            board_copy.make_move(row, col, self.symbol)
            if board_copy.check_winner() == self.symbol:
                return move
        
        # Kiểm tra nước chặn đối thủ thắng
        for move in valid_moves:
            row, col = move
            board_copy = board.copy()
            board_copy.make_move(row, col, self.opponent_symbol)
            if board_copy.check_winner() == self.opponent_symbol:
                return move
        
        return None
    
    def _order_moves(self, board):
        """Sắp xếp các nước đi hợp lệ theo thứ tự ưu tiên."""
        valid_moves = board.get_valid_moves()
        move_scores = []
        
        for move in valid_moves:
            row, col = move
            score = 0
            
            # Kiểm tra nước đi thắng/chặn
            board_copy = board.copy()
            board_copy.make_move(row, col, self.symbol)
            if board_copy.check_winner() == self.symbol:
                score += 10000
            
            board_copy = board.copy()
            board_copy.make_move(row, col, self.opponent_symbol)
            if board_copy.check_winner() == self.opponent_symbol:
                score += 10000
            
            # Ưu tiên nước đi gần quân cờ đã đặt
            score += self._calculate_distance_score(board, row, col)
            
            # Ưu tiên nước đi ở trung tâm
            center = board.size // 2
            distance_to_center = abs(row - center) + abs(col - center)
            score += (board.size - distance_to_center) * 2
            
            # Sử dụng lịch sử nước đi
            if (row, col) in self.move_history:
                score += self.move_history[(row, col)] // 100
            
            move_scores.append((move, score))
        
        # Sắp xếp nước đi theo điểm giảm dần
        move_scores.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in move_scores]
    
    def _calculate_distance_score(self, board, row, col):
        """Tính điểm cho nước đi dựa trên khoảng cách với quân cờ đã đặt."""
        score = 0
        for distance in range(1, 4):
            has_piece = False
            for dr in range(-distance, distance + 1):
                for dc in range(-distance, distance + 1):
                    if dr == 0 and dc == 0:
                        continue
                    
                    r, c = row + dr, col + dc
                    if (0 <= r < board.size and 0 <= c < board.size and 
                        board.board[r][c] != ' '):
                        has_piece = True
                        
                        # Cộng điểm nhiều hơn cho quân đối thủ gần
                        if board.board[r][c] == self.opponent_symbol:
                            score += self.distance_weights[distance] * 3
                        else:
                            score += self.distance_weights[distance] * 2
            
            if not has_piece:
                break
        
        return score
    
    def _alpha_beta(self, board, depth, alpha, beta, is_maximizing):
        """Thuật toán Alpha-Beta Pruning."""
        # Tạo hash key
        board_hash = ''.join([''.join(row) for row in board.board]) + str(board.last_move)
        
        # Kiểm tra trong bộ nhớ đệm
        if board_hash in self.transposition_table:
            cached_depth, cached_score = self.transposition_table[board_hash]
            if cached_depth >= depth:
                return cached_score
        
        # Kiểm tra điều kiện kết thúc
        winner = board.check_winner()
        if winner == self.symbol:
            return 10000
        elif winner == self.opponent_symbol:
            return -10000
        elif board.is_full() or depth == 0:
            return self._evaluate_board(board)
        
        if is_maximizing:
            best_score = float('-inf')
            valid_moves = self._order_moves(board)
            
            for move in valid_moves:
                row, col = move
                board_copy = board.copy()
                board_copy.make_move(row, col, self.symbol)
                
                score = self._alpha_beta(board_copy, depth - 1, alpha, beta, False)
                best_score = max(best_score, score)
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[board_hash] = (depth, best_score)
            return best_score
        else:
            best_score = float('inf')
            valid_moves = self._order_moves(board)
            
            for move in valid_moves:
                row, col = move
                board_copy = board.copy()
                board_copy.make_move(row, col, self.opponent_symbol)
                
                score = self._alpha_beta(board_copy, depth - 1, alpha, beta, True)
                best_score = min(best_score, score)
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            
            self.transposition_table[board_hash] = (depth, best_score)
            return best_score
    
    def _evaluate_board(self, board):
        """Đánh giá trạng thái bàn cờ."""
        # Sử dụng hàm đánh giá có sẵn của bàn cờ
        base_score = board.evaluate(self.symbol)
        
        # Đánh giá tấn công và phòng thủ
        attack_score = 0
        defense_score = 0
        
        # Đánh giá các dòng theo 4 hướng
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for row in range(board.size):
            for col in range(board.size):
                cell = board.board[row][col]
                if cell == ' ':
                    continue
                    
                for dr, dc in directions:
                    # Không đánh giá lại các dòng đã xem xét
                    if dr < 0 or (dr == 0 and dc < 0):
                        continue
                        
                    # Đếm số quân liên tiếp và số đầu mở
                    count = self._count_consecutive(board, row, col, dr, dc)
                    
                    if cell == self.symbol:
                        attack_score += self._score_line(count)
                    else:
                        defense_score -= self._score_line(count)
        
        # Cải thiện điểm số với trọng số phòng thủ
        total_score = base_score + attack_score + self.defense_weight * defense_score
        
        # Cộng thêm điểm cho kiểm soát trung tâm
        center_score = self._evaluate_center_control(board)
        total_score += center_score
        
        return total_score
    
    def _count_consecutive(self, board, row, col, dr, dc):
        """Đếm số quân liên tiếp và số đầu mở theo một hướng."""
        symbol = board.board[row][col]
        count = 1
        open_ends = 0
        
        # Kiểm tra về sau
        r, c = row + dr, col + dc
        while 0 <= r < board.size and 0 <= c < board.size:
            if board.board[r][c] == symbol:
                count += 1
            elif board.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
            r += dr
            c += dc
            
        # Kiểm tra về trước
        r, c = row - dr, col - dc
        while 0 <= r < board.size and 0 <= c < board.size:
            if board.board[r][c] == symbol:
                count += 1
            elif board.board[r][c] == ' ':
                open_ends += 1
                break
            else:
                break
            r -= dr
            c -= dc
        
        return (count, open_ends)
    
    def _score_line(self, count_data):
        """Tính điểm dựa trên số quân liên tiếp và số đầu mở."""
        count, open_ends = count_data
        
        if count >= 5:
            return 10000  # 5 liên tiếp = thắng
        elif count == 4:
            if open_ends == 2:
                return 5000  # 4 liên tiếp 2 đầu mở
            elif open_ends == 1:
                return 500   # 4 liên tiếp 1 đầu mở
        elif count == 3:
            if open_ends == 2:
                return 200   # 3 liên tiếp 2 đầu mở
            elif open_ends == 1:
                return 50    # 3 liên tiếp 1 đầu mở
        elif count == 2:
            if open_ends == 2:
                return 10    # 2 liên tiếp 2 đầu mở
            elif open_ends == 1:
                return 5     # 2 liên tiếp 1 đầu mở
        
        return 0
    
    def _evaluate_center_control(self, board):
        """Đánh giá mức độ kiểm soát trung tâm bàn cờ."""
        score = 0
        center = board.size // 2
        center_radius = board.size // 4
        
        # Đánh giá nhanh vùng trung tâm
        for row in range(center - center_radius, center + center_radius + 1):
            for col in range(center - center_radius, center + center_radius + 1):
                if not (0 <= row < board.size and 0 <= col < board.size):
                    continue
                    
                if board.board[row][col] == ' ':
                    continue
                
                # Khoảng cách đến trung tâm
                distance = abs(row - center) + abs(col - center)
                weight = max(0, center_radius - distance + 1)
                
                if board.board[row][col] == self.symbol:
                    score += weight * 2
                else:
                    score -= weight
        
        return score