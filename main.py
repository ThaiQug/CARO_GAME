import time
import random
from game.board import Board
from game.player import HumanPlayer, Game
from agents.random_agent import RandomAgent
from agents.minimax_agent import MinimaxAgent
from agents.alphabeta_agent import AlphaBetaAgent

def get_agent(agent_type, symbol, level=None):
    """Tạo agent với loại và cấp độ cho trước.
    
    Args:
        agent_type: Loại agent (1: Random, 2: Minimax, 3: Alpha-Beta)
        symbol: Ký hiệu của agent ('X' hoặc 'O')
        level: Cấp độ của agent (1-10)
        
    Returns:
        Player: Agent được tạo
    """
    if agent_type == 1:
        return RandomAgent(symbol)
    elif agent_type == 2:
        depth = max(1, min(3, level // 3))  # Chuyển đổi level thành depth (1-3)
        return MinimaxAgent(symbol, depth)
    elif agent_type == 3:
        depth = max(1, min(5, level // 2))  # Chuyển đổi level thành depth (1-5)
        return AlphaBetaAgent(symbol, depth)

def evaluate_agents():
    """Đánh giá khả năng của các agent."""
    print("\n=== ĐÁNH GIÁ KHẢ NĂNG CỦA AGENT ===")
    board_size = 10  # Kích thước bàn cờ nhỏ hơn để đánh giá nhanh hơn
    num_games = 10
    
    # Danh sách các agent cần đánh giá
    agents = [
        RandomAgent('X'),
        MinimaxAgent('X', 1),
        MinimaxAgent('X', 2),
        MinimaxAgent('X', 3),
        AlphaBetaAgent('X', 1),
        AlphaBetaAgent('X', 2),
        AlphaBetaAgent('X', 3),
        AlphaBetaAgent('X', 4),
        AlphaBetaAgent('X', 5)
    ]
    
    results = {}
    
    for i, agent1 in enumerate(agents):
        results[agent1.name] = {"wins": 0, "losses": 0, "draws": 0}
        
        for j, agent2 in enumerate(agents):
            if i == j:
                continue
                
            print(f"\nĐánh giá: {agent1.name} vs {agent2.name}")
            wins = 0
            losses = 0
            draws = 0
            
            for game_idx in range(num_games // 2):
                # Mỗi cặp agent chơi 2 ván, mỗi agent được đi trước 1 ván
                
                # Ván 1: agent1 đi trước
                board = Board(board_size)
                agent1.symbol = 'X'
                agent2.symbol = 'O'
                game = Game(board, agent1, agent2)
                print(f"Ván {game_idx*2 + 1}: {agent1.name} (X) vs {agent2.name} (O)")
                winner = game.play(verbose=False)
                
                if winner == 'X':
                    wins += 1
                    print(f"{agent1.name} thắng!")
                elif winner == 'O':
                    losses += 1
                    print(f"{agent2.name} thắng!")
                else:
                    draws += 1
                    print("Hòa!")
                
                # Ván 2: agent2 đi trước
                board = Board(board_size)
                agent1.symbol = 'O'
                agent2.symbol = 'X'
                game = Game(board, agent2, agent1)
                print(f"Ván {game_idx*2 + 2}: {agent2.name} (X) vs {agent1.name} (O)")
                winner = game.play(verbose=False)
                
                if winner == 'O':
                    wins += 1
                    print(f"{agent1.name} thắng!")
                elif winner == 'X':
                    losses += 1
                    print(f"{agent2.name} thắng!")
                else:
                    draws += 1
                    print("Hòa!")
            
            print(f"Kết quả: {agent1.name} thắng {wins}, thua {losses}, hòa {draws}")
            results[agent1.name]["wins"] += wins
            results[agent1.name]["losses"] += losses
            results[agent1.name]["draws"] += draws
    
    # Tính điểm và xếp hạng
    rankings = []
    for agent_name, stats in results.items():
        win_rate = (stats["wins"] * 3 + stats["draws"]) / ((stats["wins"] + stats["losses"] + stats["draws"]) * 3)
        rankings.append((agent_name, win_rate))
    
    # Sắp xếp theo tỷ lệ thắng giảm dần
    rankings.sort(key=lambda x: x[1], reverse=True)
    
    print("\n=== XẾP HẠNG AGENT ===")
    for rank, (agent_name, win_rate) in enumerate(rankings, 1):
        stats = results[agent_name]
        print(f"{rank}. {agent_name}: Thắng {stats['wins']}, Thua {stats['losses']}, Hòa {stats['draws']}, Tỷ lệ thắng: {win_rate:.2%}")

def main():
    """Hàm chính của chương trình."""
    print("===== GAME CỜ CARO =====")
    print("1. Người vs Người")
    print("2. Người vs Máy")
    print("3. Máy vs Máy")
    print("4. Đánh giá Agent")
    
    choice = int(input("Chọn chế độ chơi: "))
    
    if choice == 1:
        # Người vs Người
        board_size = int(input("Nhập kích thước bàn cờ (VD: 15): "))
        board = Board(board_size)
        player1 = HumanPlayer('X')
        player2 = HumanPlayer('O')
        game = Game(board, player1, player2)
        game.play()
    
    elif choice == 2:
        # Người vs Máy
        board_size = int(input("Nhập kích thước bàn cờ (VD: 15): "))
        board = Board(board_size)
        
        print("\nLựa chọn AI:")
        print("1. Random Agent")
        print("2. Minimax Agent")
        print("3. Alpha-Beta Agent")
        
        agent_type = int(input("Chọn loại AI: "))
        
        if agent_type < 1 or agent_type > 3:
            print("Lựa chọn không hợp lệ. Sử dụng Alpha-Beta Agent.")
            agent_type = 3
        
        level = int(input("Chọn cấp độ khó (1-10): "))
        level = max(1, min(10, level))  # Giới hạn cấp độ từ 1-10
        
        print("\nAI sẽ chơi với:")
        print("1. X (đi trước)")
        print("2. O (đi sau)")
        
        ai_symbol_choice = int(input("Chọn quân cờ cho AI: "))
        
        if ai_symbol_choice == 1:
            # AI đi trước
            ai_player = get_agent(agent_type, 'X', level)
            human_player = HumanPlayer('O')
            game = Game(board, ai_player, human_player)
        else:
            # AI đi sau
            human_player = HumanPlayer('X')
            ai_player = get_agent(agent_type, 'O', level)
            game = Game(board, human_player, ai_player)
        
        game.play()
    
    elif choice == 3:
        # Máy vs Máy
        board_size = int(input("Nhập kích thước bàn cờ (VD: 15): "))
        board = Board(board_size)
        
        print("\nLựa chọn AI 1 (X):")
        print("1. Random Agent")
        print("2. Minimax Agent")
        print("3. Alpha-Beta Agent")
        
        agent1_type = int(input("Chọn loại AI 1: "))
        
        if agent1_type < 1 or agent1_type > 3:
            print("Lựa chọn không hợp lệ. Sử dụng Alpha-Beta Agent.")
            agent1_type = 3
        
        level1 = int(input("Chọn cấp độ khó cho AI 1 (1-10): "))
        level1 = max(1, min(10, level1))  # Giới hạn cấp độ từ 1-10
        
        print("\nLựa chọn AI 2 (O):")
        print("1. Random Agent")
        print("2. Minimax Agent")
        print("3. Alpha-Beta Agent")
        
        agent2_type = int(input("Chọn loại AI 2: "))
        
        if agent2_type < 1 or agent2_type > 3:
            print("Lựa chọn không hợp lệ. Sử dụng Alpha-Beta Agent.")
            agent2_type = 3
        
        level2 = int(input("Chọn cấp độ khó cho AI 2 (1-10): "))
        level2 = max(1, min(10, level2))  # Giới hạn cấp độ từ 1-10
        
        ai_player1 = get_agent(agent1_type, 'X', level1)
        ai_player2 = get_agent(agent2_type, 'O', level2)
        game = Game(board, ai_player1, ai_player2)
        game.play()
    
    elif choice == 4:
        # Đánh giá Agent
        evaluate_agents()
    
    else:
        print("Lựa chọn không hợp lệ.")

if __name__ == "__main__":
    main()