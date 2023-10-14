import pygame


class Platform:
    def __init__(self, x, y):
        self.platform_width = 100
        self.platform_height = 20
        self.pos = pygame.Vector2(x, y)
        self.color = "#525252"

        self.visited = False
        self.visited_color = "#69FFF1"
        self.unvisited_color = "#F1D302"

        self.player_too_fast = False
        self.player_too_fast_color = "#D2201D"

    def get_center(self):
        return (
            self.pos[0] + self.platform_width / 2,
            self.pos[1] + self.platform_height / 2,
        )

    def set_pos_from_center(self, center):
        self.pos = pygame.Vector2(
            center[0] - self.platform_width / 2, center[1] - self.platform_height / 2
        )

    def get_edges(self):
        # return array of 4 points, top left, top right, bottom left, bottom right
        return [
            self.pos,
            self.pos + pygame.Vector2(self.platform_width, 0),
            self.pos + pygame.Vector2(0, self.platform_height),
            self.pos + pygame.Vector2(self.platform_width, self.platform_height),
        ]

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            (self.pos[0], self.pos[1], self.platform_width, self.platform_height),
        )
        #     draw status circle in the top right corner
        if self.player_too_fast:
            status_color = self.player_too_fast_color
        elif self.visited:
            status_color = self.visited_color
        else:
            status_color = self.unvisited_color
        pygame.draw.circle(
            screen,
            status_color,
            (self.pos[0] + self.platform_width - 7, self.pos[1] + 7),
            5,
        )

    def intersects_player(self, player):
        x_between = self.pos[0] <= player.pos[0] <= self.pos[0] + self.platform_width
        y_above_by_radius = player.pos[1] + player.radius >= self.pos[1]
        not_below = player.pos[1] - player.radius <= self.pos[1] + self.platform_height

        return x_between and y_above_by_radius and not_below
