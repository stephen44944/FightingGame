"""
被动技能系统 - 每个角色独特的被动能力
增加游戏的策略深度和角色差异化
"""
import pygame as pg
from pygame.sprite import Sprite
from .. import constants as c
import random

class PassiveSkill:
    """被动技能基类"""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.owner = None
    
    def attach(self, character):
        """绑定到角色"""
        self.owner = character
    
    def on_damage_dealt(self, target, damage):
        """造成伤害时触发"""
        return damage
    
    def on_damage_received(self, attacker, damage):
        """受到伤害时触发"""
        return damage
    
    def on_kill(self, target):
        """击杀敌人时触发"""
        pass
    
    def on_update(self):
        """每帧更新"""
        pass
    
    def on_skill_use(self):
        """使用技能时触发"""
        pass
    
    def on_action_use(self):
        """使用普通攻击时触发"""
        pass


class BerserkerHeart(PassiveSkill):
    """狂暴之心 - Darling专属"""
    def __init__(self):
        super().__init__("狂暴之心", "HP低于30%时，攻击伤害提升50%")
        self.threshold = 0.3
    
    def on_damage_dealt(self, target, damage):
        if self.owner and self.owner.HP < self.owner.max_HP * self.threshold:
            return int(damage * 1.5)
        return damage


class WarGod(PassiveSkill):
    """武圣 - 关羽专属"""
    def __init__(self):
        super().__init__("武圣", "击杀敌人回复15%最大HP")
        self.heal_percent = 0.15
    
    def on_kill(self, target):
        if self.owner:
            heal_amount = int(self.owner.max_HP * self.heal_percent)
            self.owner.HP = min(self.owner.max_HP, self.owner.HP + heal_amount)


class DodgeMaster(PassiveSkill):
    """闪避大师 - K专属"""
    def __init__(self):
        super().__init__("闪避大师", "有20%概率完全闪避攻击")
        self.dodge_chance = 0.2
    
    def on_damage_received(self, attacker, damage):
        if random.random() < self.dodge_chance:
            return 0  # 完全闪避
        return damage


class EagleEye(PassiveSkill):
    """鹰眼 - 弓箭手专属"""
    def __init__(self):
        super().__init__("鹰眼", "远程攻击伤害提升30%")
        self.range_bonus = 0.3
    
    def on_damage_dealt(self, target, damage):
        # 弓箭手的子弹攻击视为远程
        return int(damage * (1 + self.range_bonus))


class SpiderWeb(PassiveSkill):
    """蛛网 - 蜘蛛王子专属"""
    def __init__(self):
        super().__init__("蛛网", "攻击敌人时使其减速2秒")
        self.slow_duration = 2000  # 毫秒
    
    def on_damage_dealt(self, target, damage):
        if hasattr(target, 'apply_slow'):
            target.apply_slow(self.slow_duration)
        return damage


class Shadow(PassiveSkill):
    """暗影 - Poena专属"""
    def __init__(self):
        super().__init__("暗影", "受伤后短暂隐身1.5秒，期间无敌")
        self.invisible_duration = 1500  # 毫秒
        self.last_trigger_time = 0
        self.cooldown = 5000  # 5秒冷却
    
    def on_damage_received(self, attacker, damage):
        current_time = getattr(self.owner, 'current_time', 0)
        if current_time - self.last_trigger_time > self.cooldown:
            if damage > 0:  # 确实受到了伤害
                self.owner.invisible_time = current_time + self.invisible_duration
                self.owner.vincible = False
                self.last_trigger_time = current_time
        return damage
    
    def on_update(self):
        if self.owner and hasattr(self.owner, 'invisible_time'):
            current_time = getattr(self.owner, 'current_time', 0)
            if self.owner.invisible_time and current_time > self.owner.invisible_time:
                self.owner.vincible = True
                self.owner.invisible_time = 0


class SpiritBody(PassiveSkill):
    """灵体 - Ghost专属"""
    def __init__(self):
        super().__init__("灵体", "可以穿过玻璃类障碍物，受到的伤害减少10%")
    
    def on_damage_received(self, attacker, damage):
        return int(damage * 0.9)


class Frost(PassiveSkill):
    """冰霜 - Iccy专属"""
    def __init__(self):
        super().__init__("冰霜", "攻击有15%概率冻结敌人1秒")
        self.freeze_chance = 0.15
        self.freeze_duration = 1000
    
    def on_damage_dealt(self, target, damage):
        if random.random() < self.freeze_chance:
            if hasattr(target, 'apply_freeze'):
                target.apply_freeze(self.freeze_duration)
        return damage


# 角色被动技能映射
CHARACTER_PASSIVE_SKILLS = {
    c.DARLING: BerserkerHeart,
    c.GUAN_GONG: WarGod,
    c.K: DodgeMaster,
    c.ARCHER: EagleEye,
    c.SPIDER_PRINCE: SpiderWeb,
    c.POENA: Shadow,
    c.GHOST: SpiritBody,
    c.ICCY: Frost,
}


def get_passive_skill(character_name):
    """获取角色的被动技能实例"""
    skill_class = CHARACTER_PASSIVE_SKILLS.get(character_name)
    if skill_class:
        return skill_class()
    return None