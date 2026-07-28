# ==============================================================================
# 0. 定義劇情背景圖片 (★ 調整大小請改這裡的 zoom 數值 ★)
# ==============================================================================
image bg garden = Transform("images/garden.jpg", zoom=2.0)
image bg black_market = Transform("images/black market.jpg", zoom=2.0)
image bg mechanical = Transform("images/mechanical.jpg", zoom=2.0)
image bg god = Transform("images/God.jpg", zoom=1.6)

# ==============================================================================
# 1. 遊戲核心全局變數定義
# ==============================================================================
default player_money = 2000       
default player_lv = 1            
default player_exp = 0           
default current_chapter = 1      

default current_board_img = "images/board_bg.png" 
default current_board_zoom = 1.1  

default max_skill_slots = 1              
default player_owned_skills = []         
default player_equipped_skills = []      
default enemy_skills = []                

default board = []
default selected_pos = None      
default current_turn = "紅方"    
default last_move = (-1, -1)     
default last_capture_pos = None
default check_status = ""
default check_target_pos = None
default game_mode = "PvE"        
default ai_difficulty = "easy"   

default move_history = []        
default state_history = []       

# ==============================================================================
# 2. 遊戲故事開局標籤
# ==============================================================================
label start:
    scene bg room 
    play music "images/bg_music.mp3" fadein 2.0 loop
    "西元2026年，世界發生了被稱為【忘棋日】的神秘事件。"
    "一夜之間，全世界的人類都徹底忘記了「中國象棋」的規則與玩法。"
    "古老的棋盤成了無人能解的謎題，直到你在夢境中重溯了楚河漢界..."
    jump main_hub

# ==============================================================================
# 3. 遊戲核心控制大廳
# ==============================================================================
label main_hub:
    scene bg room
    
    # ★ 改用這個語法，如果歌還在播就不會重頭，如果被停掉就會再次叫醒它
    play music "images/bg_music.mp3" fadein 2.0 loop
        
    "【主城大廳】"
    "狀態：Lv.[player_lv] | 經驗：[player_exp]/100 | 資金：[player_money] 元"
    menu:
        "【主線劇情】《失落棋界》":
            jump story_mode_hub
        "【自由練習】 (雙人對戰 / 人機對戰)":
            jump practice_mode_hub
        "【棋魂黑市】 (購買技能 / 裝備配置)":
            jump shop_hub
        "離開遊戲":
            return

# ==============================================================================
# 4. 商店與配置整合選單
# ==============================================================================
label shop_hub:
    "【棋魂黑市入口】你要進行什麼操作？"
    menu:
        "購買變異技能":
            jump skill_shop
        "進入技能配置艙 (裝備/卸下)":
            jump skill_loadout
        "返回主城大廳":
            jump main_hub

# ==============================================================================
# 5. 技能配置系統
# ==============================================================================
label skill_loadout:
    python:
        used_slots = len(player_equipped_skills)
        free_slots = max_skill_slots - used_slots
        
    "【配置艙】目前可用欄位：[used_slots] / [max_skill_slots]"
    "已裝備技能：[player_equipped_skills]"
    
    menu:
        "裝備【斜步突刺】" if "diagonal_pawn" in player_owned_skills and "diagonal_pawn" not in player_equipped_skills:
            if free_slots > 0:
                $ player_equipped_skills.append("diagonal_pawn")
                "已裝備【斜步突刺】。"
            else:
                "【系統警告】技能欄位已滿！請先卸下其他技能。"
            jump skill_loadout
            
        "裝備【無影馬】" if "no_leg_block" in player_owned_skills and "no_leg_block" not in player_equipped_skills:
            if free_slots > 0:
                $ player_equipped_skills.append("no_leg_block")
                "已裝備【無影馬】。"
            else:
                "【系統警告】技能欄位已滿！請先卸下其他技能。"
            jump skill_loadout
            
        "裝備【重裝炮車】" if "cannon_to_rook" in player_owned_skills and "cannon_to_rook" not in player_equipped_skills:
            if free_slots > 0:
                $ player_equipped_skills.append("cannon_to_rook")
                "已裝備【重裝炮車】。"
            else:
                "【系統警告】技能欄位已滿！"
            jump skill_loadout
            
        "卸下【斜步突刺】" if "diagonal_pawn" in player_equipped_skills:
            $ player_equipped_skills.remove("diagonal_pawn")
            "已卸下技能。"
            jump skill_loadout
            
        "卸下【無影馬】" if "no_leg_block" in player_equipped_skills:
            $ player_equipped_skills.remove("no_leg_block")
            "已卸下技能。"
            jump skill_loadout
            
        "卸下【重裝炮車】" if "cannon_to_rook" in player_equipped_skills:
            $ player_equipped_skills.remove("cannon_to_rook")
            "已卸下技能。"
            jump skill_loadout
            
        "擴充技能欄位 (花費 5000 元)" if max_skill_slots < 3:
            if player_money >= 5000:
                $ player_money -= 5000
                $ max_skill_slots += 1
                "【系統解鎖】你的大腦開發度提升，現在可以裝備 [max_skill_slots] 個技能了！"
            else:
                "資金不足！"
            jump skill_loadout
            
        "返回黑市入口":
            jump shop_hub

# ==============================================================================
# 6. 棋魂變異技能商店
# ==============================================================================
label skill_shop:
    "【棋魂黑市】購買後的技能需至「技能配置艙」裝備才會生效。"
    menu:
        "【兵系：斜步突刺】(1000 元)" if "diagonal_pawn" not in player_owned_skills:
            if player_money >= 1000:
                $ player_money -= 1000
                $ player_owned_skills.append("diagonal_pawn")
                "購買成功！"
            else:
                "資金不足。"
            jump skill_shop
        "【馬系：無影馬】(3000 元)" if "no_leg_block" not in player_owned_skills:
            if player_money >= 3000:
                $ player_money -= 3000
                $ player_owned_skills.append("no_leg_block")
                "購買成功！"
            else:
                "資金不足。"
            jump skill_shop
        "【炮系：重裝炮車】(8000 元)" if "cannon_to_rook" not in player_owned_skills:
            if player_money >= 8000:
                $ player_money -= 8000
                $ player_owned_skills.append("cannon_to_rook")
                "購買成功！"
            else:
                "資金不足。"
            jump skill_shop
        "返回黑市入口":
            jump shop_hub

# ==============================================================================
# 7. 自主練習模式入口
# ==============================================================================
label practice_mode_hub:
    menu:
        "雙人對戰 (PvP免費對弈)":
            $ game_mode = "PvP"
            $ ai_difficulty = "none"
            $ current_board_img = "images/board_bg.png"
            $ current_board_zoom = 1.1
            $ reset_board("normal")
            jump init_game_match
        "人機：日常對局 (100元)":
            $ game_mode = "PvE"
            $ ai_difficulty = "easy"
            $ current_board_img = "images/board_bg.png"
            $ current_board_zoom = 1.1
            $ enemy_skills = [] 
            $ reset_board("normal")
            jump init_game_match
        "人機：困難對局 (500元)":
            $ game_mode = "PvE"
            $ ai_difficulty = "hard"
            $ current_board_img = "images/board_bg.png"
            $ current_board_zoom = 1.1
            $ enemy_skills = []
            $ reset_board("normal")
            jump init_game_match
        "人機：地獄讓九子 (2000元)":
            $ game_mode = "PvE"
            $ ai_difficulty = "hell"
            $ current_board_img = "images/board_bg.png"
            $ current_board_zoom = 1.1
            $ enemy_skills = []
            $ reset_board("hell")
            jump init_game_match
        "返回主城大廳":
            jump main_hub

# ==============================================================================
# 8. 主線劇情章節系統
# ==============================================================================
label story_mode_hub:
    # ★ 確保連戰進入劇情時音樂被喚醒
    play music "images/bg_music.mp3" fadein 2.0 loop

    menu:
        "第一章：遺忘之街" if current_chapter >= 1:
            jump chapter_1_story
        "第二章：黑市棋館" if current_chapter >= 2:
            jump chapter_2_story
        "第三章：機械棋城" if current_chapter >= 3:
            jump chapter_3_story
        "最終章：天元之局" if current_chapter >= 4:
            jump chapter_4_story
        "返回主城大廳":
            jump main_hub

label chapter_1_story:
    scene bg garden 
    "第一章：棋權之城"
    "你從墜落中驚醒。耳邊傳來刺耳的金屬碰撞聲，視線一陣模糊。當你再次睜開眼時，映入眼簾的，不再是熟悉的世界。"
    "天空被巨大的黑色棋盤切割成無數方格。高樓之間懸掛著發光的棋子旗幟。街道中央矗立著數十公尺高的「將」字雕像。"
    "而每一個路過的人，胸口都佩戴著不同的棋子徽章。這裡的人，會依照棋子的等級決定身份。"
    "在這個世界裡。棋子，不只是遊戲。而是力量、地位、金錢，甚至生死的象徵。人們稱這座城市為——「棋權之城」。"
    "你緩緩從巷口站起。這世界雖然崇拜棋子，卻沒有人真正理解「中國象棋」。沒有人知道完整規則。沒有人懂真正的棋路。"
    "就在此時，你的腦海忽然閃過一道畫面。漆黑空間中，一張古老棋盤緩緩浮現。無數棋譜如洪流般灌入你的意識。"
    "你猛然瞪大雙眼。你記得。你竟然記得真正的中國象棋規則。"
    "雨水滴落。你沿著老舊街區前進，忽然，前方傳來騷動聲。「滾開！沒錢還敢進公園？」"
    "人群中央，一名身材壯碩的男人正踩在石桌上狂笑。他是這一帶臭名昭彰的地痞——「街頭棋霸」。"
    "石桌上擺著一張破舊棋盤。而棋局……根本亂七八糟。車在斜著跑。馬像炮一樣亂跳。"
    "街頭棋霸抓起棋子狠狠砸下。「哈哈哈！看到了沒？老子這招叫『霸王衝陣』！」"
    "你緩緩走出人群。語氣平靜。「那不是象棋。」"
    "你一步步走向棋盤。腦海中，那道古老聲音再次響起。「執棋者啊——請讓世界重新想起真正的棋道。」"
    "你抬起頭，直視街頭棋霸。「我來教你。真正的象棋，該怎麼下。」"
    
    $ game_mode = "story"
    $ ai_difficulty = "story_easy"
    $ current_board_img = "images/board_bg-1.png" 
    $ current_board_zoom = 1.66 
    $ enemy_skills = [] 
    $ reset_board("normal")
    scene bg room 
    jump init_game_match

label chapter_2_story:
    scene bg black_market 
    "第二章：黑市棋館"
    "夜幕低垂。離開公園後，街頭棋霸被擊敗的消息，像野火般迅速在舊城區蔓延開來。"
    "而這些流言，也替你引來了新的去處。——地下棋館。"
    "推開門的瞬間，震耳欲聾的聲浪迎面襲來。昏暗的大廳中央擺滿數十張棋桌，四周圍滿觀戰群眾。"
    "但最讓你皺眉的，是那些「不正常」的棋局。有人的馬能連跳兩次。有人的炮能穿透兩枚棋子。"
    "就在這時，一道尖銳笑聲從人群中央傳來。「新人？」"
    "地下棋館排行榜第七名——「千術棋士」。"
    "千術棋士輕輕將一枚兵放到棋盤上，露出陰冷笑容。「小鬼，你應該還不知道吧？在黑市棋館裡……棋子，是能『進化』的。」"
    "啪。他猛然敲下棋盤。那枚「兵」的底座竟亮起淡紅色光芒。下一秒，兵的位置詭異地向斜前方移動了一格。"
    "「這招『斜步突刺』——能夠讓我的小兵突破原本限制，進行斜向突擊！」"
    "【系統提示：對手已裝備技能：斜步突刺。警告：您的防線正面臨威脅。】"
    "千術棋士靠上椅背，露出自信笑容。「讓我看看……你到底是真正的棋士，還只是運氣好的普通人？」"
    
    $ game_mode = "story"
    $ ai_difficulty = "story_hard"
    $ current_board_img = "images/board_bg-2.png"
    $ current_board_zoom = 1.1 
    $ enemy_skills = ["diagonal_pawn"] 
    $ reset_board("normal")
    scene bg room 
    jump init_game_match

label chapter_3_story:
    scene bg mechanical 
    "第三章：深藍核心"
    "黑市棋館最深處，存在一扇從不對外開放的鐵門。映入眼簾的，是一座龐大的地下研究室。"
    "牆壁中央，更懸浮著一顆散發深藍光芒的巨大核心裝置。——「深藍核心」。"
    "【警告。偵測到「傳統棋路」使用者。高效率攔截協議開始執行。】"
    "一名身穿白色長袍的男子從高台緩緩走下。地下棋館真正的支配者——「機械博士」。"
    "「哈哈哈哈……終於。我終於研究成功了！」他猛地按下控制台。一枚漆黑金屬棋子出現在聚光燈下。那是一匹「馬」。"
    "「傳統象棋最大的缺陷，就是規則太死板！我打造出了真正完美的棋子！無影馬！」"
    "機械博士張狂大笑。「只要完成所有棋子的機械化——我就能重新定義整個世界的規則！」"
    "你看著那些被扭曲改造的棋子，胸口逐漸沉重。你緩緩向前一步。「我不會讓你繼續下去。」"
    "機械博士露出猙獰笑容。「阻止我？就憑你那過時的棋路？」"
    "【系統提示：對手已裝備特殊棋子：無影馬。警告：您的後排防線遭高度威脅】"
    "你死死盯著那枚正在低鳴震動的機械馬。你知道，真正危險的，是眼前這個已經徹底瘋狂的人。"
    
    $ game_mode = "story"
    $ ai_difficulty = "story_insane" 
    $ current_board_img = "images/board_bg-3.png" 
    $ current_board_zoom = 1.67
    $ enemy_skills = ["no_leg_block"] 
    $ reset_board("normal")
    scene bg room 
    jump init_game_match

label chapter_4_story:
    scene bg god 
    "最終章：天元之局"
    "天空，裂開了。無數黑白棋線橫跨整個世界，大地開始像棋盤般崩裂重組。"
    "整個世界——正在化為一盤棋。"
    "因為在雲層最深處。有一雙眼睛，正在俯視眾生。那是這個世界真正的支配者：【神】。"
    "轟！！！一道金色光柱從天而降。你站在一座無邊無際的巨大棋盤中央。"
    "神低頭俯視著你。「凡人——你看起來，並不屬於這個世界。居然妄想以一己之力，動搖這片大地？」"
    "你握緊手中的「將」。一步一步向前。「象棋……是前人用無數歲月累積出的智慧。」"
    "「砲中砲。釣魚馬。馬後炮。雙車錯。悶宮。鐵門閂……既然只有我還記得真正的中國象棋——那麼我就有責任，把這份智慧傳承下去！」"
    "神忽然大笑。「太可笑了！規則？智慧？不過是我隨手便能改寫的遊戲罷了！」"
    "轟——！！神猛然抬手。「不只是棋子。就連你們人類——也不過是我手上的棋子！」"
    "你卻慢慢笑了。你將手中的棋子，輕輕放在棋盤上。「我知道。人生，確實像一盤棋。但是——真正執棋的人，從來都是自己。」"
    "轟！！！一道耀眼金光瞬間從你腳下爆發。真正的中國象棋棋魂，第一次完整降臨於這個世界！"
    "神的目光出現波動。「有趣。那就讓我看看——人類的棋道，究竟能走到哪一步吧。」"
    "神抬起右手。霎時間，天地崩裂。"
    "【技能發動——天崩地裂】"
    "轟隆！！！！！！整座棋盤瞬間炸裂。你眼前的棋子化為灰燼。兵消失。士粉碎。象崩裂。"
    "空蕩蕩的棋盤上。只剩下孤零零的一枚——帥獨守九宮。"
    "神的聲音落下。「失去一切的你——還能如何翻盤？」"
    "狂風呼嘯。殘破棋盤上，你獨自站立。你忽然笑了。"
    "「戰鬥開始。」"
    
    $ game_mode = "story"
    $ ai_difficulty = "god" 
    $ current_chapter = 4
    $ current_board_img = "images/board_bg-4.png"
    $ current_board_zoom = 1.0
    $ enemy_skills = [] 
    $ reset_board("god")
    scene bg room 
    jump init_game_match

# ==============================================================================
# 9. 對局初始化與迴圈 
# ==============================================================================
label init_game_match:
    $ current_turn = "紅方"
    $ selected_pos = None
    $ move_history = []
    $ state_history = [str(board)]
    $ last_move = (-1, -1)
    $ last_capture_pos = None
    $ check_status = ""
    $ check_target_pos = None
    $ refresh_check_status()
    show screen chessboard
    jump game_loop

label game_loop:
    # --- A. 電腦 AI 回合 ---
    if game_mode != "PvP" and current_turn == "黑方":
        $ renpy.pause(0.5, hard=True)
        python:
            ai_move = get_ai_move(board, ai_difficulty)
            if ai_move:
                asx, asy, acx, acy = ai_move
                captured_piece = board[acy][acx]
                move_history.append(([row[:] for row in board], current_turn))
                
                if captured_piece != 0: renpy.sound.play("images/eat.mp3")
                else: renpy.sound.play("images/move.wav")
                
                board[acy][acx] = board[asy][asx]
                board[asy][asx] = 0
                last_move = (acx, acy)
                last_capture_pos = (acx, acy) if captured_piece != 0 else None
                refresh_check_status()
                renpy.restart_interaction()
                
                current_state_str = str(board)
                state_history.append(current_state_str)
                
                if state_history.count(current_state_str) >= 3:
                    renpy.say(None, "【和局】雙方陷入三次重複局面！")
                    renpy.jump("draw_scene")
                if captured_piece == 1:
                    renpy.say(None, "【致命一擊】紅方主帥遭到擊破！")
                    renpy.jump("game_over_lose")
                    
                current_turn = "紅方"
            else:
                renpy.say(None, "【將死】黑方無子可動，大獲全勝！")
                renpy.jump("win_scene")

    # --- B. 玩家互動 ---
    $ click_pos = ui.interact()
    
    if click_pos == "undo":
        if game_mode == "PvP":
            python:
                if len(move_history) > 0:
                    last_record = move_history.pop()
                    board = last_record[0]
                    current_turn = last_record[1]
                    state_history.pop()
                    refresh_check_status()
            $ selected_pos = None
            $ last_capture_pos = None
            jump game_loop
        else:
            if player_money >= 600:
                $ player_money -= 600
                "支付 600 元啟動逆轉時空！"
                python:
                    if len(move_history) >= 2:
                        move_history.pop()
                        last_record = move_history.pop()
                        board = last_record[0]
                        current_turn = last_record[1]
                        state_history.pop()
                        state_history.pop()
                        refresh_check_status()
                    elif len(move_history) == 1:
                        last_record = move_history.pop()
                        board = last_record[0]
                        current_turn = last_record[1]
                        state_history.pop()
                        refresh_check_status()
                $ selected_pos = None
                $ last_capture_pos = None
                jump game_loop
            else:
                "資金不足 600 元，無法悔棋！"
                jump game_loop
                
    python:
        if isinstance(click_pos, tuple):
            cx, cy = click_pos
            if selected_pos is None:
                p = board[cy][cx]
                if p != 0 and ((current_turn == "紅方" and p > 0) or (current_turn == "黑方" and p < 0)):
                    selected_pos = click_pos
            else:
                sx, sy = selected_pos
                if is_valid_move(board, sx, sy, cx, cy):
                    captured_piece = board[cy][cx]
                    move_history.append(([row[:] for row in board], current_turn))
                    
                    if captured_piece != 0: renpy.sound.play("images/eat.mp3")
                    else: renpy.sound.play("images/move.wav")
                    
                    board[cy][cx] = board[sy][sx]
                    board[sy][sx] = 0
                    last_move = (cx, cy)
                    last_capture_pos = (cx, cy) if captured_piece != 0 else None
                    selected_pos = None
                    refresh_check_status()
                    renpy.restart_interaction()
                    
                    current_state_str = str(board)
                    state_history.append(current_state_str)
                    
                    if state_history.count(current_state_str) >= 3:
                        renpy.say(None, "【和局】雙方陷入三次重複局面！")
                        renpy.jump("draw_scene")
                    if captured_piece == -1:
                        renpy.say(None, "【將死】黑方將領遭到擊破！")
                        renpy.jump("win_scene")
                    elif captured_piece == 1: 
                        renpy.say(None, "【失誤】你不小心犧牲了主帥！")
                        renpy.jump("game_over_lose")
                    else:
                        current_turn = "黑方" if game_mode != "PvP" else ("黑方" if current_turn == "紅方" else "紅方")
                else:
                    selected_pos = None
    jump game_loop

# ==============================================================================
# 10. 結局標籤
# ==============================================================================
label draw_scene:
    hide screen chessboard
    stop music fadeout 1.0
    $ export_match_data("Draw") 
    jump game_over

label win_scene:
    hide screen chessboard
    stop music fadeout 1.0
    play sound "images/win.mp3"
    $ export_match_data("Player") 
    
    "【結算報告：大獲全勝】"
    python:
        if ai_difficulty == "god": prize = 10000
        elif ai_difficulty == "hell": prize = 2000
        elif ai_difficulty == "hard": prize = 500
        elif ai_difficulty == "story_insane": prize = 1000
        elif ai_difficulty in ["story_easy", "story_hard"]: prize = 300
        else: prize = 100
            
        player_money += prize
        player_exp += 50
        
        if game_mode == "story":
            if ai_difficulty == "story_easy" and current_chapter == 1: current_chapter = 2
            elif ai_difficulty == "story_hard" and current_chapter == 2: current_chapter = 3
            elif ai_difficulty == "story_insane" and current_chapter == 3: current_chapter = 4
        
    "你贏得了 [prize] 元，獲得 50 點經驗值！"
    if player_exp >= 100:
        $ player_lv += 1
        $ player_exp -= 100
        "恭喜！角色等級提升至 Lv.[player_lv]！"
        
    if game_mode == "story" and current_chapter <= 4:
        "要直接進入下一章嗎？"
        menu:
            "繼續挑戰下一章":
                jump story_mode_hub
            "返回主城大廳休息":
                jump main_hub
    else:
        jump game_over

label game_over_lose:
    hide screen chessboard
    stop music fadeout 1.0
    play sound "images/lose.mp3"
    $ export_match_data("AI") 
    
    "【結算報告：棋力崩潰】"
    jump game_over

label game_over:
    menu:
        "點擊返回主城大廳 (繼續遊玩)": 
            jump main_hub
