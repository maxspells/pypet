import pygame
import os
import math
import random


class pet:
    def __init__(self, name, sprite=None, age_stage="egg"):
        if age_stage == "egg":
            sprite = pygame.image.load("assets/eggs/01.png").convert_alpha()
        elif sprite is None:
            sprite = pygame.image.load("assets/Round/zebra.png").convert_alpha()
        self.name = name
        self.sprite = sprite
        self.age_stage = age_stage  # egg, baby, teen, adult, dead
        self.state = "idle"  # Possible values: "idle", "sleeping", etc.
        self.hunger = 50
        self.happiness = 50
        self.energy = 50
        self.isSleeping = False
        self.age = 0  # Age in seconds
        self.rect = self.sprite.get_rect(center=(400, 300))  # Default position
        self.set_sprite_for_stage()

    def hatch(self):
        if self.age_stage == "egg":
            hatch_sound_path = os.path.join("sounds", "hatch.ogg")
            self._hatch_sound = pygame.mixer.Sound(hatch_sound_path)
            self._hatch_channel = self._hatch_sound.play()
            self.age = 0  # Reset age when hatching
            self._hatching = True  # Set a flag to indicate hatching is in progress

    def play(self):
        if self.energy > 10:
            self.happiness = min(100, self.happiness + 10)
            self.energy -= 10

    def update(self, seconds_passed):
        self.age += seconds_passed  # Increment age

        if self.age_stage == "egg":
            # Handle hatching state
            if hasattr(self, "_hatching") and self._hatching:
                if not self._hatch_channel.get_busy():
                    self.age_stage = "baby"
                    self.set_sprite_for_stage()
                    self._hatching = False  # Reset flag
                return

            # --- Egg hatching logic ---
            if self.age >= 180:
                max_age = 360  # 6 minutes
                chance = min(1.0, (self.age - 180) / (max_age - 180))
                if random.random() < chance:
                    self.hatch()
            return  # Skip hunger/energy updates for eggs

        # Starvation check
        if self.hunger >= 100 and self.age_stage != "dead":
            self.age_stage = "dead"
            self.set_sprite_for_stage()
            return  # Stop further updates if dead

        # Energy decreases slowly
        self.energy = max(0, self.energy - 0.05 * seconds_passed)

        if self.state == "sleeping":
            self.hunger = min(100, self.hunger + 0.01 * seconds_passed)
            self.energy = min(100, self.energy + 0.25 * seconds_passed)
            if self.energy >= 100:
                self.bark()
                self.state = "idle"
        else:  # idle or other states
            self.hunger = min(100, self.hunger + 0.1 * seconds_passed)

        if self.energy <= 10 and self.state != "sleeping":
            self.state = "sleeping"

        # Handle hatching state for non-egg (shouldn't be needed, but safe)
        if hasattr(self, "_hatching") and self._hatching:
            if not self._hatch_channel.get_busy():
                self.age_stage = "baby"
                self.set_sprite_for_stage()
                self._hatching = False  # Reset flag
            return  # Skip the rest of update while hatching

    def draw(self, surface):
        original_x = self.rect.x
        original_y = self.rect.y

        if self.age_stage == "egg":
            # Every 6 seconds, do a left-right wobble for 1 second, unless sleeping
            if self.state != "sleeping":
                ticks = pygame.time.get_ticks()
                cycle = 6000  # 6 seconds in ms
                wobble_duration = 1000  # 1 second in ms
                time_in_cycle = ticks % cycle
                if time_in_cycle < wobble_duration:
                    # Wobble left and right for 1 second
                    wiggle_offset = math.sin((time_in_cycle / wobble_duration) * math.pi * 4) * 8
                    self.rect.x += wiggle_offset
        # Else, stand still (no offset)
        else:
            # Normal up and down wobble, unless sleeping
            if self.state != "sleeping":
                wobble_offset = math.sin(pygame.time.get_ticks() / 200) * 5
                self.rect.y += wobble_offset

        surface.blit(self.sprite, self.rect)

        # Reset position so physics/collision stay correct
        self.rect.x = original_x
        self.rect.y = original_y

    def set_sprite_for_stage(self):
        """Set and scale the sprite based on the pet's age_stage."""
        if self.age_stage == "egg":
            sprite = pygame.image.load("assets/eggs/01.png").convert_alpha()
            scale = 5.0
        elif self.age_stage == "baby":
            sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
            scale = .25
        elif self.age_stage == "teen":
            sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
            scale = 0.75
        elif self.age_stage == "dead":
            sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
            scale = 1.0
            # Optionally, tint or rotate the sprite to indicate death
            sprite.fill((100, 100, 100, 128), special_flags=pygame.BLEND_RGBA_MULT)
        else:  # adult or any other stage
            sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
            scale = 1.0

        # Scale the sprite
        w, h = sprite.get_size()
        sprite = pygame.transform.scale(sprite, (int(w * scale), int(h * scale)))
        prev_center = self.rect.center if hasattr(self, "rect") else (400, 300)
        self.sprite = sprite
        self.rect = self.sprite.get_rect(center=prev_center)


class dog(pet):
    def __init__(self, name, x=400, y=300, age_stage="egg"):
        dog_sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
        super().__init__(name, dog_sprite, age_stage=age_stage)
        self.rect = self.sprite.get_rect(center=(x, y))
        sound_path = os.path.join("sounds", "dog.mp3")
        self.sound = pygame.mixer.Sound(sound_path)

    def bark(self):
        self.sound.play()
