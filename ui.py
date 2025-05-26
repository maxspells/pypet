import pygame
import item


class Button:
    def __init__(
        self, rect, text, callback=None, color=(200, 200, 200), text_color=(0, 0, 0)
    ):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.callback = callback  # Optional function to call when clicked
        self.font = pygame.font.SysFont(None, 24)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.callback:
                    self.callback()


class ItemPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.visible = False
        # Create PetFood item 1
        pet_food_1 = item.PetFood(x + 10, y + 10)
        pet_food_1.orig_pos = (x + 10, y + 10)

        # Create PetFood item 2
        pet_food_2 = item.PetFood(x + 10, y + 70)
        pet_food_2.orig_pos = (x + 10, y + 70)
        self.items = [pet_food_1, pet_food_2]
        self.dragging_item = None
        self.drag_offset = (0, 0)

    def toggle(self):
        self.visible = not self.visible

    def draw(self, surface):
        if not self.visible:
            return
        # Draw panel background
        pygame.draw.rect(surface, (200, 200, 200), self.rect)  # Light gray
        # Draw each item
        for i in self.items:
            surface.blit(i.image, i.rect)

    def handle_event(self, event, dog):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for thing in self.items:
                if thing.rect.collidepoint(event.pos):
                    self.dragging_item = thing
                    mouse_x, mouse_y = event.pos
                    offset_x = thing.rect.x - mouse_x
                    offset_y = thing.rect.y - mouse_y
                    self.drag_offset = (offset_x, offset_y)
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging_item:
            mouse_x, mouse_y = event.pos
            self.dragging_item.rect.x = mouse_x + self.drag_offset[0]
            self.dragging_item.rect.y = mouse_y + self.drag_offset[1]

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging_item:
            mouse_pos = event.pos
            print(f"Dropping item at {mouse_pos}")
            print(f"Dog rect: {dog.rect}")
            print(f"Collision? {dog.rect.collidepoint(mouse_pos)}")
            if dog.rect.colliderect(self.dragging_item.rect):
                # Feed the dog
                self.dragging_item.use(dog)
                # Option 1: Remove item after use (if consumable)
                self.items.remove(self.dragging_item)
            else:
                # Return item to original place (you'll want to store this on item)
                self.dragging_item.rect.topleft = self.dragging_item.orig_pos
            self.dragging_item = None
