init python:
    import random
    import json
    import os
    import datetime
    
    # ★ 已經拔除 import renpy 和 import store，不再引發系統崩潰！

    # --- 1. 重置棋盤 ---
    def reset_board(mode="normal"):
        global board
        board = [[0 for _ in range(9)] for _ in range(10)]
        
        board[0] = [-5, -4, -3, -2, -1, -2, -3, -4, -5] 
        board[2][1] = -6; board[2][7] = -6              
        board[3] = [-7, 0, -7, 0, -7, 0, -7, 0, -7]
        
        board[9] = [5, 4, 3, 2, 1, 2, 3, 4, 5]          
        board[7][1] = 6; board[7][7] = 6                
        board[6] = [7, 0, 7, 0, 7, 0, 7, 0, 7]
        
        if mode == "hell":
            board[6] = [0, 0, 0, 0, 0, 0, 0, 0, 0] 
            board[9][3] = 0; board[9][5] = 0       
            board[9][2] = 0; board[9][6] = 0       
        elif mode == "god": 
            board[6] = [0, 0, 0, 0, 0, 0, 0, 0, 0] 
            board[9][3] = 0; board[9][5] = 0       
            board[9][2] = 0; board[9][6] = 0

    # --- 2. 盤面評分系統 ---
    def evaluate_board(b, difficulty="easy"):
        score = 0
        values = {1: 1000000, 2: 250, 3: 250, 4: 450, 5: 1000, 6: 500, 7: 100}
        
        bx, by, rx, ry = -1, -1, -1, -1
        for y in range(10):
            for x in range(9):
                if b[y][x] == -1: bx, by = x, y
                elif b[y][x] == 1: rx, ry = x, y

        for y in range(10):
            for x in range(9):
                p = b[y][x]
                if p != 0:
                    abs_p = abs(p)
                    val = values.get(abs_p, 0)
                    
                    if difficulty in ["hard", "nightmare", "hell", "story_easy", "story_hard", "story_insane", "god"]:
                        if abs_p == 5 and y != 0 and y != 9: val += 15
                        if abs_p == 4 and ((p < 0 and y >= 4) or (p > 0 and y <= 5)): val += 20
                        if abs_p == 7 and ((p < 0 and y > 4) or (p > 0 and y < 5)): val += 20
                        if abs_p == 6:
                            if p > 0 and bx != -1 and x == bx: val += 60
                            if p < 0 and rx != -1 and x == rx: val += 60
                            
                    if difficulty == "story_insane":
                        if p == -7 and y == 3 and x == 4: val += 150 
                        if p == -4 and y == 2 and (x == 3 or x == 5): val += 100 
                        
                    score += val if p < 0 else -val
                        
        if difficulty in ["hard", "nightmare", "hell", "story_easy", "story_hard", "story_insane", "god"] and bx != -1:
            danger_zone = 0
            for dy in [-1, 0, 1, 2]:
                for dx in [-1, 0, 1]:
                    ny, nx = by + dy, bx + dx
                    if 0 <= ny < 10 and 0 <= nx < 9 and b[ny][nx] > 0 and abs(b[ny][nx]) in [4, 5, 6]:
                        danger_zone += 80
            score -= danger_zone
            
        return score

    # --- 3. 王對王檢查 ---
    def is_face_to_face(b):
        rx, ry, bx, by = -1, -1, -1, -1
        for y in range(10):
            for x in range(9):
                if b[y][x] == 1: rx, ry = x, y
                if b[y][x] == -1: bx, by = x, y
        if rx == bx and rx != -1: 
            min_y, max_y = min(ry, by), max(ry, by)
            for check_y in range(min_y + 1, max_y):
                if b[check_y][rx] != 0: return False 
            return True 
        return False

    # --- 4. 核心規則與技能變異判定 ---
    def is_valid_move(board, sx, sy, cx, cy):
        piece = board[sy][sx]
        target = board[cy][cx]
        
        if sx == cx and sy == cy: return False
        if (piece > 0 and target > 0) or (piece < 0 and target < 0): return False
        
        abs_p, dx, dy = abs(piece), abs(cx - sx), abs(cy - sy)
        can_skill = (game_mode == "story")
        
        def count_obs(x1, y1, x2, y2):
            c = 0
            if x1 == x2:
                for y in range(min(y1, y2)+1, max(y1, y2)):
                    if board[y][x1] != 0: c += 1
            elif y1 == y2:
                for x in range(min(x1, x2)+1, max(x1, x2)):
                    if board[y1][x] != 0: c += 1
            return c

        valid = False
        if abs_p == 1: valid = (dx + dy == 1) and (3 <= cx <= 5) and ((piece > 0 and cy >= 7) or (piece < 0 and cy <= 2))
        elif abs_p == 2: valid = (dx == 1 and dy == 1) and (3 <= cx <= 5) and ((piece > 0 and cy >= 7) or (piece < 0 and cy <= 2))
        elif abs_p == 3: valid = (dx == 2 and dy == 2) and (board[(sy+cy)//2][(sx+cx)//2] == 0) and ((piece > 0 and cy >= 5) or (piece < 0 and cy <= 4))
        elif abs_p == 4: 
            if can_skill and (("no_leg_block" in player_equipped_skills and piece > 0) or ("no_leg_block" in enemy_skills and piece < 0)):
                valid = (dx == 1 and dy == 2) or (dx == 2 and dy == 1)
            else:
                valid = (dx == 1 and dy == 2 and board[sy + (1 if cy > sy else -1)][sx] == 0) or (dx == 2 and dy == 1 and board[sy][sx + (1 if cx > sx else -1)] == 0)
        elif abs_p == 5: valid = (sx == cx or sy == cy) and count_obs(sx, sy, cx, cy) == 0
        elif abs_p == 6: 
            is_rook_skill = can_skill and (("cannon_to_rook" in player_equipped_skills and piece > 0) or ("cannon_to_rook" in enemy_skills and piece < 0))
            if is_rook_skill:
                valid = (sx == cx or sy == cy) and count_obs(sx, sy, cx, cy) == 0
            else:
                obs = count_obs(sx, sy, cx, cy)
                if sx == cx or sy == cy:
                    if target != 0: valid = (obs == 1)
                    else: valid = (obs == 0)
        elif abs_p == 7: 
            if can_skill and (("diagonal_pawn" in player_equipped_skills and piece > 0) or ("diagonal_pawn" in enemy_skills and piece < 0)):
                if dx == 1 and dy == 1 and ((piece > 0 and cy < sy) or (piece < 0 and cy > sy)): valid = True
            if not valid:
                valid = (dx + dy == 1) and ((piece > 0 and cy <= sy and (sy < 5 or sx == cx)) or (piece < 0 and cy >= sy and (sy > 4 or sx == cx)))

        # 模擬移動防止王對王
        if valid:
            old_target = board[cy][cx]
            board[cy][cx] = board[sy][sx]
            board[sy][sx] = 0
            if is_face_to_face(board): valid = False 
            board[sy][sx] = board[cy][cx]
            board[cy][cx] = old_target

        return valid

    # --- 5. AI 決策引擎 ---
    def get_all_possible_moves(b, is_black):
        moves = []
        for sy in range(10):
            for sx in range(9):
                if (is_black and b[sy][sx] < 0) or (not is_black and b[sy][sx] > 0):
                    for cy in range(10):
                        for cx in range(9):
                            if is_valid_move(b, sx, sy, cx, cy):
                                moves.append((sx, sy, cx, cy))
        return moves

    def alphabeta(board, depth, alpha, beta, is_maximizing, difficulty):
        king_b, king_r = False, False
        for row in board:
            if -1 in row: king_b = True
            if 1 in row: king_r = True
            if king_b and king_r: break
            
        if not king_b: return -9999999 
        if not king_r: return 9999999  

        if depth <= 0: return evaluate_board(board, difficulty)
        
        moves = get_all_possible_moves(board, is_black=is_maximizing)
        if not moves: return -9999999 if is_maximizing else 9999999
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in moves:
                sx, sy, cx, cy = move
                temp_b = [row[:] for row in board]
                temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
                eval_score = alphabeta(temp_b, depth - 1, alpha, beta, False, difficulty)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval
        else:
            min_eval = float('inf')
            for move in moves:
                sx, sy, cx, cy = move
                temp_b = [row[:] for row in board]
                temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
                eval_score = alphabeta(temp_b, depth - 1, alpha, beta, True, difficulty)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval

    def get_ai_move(board, difficulty="easy"):
        ai_moves = get_all_possible_moves(board, is_black=True)
        if not ai_moves: return None

        piece_count = sum(1 for row in board for p in row if p != 0)
        
        if difficulty in ["story_insane", "god"]:
            depth = 4 if piece_count < 18 else 3
        elif difficulty in ["hard", "hell", "story_hard"]:
            depth = 3
        else:
            depth = 2
            
        for move in ai_moves:
            if board[move[3]][move[2]] == 1:
                return move
            
        random.shuffle(ai_moves)
        best_moves = []
        best_score = -float('inf')
        
        for move in ai_moves:
            sx, sy, cx, cy = move
            temp_b = [row[:] for row in board]
            temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
            score = alphabeta(temp_b, depth - 1, -float('inf'), float('inf'), False, difficulty)
            
            if difficulty == "god": 
                if temp_b[cy][cx] > 0: score += 50
                
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)
                
        return random.choice(best_moves) if best_moves else None

    # --- 6. 機器學習資料收集模組 (JSON Exporter) ---
    def export_match_data(winner):
        # 使用內建 config 而不是 import renpy
        data_dir = os.path.join(config.basedir, "game", "ml_dataset")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

        # 使用內建 getattr 讀取全域變數
        g_mode = getattr(store, "game_mode", "unknown")
        ai_diff = getattr(store, "ai_difficulty", "unknown")
        s_history = getattr(store, "state_history", [])

        game_record = {
            "timestamp": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "game_mode": g_mode,
            "ai_difficulty": ai_diff,
            "winner": winner,
            "total_moves": len(s_history),
            "states": s_history
        }

        filename = f"match_{game_record['timestamp']}.json"
        filepath = os.path.join(data_dir, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(game_record, f, ensure_ascii=False, indent=4)
        except Exception as e:
            pass