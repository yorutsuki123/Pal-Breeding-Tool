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

class PalBox():
    def __init__(self, box: list):
        self.my_box = [box]
        self.total_box = []
        self.level = 0

        while self.my_box[self.level] != []:
            self.level += 1
            self.total_box.append({})
            for i in range(self.level):
                for b_id, b_sex in self.my_box[i]:
                    if b_id not in self.total_box[-1]:
                        self.total_box[-1][b_id] = b_sex
                    elif b_sex != self.total_box[-1][b_id]:
                        self.total_box[-1][b_id] = 0
            tmp_ttl_box = list(self.total_box[-1].items())
            self.my_box.append([])
            for p, q in combinations(tmp_ttl_box, 2):
                if -1 <= p[1] + q[1] <= 1 and (p[0], q[0]) in breed_dict:
                    if (breed_dict[p[0], q[0]], 0) not in tmp_ttl_box and (breed_dict[p[0], q[0]], 0) not in self.my_box[self.level]:
                        self.my_box[self.level].append((breed_dict[p[0], q[0]], 0))
            self.my_box[self.level].sort(key=lambda x: id2i(x[0]) * 10 + x[1])
    
    def get_bread_list(self, pal_id: str, sex: int, is_included_self_lv = False):
        lv = self.level
        for i, b in enumerate(self.my_box):
            if (pal_id, sex) in b:
                lv = i
        if not is_included_self_lv:
            if lv == 0:
                return []
            ttl_box_dict = self.total_box[lv - 1]
        else:
            ttl_box_dict = self.total_box[lv]
        s = set()
        for p, q in breed_rev_dict[pal_id]:
            if p in ttl_box_dict and q in ttl_box_dict and -1 <= ttl_box_dict[p] + ttl_box_dict[q] <= 1:
                s.add(tuple(sorted(((p, ttl_box_dict[p]), (q, ttl_box_dict[q])), key=lambda x: id2i(x[0]) * 10 + x[1])))
        return sorted(list(s), key=lambda x: (id2i(x[0][0]) * 10 + x[0][1]) * 10000 + (id2i(x[1][0]) * 10 + x[1][1]))

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

        PalSprite.sprite_dict[self.pal_id] = self

    def get_sprite(pal_id):
        if pal_id not in PalSprite.sprite_dict:
            PalSprite.sprite_dict[pal_id] = PalSprite(pal_id)
        return PalSprite.sprite_dict[pal_id]
    
    def blitme(self, surface, x = 0, y = 0):
        self.canvas.fill((255, 255, 255, 0))
        self.canvas.blit(self.image, (self.canvas.get_width()//2 - self.image.get_width()//2, 3))
        self.canvas.blit(self.label, (self.canvas.get_width()//2 - self.label.get_width()//2, 52))
        surface.blit(self.canvas, (x, y))

class SexSprite():
    sprite_dict = {}
    x_border = 10
    y_border = 10

    def __init__(self, sex):
        self.head_font = pygame.font.Font('font/msjh.ttc', 14)
        self.label = self.head_font.render('♀' if sex == -1 else '♂', True, (255, 0, 0) if sex == -1 else (0, 0, 255))
        self.w = self.label.get_width()
        self.h = self.label.get_height()
        
        SexSprite.sprite_dict[sex] = self

    def get_sprite(sex):
        if sex not in SexSprite.sprite_dict:
            SexSprite.sprite_dict[sex] = SexSprite(sex)
        return SexSprite.sprite_dict[sex]
    
    def blitme(self, surface, x = 0, y = 0):
        surface.blit(self.label, (x, y))

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
    def __init__(self, pal_id, x=0, y=0, sex=0, isshowsex=False, choosing_mode=False):
        self.pal_id = pal_id
        self.sprite = PalSprite.get_sprite(pal_id)
        self.frame = False
        self.pal_sex = sex # 0: both, 1: male, -1: female, choose_mode only 0 
        self.isshowsex = isshowsex
        self.choosing_mode = choosing_mode
        if self.choosing_mode:
            self.touch_objs = {1: TouchableObj(0, 0, self.sprite.w // 2, self.sprite.h), 
                               -1: TouchableObj(self.sprite.w // 2, 0, self.sprite.w // 2, self.sprite.h)}
        super().__init__(x, y, self.sprite.w, self.sprite.h)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        if self.choosing_mode and self.isshowsex:
            self.touch_objs[1].fill()
            self.touch_objs[-1].fill()
            self.touch_objs[1].blitme(self.canvas, 0, 0)
            self.touch_objs[-1].blitme(self.canvas, 0, 0)
        self.sprite.blitme(self.canvas, 0, 0)
        if self.isshowsex:
            if self.pal_sex <= 0 or self.choosing_mode:
                SexSprite.get_sprite(-1).blitme(self.canvas, self.w - SexSprite.get_sprite(-1).w - SexSprite.x_border, SexSprite.y_border)
            if self.pal_sex >= 0 or self.choosing_mode:
                SexSprite.get_sprite(1).blitme(self.canvas, SexSprite.x_border, SexSprite.y_border)
        if self.frame:
            pygame.draw.rect(self.canvas, (0, 0, 0, 100), (0, 0, self.w, self.h), 1)
        surface.blit(self.canvas, (self.x + dx, self.y + dy))

class PalBreedObj(TouchableObj):
    def __init__(self, pal1, pal2, x=0, y=0):
        print(pal1, pal2)
        pal_id1, pal_sex1 = pal1
        pal_id2, pal_sex2 = pal2
        self.pal_id1 = pal_id1
        self.pal_sex1 = pal_sex1
        self.pal_id2 = pal_id2
        self.pal_sex2 = pal_sex2
        self.sprite1 = PalSprite.get_sprite(pal_id1)
        self.sprite2 = PalSprite.get_sprite(pal_id2)
        self.font = pygame.font.Font('font/msjh.ttc', 10)
        self.label = self.font.render('X', True, (0, 0, 0))
        super().__init__(x, y, self.sprite1.w + self.sprite2.w + 10, self.sprite1.h)

    def blitme(self, surface, dx = 0, dy = 0):
        self.fill()
        self.sprite1.blitme(self.canvas, 0, 0)
        if self.pal_sex1 < 0:
            SexSprite.get_sprite(-1).blitme(self.canvas, self.sprite1.w - SexSprite.get_sprite(-1).w - SexSprite.x_border, SexSprite.y_border)
        elif self.pal_sex1 > 0:
            SexSprite.get_sprite(1).blitme(self.canvas, SexSprite.x_border, SexSprite.y_border)
        self.canvas.blit(self.label, (self.sprite1.w, self.sprite1.h//2 - self.label.get_height()//2))
        self.sprite2.blitme(self.canvas, self.sprite1.w + self.label.get_width(), 0)
        if self.pal_sex2 < 0:
            SexSprite.get_sprite(-1).blitme(self.canvas, self.sprite1.w + self.label.get_width() + self.sprite2.w - SexSprite.get_sprite(-1).w - SexSprite.x_border, SexSprite.y_border)
        elif self.pal_sex2 > 0:
            SexSprite.get_sprite(1).blitme(self.canvas, self.sprite1.w + self.label.get_width() + SexSprite.x_border, SexSprite.y_border)
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

class PalTable(SubWindow):
    save = []
    sex_mode = False
    table = None
    def __init__(self, x, y, w, h, frame = False, color = (255, 255, 255, 255)):
        super().__init__(x, y, w, h, frame, color)
        self.read_save()
        for id in id_list:
            obj = PalObj(id, isshowsex=PalTable.sex_mode, choosing_mode=True)
            for save_obj in PalTable.save:
                if id == save_obj[0]:
                    if len(save_obj) > 1:
                        obj.pal_sex = save_obj[1]
                    if not PalTable.sex_mode:
                        obj.isChosen = True
                    else:
                        if obj.pal_sex >= 0:
                            obj.touch_objs[1].isChosen = True
                        if obj.pal_sex <= 0:
                            obj.touch_objs[-1].isChosen = True
                    break
            self.add_obj(obj)
        PalTable.table = self
    
    def detect_touch(self, x, y, isClicked=False):
        x -= self.x - self.scroll_x
        y -= self.y - self.scroll_y
        if not PalTable.sex_mode:
            for obj in self.objlist:
                if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                    obj.isTouched = True
                    if isClicked:
                        obj.isChosen = not obj.isChosen
                        self.write_save()
                else:
                    obj.isTouched = False
        else:
            for obj in self.objlist:
                for oo in obj.touch_objs.values():
                    if obj.x + oo.x <= x <= obj.x + oo.x + oo.w and obj.y + oo.y <= y <= obj.y + oo.y + oo.h:
                        oo.isTouched = True
                        if isClicked:
                            oo.isChosen = not oo.isChosen
                            obj.pal_sex = int(obj.touch_objs[1].isChosen) - int(obj.touch_objs[-1].isChosen)
                            self.write_save()
                    else:
                        oo.isTouched = False

    def get_chosen_objs(self):
        for obj in self.objlist:
            if obj.isChosen or (PalTable.sex_mode and obj.touch_objs[1].isChosen or obj.touch_objs[-1].isChosen):
                yield obj
    
    def read_save(self):
        with open('save.txt', 'a') as f:
            pass
        with open('save.txt', 'r') as f:
            PalTable.save = [x.strip().split(':') for x in f.readlines()]
            PalTable.save = [[x[0], int(x[1])] if len(x) > 1 else [x[0], 0] for x in PalTable.save if x[0] in id_list]
            print(PalTable.save)
    
    def write_save(self):
        with open('save.txt', 'w') as f:
            f.write('\n'.join([':'.join([obj.pal_id, str(obj.pal_sex)]) for obj in self.get_chosen_objs()]))

class BoxTable(SubWindow):
    table = None
    is_included_self_lv = False
    xx, yy, ww, hh = border_x, border_y, window_x-breed_col_w, window_y-border_y*2
    def __init__(self, box: PalBox, frame = True, color = (255, 255, 255, 255)):
        super().__init__(BoxTable.xx, BoxTable.yy, BoxTable.ww, BoxTable.hh, frame, color)
        self.box = box
        for i, subbox in enumerate(self.box.my_box[:-1]):
            self.add_obj(LabelObj('第' + str(i) + '代' if i > 0 else '你擁有的', 20), newline = True)
            for j, (pal_id, pal_sex) in enumerate(subbox):
                self.add_obj(PalObj(pal_id, sex=pal_sex, isshowsex=pal_sex != 0), newline = True if j == 0 else False)
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
                        BreedTable(obj.pal_id, obj.pal_sex, BoxTable.is_included_self_lv)
                    else:
                        BreedTable('', 0)
            else:
                obj.isTouched = False
                if isClicked:
                    obj.isChosen = False
                    
    def get_obj(self, id, sex):
        for obj in self.objlist:
            if type(obj) == LabelObj: continue
            if obj.pal_id == id and obj.pal_sex == sex:
                return obj
        return None
    
    def clear_frame(self):
        for obj in self.objlist:
            if type(obj) == LabelObj: continue
            obj.frame = False

class BreedTable(SubWindow):
    table = None
    xx, yy, ww, hh = window_x-breed_col_w, border_y, breed_col_w-border_x, window_y-border_y*2
    def __init__(self, pal_id, sex, is_included_self_lv = False, frame = True, color = (255, 255, 255, 255)):
        super().__init__(BreedTable.xx, BreedTable.yy, BreedTable.ww, BreedTable.hh, frame, color)
        self.pal_id = pal_id
        self.pal_sex = sex
        if pal_id in id_list:
            self.bread_list = BoxTable.table.box.get_bread_list(pal_id, sex, is_included_self_lv)
            if self.bread_list == []: self.add_obj(LabelObj('   沒有繁殖配方', 20))
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
        oo = BoxTable.table.get_obj(self.pal_id, self.pal_sex)
        if oo is not None: oo.isChosen = True
        for obj in self.objlist:
            if obj.x <= x <= obj.x + obj.w and obj.y <= y <= obj.y + obj.h:
                obj.isTouched = True
                if isClicked:
                    obj.isChosen = not obj.isChosen
                    if obj.isChosen:
                        BoxTable.table.get_obj(obj.pal_id1, obj.pal_sex1).frame = obj.isChosen
                        BoxTable.table.get_obj(obj.pal_id2, obj.pal_sex2).frame = obj.isChosen
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

def next_btn_click():
    global game_mode
    box = PalBox([(obj.pal_id, (obj.pal_sex if PalTable.sex_mode else 0)) for obj in PalTable.table.get_chosen_objs()])
    BoxTable(box)
    BreedTable('', 0)
    game_mode = 'gaming'

def return_btn_click():
    global game_mode
    game_mode = 'choosing'

def sex_btn_click():
    PalTable.sex_mode = not PalTable.sex_mode
    PalTable(border_x, border_y, window_x-border_x*2, window_y-border_y*2, True)

def included_lv_btn_click():
    BoxTable.table.clear_frame()
    BoxTable.is_included_self_lv = not BoxTable.is_included_self_lv
    BreedTable(BreedTable.table.pal_id, BreedTable.table.pal_sex, BoxTable.is_included_self_lv)

paltb_label = LabelObj('選擇你持有的帕魯', 20, 10, 15)
PalTable(border_x, border_y, window_x-border_x*2, window_y-border_y*2, True)
next_btn = BtnObj('選擇完畢', 20, next_btn_click, window_x-100, window_y-45)
sex_btn = BtnObj('切換模式', 20, sex_btn_click, window_x-100, 10)
sex_labels = {True: LabelObj('模式：考慮性別', 20, window_x-250, 15), False:LabelObj('模式：不論性別', 20, window_x-250, 15)}


boxtb_label = LabelObj('你可以繁殖出的帕魯 (不考慮雌雄的話啦XD)', 20, 10, 15)
return_btn = BtnObj('返回', 20, return_btn_click, 10, window_y-45)
lv_btn = BtnObj('切換模式', 20, included_lv_btn_click, window_x-100, 10)
lv_labels = {True: LabelObj('模式：包含同代', 20, window_x-250, 15), False:LabelObj('模式：不含同代', 20, window_x-250, 15)}

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
            PalTable.table.running(*mouse_event)
            next_btn.running(*mouse_event)
            sex_btn.running(*mouse_event)
            sex_labels[PalTable.sex_mode].blitme(window_surface)
            paltb_label.blitme(window_surface)
            PalTable.table.blitme(window_surface)
            next_btn.blitme(window_surface)
            sex_btn.blitme(window_surface)
        elif game_mode == 'gaming':
            BoxTable.table.running(*mouse_event)
            BreedTable.table.running(*mouse_event)
            return_btn.running(*mouse_event)
            lv_btn.running(*mouse_event)
            lv_labels[BoxTable.is_included_self_lv].blitme(window_surface)
            return_btn.blitme(window_surface)
            boxtb_label.blitme(window_surface)
            BoxTable.table.blitme(window_surface)
            BreedTable.table.blitme(window_surface)
            lv_btn.blitme(window_surface)
            
    pygame.display.update()
    clock.tick(60)
