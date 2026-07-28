init python:
    import random
    import json
    import os
    import datetime
    import math
    import time
    
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

    piece_asset_map = {
        1: "images/pieces/red_king.png",
        2: "images/pieces/red_advisor.png",
        3: "images/pieces/red_elephant.png",
        4: "images/pieces/red_horse.png",
        5: "images/pieces/red_rook.png",
        6: "images/pieces/red_cannon.png",
        7: "images/pieces/red_pawn.png",
        -1: "images/pieces/black_king.png",
        -2: "images/pieces/black_advisor.png",
        -3: "images/pieces/black_elephant.png",
        -4: "images/pieces/black_horse.png",
        -5: "images/pieces/black_rook.png",
        -6: "images/pieces/black_cannon.png",
        -7: "images/pieces/black_pawn.png",
    }

    def piece_asset(piece_code):
        return piece_asset_map.get(piece_code, "images/pieces/empty_marker.png")

    def find_king(b, side):
        target = 1 if side == "red" else -1
        for y in range(10):
            for x in range(9):
                if b[y][x] == target:
                    return (x, y)
        return None

    def is_in_check(b, side):
        king_pos = find_king(b, side)
        if king_pos is None:
            return False

        kx, ky = king_pos
        opponent_is_black = (side == "red")
        for sy in range(10):
            for sx in range(9):
                p = b[sy][sx]
                if (opponent_is_black and p < 0) or ((not opponent_is_black) and p > 0):
                    if is_valid_move(b, sx, sy, kx, ky):
                        return True
        return False

    def refresh_check_status():
        global check_status, check_target_pos

        if is_in_check(board, "red"):
            check_status = "將軍！紅方主帥受威脅"
            check_target_pos = find_king(board, "red")
        elif is_in_check(board, "black"):
            check_status = "將軍！黑方將領受威脅"
            check_target_pos = find_king(board, "black")
        else:
            check_status = ""
            check_target_pos = None

    board_image_sizes = {
        "images/board_bg.png": (706, 716),
        "images/board_bg-1.png": (434, 483),
        "images/board_bg-2.png": (649, 724),
        "images/board_bg-3.png": (447, 468),
        "images/board_bg-4.png": (719, 791),
    }

    def chessboard_layout(image_name, zoom):
        screen_w = getattr(config, "screen_width", 1920)
        screen_h = getattr(config, "screen_height", 1080)
        img_w, img_h = board_image_sizes.get(image_name, (706, 716))

        image_w = img_w * zoom
        image_h = img_h * zoom
        image_x = (screen_w - image_w) / 2.0
        image_y = (screen_h - image_h) / 2.0

        # Ratios measured from the normal board image. They mark the first
        # vertical/horizontal grid line and the opposite edge grid line.
        grid_left = img_w * 0.085
        grid_top = img_h * 0.031
        grid_right = img_w * 0.923
        grid_bottom = img_h * 0.974
        point_dx = ((grid_right - grid_left) / 8.0) * zoom
        point_dy = ((grid_bottom - grid_top) / 9.0) * zoom
        cell = 72

        return {
            "image_x": int(round(image_x)),
            "image_y": int(round(image_y)),
            "grid_x": int(round(image_x + grid_left * zoom - cell / 2.0)),
            "grid_y": int(round(image_y + grid_top * zoom - cell / 2.0)),
            "xspacing": int(round(point_dx - cell)),
            "yspacing": int(round(point_dy - cell)),
            "cell": cell,
        }

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

    ai_piece_values = {1: 1000000, 2: 250, 3: 250, 4: 450, 5: 1000, 6: 500, 7: 100}

    def quick_move_score(b, move):
        sx, sy, cx, cy = move
        piece = abs(b[sy][sx])
        captured = abs(b[cy][cx])
        score = ai_piece_values.get(captured, 0) * 8

        # Prefer active, central moves when captures are equal.
        score += max(0, 4 - abs(cx - 4)) * 3
        score += max(0, 5 - abs(cy - 4)) * 2
        score += ai_piece_values.get(piece, 0) * 0.01
        return score

    def ai_search_budget(difficulty):
        if difficulty in ["story_insane", "god"]:
            return 1.8
        if difficulty in ["hell", "story_hard"]:
            return 1.2
        if difficulty == "hard":
            return 0.9
        return 0.35

    def alphabeta(board, depth, alpha, beta, is_maximizing, difficulty, deadline=None):
        if deadline is not None and time.perf_counter() >= deadline:
            return evaluate_board(board, difficulty)

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
        moves.sort(key=lambda move: quick_move_score(board, move), reverse=True)
        
        if is_maximizing:
            max_eval = -float('inf')
            for move in moves:
                if deadline is not None and time.perf_counter() >= deadline:
                    break
                sx, sy, cx, cy = move
                temp_b = [row[:] for row in board]
                temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
                eval_score = alphabeta(temp_b, depth - 1, alpha, beta, False, difficulty, deadline)
                max_eval = max(max_eval, eval_score)
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval if max_eval != -float('inf') else evaluate_board(board, difficulty)
        else:
            min_eval = float('inf')
            for move in moves:
                if deadline is not None and time.perf_counter() >= deadline:
                    break
                sx, sy, cx, cy = move
                temp_b = [row[:] for row in board]
                temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
                eval_score = alphabeta(temp_b, depth - 1, alpha, beta, True, difficulty, deadline)
                min_eval = min(min_eval, eval_score)
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval if min_eval != float('inf') else evaluate_board(board, difficulty)

    learned_policy_cache = None

    def learned_board_key(b):
        return "/".join(",".join(str(cell) for cell in row) for row in b)

    def learned_move_code(move):
        return "{},{},{},{}".format(move[0], move[1], move[2], move[3])

    def get_learned_policy():
        global learned_policy_cache

        if learned_policy_cache is not None:
            return learned_policy_cache

        policy_path = os.path.join(config.basedir, "game", "xq_learned_policy.json")
        try:
            with open(policy_path, "r", encoding="utf-8") as f:
                learned_policy_cache = json.load(f)
        except Exception:
            learned_policy_cache = {"metadata": {}, "positions": {}, "priors": {}}

        return learned_policy_cache

    def learned_prior_score(b, move, difficulty="easy"):
        policy = get_learned_policy()
        priors = policy.get("priors", {})
        sx, sy, cx, cy = move
        piece = b[sy][sx]
        code = learned_move_code(move)

        score = 0.0
        for key, weight in (
            ("move:{}:{}".format(piece, code), 260.0),
            ("to:{}:{},{}".format(piece, cx, cy), 90.0),
            ("delta:{}:{},{}".format(piece, cx - sx, cy - sy), 45.0),
        ):
            stat = priors.get(key)
            if stat:
                score += float(stat.get("score", 0.0)) * weight
                score += math.log(float(stat.get("count", 0)) + 1.0) * (weight * 0.035)

        if difficulty in ["story_insane", "god"]:
            return score * 1.25
        if difficulty in ["hard", "hell", "story_hard"]:
            return score
        return score * 0.65

    def get_learned_book_move(b, legal_moves, difficulty="easy"):
        policy = get_learned_policy()
        position = policy.get("positions", {}).get(learned_board_key(b))
        if not position:
            return None

        legal_codes = set(learned_move_code(move) for move in legal_moves)
        candidates = []

        for item in position.get("moves", []):
            move = tuple(item.get("move", []))
            if len(move) != 4:
                continue
            code = learned_move_code(move)
            if code not in legal_codes:
                continue

            count = float(item.get("count", 0))
            score = float(item.get("score", 0.0))
            rank_score = score * 1000.0 + math.log(count + 1.0) * 120.0
            candidates.append((rank_score, move))

        if not candidates:
            return None

        candidates.sort(reverse=True)

        if difficulty in ["story_insane", "god", "hard", "hell", "story_hard"]:
            return candidates[0][1]

        # Easy AI still learns, but keeps a little variety.
        top = candidates[:min(3, len(candidates))]
        total = sum(max(1.0, item[0] - top[-1][0] + 1.0) for item in top)
        pick = random.random() * total
        running = 0.0
        for score, move in top:
            running += max(1.0, score - top[-1][0] + 1.0)
            if running >= pick:
                return move

        return top[0][1]

    def get_ai_move(board, difficulty="easy"):
        ai_moves = get_all_possible_moves(board, is_black=True)
        if not ai_moves: return None

        learned_move = get_learned_book_move(board, ai_moves, difficulty)
        if learned_move:
            return learned_move

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
        ai_moves.sort(key=lambda move: quick_move_score(board, move) + learned_prior_score(board, move, difficulty), reverse=True)

        deadline = time.perf_counter() + ai_search_budget(difficulty)
        best_moves = []
        best_score = -float('inf')
        
        for move in ai_moves:
            if time.perf_counter() >= deadline and best_moves:
                break

            sx, sy, cx, cy = move
            temp_b = [row[:] for row in board]
            temp_b[cy][cx] = temp_b[sy][sx]; temp_b[sy][sx] = 0
            score = alphabeta(temp_b, depth - 1, -float('inf'), float('inf'), False, difficulty, deadline)
            score += learned_prior_score(board, move, difficulty)
            
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
