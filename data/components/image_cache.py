"""
图片缓存系统 - 解决游戏性能问题
每帧重复加载图片是性能瓶颈，使用缓存可以大幅提升流畅度
"""
import pygame as pg
from pygame.sprite import Sprite

class ImageCache:
    """全局图片缓存，避免重复加载"""
    _cache = {}
    
    @classmethod
    def get_image(cls, path, size=None, flip=False):
        """
        获取缓存图片，如果不存在则加载并缓存
        
        Args:
            path: 图片路径
            size: 缩放尺寸 (width, height)
            flip: 是否水平翻转
        
        Returns:
            pygame.Surface: 图片对象
        """
        # 创建缓存键
        cache_key = (path, size, flip)
        
        if cache_key not in cls._cache:
            try:
                image = pg.image.load(path).convert()
                if size:
                    image = pg.transform.scale(image, size)
                if flip:
                    image = pg.transform.flip(image, True, False)
                cls._cache[cache_key] = image
            except:
                # 如果加载失败，返回一个占位图片
                placeholder = pg.Surface(size if size else (50, 50))
                placeholder.fill((255, 0, 255))  # 紫色表示错误
                cls._cache[cache_key] = placeholder
        
        return cls._cache[cache_key]
    
    @classmethod
    def preload_character(cls, character_name, size, postfix='gif'):
        """预加载角色所有动画帧"""
        actions = ['stand', 'walk', 'action', 'skill']
        for action in actions:
            # 尝试加载该动作的所有帧
            for i in range(30):  # 最多预加载30帧
                path = f'images/{character_name}/{action}/{i}.{postfix}'
                try:
                    cls.get_image(path, size)
                    cls.get_image(path, size, flip=True)
                except:
                    break  # 没有更多帧了
    
    @classmethod
    def preload_bricks(cls, brick_kinds, brick_size):
        """预加载所有砖块图片"""
        for kind, info in brick_kinds.items():
            base_path = info['name']
            if info['movable']:
                for i in range(info.get('frame', 1)):
                    path = f'{base_path}{i}.png'
                    cls.get_image(path, brick_size)
            else:
                path = f'{base_path}.png'
                cls.get_image(path, brick_size)
    
    @classmethod
    def clear(cls):
        """清空缓存（用于切换场景）"""
        cls._cache.clear()
    
    @classmethod
    def stats(cls):
        """返回缓存统计信息"""
        return f"缓存图片数量: {len(cls._cache)}"