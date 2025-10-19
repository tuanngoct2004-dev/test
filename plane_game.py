"""Simple top-down airplane flying game using pygame.

Use the arrow keys or WASD to move the plane and avoid incoming enemies.
Collect fuel pickups to increase score. The game speeds up over time.
"""

from __future__ import annotations

import random
import sys
from dataclasses import dataclass
from typing import Tuple

import pygame

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Gameplay constants
PLAYER_SPEED = 6
ENEMY_MIN_SPEED = 3
ENEMY_MAX_SPEED = 7
FUEL_MIN_SPEED = 2
FUEL_MAX_SPEED = 5
SPAWN_EVENT = pygame.USEREVENT + 1
SPAWN_INTERVAL = 900  # milliseconds
LEVEL_UP_EVENT = pygame.USEREVENT + 2
LEVEL_UP_INTERVAL = 8000
MAX_ENEMIES = 6

# Colours
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (25, 30, 55)
YELLOW = (255, 215, 0)
RED = (231, 76, 60)


@dataclass
class GameObject(pygame.sprite.Sprite):
    """Base sprite with convenience helpers."""

    color: Tuple[int, int, int]
    size: Tuple[int, int]
    speed: pygame.math.Vector2

    def __post_init__(self) -> None:
        super().__init__()
        self.image = pygame.Surface(self.size)
        self.image.fill(self.color)
        self.rect = self.image.get_rect()

    def update(self) -> None:  # pragma: no cover - pygame update loop
        self.rect.move_ip(self.speed)

        # Remove sprite when it goes off-screen
        if self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:
            self.kill()


class Player(GameObject):
    def __init__(self) -> None:
        super().__init__(color=WHITE, size=(48, 48), speed=pygame.math.Vector2(0, 0))
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80)

    def update(self) -> None:  # pragma: no cover - pygame update loop
        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize() * PLAYER_SPEED

        self.rect.move_ip(direction.x, direction.y)

        # Keep the player on screen
        self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))


class Enemy(GameObject):
    def __init__(self) -> None:
        speed = pygame.math.Vector2(0, random.randint(ENEMY_MIN_SPEED, ENEMY_MAX_SPEED))
        super().__init__(color=RED, size=(40, 60), speed=speed)
        self.rect.midbottom = (random.randint(40, SCREEN_WIDTH - 40), -10)


class Fuel(GameObject):
    def __init__(self) -> None:
        speed = pygame.math.Vector2(0, random.randint(FUEL_MIN_SPEED, FUEL_MAX_SPEED))
        super().__init__(color=YELLOW, size=(28, 28), speed=speed)
        self.rect.midbottom = (random.randint(20, SCREEN_WIDTH - 20), -10)


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption("Sky Runner")
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 24)

        self.all_sprites = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.fuel_items = pygame.sprite.Group()

        self.player = Player()
        self.all_sprites.add(self.player)

        self.score = 0
        self.running = True
        self.difficulty_multiplier = 1.0

        pygame.time.set_timer(SPAWN_EVENT, SPAWN_INTERVAL)
        pygame.time.set_timer(LEVEL_UP_EVENT, LEVEL_UP_INTERVAL)

    def spawn_enemy(self) -> None:
        if len(self.enemies) < MAX_ENEMIES:
            enemy = Enemy()
            enemy.speed.y *= self.difficulty_multiplier
            self.enemies.add(enemy)
            self.all_sprites.add(enemy)

    def spawn_fuel(self) -> None:
        fuel = Fuel()
        fuel.speed.y *= self.difficulty_multiplier
        self.fuel_items.add(fuel)
        self.all_sprites.add(fuel)

    def draw_background(self) -> None:
        self.screen.fill(SKY_BLUE)
        # Draw a simple horizon line and stars
        pygame.draw.rect(self.screen, BLACK, (0, SCREEN_HEIGHT - 120, SCREEN_WIDTH, 120))
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT // 2)
            self.screen.set_at((x, y), WHITE)

    def draw_ui(self) -> None:
        score_text = self.font.render(f"Điểm: {self.score}", True, WHITE)
        self.screen.blit(score_text, (20, 20))
        info_text = self.font.render("Di chuyển bằng phím mũi tên hoặc WASD", True, WHITE)
        self.screen.blit(info_text, (20, 50))

    def handle_collisions(self) -> None:
        if pygame.sprite.spritecollideany(self.player, self.enemies):
            self.running = False

        fuel_collisions = pygame.sprite.spritecollide(self.player, self.fuel_items, dokill=True)
        if fuel_collisions:
            self.score += 10 * len(fuel_collisions)

    def increase_difficulty(self) -> None:
        self.difficulty_multiplier = min(self.difficulty_multiplier + 0.15, 3.5)

    def game_over(self) -> None:
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        title = self.font.render("Hết năng lượng! Nhấn Enter để chơi lại hoặc Esc để thoát.", True, WHITE)
        score_text = self.font.render(f"Tổng điểm: {self.score}", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)))
        self.screen.blit(score_text, score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20)))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        waiting = False
                        self.reset()
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
            self.clock.tick(30)

    def reset(self) -> None:
        self.score = 0
        self.difficulty_multiplier = 1.0
        self.all_sprites.empty()
        self.enemies.empty()
        self.fuel_items.empty()
        self.player = Player()
        self.all_sprites.add(self.player)

    def run(self) -> None:  # pragma: no cover - interactive loop
        while True:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == SPAWN_EVENT:
                    self.spawn_enemy()
                    if random.random() < 0.4:
                        self.spawn_fuel()
                if event.type == LEVEL_UP_EVENT:
                    self.increase_difficulty()

            if self.running:
                self.all_sprites.update()
                self.handle_collisions()

                # Increment score slowly for survival
                self.score += 1

                self.draw_background()
                self.all_sprites.draw(self.screen)
                self.draw_ui()
            else:
                self.game_over()

            pygame.display.flip()


def main() -> None:
    Game().run()


if __name__ == "__main__":
    main()
