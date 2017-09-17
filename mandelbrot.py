import pygame
import numpy as np
from multiprocessing import Process, Array, Queue, cpu_count
from queue import Empty
from itercalc import cudaiter, cpuiter
from decimal import Decimal

THREADS = cpu_count()
ITERATIONS = 500

AR = 16 / 9
SIZE_X = 30 * 16
SIZE_Y = int(SIZE_X / AR)
CHUNKS = int(SIZE_Y / 10)

X_START = -2.55
X_END = .75
Y_START = (X_END - X_START) / AR / 2
Y_END = -Y_START

def clear_queue(q):
    while True:
        try:
            q.get(block = False)
        except Empty:
            break

def parallel_draw_cpu(arr, work_queue):
    while True:
        try:
            y_offset, count, x_start, x_end, y_start, y_end, iterations = work_queue.get(block = False)    
            cpuiter(y_offset, count, x_start, x_end, y_start, y_end, iterations, SIZE_X, SIZE_Y, arr)
        except Empty:
            break
                  
def populate_queue(x_start, x_end, y_start, y_end, iterations, work_queue):
    chunk_size = int(SIZE_Y / CHUNKS)
    clear_queue(work_queue)
 
    for i in range(CHUNKS):
        count = chunk_size if i < CHUNKS - 1 else SIZE_Y - i * chunk_size # make sure last chunk fills rest of the screen
        work_queue.put((i * chunk_size, count, x_start, x_end, y_start, y_end, iterations))
        
def update_view(method, x_start, x_end, y_start, y_end, SIZE_X, SIZE_Y, iterations, work_queue, values):
    if method == 'CUDA':
        Process(target = cudaiter, 
                args=(x_start, x_end, y_start, y_end, iterations, SIZE_X, SIZE_Y, values),
                daemon = True).start()
    elif method == 'CPU_MT':
        populate_queue(x_start, x_end, y_start, y_end, iterations, work_queue)
        for _ in range(THREADS):
            Process(target=parallel_draw_cpu,
                    args=(values, work_queue),
                    daemon=True).start()
                        
def start():    
    pygame.init()
    screen = pygame.display.set_mode((SIZE_X, SIZE_Y))
    myfont = pygame.font.SysFont("DejaVu Sans Mono, Bold", 16, True)
    font_color = (255, 0, 0)
    
    values = Array('i', [0 for _ in range(SIZE_X * SIZE_Y)], lock=False)
    work_queue = Queue()
    method = 'CUDA'
    
    x_start = X_START
    x_end = X_END
    y_start = Y_START
    y_end = Y_END
    
    iterations = ITERATIONS
    
    update_view(method, x_start, x_end, y_start, y_end, SIZE_X, SIZE_Y, iterations, work_queue, values)
    
    text_level = 3
    update = False
    update_counter = 0
    done = False
    while not done:
        if update_counter == 0: # Update values from multiprocess array
            value_copy = np.array(values).reshape((SIZE_X, SIZE_Y), order='F')
            
        pygame.surfarray.blit_array(screen, value_copy)
        
        surfaces = []
        if text_level > 0:
            surfaces.append(myfont.render("Method: " + method, True, font_color))
            surfaces.append(myfont.render("Iterations: " + repr(iterations), True, font_color))
        if text_level > 1:
            surfaces.append(myfont.render("X-Start: " + '%.6E' % Decimal(x_start), True, font_color))
            surfaces.append(myfont.render("X-End:   " + '%.6E' % Decimal(x_end), True, font_color))
            surfaces.append(myfont.render("Y-Start: " + '%.6E' % Decimal(y_end), True, font_color))
            surfaces.append(myfont.render("Y-End:   " + '%.6E' % Decimal(y_start), True, font_color))
        if text_level > 2:
            surfaces.append(myfont.render("", True, font_color))
            surfaces.append(myfont.render("Keyboard shortcuts:", True, font_color))
            surfaces.append(myfont.render("Space      : Return to default view", True, font_color))
            surfaces.append(myfont.render("Escape     : Exit program", True, font_color))
            surfaces.append(myfont.render("Numpad -/+ : Inc/dec iterations", True, font_color))
            surfaces.append(myfont.render("M          : Change compute method", True, font_color))
            surfaces.append(myfont.render("H          : Change information level", True, font_color))  
            
        for i in range(len(surfaces)):
            screen.blit(surfaces[i], (5, 2 + i*20))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                pixel_width = (x_end - x_start) / SIZE_X
                
                x_offset = mouse_x - SIZE_X / 2
                y_offset = mouse_y - SIZE_Y / 2
                
                zoom_x = (x_end - x_start) * 0.4
                zoom_y = zoom_x / AR
                
                x_start += x_offset * pixel_width + zoom_x
                x_end += x_offset * pixel_width - zoom_x
                y_start -= y_offset * pixel_width + zoom_y
                y_end = y_start - (x_end - x_start) / AR
                    
                update = True
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_KP_PLUS:
                    iterations = int(iterations * 1.25)
                    update = True
                elif event.key == pygame.K_KP_MINUS:
                    iterations = int(max(iterations * 0.8, 10))
                    update = True
                elif event.key == pygame.K_SPACE:
                    x_start = X_START
                    x_end = X_END
                    y_start = Y_START
                    y_end = Y_END
                    iterations = ITERATIONS
                    update = True
                elif event.key == pygame.K_ESCAPE:
                    done = True
                elif event.key == pygame.K_m:
                    if method == 'CUDA':
                        method = 'CPU_MT'
                    else:
                        clear_queue(work_queue)
                        method = 'CUDA'
                    update = True
                elif event.key == pygame.K_h:
                    text_level = (text_level + 1) % 4
                    
        if update:
            update_view(method, x_start, x_end, y_start, y_end, SIZE_X, SIZE_Y, iterations, work_queue, values)
            update = False
                   
        pygame.time.wait(20)
        update_counter = (update_counter + 1) % 5
    clear_queue(work_queue)
    
if __name__ == '__main__':
    start()
