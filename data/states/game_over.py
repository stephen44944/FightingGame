import pygame as pg

from .. import tools, setup
from .. import constants as c


class GameOver(tools._State):
    def __init__(self):
        super(GameOver, self).__init__()

    def startup(self, current_time, persist):
        self.game_info = persist
        self.persist = self.game_info
        self.next = c.CHOOSING

        self.state = c.PLAY

        print(self.game_info)

        self.setup_background()
        #self.setup_cursor()
        self.setup_UI()
        self.setup_poster()

        # For test
        #self.quit = True


    def setup_UI(self):
        self.UI = {c.PLAY: [{'image': pg.transform.scale(pg.image.load('images/UI/once_more.png'), (150, 50))},
                            {'image': pg.transform.scale(pg.image.load('images/UI/once_more.png'), (180, 60))}],
                   c.QUIT: [{'image': pg.transform.scale(pg.image.load('images/UI/exit_game.png'), (150, 50))},
                            {'image': pg.transform.scale(pg.image.load('images/UI/exit_game.png'), (180, 60))}]}
        for state, k in zip(self.UI.keys(), range(0, 2)):
            for i in range(0, 2):
                rect = self.UI[state][i]['image'].get_rect()
                rect.centerx = c.SCREEN_WIDTH // 2
                rect.centery = 430 + 60 * k
                self.UI[state][i]['rect'] = rect
        self.Victory = pg.image.load('images/Victory.png')
        self.Defeated = pg.image.load('images/Defeated.png')


    def setup_background(self):
        self.background = pg.transform.scale(pg.image.load('images/%s' % c.RESULT_SCREEN), c.SCREEN_SIZE)
        self.background_rect = self.background.get_rect()


    def setup_poster(self):
        self.chara_poster = {}
        for character_name in c.CHARACTERS:
            self.chara_poster[character_name] = [
                pg.transform.scale(pg.image.load('images/posters/%s.png' % (character_name)), c.HALF_SCREEN_SIZE),
                pg.transform.flip(pg.transform.scale(pg.image.load('images/posters/%s.png' % (character_name)), c.HALF_SCREEN_SIZE), True, False),
                ]


    def setup_cursor(self):
        pass
        # self.cursor = pg.sprite.Sprite()
        # self.cursor.image = pg.Surface([c.TITLE_CURSOR_WIDTH, c.TITLE_CURSOR_HEIGHT])
        # # self.cursor.image.set_colorkey(c.BLACK)
        # self.cursor.rect = self.cursor.image.get_rect()
        # self.cursor.rect.x = 350
        # self.cursor.rect.y = 400
        # self.cursor.state = c.PLAY


    def update(self, surface, keys, current_time):
        self.current_time = current_time
        self.game_info[c.CURRENT_TIME] = self.current_time
        self.update_cursor(keys)
        self.blit_everything(surface)


    def get_event(self, event):
        # ========== 鼠标点击支持 ==========
        if event.type == pg.MOUSEBUTTONDOWN:
            mouse_pos = pg.mouse.get_pos()
            # 检查是否点击了"再来一局"按钮
            if self.UI[c.PLAY][0]['rect'].collidepoint(mouse_pos):
                self.state = c.PLAY
                self.done = True
            # 检查是否点击了"退出游戏"按钮
            elif self.UI[c.QUIT][0]['rect'].collidepoint(mouse_pos):
                self.state = c.QUIT
                self.quit = True
        
        # ========== 鼠标悬停效果 ==========
        elif event.type == pg.MOUSEMOTION:
            mouse_pos = pg.mouse.get_pos()
            if self.UI[c.PLAY][0]['rect'].collidepoint(mouse_pos):
                self.state = c.PLAY
            elif self.UI[c.QUIT][0]['rect'].collidepoint(mouse_pos):
                self.state = c.QUIT

    def update_cursor(self, keys):
        if self.state == c.PLAY:
            if keys[pg.K_DOWN]:
                self.state = c.QUIT
            if keys[pg.K_RETURN]:
                self.done = True
        elif self.state == c.QUIT:
            if keys[pg.K_UP]:
                self.state = c.PLAY
            if keys[pg.K_RETURN]:
                self.quit = True


    def blit_everything(self, surface):
        surface.blit(self.background, self.background_rect)
        surface.blit(self.chara_poster[self.game_info[c.P1_CHARACTER]][0], pg.Rect((0, 0), c.HALF_SCREEN_SIZE))
        surface.blit(self.chara_poster[self.game_info[c.P2_CHARACTER]][1],
                     pg.Rect((c.SCREEN_WIDTH / 2, 0), c.HALF_SCREEN_SIZE))
        #surface.blit(self.cursor.image, self.cursor.rect)
        for state in self.UI.keys():
            if state == self.state:
                surface.blit(self.UI[state][1]['image'], self.UI[state][1]['rect'])
            else:
                surface.blit(self.UI[state][0]['image'], self.UI[state][0]['rect'])
        
        # ========== 优化胜负显示 ==========
        # 根据HP判断胜负（更直观）
        p1_hp = self.game_info.get(c.P1_HP, 0)
        p2_hp = self.game_info.get(c.P2_HP, 0)
        p1_heart = self.game_info.get(c.P1_HEART, 0)
        p2_heart = self.game_info.get(c.P2_HEART, 0)
        
        # 判断胜负：HP<=0 或 heart<=0 都算输
        p1_lost = (p1_hp <= 0 or p1_heart <= 0)
        p2_lost = (p2_hp <= 0 or p2_heart <= 0)
        
        if p1_lost and not p2_lost:
            # 玩家1输，玩家2赢
            surface.blit(self.Victory, (600, 40))
            surface.blit(self.Defeated, (0, 40))
            self.draw_winner_text(surface, "玩家2 获胜！", c.SCREEN_WIDTH * 3 // 4, 150)
        elif p2_lost and not p1_lost:
            # 玩家2输，玩家1赢
            surface.blit(self.Victory, (0, 40))
            surface.blit(self.Defeated, (600, 40))
            self.draw_winner_text(surface, "玩家1 获胜！", c.SCREEN_WIDTH // 4, 150)
        elif p1_lost and p2_lost:
            # 平局
            self.draw_winner_text(surface, "平局！", c.SCREEN_WIDTH // 2, 150, c.YELLOW)
        else:
            # 默认显示（根据原来的逻辑）
            if self.game_info[c.P1_HEART] == 0:
                surface.blit(self.Victory, (600, 40))
                surface.blit(self.Defeated, (0, 40))
            else:
                surface.blit(self.Victory, (0, 40))
                surface.blit(self.Defeated, (600, 40))
    
    def draw_winner_text(self, surface, text, x, y, color=c.WHITE):
        """绘制获胜文字"""
        font = pg.font.SysFont("simhei", 48)  # 使用黑体
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.centerx = x
        text_rect.centery = y
        # 绘制阴影效果
        shadow_surface = font.render(text, True, c.BLACK)
        shadow_rect = shadow_surface.get_rect()
        shadow_rect.centerx = x + 2
        shadow_rect.centery = y + 2
        surface.blit(shadow_surface, shadow_rect)
        surface.blit(text_surface, text_rect)