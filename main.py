import pygame
import sys
import pet
from ui import ItemPanel, Button, WorldItemPanel, TrashPanel
import saveload

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
WIDTH, HEIGHT = 450, 450
BG_COLOR = (0, 140, 140)
PET_COLOR = (255, 100, 100)
FPS = 30

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PyPet")

# UI stuffs
item_panel = ItemPanel(WIDTH - 100, 50, 80, 300)
world_items = WorldItemPanel()
trash_panel = TrashPanel(x=10, y=HEIGHT-60, width=80, height=50)


def toggle_item_panel():
    item_panel.toggle()


# Button setup
button_width, button_height = 80, 30
item_button = Button(rect=(355, 10, 80, 30), text="Items", callback=toggle_item_panel)
menu_button = Button(rect=(WIDTH - 180, 10, button_width, button_height), text="Menu")


# Clock for frame rate
clock = pygame.time.Clock()

# Pet state (position)
pet_pos = (WIDTH // 2, HEIGHT // 2)
pet_radius = 40
thepet = saveload.load_data(pet.dog("Theo"), world_items)
if thepet is None:
    thepet = pet.dog("Theo", x=pet_pos[0], y=pet_pos[1])
else:
    thepet.relink_fetch_item(world_items)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            saveload.save_data(thepet, world_items)
            running = False
        thepet.handle_event(event, WIDTH, HEIGHT)
        item_button.handle_event(event)
        menu_button.handle_event(event)
        item_panel.handle_event(event, thepet, world_items, WIDTH, HEIGHT)
        world_items.handle_event(event, WIDTH, HEIGHT, trash_panel)

    # Clear screen
    screen.fill(BG_COLOR)

    # Draw
    item_button.draw(screen)
    menu_button.draw(screen)
    trash_panel.draw(screen)
    world_items.draw(screen)
    thepet.draw(screen)
    item_panel.draw(screen)
    font = pygame.font.SysFont(None, 24)
    hunger_text = font.render(f"Hunger: {int(thepet.hunger)}", True, (0, 0, 0))
    screen.blit(hunger_text, (10, 10))
    energy_text = font.render(f"Energy: {int(thepet.energy)}", True, (0, 0, 0))
    screen.blit(energy_text, (10, 24))
    happiness_text = font.render(f"Happiness: {int(thepet.happiness)}", True, (0, 0, 0))
    screen.blit(happiness_text, (10, 38))
    age_text = font.render(f"Age: {int(thepet.age)}s", True, (0, 0, 0))
    age_rect = age_text.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
    screen.blit(age_text, age_rect)
    seconds = clock.get_time() / 1000  # time in seconds since last frame
    thepet.update(seconds, world_items)

    # Update display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

pygame.quit()
sys.exit()
