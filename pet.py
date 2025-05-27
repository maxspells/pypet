import pygame
import os
import item
import math
import random


class pet:
    AGE_STAGES = [
        ("egg", 0),
        ("baby", 0),         # 0+ seconds (after hatching)
        ("teen", 3600),      # 1 hour
        ("adult", 7200),     # 2 hours
        ("dead", float("inf"))
    ]

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
        self.age = 0  # Age in seconds
        self.rect = self.sprite.get_rect(center=(400, 300))  # Default position
        self.set_sprite_for_stage()
        self.idle_time = 0  # Time spent in idle state
        self.next_wander_time = 0  # Time until next wander action
        self.wander_target = None
        self.wander_speed = 80  # pixels per second
        self.dragging = False
        self.drag_offset = (0, 0)
        self.poop_timer = 0  # Time since last poop
        self.hasEaten = False  # Flag to track if the pet has eaten
        self.can_fetch = False  # Whether the pet can fetch items

    def hatch(self):
        if self.age_stage == "egg":
            hatch_sound_path = os.path.join("sounds", "hatch.ogg")
            self._hatch_sound = pygame.mixer.Sound(hatch_sound_path)
            self._hatch_channel = self._hatch_sound.play()
            self.age = 0  # Reset age when hatching
            self._hatching = True  # Set a flag to indicate hatching is in progress

    # Update age stage based on age
    def update_age_stage(self):
        for stage, threshold in reversed(self.AGE_STAGES):
            if self.age >= threshold:
                if self.age_stage != stage:
                    self.age_stage = stage
                    self.set_sprite_for_stage()
            break

    def play(self):
        if self.energy > 10:
            self.happiness = min(100, self.happiness + 10)
            self.energy -= 10

    def pick_wander_target(self, screen_width, screen_height):
        sprite_w, sprite_h = self.rect.width, self.rect.height
        margin = 5
        x = random.randint(margin + sprite_w // 2, screen_width - margin - sprite_w // 2)
        y = random.randint(margin + sprite_h // 2, screen_height - margin - sprite_h // 2)
        self.wander_target = (x, y)

    def poop(self, world_items=None):
        """Create a poop item at the pet's current position."""
        if world_items is not None:
            poop = item.Poop(self.rect.centerx, self.rect.bottom)
            world_items.add_item(poop)

    def update(self, seconds_passed, world_items=None):
        if self.age_stage == "egg":
            # Handle hatching state
            if hasattr(self, "_hatching") and self._hatching:
                if not self._hatch_channel.get_busy():
                    self.age_stage = "baby"
                    self.set_sprite_for_stage()
                    self._hatching = False  # Reset flag
                return

            # --- Egg hatching logic ---
            self.age += seconds_passed
            self.age += seconds_passed
            self.update_age_stage()
            if self.age >= 180:
                max_age = 360  # 6 minutes
                chance = min(1.0, (self.age - 180) / (max_age - 180))
                if random.random() < chance:
                    self.hatch()
            return  # Skip all other logic for eggs

        self.age += seconds_passed
        self.poop_timer += seconds_passed

        # Poop every 30 seconds
        if self.poop_timer >= 30 and self.hasEaten:
            self.poop(world_items)
            self.hasEaten = False

        # --- Toy seeking behavior ---
        if self.state == "idle" and world_items is not None:
            # Look for toys in the world
            for thing in world_items.items:
                if hasattr(thing, "itemType") and thing.itemType == "Toy":
                    # Go to the first toy found
                    self.state = "seek_toy"
                    self.target_toy = thing
                    break

        # Toy seeking state
        if getattr(self, "state", None) == "seek_toy" and hasattr(self, "target_toy"):
            toy = self.target_toy
            # Move toward the toy
            x, y = self.rect.center
            tx, ty = toy.rect.center
            dx, dy = tx - x, ty - y
            dist = math.hypot(dx, dy)
            if dist < 10:
                # Reached the toy, use it
                prev_state = self.state
                toy.use(self)
                # Only return to idle if we didn't start fetching
                if self.state == prev_state:
                    self.state = "idle"
                if hasattr(self, "target_toy"):
                    del self.target_toy
            else:
                step = self.wander_speed * seconds_passed
                if step > dist:
                    step = dist
                nx = x + dx / dist * step
                ny = y + dy / dist * step
                self.rect.center = (int(nx), int(ny))
            return  # Skip other movement logic while seeking toy

        # Idle logic
        if self.state == "idle":
            self.idle_time += seconds_passed
            if self.idle_time >= self.next_wander_time:
                self.state = "wander"
                self.idle_time = 0
                self.next_wander_time = random.uniform(20, 100)
                self.wander_target = None
        else:
            self.idle_time = 0  # Reset if not idling

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

        if self.state == "wander":
            if self.wander_target is None:
                self.pick_wander_target(450, 450)  # Use your WIDTH, HEIGHT

            x, y = self.rect.center
            tx, ty = self.wander_target
            dx, dy = tx - x, ty - y
            dist = math.hypot(dx, dy)
            if dist < 2:
                self.wander_target = None
                if random.random() < 0.3:  # 30% chance to wander again
                    self.state = "wander"
                else:
                    self.state = "idle"
                    self.idle_time = 0
                    self.next_wander_time = random.uniform(60, 180)
            else:
                step = self.wander_speed * seconds_passed
                if step > dist:
                    step = dist
                nx = x + dx / dist * step
                ny = y + dy / dist * step
                self.rect.center = (int(nx), int(ny))

        # Handle hatching state for non-egg (shouldn't be needed, but safe)
        if hasattr(self, "_hatching") and self._hatching:
            if not self._hatch_channel.get_busy():
                self.age_stage = "baby"
                self.set_sprite_for_stage()
                self._hatching = False  # Reset flag
            return  # Skip the rest of update while hatching

        if getattr(self, "state", None) == "fetch":
            missing = (
                not hasattr(self, "fetch_item") or
                not hasattr(self, "fetch_dest") or
                world_items is None or
                not hasattr(world_items, "items") or
                not any(getattr(i, "item_id", None) == getattr(self.fetch_item, "item_id", None) for i in world_items.items)
            )
            if missing:
                print("Fetch failsafe triggered: resetting to idle")
                self.state = "idle"
                if hasattr(self, "fetch_item"):
                    del self.fetch_item
                if hasattr(self, "fetch_dest"):
                    del self.fetch_dest
                if hasattr(self, "carrying_item"):
                    del self.carrying_item
                return

            # Update fetch_item reference to the actual object in world_items
            for i in world_items.items:
                if getattr(i, "item_id", None) == getattr(self.fetch_item, "item_id", None):
                    self.fetch_item = i
                    break

            # --- Fetch logic ---
            if not getattr(self, "carrying_item", False):
                # Move toward the item to fetch
                x, y = self.rect.center
                tx, ty = self.fetch_item.rect.center
                dx, dy = tx - x, ty - y
                dist = math.hypot(dx, dy)
                if dist < 10:
                    # Pick up the item
                    self.carrying_item = True
                else:
                    step = self.wander_speed * seconds_passed
                    if step > dist:
                        step = dist
                    nx = x + dx / dist * step
                    ny = y + dy / dist * step
                    self.rect.center = (int(nx), int(ny))
                return
            else:
                # Move toward the fetch destination with the item
                x, y = self.rect.center
                tx, ty = self.fetch_dest
                dx, dy = tx - x, ty - y
                dist = math.hypot(dx, dy)
                if dist < 10:
                    # Drop the item at the destination
                    self.fetch_item.rect.center = (int(tx), int(ty))
                    self.fetch_item.fetched = True  # Mark as fetched
                    self.carrying_item = False
                    
                    # Stay in fetch state until item is picked up
                    return
                else:
                    step = self.wander_speed * seconds_passed
                    if step > dist:
                        step = dist
                    nx = x + dx / dist * step
                    ny = y + dy / dist * step
                    self.rect.center = (int(nx), int(ny))
                    # Carry the item with the pet
                    self.fetch_item.rect.center = self.rect.center
                return

            # After dropping, check if the item is still in the world
            if hasattr(self, "fetch_item") and getattr(self.fetch_item, "fetched", False):
                # If the item is no longer in the world (picked up), return to idle
                if not any(i is self.fetch_item for i in world_items.items):
                    self.state = "idle"
                    del self.fetch_item
                    del self.fetch_dest
                    if hasattr(self, "carrying_item"):
                        del self.carrying_item

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
            if self.state == "idle":
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

    def handle_event(self, event, WIDTH, HEIGHT):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                mouse_x, mouse_y = event.pos
                offset_x = self.rect.x - mouse_x
                offset_y = self.rect.y - mouse_y
                self.drag_offset = (offset_x, offset_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            mouse_x, mouse_y = event.pos
            self.rect.x = mouse_x + self.drag_offset[0]
            self.rect.y = mouse_y + self.drag_offset[1]

            # Clamp to window bounds (assuming WIDTH and HEIGHT are your screen size)
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > WIDTH:
                self.rect.right = WIDTH
            if self.rect.top < 0:
                self.rect.top = 0
            if self.rect.bottom > HEIGHT:
                self.rect.bottom = HEIGHT


class dog(pet):
    def __init__(self, name, x=400, y=300, age_stage="egg"):
        dog_sprite = pygame.image.load("assets/Round/dog.png").convert_alpha()
        super().__init__(name, dog_sprite, age_stage=age_stage)
        self.rect = self.sprite.get_rect(center=(x, y))
        sound_path = os.path.join("sounds", "dog.mp3")
        self.sound = pygame.mixer.Sound(sound_path)
        self.can_fetch = True  # Dogs can fetch items

    def bark(self):
        self.sound.play()

    def fetch(self, item_to_fetch, fetch_dest):
        """Start fetch behavior: go to item, then carry it to fetch_dest (x, y)."""
        # Only fetch if the item is in the world
        world_items = None
        if hasattr(self, "world_items_ref"):
            world_items = self.world_items_ref
        if world_items and hasattr(world_items, "items"):
            if item_to_fetch not in world_items.items:
                print("Fetch aborted: item not in world_items")
                return
        self.state = "fetch"
        self.fetch_item = item_to_fetch
        self.fetch_dest = fetch_dest
        self.carrying_item = False
        self.happiness = min(self.happiness + 10, 100)

    def relink_fetch_item(self, world_items):
        if hasattr(self, "fetch_item") and world_items and hasattr(world_items, "items"):
            for thing in world_items.items:
                if getattr(thing, "item_id", None) == getattr(self.fetch_item, "item_id", None):
                    self.fetch_item = thing
                    return
            # If not found, clear fetch state
            self.state = "idle"
            if hasattr(self, "fetch_item"):
                del self.fetch_item
            if hasattr(self, "fetch_dest"):
                del self.fetch_dest
            if hasattr(self, "carrying_item"):
                del self.carrying_item


