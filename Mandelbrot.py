import pygame
import numpy as np
from multiprocessing import Process, Array, Queue, cpu_count
from queue import Empty

THREADS = cpu_count()
ITERATIONS = 512

AR = 16 / 9
SIZE_X = 80 * 16
SIZE_Y = int(SIZE_X / AR)
CHUNKS = int(SIZE_Y / 5)

def parallel_draw(arr, work_queue):
    while True:
        y_offset, count, x_start, x_end, y_start, iterations = work_queue.get(block = True)
        
        y_end = y_start - (x_end - x_start) / AR
        
        x_dist = x_end - x_start
        y_dist = y_start - y_end
    
        for y in range(y_offset, y_offset + count):  
            for x in range(SIZE_X):
                c = x_start + x * x_dist / SIZE_X + 1j * (y_start - y * y_dist / SIZE_Y)
                result = c
                for i in range(iterations):
                    nextnum = result * result + c
                    real = result.real
                    imag = result.imag
                    if result == nextnum:
                        arr[x + y*SIZE_X] = 0
                        break
                    if real * real + imag * imag > 4:
                        arr[x + y*SIZE_X] = int(i * 255 / iterations) * 256
                        break
                    else:
                        result = nextnum
                else:
                    arr[x + y*SIZE_X] = 0

def populate_queue(x_start, x_end, y_start, iterations, work_queue):
    chunk_size = int(SIZE_Y / CHUNKS)
    
    while True:
        try:
            work_queue.get(block = False)
        except Empty:
            break

    for i in range(CHUNKS):
        count = chunk_size if i < CHUNKS - 1 else SIZE_Y - i * chunk_size # make sure last chunk fills rest of the screen
        work_queue.put((i * chunk_size, count, x_start, x_end, y_start, iterations))
                        
def start():
    pygame.init()
    screen = pygame.display.set_mode((SIZE_X, SIZE_Y))
    myfont = pygame.font.SysFont("System", 24)
    
    values = Array('i', [0 for _ in range(SIZE_X * SIZE_Y)], lock=False)
    work_queue = Queue()
    
    x_start = -2.0
    x_end = 0.75
    y_start = 0.773
    iterations = ITERATIONS

    populate_queue(x_start, x_end, y_start, iterations, work_queue)
    
    for _ in range(THREADS):
        Process(target=parallel_draw, args=(values, work_queue), daemon=True).start()
    
    done = False
    while not done:
        value_copy = [[values[x + y*SIZE_X] for y in range(SIZE_Y)] for x in range(SIZE_X)]
        pygame.surfarray.blit_array(screen, np.array(value_copy))
        textsurface = myfont.render("Iterations: " + repr(iterations), True, (160, 0, 0))
        screen.blit(textsurface, (5, 5))
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pixel_width = (x_end - x_start) / SIZE_X
                
                x_offset = mouse_x - SIZE_X / 2
                y_offset = mouse_y - SIZE_Y / 2
                
                zoom_x = (x_end - x_start) * 0.4
                zoom_y = zoom_x / AR
                
                x_start += x_offset * pixel_width + zoom_x
                x_end += x_offset * pixel_width - zoom_x
                y_start -= y_offset * pixel_width + zoom_y
                       
                populate_queue(x_start, x_end, y_start, iterations, work_queue)
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_PLUS:
                    iterations = int(iterations * 1.25)
                    populate_queue(x_start, x_end, y_start, iterations, work_queue)
                elif event.key == pygame.K_KP_MINUS:
                    iterations = int(max(iterations * 0.8, 10))
                    populate_queue(x_start, x_end, y_start, iterations, work_queue)
                elif event.key == pygame.K_ESCAPE:
                    x_start = -2.0
                    x_end = 0.75
                    y_start = 0.773
                    iterations = ITERATIONS
                    populate_queue(x_start, x_end, y_start, iterations, work_queue)
                   
        pygame.time.wait(20)
        
if __name__ == '__main__':
    start()
