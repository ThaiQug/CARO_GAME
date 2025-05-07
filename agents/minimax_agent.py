import time
import random
from game.player import Player

class MinimaxAgent(Player):
    """Agent sử dụng thuật toán Minimax."""
    
    def __init__(self, symbol, depth=2):
        """Khởi tạo agent Minimax.
        
        Args:
            symbol: Ký hiệu của agent ('X' hoặc 'O')
            depth: Độ sâu tìm kiếm của Minimax
        """
        super().__init__(symbol)
        self.depth = depth
        self.name = f"Minimax Agent (Level {depth}) ({symbol})"
        self.opponent_symbol = 'O' if symbol == 'X' else 'X'
        self.position_cache = {}
        
        # Pattern scores - điểm cố định cho các mẫu
        self.pattern_scores = {
            5: 10000,     # 5 liên tiếp = thắng
            4: {2: 500, 1: 100},  # 4 liên tiếp: 2 đầu mở = 500, 1 đầu mở = 100
            3: {2: 50, 1: 10},    # 3 liên tiếp: 2 đầu mở = 50, 1 đầu mở = 10
            2: {2: 5, 1: 2}       # 2 liên tiếp: 2 đầu mở = 5, 1 đầu mở = 2
        }
        
    def get_move(self, board):
        """Lấy nước đi tốt nhất Minimax."""
        start_time = time.time()
        self.position_cache.clear()  # Xóa cache
        
        # Kiểm tra nhanh các trường hợp đặc biệt
        if board.moves_count == 0:
            mid = board.size // 2
            return (mid, mid)
            
        valid_moves = self._get_promising_moves(board)
        
        # Kiểm tra nước thắng và nước chặn thắng
        for move in valid_moves[:min(len(valid_moves), 5)]:  # Chỉ kiểm tra top 5 nước đi
            row, col = move
            
            # Kiểm tra nước thắng nhanh
            board_copy = board.copy()
            board_copy.make_move(row, col, self.symbol)
            if board_copy.check_winner() == self.symbol:
                return move
            
            # Kiểm tra nước chặn thắng
            board_copy = board.copy()
            board_copy.make_move(row, col, self.opponent_symbol)
            if board_copy.check_winner() == self.opponent_symbol:
                return move
        
        # Chạy minimax cho những nước đi hứa hẹn nhất
        best_score = float('-inf')
        best_moves = []
        
        # Chỉ xét tối đa 12 nước đi hứa hẹn nhất để tăng tốc
        for move in valid_moves[:min(len(valid_moves), 12)]:
            row, col = move
            board_copy = board.copy()
            board_copy.make_move(row, col, self.symbol)
            
            score = self._minimax(board_copy, self.depth - 1, False, float('-inf'), float('inf'))
            
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
        
        end_time = time.time()
        print(f"AI đã suy nghĩ trong {end_time - start_time:.2f} giây")
        
        return random.choice(best_moves) if best_moves else valid_moves[0]
    
    def _get_promising_moves(self, board):
        """Lấy và sắp xếp các nước đi hứa hẹn."""
        valid_moves = board.get_valid_moves()
        if not valid_moves:
            return []
            
        scored_moves = []
        
        for move in valid_moves:
            row, col = move
            score = 0
            
            # 1. Ưu tiên nước đi gần quân cờ đã đặt
            nearby_pieces = 0
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    r, c = row + dr, col + dc
                    if 0 <= r < board.size and 0 <= c < board.size and board.board[r][c] != ' ':
                        # Quân càng gần càng có giá trị cao
                        dist = abs(dr) + abs(dc)
                        if dist == 1:
                            nearby_pieces += 3  # Liền kề
                        elif dist == 2:
                            nearby_pieces += 1  # Cách 1 ô
            
            score += nearby_pieces * 10
            
            # 2. Điểm cho vị trí trung tâm
            center = board.size // 2
            distance_to_center = abs(row - center) + abs(col - center)
            center_score = max(0, board.size - distance_to_center * 2)
            score += center_score
            
            # 3. Đánh giá nhanh mẫu tấn công/phòng thủ
            # Kiểm tra mẫu tấn công nhanh
            board_copy = board.copy()
            board_copy.make_move(row, col, self.symbol)
            if self._has_potential_threat(board_copy, self.symbol):
                score += 300
                
            # Kiểm tra mẫu phòng thủ nhanh
            board_copy = board.copy()
            board_copy.make_move(row, col, self.opponent_symbol)
            if self._has_potential_threat(board_copy, self.opponent_symbol):
                score += 250
            
            scored_moves.append((move, score))
        
        # Sắp xếp theo điểm giảm dần
        scored_moves.sort(key=lambda x: x[1], reverse=True)
        return [move for move, _ in scored_moves]
    
    def _has_potential_threat(self, board, symbol):
        """Kiểm tra nhanh xem có mối đe dọa tiềm năng không."""
        # Kiểm tra nhanh các mẫu nguy hiểm: 4 liên tiếp hoặc 3 liên tiếp 2 đầu mở
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != symbol:
                    continue
                
                # Kiểm tra các hướng
                directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                for dr, dc in directions:
                    consecutive = 1
                    open_ends = 0
                    
                    # Kiểm tra trước
                    r, c = row - dr, col - dc
                    if 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] == ' ':
                            open_ends += 1
                        elif board.board[r][c] == symbol:
                            consecutive += 1
                            # Kiểm tra thêm
                            r2, c2 = r - dr, c - dc
                            if 0 <= r2 < board.size and 0 <= c2 < board.size:
                                if board.board[r2][c2] == symbol:
                                    consecutive += 1
                                    r3, c3 = r2 - dr, c2 - dc
                                    if 0 <= r3 < board.size and 0 <= c3 < board.size:
                                        if board.board[r3][c3] == symbol:
                                            consecutive += 1
                                            r4, c4 = r3 - dr, c3 - dc
                                            if 0 <= r4 < board.size and 0 <= c4 < board.size and board.board[r4][c4] == ' ':
                                                open_ends += 1
                                        elif board.board[r3][c3] == ' ':
                                            open_ends += 1
                                elif board.board[r2][c2] == ' ':
                                    open_ends += 1
                    
                    # Kiểm tra sau
                    r, c = row + dr, col + dc
                    if 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] == ' ':
                            open_ends += 1
                        elif board.board[r][c] == symbol:
                            consecutive += 1
                            # Kiểm tra thêm
                            r2, c2 = r + dr, c + dc
                            if 0 <= r2 < board.size and 0 <= c2 < board.size:
                                if board.board[r2][c2] == symbol:
                                    consecutive += 1
                                    r3, c3 = r2 + dr, c2 + dc
                                    if 0 <= r3 < board.size and 0 <= c3 < board.size:
                                        if board.board[r3][c3] == symbol:
                                            consecutive += 1
                                            r4, c4 = r3 + dr, c3 + dc
                                            if 0 <= r4 < board.size and 0 <= c4 < board.size and board.board[r4][c4] == ' ':
                                                open_ends += 1
                                        elif board.board[r3][c3] == ' ':
                                            open_ends += 1
                                elif board.board[r2][c2] == ' ':
                                    open_ends += 1
                    
                    # Mẫu nguy hiểm
                    if consecutive >= 4 or (consecutive == 3 and open_ends == 2):
                        return True
        
        return False
    
    def _minimax(self, board, depth, is_maximizing, alpha, beta):
        """Thuật toán Minimax với cắt tỉa Alpha-Beta."""
        # Hash bàn cờ
        board_hash = hash(str(board.board))
        cache_key = (board_hash, depth, is_maximizing)
        
        # Kiểm tra cache
        if cache_key in self.position_cache:
            return self.position_cache[cache_key]
        
        # Kiểm tra điều kiện kết thúc
        winner = board.check_winner()
        if winner == self.symbol:
            return 10000 + depth  # Thêm depth để ưu tiên thắng sớm
        elif winner == self.opponent_symbol:
            return -10000 - depth  # Ưu tiên thua muộn
        elif board.is_full() or depth == 0:
            return self._evaluate_board(board)
        
        # Chỉ lấy một số nước đi hứa hẹn để tăng tốc
        moves = self._get_promising_moves(board)[:8]  # Giới hạn 8 nước đi
        
        if is_maximizing:
            best_score = float('-inf')
            for move in moves:
                row, col = move
                board_copy = board.copy()
                board_copy.make_move(row, col, self.symbol)
                
                score = self._minimax(board_copy, depth - 1, False, alpha, beta)
                best_score = max(best_score, score)
                
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            
            self.position_cache[cache_key] = best_score
            return best_score
        else:
            best_score = float('inf')
            for move in moves:
                row, col = move
                board_copy = board.copy()
                board_copy.make_move(row, col, self.opponent_symbol)
                
                score = self._minimax(board_copy, depth - 1, True, alpha, beta)
                best_score = min(best_score, score)
                
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            
            self.position_cache[cache_key] = best_score
            return best_score
    
    def _evaluate_board(self, board):
        """Đánh giá trạng thái bàn cờ."""
        score = 0
        
        # Đánh giá cho cả agent và đối thủ
        score += self._evaluate_patterns(board, self.symbol, 1.0)
        score -= self._evaluate_patterns(board, self.opponent_symbol, 0.9)  # Trọng số phòng thủ nhẹ hơn
        
        return score
    
    def _evaluate_patterns(self, board, symbol, weight):
        """Đánh giá các mẫu cho một người chơi cụ thể."""
        score = 0
        checked = set()  # Tránh đánh giá lặp lại
        
        for row in range(board.size):
            for col in range(board.size):
                if board.board[row][col] != symbol or (row, col) in checked:
                    continue
                
                # Đánh giá 4 hướng
                directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
                
                for dr, dc in directions:
                    # Bỏ qua nếu đã kiểm tra
                    if (row, col, dr, dc) in checked:
                        continue
                        
                    consecutive = 1
                    open_ends = 0
                    pattern_cells = [(row, col)]
                    
                    # Kiểm tra về trước
                    r, c = row - dr, col - dc
                    while 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] == symbol:
                            consecutive += 1
                            pattern_cells.append((r, c))
                        elif board.board[r][c] == ' ':
                            open_ends += 1
                            break
                        else:
                            break
                        r -= dr
                        c -= dc
                    
                    # Kiểm tra về sau
                    r, c = row + dr, col + dc
                    while 0 <= r < board.size and 0 <= c < board.size:
                        if board.board[r][c] == symbol:
                            consecutive += 1
                            pattern_cells.append((r, c))
                        elif board.board[r][c] == ' ':
                            open_ends += 1
                            break
                        else:
                            break
                        r += dr
                        c += dc
                    
                    # Đánh dấu các ô đã kiểm tra
                    for cell in pattern_cells:
                        checked.add(cell)
                    checked.add((row, col, dr, dc))
                    
                    # Tính điểm dựa trên mẫu
                    if consecutive >= 5:
                        score += self.pattern_scores[5] * weight
                    elif consecutive == 4:
                        if open_ends in self.pattern_scores[4]:
                            score += self.pattern_scores[4][open_ends] * weight
                    elif consecutive == 3:
                        if open_ends in self.pattern_scores[3]:
                            score += self.pattern_scores[3][open_ends] * weight
                    elif consecutive == 2:
                        if open_ends in self.pattern_scores[2]:
                            score += self.pattern_scores[2][open_ends] * weight
        
        return score