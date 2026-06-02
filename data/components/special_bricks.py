"""
特殊地图元素 - 增加游戏的互动性和策略性
包括传送门、弹跳板、陷阱地板、加速带等
"""
import pygame as pg
from pygame.sprite import Sprite
from .. import constants as c
from .. import tools as t
import random

class SpecialBrick(Sprite):
    """特殊砖块基类"""
    def __init__(self, x, y, kind):
        super().__init__()
        self.x = x
        self.y = y
        self.kind = kind
        self.rect = pg.Rect((x, y), c.BRICK_SIZE)
        self.HP = 10000
        self.activation_cooldown = 0
    
    def ActOnCharacter(self, character, current_time):
        """对角色产生影响"""
        pass
    
    def update(self, current_time):
        """更新状态"""
        pass


class Portal(SpecialBrick):
    """传送门 - 站在上面会被传送到另一个传送门"""
    def __init__(self, x, y, portal_id=0):
        super().__init__(x, y, 'portal')
        self.portal_id = portal_id
        self.linked_portal = None  # 关联的目标传送门
        self.cooldown = 1000  # 1秒冷却
        self.last_use_time = 0
        self.color = (100, 200, 255) if portal_id == 0 else (255, 100, 200)
        
        # 创建传送门视觉效果
        self.image = self._create_portal_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_portal_image(self):
        """创建传送门视觉效果"""
        size = (c.BRICK_WIDTH * 2, c.BRICK_HEIGHT * 2)
        image = pg.Surface(size, pg.SRCALPHA)
        # 绘制漩涡效果
        center = (size[0] // 2, size[1] // 2)
        for i in range(5):
            radius = size[0] // 2 - i * 4
            alpha = 200 - i * 30
            color = (*self.color[:3], alpha)
            pg.draw.circle(image, color, center, radius, 2)
        return image
    
    def ActOnCharacter(self, character, current_time):
        """传送角色"""
        if self.linked_portal and current_time - self.last_use_time > self.cooldown:
            if character.state != c.FREEZING:
                # 传送到关联传送门
                character.rect.centerx = self.linked_portal.rect.centerx
                character.rect.bottom = self.linked_portal.rect.top
                self.last_use_time = current_time
                self.linked_portal.last_use_time = current_time
                # 添加传送冷却状态
                character.portal_cooldown = current_time + self.cooldown


class JumpPad(SpecialBrick):
    """弹跳板 - 站在上面会被弹飞"""
    def __init__(self, x, y, jump_power=20):
        super().__init__(x, y, 'jump_pad')
        self.jump_power = jump_power
        self.cooldown = 500
        self.last_use_time = 0
        
        # 创建弹跳板视觉效果
        self.image = self._create_jump_pad_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_jump_pad_image(self):
        """创建弹跳板视觉效果"""
        size = (c.BRICK_WIDTH * 2, c.BRICK_HEIGHT)
        image = pg.Surface(size)
        # 黄色弹簧效果
        image.fill((255, 200, 50))
        # 绘制弹簧线条
        for i in range(4):
            y = i * 6 + 3
            pg.draw.line(image, (200, 150, 30), (5, y), (size[0] - 5, y), 2)
        return image
    
    def ActOnCharacter(self, character, current_time):
        """弹飞角色"""
        if current_time - self.last_use_time > self.cooldown:
            if character.state in [c.STANDING, c.WALKING]:
                character.y_vel = -self.jump_power
                character.state = c.JUMPING
                character.allow_jump = False
                self.last_use_time = current_time


class TrapFloor(SpecialBrick):
    """陷阱地板 - 站在上面会持续受到伤害"""
    def __init__(self, x, y, damage=5, interval=500):
        super().__init__(x, y, 'trap_floor')
        self.damage = damage
        self.damage_interval = interval  # 每interval毫秒造成伤害
        self.last_damage_time = 0
        
        # 创建陷阱地板视觉效果
        self.image = self._create_trap_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_trap_image(self):
        """创建陷阱视觉效果"""
        size = c.BRICK_SIZE
        image = pg.Surface(size)
        # 红色尖刺效果
        image.fill((80, 80, 80))
        # 绘制尖刺
        spike_count = 3
        for i in range(spike_count):
            x_start = i * (size[0] // spike_count) + 2
            x_end = (i + 1) * (size[0] // spike_count) - 2
            pg.draw.polygon(image, (255, 50, 50), [
                (x_start, size[1]),
                (x_start + (x_end - x_start) // 2, 5),
                (x_end, size[1])
            ])
        return image
    
    def ActOnCharacter(self, character, current_time):
        """造成伤害"""
        if current_time - self.last_damage_time > self.damage_interval:
            if character.vincible:
                character.HP -= self.damage
                self.last_damage_time = current_time


class SpeedBoost(SpecialBrick):
    """加速带 - 经过时获得短暂加速"""
    def __init__(self, x, y, boost_factor=2, duration=2000):
        super().__init__(x, y, 'speed_boost')
        self.boost_factor = boost_factor
        self.duration = duration
        
        # 创建加速带视觉效果
        self.image = self._create_speed_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_speed_image(self):
        """创建加速带视觉效果"""
        size = (c.BRICK_WIDTH * 2, c.BRICK_HEIGHT)
        image = pg.Surface(size)
        # 绿色箭头效果
        image.fill((50, 150, 50))
        # 绘制箭头
        arrow_points = [
            (size[0] // 4, size[1] // 2),
            (size[0] * 3 // 4, size[1] // 4),
            (size[0] * 3 // 4, size[1] // 2),
            (size[0] - 5, size[1] // 2),
            (size[0] * 3 // 4, size[1] * 3 // 4),
            (size[0] * 3 // 4, size[1] // 2),
        ]
        pg.draw.lines(image, (255, 255, 255), False, arrow_points, 3)
        return image
    
    def ActOnCharacter(self, character, current_time):
        """给予加速效果"""
        if character.state in [c.STANDING, c.WALKING, c.FALLING]:
            character.max_x_vel = c.MAX_X_VEL * self.boost_factor
            character.acctime = self.duration // 16  # 转换为帧数


class HealingZone(SpecialBrick):
    """治疗区域 - 站在上面持续恢复HP"""
    def __init__(self, x, y, heal_amount=3, interval=500):
        super().__init__(x, y, 'healing_zone')
        self.heal_amount = heal_amount
        self.heal_interval = interval
        self.last_heal_time = 0
        
        # 创建治疗区域视觉效果
        self.image = self._create_healing_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_healing_image(self):
        """创建治疗区域视觉效果"""
        size = (c.BRICK_WIDTH * 2, c.BRICK_HEIGHT)
        image = pg.Surface(size, pg.SRCALPHA)
        # 绿色半透明效果
        image.fill((100, 255, 100, 150))
        # 绘制十字
        center = (size[0] // 2, size[1] // 2)
        pg.draw.line(image, (255, 255, 255), (center[0] - 8, center[1]), (center[0] + 8, center[1]), 3)
        pg.draw.line(image, (255, 255, 255), (center[0], center[1] - 8), (center[0], center[1] + 8), 3)
        return image
    
    def ActOnCharacter(self, character, current_time):
        """恢复HP"""
        if current_time - self.last_heal_time > self.heal_interval:
            if character.HP < character.max_HP:
                character.HP = min(character.max_HP, character.HP + self.heal_amount)
                self.last_heal_time = current_time


class IceFloor(SpecialBrick):
    """冰面 - 经过时滑行，难以控制方向"""
    def __init__(self, x, y):
        super().__init__(x, y, 'ice_floor')
        self.friction_reduction = 0.3  # 摩擦力降低
        
        # 创建冰面视觉效果
        self.image = self._create_ice_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_ice_image(self):
        """创建冰面视觉效果"""
        size = c.BRICK_SIZE
        image = pg.Surface(size, pg.SRCALPHA)
        # 浅蓝色半透明冰效果
        image.fill((200, 230, 255, 200))
        # 添加冰晶纹理
        for i in range(3):
            pg.draw.line(image, (150, 200, 255), 
                        (random.randint(0, size[0]), random.randint(0, size[1])),
                        (random.randint(0, size[0]), random.randint(0, size[1])), 1)
        return image
    
    def ActOnCharacter(self, character, current_time):
        """降低角色控制力"""
        if character.state == c.WALKING:
            # 冰面上移动时保持惯性
            if character.x_vel != 0:
                character.ice_sliding = True


class MovingPlatform(SpecialBrick):
    """移动平台 - 自动左右移动的平台"""
    def __init__(self, x, y, move_range=100, speed=2):
        super().__init__(x, y, 'moving_platform')
        self.original_x = x
        self.move_range = move_range
        self.speed = speed
        self.direction = 1  # 1向右，-1向左
        
        # 创建移动平台视觉效果
        self.image = self._create_platform_image()
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y
    
    def _create_platform_image(self):
        """创建平台视觉效果"""
        size = (c.BRICK_WIDTH * 3, c.BRICK_HEIGHT)
        image = pg.Surface(size)
        # 金色金属效果
        image.fill((180, 150, 50))
        pg.draw.rect(image, (200, 170, 60), (0, 0, size[0], 5))
        return image
    
    def update(self, current_time):
        """更新平台位置"""
        self.rect.x += self.speed * self.direction
        
        # 到达边界时反向
        if self.rect.x >= self.original_x + self.move_range:
            self.direction = -1
        elif self.rect.x <= self.original_x - self.move_range:
            self.direction = 1
    
    def ActOnCharacter(self, character, current_time):
        """角色站在平台上时跟随移动"""
        if character.state == c.WALKING:
            character.rect.x += self.speed * self.direction


# 特殊砖块类型映射
SPECIAL_BRICK_TYPES = {
    'portal': Portal,
    'jump_pad': JumpPad,
    'trap_floor': TrapFloor,
    'speed_boost': SpeedBoost,
    'healing_zone': HealingZone,
    'ice_floor': IceFloor,
    'moving_platform': MovingPlatform,
}


def create_special_brick(x, y, kind, **kwargs):
    """创建特殊砖块"""
    brick_class = SPECIAL_BRICK_TYPES.get(kind)
    if brick_class:
        return brick_class(x, y, **kwargs)
    return None