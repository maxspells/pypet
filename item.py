import pygame


class Item:
    _next_id = 1

    def __init__(self, x=0, y=0, name=None, cost=0, itemType=None):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.name = name
        self.cost = cost
        self.itemType = itemType
        self.item_id = Item._next_id
        Item._next_id += 1

        self.image = None
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
    def __init__(self, x=0, y=0, name=None, cost=0, calories=None):
        super().__init__(x, y, name=name, cost=cost, itemType="Food")
        self.calories = calories

    def use(self, pet):
        pet.hunger = max(pet.hunger - self.calories, 0)
        if hasattr(pet, "bark"):
            pet.bark()
        pet.poop_timer = 0  # Reset poop timer after feeding
        pet.hasEaten = True


class PetFood(Food):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, name="Pet Food", cost=0, calories=10)
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


class Toy(Item):
    def __init__(self, x=0, y=0, name="Toy", cost=5):
        super().__init__(x, y, name=name, cost=cost, itemType="Toy")
        self.description = "A generic toy for your pet to play with."
        # Placeholder image, replace with your toy asset later
        self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
        self.image.fill((200, 200, 50, 255))  # Yellowish color
        self.rect = self.image.get_rect(topleft=(x, y))

    def use(self, pet):
        # Toys might increase happiness or trigger play in the future
        pass


class Ball(Toy):
    def __init__(self, x=0, y=0):
        super().__init__(x, y, name="Ball", cost=10)
        self.description = "A bouncy ball for your pet to chase!"
        # Draw a simple ball as a placeholder (replace with image if you have one)
        size = 32
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, (255, 80, 80), (size // 2, size // 2), size // 2)
        pygame.draw.circle(self.image, (255, 255, 255), (size // 2 + 6, size // 2 - 6), 6)
        self.rect = self.image.get_rect(topleft=(x, y))

    def use(self, pet):
        # If the pet can fetch, trigger fetch behavior
        if hasattr(pet, "can_fetch") and pet.can_fetch:
            # Fetch to current mouse position
            import pygame
            fetch_dest = pygame.mouse.get_pos()
            pet.fetch(self, fetch_dest)
        else:
            # Otherwise, just play with the ball (increase happiness, etc.)
            if hasattr(pet, "happiness"):
                pet.happiness = min(pet.happiness + 10, 100)
