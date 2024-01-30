import json
import pandas as pd
from itertools import combinations
import sys
import pygame
from pygame.locals import *

caption = '帕魯配種世界線'
window_x, window_y = 800, 600
border_x, border_y = 40, 50
breed_col_w = 250

def id2i(id):
    return int(id) if id[-1].isdigit() else int(id[:-1]) + .5

with open('breed_dict.json') as f:
    data = json.load(f)
breed_dict = {(p, q): r for [p, q], r in data}

with open('breed_dict_rev.json') as f:
    breed_rev_dict = json.load(f)

id_df = pd.read_csv('real_id.csv')
id2name = {r['編號'].strip().lstrip('0'): r['名稱'] for _, r in id_df.iterrows()}
id_list = sorted(id2name, key=id2i)

with open('save.txt', 'a') as f:
    pass
with open('save.txt', 'r') as f:
    save = [x.strip() for x in f.readlines() if x.strip() in id_list]

class PalBox():
    def __init__(self, box: list):
        self.my_box = [box]
        self.total_box = []
        self.level = 0

        while self.my_box[self.level] != []:
            self.level += 1
            self.total_box.append([])
            for i in range(self.level):
                self.total_box[-1] += self.my_box[i]
            self.my_box.append([])
            for p, q in combinations(self.total_box[-1], 2):
                if (p, q) in breed_dict and breed_dict[p, q] not in self.total_box[-1] and breed_dict[p, q] not in self.my_box[self.level]:
                    self.my_box[self.level].append(breed_dict[p, q])
            self.my_box[self.level].sort(key=id2i)
    
    def get_bread_list(self, pal_id: str, is_included_self_lv = False):
        lv = self.level
        for i, b in enumerate(self.my_box):
            if pal_id in b:
                lv = i
        if not is_included_self_lv:
            if lv == 0:
                return []
            s = {tuple(sorted((p, q), key=id2i)) for p, q in breed_rev_dict[pal_id] if p in self.total_box[lv - 1] and q in self.total_box[lv - 1]}
        else:
            s = {tuple(sorted((p, q), key=id2i)) for p, q in breed_rev_dict[pal_id] if p in self.total_box[lv] and q in self.total_box[lv]}
        return sorted(list(s), key=lambda x: id2i(x[0]) * 10000 + id2i(x[1]))

class PalSprite():
    sprite_dict = {}

    def __init__(self, pal_id):
        self.pal_id = pal_id
        self.name = id2name[self.pal_id]
        self.showname = self.pal_id + ' ' + self.name

        self.w = 100
        self.h = 75

        self.image = pygame.transform.scale(pygame.image.load(f'img/{self.pal_id}.png'), (50, 50))
        self.head_font = pygame.font.Font('font/msjh.ttc', 14)# 宣告 font 文字物件
        self.label = self.head_font.render(self.showname, True, (0, 0, 0))
        self.canvas = pygame.Surface((self.w, self.h), flags=SRCALPHA)

        self.sprite_dict[self.pal_id] = self

    def get_sprite(pal_id):
        if pal_id not in PalSprite.sprite_dict:
            PalSprite.sprite_dict[pal_id] = PalSprite(pal_id)
        return PalSprite.sprite_dict[pal_id]
    
    def blitme(self, surface, x = 0, y = 0):
        self.canvas.fill((255, 255, 255, 0))
        self.canvas.blit(self.image, (self.canvas.get_width()//2 - self.image.get_width()//2, 3))
        self.canvas.blit(self.label, (self.canvas.get_width()//2 - self.label.get_width()//2, 52))
        surface.blit(self.canvas, (x, y))

class TouchableObj():
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.isChosen = False
        self.isTouched = False
        self.canvas = pygame.Surface((self.w, self.h), flags=SRCALPHA)

    def set_pos(self, x, y):
        self.x = x
        self.y = y

    def fill(self):
        if self.isChosen and not self.isTouched:
            color = (255, 180, 180, 100)
        elif self.isTouched and not self.isChosen:
            color = (180, 240, 240, 100)
        elif self.isTouched and self.isChosen:
            color = (218, 210, 210, 200)
        else:
            color = (255, 255, 255, 0)
        self.canvas.fill(color)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        surface.blit(self.canvas, (self.x + dx, self.y + dy))

class PalObj(TouchableObj):
    def __init__(self, pal_id, x=0, y=0):
        self.pal_id = pal_id
        self.sprite = PalSprite.get_sprite(pal_id)
        self.frame = False
        super().__init__(x, y, self.sprite.w, self.sprite.h)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        self.sprite.blitme(self.canvas, 0, 0)
        if self.frame:
            pygame.draw.rect(self.canvas, (0, 0, 0, 100), (0, 0, self.w, self.h), 1)
        surface.blit(self.canvas, (self.x + dx, self.y + dy))

class PalBreedObj(TouchableObj):
    def __init__(self, pal_id1, pal_id2, x=0, y=0):
        self.pal_id1 = pal_id1
        self.pal_id2 = pal_id2
        self.sprite1 = PalSprite.get_sprite(pal_id1)
        self.sprite2 = PalSprite.get_sprite(pal_id2)
        self.font = pygame.font.Font('font/msjh.ttc', 10)
        self.label = self.font.render('X', True, (0, 0, 0))
        super().__init__(x, y, self.sprite1.w + self.sprite2.w + 10, self.sprite1.h)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        self.sprite1.blitme(self.canvas, 0, 0)
        self.canvas.blit(self.label, (self.sprite1.w, self.sprite1.h//2 - self.label.get_height()//2))
        self.sprite2.blitme(self.canvas, self.sprite1.w + self.label.get_width(), 0)
        surface.blit(self.canvas, (self.x + dx, self.y + dy))

class LabelObj(TouchableObj):
    def __init__(self, text, size, x=0, y=0):
        self.text = text
        self.font = pygame.font.Font('font/msjh.ttc', size)
        self.label = self.font.render(self.text, True, (0, 0, 0))
        super().__init__(x, y, self.label.get_width(), self.label.get_height())

    def blitme(self, surface, dx = 0, dy = 0):
        surface.blit(self.label, (self.x + dx, self.y + dy))

class BtnObj(TouchableObj):
    def __init__(self, text, size, action, x=0, y=0):
        self.text = text
        self.font = pygame.font.Font('font/msjh.ttc', size)
        self.label = self.font.render(self.text, True, (0, 0, 0))
        self.on_click = action
        self.border = 5

        super().__init__(x, y, self.label.get_width() + self.border * 2, self.label.get_height() + self.border * 2)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        self.canvas.blit(self.label, (self.border, self.border))
        pygame.draw.rect(self.canvas, (0, 0, 0, 255), (0, 0, self.w, self.h), 1)
        surface.blit(self.canvas, (self.x + dx, self.y + dy))

    def is_mouse_over(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h

    def running(self, mouse_x, mouse_y, click, scroll):
        if self.is_mouse_over(mouse_x, mouse_y):
            self.isTouched = True
            if click == 1:
                self.on_click()
        else:
            self.isTouched = False

class SubWindow():

    def __init__(self, x, y, w, h, frame = False, color = (255, 255, 255, 255)):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

        self.scroll_x_max = 0
        self.scroll_y_max = 0
        self.scroll_x = 0
        self.scroll_y = 0

        self.color = color
        self.frame = frame
        self.border = 1

        self.objlist = []

        self.canvas = pygame.Surface((self.w, self.h), flags=SRCALPHA)

    def blitme(self, surface):
        self.canvas.fill(self.color)
        for obj in self.objlist:
            obj.blitme(self.canvas, -self.scroll_x, -self.scroll_y)
        if self.frame:
            pygame.draw.rect(self.canvas, (0, 0, 0, 255), (0, 0, self.w, self.h), 1)
        surface.blit(self.canvas, (self.x, self.y))
    
    def add_obj(self, obj, newline = False):
        if self.objlist == []:
            obj.set_pos(self.border, self.border)
        elif not newline and self.objlist[-1].x + self.objlist[-1].w + obj.w + 2 * self.border < self.w:
            obj.set_pos(self.objlist[-1].x + self.objlist[-1].w + self.border, self.objlist[-1].y)
        else:
            obj.set_pos(self.border, self.objlist[-1].y + self.objlist[-1].h + self.border)
        self.objlist.append(obj)
        self.scroll_y_max = self.objlist[-1].y + self.objlist[-1].h + self.border - self.h
        self.scroll_y_max = self.scroll_y_max if self.scroll_y_max > 0 else 0
    
    def is_mouse_over(self, x, y):
        return self.x <= x <= self.x + self.w and self.y <= y <= self.y + self.h

    def detect_touch(self, x, y, isClicked=False):
        pass

    def scroll(self, x, y):
        self.scroll_x += x * -50
        self.scroll_y += y * -50
        if self.scroll_x > self.scroll_x_max:
            self.scroll_x = self.scroll_x_max
        elif self.scroll_x < 0:
            self.scroll_x = 0
        if self.scroll_y > self.scroll_y_max:
            self.scroll_y = self.scroll_y_max
        elif self.scroll_y < 0:
            self.scroll_y = 0
    
    def running(self, mouse_x, mouse_y, click, scroll):
        if self.is_mouse_over(mouse_x, mouse_y):
            self.detect_touch(mouse_x, mouse_y, click == 1)
            self.scroll(0, scroll)
            return True
        return False

class PalTabel(SubWindow):
    def __init__(self, x, y, w, h, frame = False, color = (255, 255, 255, 255)):
        super().__init__(x, y, w, h, frame, color)
        for id in id_list:
            obj = PalObj(id)
            if id in save:
                obj.isChosen = True
            self.add_obj(obj)
    
    def detect_touch(self, x, y, isClicked=False):
        x -= self.x - self.scroll_x
        y -= self.y - self.scroll_y
        for obj in self.objlist:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                obj.isTouched = True
                if isClicked:
                    obj.isChosen = not obj.isChosen
                    with open('save.txt', 'w') as f:
                        f.write('\n'.join([obj.pal_id for obj in self.get_chosen_objs()]))
            else:
                obj.isTouched = False

    def get_chosen_objs(self):
        for obj in self.objlist:
            if obj.isChosen:
                yield obj

class BoxTable(SubWindow):
    table = None
    is_included_self_lv = False
    xx, yy, ww, hh = border_x, border_y, window_x-breed_col_w, window_y-border_y*2
    def __init__(self, box: PalBox, frame = True, color = (255, 255, 255, 255)):
        super().__init__(BoxTable.xx, BoxTable.yy, BoxTable.ww, BoxTable.hh, frame, color)
        self.box = box
        for i, subbox in enumerate(self.box.my_box[:-1]):
            self.add_obj(LabelObj('第' + str(i) + '代' if i > 0 else '你擁有的', 20), newline = True)
            for j, pal_id in enumerate(subbox):
                self.add_obj(PalObj(pal_id), newline = True if j == 0 else False)
        BoxTable.table = self

    def detect_touch(self, x, y, isClicked=False):
        x -= self.x - self.scroll_x
        y -= self.y - self.scroll_y
        if isClicked: self.clear_frame()
        for obj in self.objlist:
            if type(obj) == LabelObj: continue
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                obj.isTouched = True
                if isClicked:
                    obj.isChosen = not obj.isChosen
                    if obj.isChosen:
                        BreedTable(obj.pal_id, BoxTable.is_included_self_lv)
                    else:
                        BreedTable('')
            else:
                obj.isTouched = False
                if isClicked:
                    obj.isChosen = False
                    
    def get_obj(self, id):
        for obj in self.objlist:
            if type(obj) == LabelObj: continue
            if obj.pal_id == id:
                return obj
        return None
    
    def clear_frame(self):
        for obj in self.objlist:
            if type(obj) == LabelObj: continue
            obj.frame = False

class BreedTable(SubWindow):
    table = None
    xx, yy, ww, hh = window_x-breed_col_w, border_y, breed_col_w-border_x, window_y-border_y*2
    def __init__(self, pal_id, is_included_self_lv = False, frame = True, color = (255, 255, 255, 255)):
        super().__init__(BreedTable.xx, BreedTable.yy, BreedTable.ww, BreedTable.hh, frame, color)
        self.pal_id = pal_id
        if pal_id in id_list:
            self.bread_list = BoxTable.table.box.get_bread_list(pal_id, is_included_self_lv)
            if self.bread_list == []: self.add_obj(LabelObj('   你已經有了', 20))
            for bread in self.bread_list:
                self.add_obj(PalBreedObj(*bread))
        else:
            self.bread_list = []
            self.add_obj(LabelObj('   沒有選擇的帕魯', 20))
        BreedTable.table = self

    def detect_touch(self, x, y, isClicked=False):
        x -= self.x - self.scroll_x
        y -= self.y - self.scroll_y
        if isClicked: BoxTable.table.clear_frame()
        oo = BoxTable.table.get_obj(self.pal_id)
        if oo is not None: oo.isChosen = True
        for obj in self.objlist:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                obj.isTouched = True
                if isClicked:
                    obj.isChosen = not obj.isChosen
                    if obj.isChosen:
                        BoxTable.table.get_obj(obj.pal_id1).frame = obj.isChosen
                        BoxTable.table.get_obj(obj.pal_id2).frame = obj.isChosen
            else:
                obj.isTouched = False
                if isClicked:
                    obj.isChosen = False

pygame.init()
window_surface = pygame.display.set_mode((window_x, window_y))
clock = pygame.time.Clock()
pygame.display.set_caption(caption)
window_surface.fill((255, 255, 255))
game_mode = 'choosing'

def paltb_btn_click():
    global game_mode
    global paltb
    global boxtb
    box = PalBox([obj.pal_id for obj in paltb.get_chosen_objs()])
    BoxTable(box)
    BreedTable('')
    game_mode = 'gaming'

def return_btn_click():
    global game_mode
    game_mode = 'choosing'

def included_lv_btn_click():
    BoxTable.table.clear_frame()
    BoxTable.is_included_self_lv = not BoxTable.is_included_self_lv
    BreedTable(BreedTable.table.pal_id, BoxTable.is_included_self_lv)

paltb_label = LabelObj('選擇你持有的帕魯', 20, 10, 10)
paltb = PalTabel(border_x, border_y, window_x-border_x*2, window_y-border_y*2, True)
paltb_btn = BtnObj('選擇完畢', 20, paltb_btn_click, window_x-100, window_y-45)
boxtb_label = LabelObj('你可以繁殖出的帕魯 (不考慮雌雄的話啦XD)', 20, 10, 10)
breedtb = None
boxtb = None
return_btn = BtnObj('返回', 20, return_btn_click, 10, window_y-45)
included_lv_btn = BtnObj('  含同代  ', 20, included_lv_btn_click, window_x-100, 10)
not_included_lv_btn = BtnObj('不含同代', 20, included_lv_btn_click, window_x-100, 10)

pygame.display.update()

# 事件迴圈監聽事件，進行事件處理
while True:
    # 迭代整個事件迴圈，若有符合事件則對應處理
    for event in pygame.event.get():
        # 當使用者結束視窗，程式也結束
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        mouse_event = [*pygame.mouse.get_pos(), 
                       event.button if event.type == MOUSEBUTTONUP else 0, 
                       event.y if event.type == MOUSEWHEEL else 0]
        window_surface.fill((255, 255, 255))
        if game_mode == 'choosing':
            paltb.running(*mouse_event)
            paltb_btn.running(*mouse_event)
            paltb_label.blitme(window_surface)
            paltb.blitme(window_surface)
            paltb_btn.blitme(window_surface)
        elif game_mode == 'gaming':
            lv_btn = not_included_lv_btn if BoxTable.is_included_self_lv else included_lv_btn
            BoxTable.table.running(*mouse_event)
            BreedTable.table.running(*mouse_event)
            return_btn.running(*mouse_event)
            lv_btn.running(*mouse_event)
            lv_btn = not_included_lv_btn if BoxTable.is_included_self_lv else included_lv_btn
            return_btn.blitme(window_surface)
            boxtb_label.blitme(window_surface)
            BoxTable.table.blitme(window_surface)
            BreedTable.table.blitme(window_surface)
            lv_btn.blitme(window_surface)
            
    pygame.display.update()
    clock.tick(60)
