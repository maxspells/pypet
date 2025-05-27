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

        # Create Ball item
        ball_1 = item.Ball(x + 10, y + 130)
        ball_1.orig_pos = (x + 10, y + 130)

        self.items = [pet_food_1, pet_food_2, ball_1]
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

    def handle_event(self, event, pet, world_items=None, WIDTH=450, HEIGHT=450):
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

            # Clamp to game window bounds
            if self.dragging_item.rect.left < 0:
                self.dragging_item.rect.left = 0
            if self.dragging_item.rect.right > WIDTH:
                self.dragging_item.rect.right = WIDTH
            if self.dragging_item.rect.top < 0:
                self.dragging_item.rect.top = 0
            if self.dragging_item.rect.bottom > HEIGHT:
                self.dragging_item.rect.bottom = HEIGHT

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging_item:
            item_type = getattr(self.dragging_item, "itemType", None)
            # Dropped on pet: feed if food
            if item_type == "Food" and pet.rect.colliderect(self.dragging_item.rect):
                self.dragging_item.use(pet)
                # Snap back to original position (do NOT remove from panel)
                self.dragging_item.rect.topleft = self.dragging_item.orig_pos
            # Dropped outside the panel: add toy to world
            elif item_type == "Toy" and not self.rect.colliderect(self.dragging_item.rect) and world_items is not None:
                # Create a new toy of the same type at the drop location
                toy_class = type(self.dragging_item)
                drop_x, drop_y = self.dragging_item.rect.topleft
                new_toy = toy_class(drop_x, drop_y)
                world_items.add_item(new_toy)
                # Snap the original back to its slot
                self.dragging_item.rect.topleft = self.dragging_item.orig_pos
            else:
                # Snap back to original position
                self.dragging_item.rect.topleft = self.dragging_item.orig_pos
            self.dragging_item = None


class WorldItemPanel:
    def __init__(self):
        self.items = []
        self.dragging_item = None
        self.drag_offset = (0, 0)

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)

    def draw(self, surface):
        for i in self.items:
            surface.blit(i.image, i.rect)

    def handle_event(self, event, WIDTH, HEIGHT, trash_panel=None):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for thing in self.items[:]:  # Copy to allow removal
                if thing.rect.collidepoint(event.pos):
                    # If the item was fetched and dropped off, remove it immediately
                    if getattr(thing, "fetched", False):
                        self.items.remove(thing)
                        return
                    # If the item was clicked, start dragging it
                    mouse_x, mouse_y = event.pos
                    self.dragging_item = thing
                    offset_x = thing.rect.x - mouse_x
                    offset_y = thing.rect.y - mouse_y
                    self.drag_offset = (offset_x, offset_y)
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging_item:
            mouse_x, mouse_y = event.pos
            self.dragging_item.rect.x = mouse_x + self.drag_offset[0]
            self.dragging_item.rect.y = mouse_y + self.drag_offset[1]

            # Clamp to game window bounds
            if self.dragging_item.rect.left < 0:
                self.dragging_item.rect.left = 0
            if self.dragging_item.rect.right > WIDTH:
                self.dragging_item.rect.right = WIDTH
            if self.dragging_item.rect.top < 0:
                self.dragging_item.rect.top = 0
            if self.dragging_item.rect.bottom > HEIGHT:
                self.dragging_item.rect.bottom = HEIGHT

        elif event.type == pygame.MOUSEBUTTONUP and self.dragging_item:
            if trash_panel.is_over(self.dragging_item):
                self.remove_item(self.dragging_item)
            self.dragging_item = None


class TrashPanel:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = (180, 60, 60)  # Reddish

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=8)
        font = pygame.font.SysFont(None, 24)
        text_surf = font.render("Trash", True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_over(self, item):
        return self.rect.colliderect(item.rect)
