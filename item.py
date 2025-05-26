import pygame


class Item:
    def __init__(self, x, y, name=None, cost=0, itemType=None):
        self.name = name
        self.cost = cost
        self.itemType = itemType

        self.image = None
        self.rect = None
        self.dragging = False
        self.offset_x = 0
        self.offset_y = 0

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                self.offset_x = self.rect.x - mouse_x
                self.offset_y = self.rect.y - mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.rect.x = mouse_x + self.offset_x
            self.rect.y = mouse_y + self.offset_y

    def use(self, target):
        pass


class Food(Item):
    def __init__(self, name=None, cost=0, calories=None):
        super().__init__(
            name,
            cost,
        )
        self.itemType = "Food"
        self.calories = calories

    def use(self, pet):
        pet.hunger = max(pet.hunger - self.calories, 0)
        if hasattr(pet, "bark"):
            pet.bark()


class PetFood(Food):
    def __init__(self, x=0, y=0):
        super().__init__(name="Pet Food", cost=0, calories=10)
        self.description = (
            "Some bland pet food. Doesn't taste very good, but it's there."
        )
        self.image = pygame.image.load("assets/FruitAssets/fruit1.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))


class Poop(Item):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, name="Poop", cost=0, itemType="Poop")
        self.description = "A stinky pile left by your pet."
        image = pygame.image.load("assets/poop.png").convert_alpha()
        w, h = image.get_size()
        self.image = pygame.transform.scale(image, (w * 2, h * 2))
        self.rect = self.image.get_rect(topleft=(x, y))
