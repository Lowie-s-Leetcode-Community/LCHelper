from PIL import Image, ImageDraw, ImageFont

width = 800
height = 800

img = Image.new(mode = "RGB", size = (width, height), color = (255, 255, 255))
# img.show()

draw = ImageDraw.Draw(img)
text_color = (7, 85, 186)

# show:
# daily_task(finished_daily, total-score-excluding-daily, easy, medium, hard, gacha)
# all-time(max_daily_streak, current_streak, max_score)
# current_month(max_daily_streak, current_streak, score)
# previous_month(max_daily_streak, current_streak, score)

username = "Lowie Leetcode Community"
username_pos = (50, 40)
font_username = ImageFont.truetype(font = "fonts/comic.ttf", size = 50)

draw.text(username_pos, username, fill = text_color, font = font_username)

status = {
    "current_month": {
        "max_daily_streak": 0,
        "current_daily_streak": 0,
        "score": 0
    },
    "previous_month": {
        "max_daily_streak": 0,
        "current_daily_streak": 0,
        "score": 1
    },
    "all_time": {
        "max_daily_streak": 2,
        "current_daily_streak": 0,
        "score": 17
    },
    "daily_task": {
        "finished_today_daily": False,
        "scores_earned_excluding_daily": 0,
        "easy_solved": 0,
        "medium_solved": 0,
        "hard_solved": 0,
        "gacha": False
    }
}
font_large = ImageFont.truetype(font = "fonts/comic.ttf", size = 35)
font_medium = ImageFont.truetype(font = "fonts/comic.ttf", size = 25)

daily_task = "daily_task"


col = ["", "current_month", "previous_month", "all_time"]
col_alternate = ["", "this month", "last month", "all time"]
row = ["", "max_daily_streak", "current_daily_streak", "score"]
row_alternate = ["", "max daily streak", "current daily streak", "score"]
board_pos_row = [50, 200, 420, 680, 730]
board_pos_col = [300]
for i in range(3):
    board_pos_col.append(board_pos_col[-1] + 50)

for i in range(4):
    for j in range(4):
        if i == 0:
            temp_pos = (board_pos_row[j], board_pos_col[i])
            draw.text(temp_pos, row_alternate[j], fill = text_color, font = font_medium)
        elif j == 0:
            temp_pos = (board_pos_row[j], board_pos_col[i])
            draw.text(temp_pos, col_alternate[i], fill = text_color, font = font_medium)
        else :
            temp_pos = (board_pos_row[j] + (board_pos_row[j + 1] - board_pos_row[j]) / 2,
                board_pos_col[i])
            draw.text(temp_pos, str(status[col[i]][row[j]]), fill = text_color, font = font_medium)

for i in range(3):
    line = [(board_pos_row[i + 1] - 10, board_pos_col[0]),
        (board_pos_row[i + 1] - 10), board_pos_col[-1] + 35]
    draw.line(line, fill = text_color, width = 1)

img.show()