import math
import numpy as np
import skimage.morphology as mp

from skimage import io, filters, measure, data
from skimage.color import rgb2gray
from matplotlib import pylab as plt

# Minimalne wymiary planszy do wykrycia
MIN_GAME_WIDTH = 400
MIN_GAME_HEIGHT = 400
# Minimalne wymiary znaków 'X' i 'O'
MIN_FIGURE_WIDTH = 100
MIN_FIGURE_HEIGHT = 100
MIN_CIRCLE_DIAMETER = 100

def closest_point(pos, positions) -> int:
    """Zwraca indeks najbliższego pola

    Funkcja sprawdza dystans pomiedzy dwoma punktami i zwraca
    indeks pola z najbliższym środkiem
    """
    min_dist = float('inf')
    index = 0
    for i, x in enumerate(positions):
        if (x[0]-pos[0])**2 + (x[1]-pos[1])**2 < min_dist:
            min_dist = (x[0]-pos[0])**2 + (x[1]-pos[1])**2
            index = i
    return index

def distance(pos, positions) -> float:
    """Zwraca dystans środka figury do najbliższego punktu"""
    min_dist = float('inf')
    for x in positions:
        if (x[0]-pos[0])**2 + (x[1]-pos[1])**2 < min_dist:
            min_dist = (x[0]-pos[0])**2 + (x[1]-pos[1])**2
    return min_dist
    
def plot_regions(regions, labeled_image):
    """Rysuje obramowanie dla kazdego regionu

    Pomocnicza funkcja do zaznaczenia regionu,
    w którym znajduje się wykrytu obiekt
    """
    plt.subplots()
    plt.imshow(labeled_image)

    for region in regions:
        minr, minc, maxr, maxc = region.bbox
        bx = (minc, maxc, maxc, minc, minc)
        by = (minr, minr, maxr, maxr, minr)
        plt.plot(bx, by, '-r', linewidth=1)
    plt.title("Podział na regiony")

def detect_tictactoe(name):
    """Główna funkcja do wykrywania gry w kółko i krzyżyk"""
    game_dimensions = [] # Lista skrajnych punktów planszy (min_x, min_y, max_x, max_y)
    game_positions = []  # Lista środków wszystkich dziewięciu pól (y, x)
    answers = []         # Lista wykrytych znaków 'O' i 'X'

    # Zamiana kolorów na odcienie szarości
    img = rgb2gray(io.imread(name))
    # Progowanie obrazu
    img_threshold = img < filters.threshold_sauvola(img, window_size = 91, k = 0.05)
    # Usuwanie małych obiektów
    img_remove_small = mp.remove_small_objects(img_threshold, min_size = 100)
    # Dylatacja czyli wypełnianie dziur,  K - sąsiadujące ze sobą pixele
    K = np.ones((5,5))
    img_dyla = mp.dilation(img_remove_small, selem = K)
    # Ponowne usuwanie małych obiektów
    img_remove = mp.remove_small_objects(img_dyla, min_size = 600)
    # Łączenie ze sobą pikseli
    labeled_img = measure.label(img_remove)
    # Podział na regiony
    regions = measure.regionprops(labeled_img)
    #plot_regions(regions, labeled_img)

    # Plansze
    for region in regions:
        width = region.bbox[3] - region.bbox[1]
        height = region.bbox[2] - region.bbox[0]
        if (width > MIN_GAME_WIDTH
                and height > MIN_GAME_HEIGHT
                and width / height > 0.5
                and width / height < 2
                and region.area / region.convex_area < 0.5):
            # Jeśli dany region spełnia wszystkie warunki uznaję go za plansze
            central_positions = []
            answers.append(['-' for i in range(9)])
            game_dimensions.append(region.bbox)
            # Wyznaczanie współrzędnych środków 9 pól znalezionej planszy
            h = region.bbox[0] + height/6
            for i in range(3):
                w = region.bbox[1] + width/6
                for j in range(3):
                    central_positions.append((h, w))
                    w += width/3
                h += height/3
            game_positions.append(central_positions)

    # Figury
    for region in regions:
        width = region.bbox[3] - region.bbox[1]
        height = region.bbox[2] - region.bbox[0]
        for i, x in enumerate(game_dimensions):
            game_width = game_dimensions[i][3] - game_dimensions[i][1]
            game_height = game_dimensions[i][2] - game_dimensions[i][0]
            if (width*2 < game_width
                    and width > MIN_FIGURE_WIDTH
                    and width > game_width / 10
                    and height*2 < game_height
                    and height > MIN_FIGURE_HEIGHT
                    and height > game_height / 10
                    and region.centroid[0] >= x[0]
                    and region.centroid[1] >= x[1]
                    and region.centroid[0] <= x[2]
                    and region.centroid[1] <= x[3]):
                # Dystans srodka figury do najblizszego punkty (duzy dystans == kolko)
                dist = distance(region.centroid, region.coords)
                # Znajduje pole z najblizszym srodkiem jednego z 9 pól
                index = closest_point(region.centroid, game_positions[i])
                if dist > MIN_CIRCLE_DIAMETER:
                    answers[i][index] = 'O'
                else:
                    answers[i][index] = 'X'
    # Wyświetlenie w konsoli znalezionej gry
    for i in range(len(game_dimensions)):
        print("Game " + str(i+1) + ":")
        for j in range(3):
            print(answers[i][3*j : 3*(j+1)])

def main():
    name = "plansze/plansza1.jpg"
    plt.figure(1)
    plt.imshow(io.imread(name))
    plt.axis('off')
    detect_tictactoe(name)
    plt.show()
    # plt.figure(1)
    # plt.imshow(img)
    # plt.figure(2)
    # plt.imshow(img_grey)
    # plt.figure(2)
    # plt.imshow(img)
    # plt.figure(3)
    # plt.imshow(img_threshold)
    # plt.figure(4)
    # plt.imshow(img_remove_small)
    # plt.title("Usunięcie małych obiektów")
    # plt.figure(5)
    # plt.imshow(img_dyla)
    # plt.title("Dylatacja")
    # plt.figure(6)
    # plt.imshow(img_remove)
    # plt.title("Ponowne usunięcie małych obiektów")
    # plt.figure(7)
    # plt.imshow(labeled_img)
    # plt.title("Po złączeniu pikseli o tej samej wartości")
    # plt.show()

if __name__ == "__main__":
    main()