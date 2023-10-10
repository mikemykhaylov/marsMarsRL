import pygame


class Player:
    def __init__(self, radius, color, scene_width, scene_height):
        self.scene_width = scene_width
        self.scene_height = scene_height

        self.prev_pos = pygame.Vector2(0, 0)
        self.pos = pygame.Vector2(0, 0)
        self.vel = pygame.Vector2(0, 0)
        self.radius = radius
        self.color = color

        self.terrain = None

        self.jump_cooldown = 0
        self.fuel = 0

        self.ui_padding = 10
        self.fuel_bar_dimensions = (100, 25)
        self.fuel_bar_border = 5
        self.fuel_surface = pygame.Surface((90, 15))

        self.score = 0

    def draw(self, screen):
        self.draw_player(screen)
        self.draw_fuel(screen)
        self.draw_score(screen)

    def draw_player(self, screen):
        pygame.draw.circle(screen, self.color, self.pos, self.radius)

    def draw_fuel(self, screen):
        fuel_bar_pos = (self.scene_width - 100 - self.ui_padding, self.ui_padding)

        pygame.draw.rect(
            screen,
            "white",
            (*fuel_bar_pos, *self.fuel_bar_dimensions),
            self.fuel_bar_border,
        )

        self.fuel_surface.set_alpha(64)
        self.fuel_surface.fill("black")
        screen.blit(
            self.fuel_surface,
            (
                fuel_bar_pos[0] + self.fuel_bar_border,
                fuel_bar_pos[1] + self.fuel_bar_border,
            ),
        )

        pygame.draw.rect(
            screen,
            "white",
            (
                fuel_bar_pos[0] + self.fuel_bar_border,
                fuel_bar_pos[1] + self.fuel_bar_border,
                self.fuel
                * (self.fuel_bar_dimensions[0] - 2 * self.fuel_bar_border)
                / 1000,
                self.fuel_bar_dimensions[1] - 2 * self.fuel_bar_border,
            ),
        )

    def draw_score(self, screen):
        font = pygame.font.SysFont("Arial", 20)
        text = font.render(str(self.score), True, "white")
        #     blit in the top center of the screen
        screen.blit(
            text, (self.scene_width / 2 - text.get_width() / 2, self.ui_padding)
        )
