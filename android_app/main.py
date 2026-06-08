 # -*- coding: utf-8 -*-
 import os, string, secrets, datetime, sqlite3
 from kivy.app import App
 from kivy.uix.screenmanager import ScreenManager, Screen
 from kivy.uix.boxlayout import BoxLayout
 from kivy.uix.gridlayout import GridLayout
 from kivy.uix.scrollview import ScrollView
 from kivy.uix.popup import Popup
 from kivy.uix.label import Label
 from kivy.uix.button import Button
 from kivy.uix.textinput import TextInput
 from kivy.uix.checkbox import CheckBox
 from kivy.uix.slider import Slider
 from kivy.uix.spinner import Spinner
 from kivy.uix.progressbar import ProgressBar
 from kivy.core.clipboard import Clipboard
 from kivy.metrics import dp
 from kivy.utils import get_color_from_hex
 
 try: from cryptography.fernet import Fernet; HAS_CRYPTO = True
 except ImportError: HAS_CRYPTO = False
 
 DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passwords.db")
 KEY = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".encrypt_key")
 
 def get_cipher():
     if not HAS_CRYPTO: return None
     if os.path.exists(KEY):
         with open(KEY, "rb") as f: key = f.read()
     else:
         key = Fernet.generate_key()
         with open(KEY, "wb") as f: f.write(key)
     return Fernet(key)
 
 def enc(plain):
     c = get_cipher(); return c.encrypt(plain.encode()) if c else plain.encode()
 def dec(data):
     c = get_cipher(); return c.decrypt(data).decode() if c else data.decode()
 def init_db():
     c = sqlite3.connect(DB)
     c.execute("CREATE TABLE IF NOT EXISTS passwords (id INTEGER PRIMARY KEY AUTOINCREMENT, site_name TEXT, url TEXT, username TEXT, enc BLOB, note TEXT, ct TEXT, ut TEXT)")
     c.commit(); c.close()
 def add_pw(site, url, user, pwd, note=""):
     now = datetime.datetime.now().isoformat()
     c = sqlite3.connect(DB)
     c.execute("INSERT INTO passwords (site_name,url,username,enc,note,ct,ut) VALUES (?,?,?,?,?,?,?)", (site,url,user,enc(pwd),note,now,now))
     c.commit(); c.close()
 def upd_pw(rid, site, url, user, pwd, note=""):
     now = datetime.datetime.now().isoformat()
     c = sqlite3.connect(DB)
     c.execute("UPDATE passwords SET site_name=?,url=?,username=?,enc=?,note=?,ut=? WHERE id=?", (site,url,user,enc(pwd),note,now,rid))
     c.commit(); c.close()
 def del_pw(rid):
     c = sqlite3.connect(DB); c.execute("DELETE FROM passwords WHERE id=?", (rid,)); c.commit(); c.close()
 def list_pw(kw=""):
     c = sqlite3.connect(DB)
     if kw: rs = c.execute("SELECT * FROM passwords WHERE site_name LIKE ? OR username LIKE ? ORDER BY ut DESC", (f"%{kw}%", f"%{kw}%")).fetchall()
     else: rs = c.execute("SELECT * FROM passwords ORDER BY ut DESC").fetchall()
     c.close()
     return [{"id":r[0],"site":r[1],"url":r[2],"user":r[3],"pwd":dec(r[4]),"note":r[5],"ct":r[6]} for r in rs]
 def cnt_pw():
     c = sqlite3.connect(DB); n = c.execute("SELECT COUNT(*) FROM passwords").fetchone()[0]; c.close(); return n
 
 PRESETS = {
     "自定义": {"s":"","u":"","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":""},
     "Google": {"s":"Google","u":"https://accounts.google.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "GitHub": {"s":"GitHub","u":"https://github.com","l":20,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"建议 15 位以上"},
     "Microsoft": {"s":"Microsoft","u":"https://account.microsoft.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "Apple ID": {"s":"Apple ID","u":"https://appleid.apple.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "Twitter/X": {"s":"Twitter/X","u":"https://x.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "Facebook": {"s":"Facebook","u":"https://www.facebook.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 6 位"},
     "Instagram": {"s":"Instagram","u":"https://www.instagram.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 6 位"},
     "Amazon": {"s":"Amazon","u":"https://www.amazon.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 6 位"},
     "Netflix": {"s":"Netflix","u":"https://www.netflix.com","l":12,"U":1,"L":1,"D":1,"S":0,"c":"","e":0,"n":"不支持特殊字符"},
     "PayPal": {"s":"PayPal","u":"https://www.paypal.com","l":20,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "Steam": {"s":"Steam","u":"https://store.steampowered.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "QQ": {"s":"QQ","u":"https://im.qq.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"8-16 位"},
     "微信": {"s":"微信","u":"","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"8-16 位"},
     "支付宝": {"s":"支付宝","u":"https://www.alipay.com","l":20,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"至少 8 位"},
     "百度": {"s":"百度","u":"https://www.baidu.com","l":14,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"6-14 位"},
     "Bilibili": {"s":"Bilibili","u":"https://www.bilibili.com","l":16,"U":1,"L":1,"D":1,"S":1,"c":"","e":0,"n":"6-16 位"},
 }
 
 def gen_pwd(l=16, U=1, L=1, D=1, S=1, cs="", e=0):
     ch = ""
     if U: ch += string.ascii_uppercase
     if L: ch += string.ascii_lowercase
     if D: ch += string.digits
     if S: ch += "!@#$%^&*()_+-=[]{}|;:,.<>?"
     if cs: ch = cs
     if e:
         for c in "1lI0O": ch = ch.replace(c, "")
     if not ch: ch = string.ascii_letters + string.digits
     return "".join(secrets.choice(ch) for _ in range(l))
 
 def strength(pwd):
     s = 0
     if len(pwd) >= 8: s += 10
     if len(pwd) >= 12: s += 10
     if len(pwd) >= 16: s += 10
     if any(c.isupper() for c in pwd): s += 15
     if any(c.islower() for c in pwd): s += 15
     if any(c.isdigit() for c in pwd): s += 15
     if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd): s += 15
     if len(set(pwd)) > len(pwd) * 0.7: s += 10
     return min(s, 100)
 
 class GenScreen(Screen):
     def __init__(self, **kw):
         super().__init__(**kw); self.pwd = ""
         sv = ScrollView()
         bx = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8), size_hint_y=None)
         bx.bind(minimum_height=bx.setter("height"))
         bx.add_widget(Label(text="网站预设", size_hint_y=None, height=dp(22), bold=True))
         self.sp = Spinner(text="自定义", values=list(PRESETS.keys()), size_hint_y=None, height=dp(42))
         self.sp.bind(text=self.on_preset); bx.add_widget(self.sp)
         self.note = Label(text="", size_hint_y=None, height=dp(18), font_size="11sp", color=get_color_from_hex("#888"))
         bx.add_widget(self.note)
         bx.add_widget(Label(text="密码长度", size_hint_y=None, height=dp(22), bold=True))
         self.sl = Slider(min=4, max=128, value=16, step=1, size_hint_y=None, height=dp(40))
         self.ll = Label(text="16 位", size_hint_y=None, height=dp(18), font_size="12sp")
         self.sl.bind(value=lambda s, v: setattr(self.ll, "text", f"{int(v)} 位"))
         bx.add_widget(self.sl); bx.add_widget(self.ll)
         bx.add_widget(Label(text="字符类型", size_hint_y=None, height=dp(22), bold=True))
         g = GridLayout(cols=2, size_hint_y=None, height=dp(120), spacing=dp(2))
         self.cU, self.cL, self.cD, self.cS = CheckBox(active=1), CheckBox(active=1), CheckBox(active=1), CheckBox(active=1)
         for t, c in [("大写 (A-Z)", self.cU), ("小写 (a-z)", self.cL), ("数字 (0-9)", self.cD), ("特殊 (!@#)", self.cS)]:
             r = BoxLayout(size_hint_y=None, height=dp(28)); r.add_widget(Label(text=t, font_size="12sp")); r.add_widget(c); g.add_widget(r)
         bx.add_widget(g)
         self.cE = CheckBox(active=0, size_hint_y=None, height=dp(28))
         r = BoxLayout(size_hint_y=None, height=dp(28)); r.add_widget(Label(text="排除相似字符", font_size="12sp")); r.add_widget(self.cE); bx.add_widget(r)
         bx.add_widget(Label(text="自定义字符集", size_hint_y=None, height=dp(22), bold=True))
         self.ci = TextInput(hint_text="留空使用上方选项", size_hint_y=None, height=dp(40), multiline=False)
         self.ci.bind(text=lambda x,y: self.do_gen()); bx.add_widget(self.ci)
         bx.add_widget(Label(text="生成的密码", size_hint_y=None, height=dp(22), bold=True))
         self.pt = TextInput(text="", readonly=True, size_hint_y=None, height=dp(48), font_size="16sp", multiline=False)
         bx.add_widget(self.pt)
         self.bar = ProgressBar(max=100, value=0, size_hint_y=None, height=dp(16)); bx.add_widget(self.bar)
         btns = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
         btns.add_widget(Button(text="生成密码", on_press=lambda x: self.do_gen()))
         btns.add_widget(Button(text="复制", on_press=lambda x: Clipboard.copy(self.pwd) if self.pwd else None))
         bx.add_widget(btns)
         bx.add_widget(Button(text="保存到密码管理器", size_hint_y=None, height=dp(46), background_color=get_color_from_hex("#2196F3"), on_press=self.on_save))
         sv.add_widget(bx); self.add_widget(sv); self.do_gen()
     
     def on_preset(self, sp, text):
         p = PRESETS.get(text, {}); self.sl.value = p.get("l", 16)
         self.cU.active = p.get("U", 1); self.cL.active = p.get("L", 1)
         self.cD.active = p.get("D", 1); self.cS.active = p.get("S", 1)
         self.ci.text = p.get("c", ""); self.cE.active = p.get("e", 0)
         self.note.text = p.get("n", ""); self.do_gen()
     
     def do_gen(self, *a):
         self.pwd = gen_pwd(l=int(self.sl.value), U=self.cU.active, L=self.cL.active, D=self.cD.active, S=self.cS.active, cs=self.ci.text, e=self.cE.active)
         self.pt.text = self.pwd; self.bar.value = strength(self.pwd)
     
     def on_save(self, *a):
         if not self.pwd: return
         pn = self.sp.text; p = PRESETS.get(pn, {})
         site = p.get("s", "") if pn != "自定义" else ""
         url = p.get("u", "") if pn != "自定义" else ""
         self.manager.get_screen("mgr").open_add(self.pwd, site, url)
         self.manager.current = "mgr"
 
 class MgrScreen(Screen):
     def __init__(self, **kw):
         super().__init__(**kw)
         bx = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))
         sr = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(4))
         self.kw_inp = TextInput(hint_text="搜索网站名或用户名...", multiline=False, size_hint_y=None, height=dp(40))
         sr.add_widget(self.kw_inp)
         sr.add_widget(Button(text="搜索", size_hint_x=None, width=dp(60), on_press=lambda x: self.refresh()))
         sr.add_widget(Button(text="清除", size_hint_x=None, width=dp(60), on_press=lambda x: (setattr(self.kw_inp, "text", ""), self.refresh())))
         bx.add_widget(sr)
         self.list_bx = BoxLayout(orientation="vertical", spacing=dp(4), size_hint_y=None)
         self.list_bx.bind(minimum_height=self.list_bx.setter("height"))
         sv = ScrollView(); sv.add_widget(self.list_bx); bx.add_widget(sv)
         ab = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
         ab.add_widget(Button(text="新增记录", on_press=lambda x: self.open_add()))
         ab.add_widget(Button(text="导出", on_press=self.export_data))
         bx.add_widget(ab)
         self.add_widget(bx)
     
     def on_enter(self, *a): self.refresh()
     
     def refresh(self):
         self.list_bx.clear_widgets()
         items = list_pw(self.kw_inp.text.strip())
         for r in items:
             row = BoxLayout(size_hint_y=None, height=dp(48), padding=dp(6), spacing=dp(4))
             row.add_widget(Label(text=r["site"], size_hint_x=0.3, font_size="13sp", shorten=True))
             row.add_widget(Label(text=r["user"], size_hint_x=0.3, font_size="12sp", shorten=True, color=get_color_from_hex("#888")))
             row.add_widget(Button(text="复制", size_hint_x=0.2, font_size="11sp", on_press=lambda x, r=r: Clipboard.copy(r["pwd"])))
             row.add_widget(Button(text="编辑", size_hint_x=0.1, font_size="11sp", on_press=lambda x, r=r: self.open_edit(r)))
             row.add_widget(Button(text="删除", size_hint_x=0.1, font_size="11sp", background_color=get_color_from_hex("#F44336"), on_press=lambda x, r=r: self.confirm_del(r)))
             self.list_bx.add_widget(row)
     
     def open_add(self, pwd="", site="", url=""):
         box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
         box.add_widget(Label(text="新增密码记录", bold=True, size_hint_y=None, height=dp(28)))
         site_inp = TextInput(text=site, hint_text="网站/应用名", size_hint_y=None, height=dp(40), multiline=False)
         url_inp = TextInput(text=url, hint_text="网址", size_hint_y=None, height=dp(40), multiline=False)
         user_inp = TextInput(hint_text="用户名/邮箱", size_hint_y=None, height=dp(40), multiline=False)
         pwd_inp = TextInput(text=pwd, hint_text="密码", size_hint_y=None, height=dp(40), multiline=False)
         note_inp = TextInput(hint_text="备注", size_hint_y=None, height=dp(60), multiline=True)
         if site: box.add_widget(Button(text="还原预设网站名和网址", size_hint_y=None, height=dp(32), background_color=get_color_from_hex("#607D8B"), on_press=lambda x: [setattr(site_inp, "text", site), setattr(url_inp, "text", url)]))
         for t, w in [("网站名 *", site_inp), ("网址", url_inp), ("用户名", user_inp), ("密码 *", pwd_inp), ("备注", note_inp)]:
             box.add_widget(Label(text=t, size_hint_y=None, height=dp(20), font_size="12sp"))
             box.add_widget(w)
         btn = Button(text="保存", size_hint_y=None, height=dp(40), background_color=get_color_from_hex("#4CAF50"),
             on_press=lambda x: self.do_save(None, site_inp.text, url_inp.text, user_inp.text, pwd_inp.text, note_inp.text))
         box.add_widget(btn)
         self.pop = Popup(title="", content=box, size_hint=(0.9, 0.9), auto_dismiss=True)
         self.pop.open()
     
     def do_save(self, rid, site, url, user, pwd, note):
         if not site or not pwd: return
         if rid: upd_pw(rid, site, url, user, pwd, note)
         else: add_pw(site, url, user, pwd, note)
         self.pop.dismiss(); self.refresh()
     
     def open_edit(self, r):
         box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
         box.add_widget(Label(text="编辑密码记录", bold=True, size_hint_y=None, height=dp(28)))
         site_inp = TextInput(text=r["site"], hint_text="网站/应用名", size_hint_y=None, height=dp(40), multiline=False)
         url_inp = TextInput(text=r["url"], hint_text="网址", size_hint_y=None, height=dp(40), multiline=False)
         user_inp = TextInput(text=r["user"], hint_text="用户名/邮箱", size_hint_y=None, height=dp(40), multiline=False)
         pwd_inp = TextInput(text=r["pwd"], hint_text="密码", size_hint_y=None, height=dp(40), multiline=False)
         note_inp = TextInput(text=r["note"], hint_text="备注", size_hint_y=None, height=dp(60), multiline=True)
         for t, w in [("网站名 *", site_inp), ("网址", url_inp), ("用户名", user_inp), ("密码 *", pwd_inp), ("备注", note_inp)]:
             box.add_widget(Label(text=t, size_hint_y=None, height=dp(20), font_size="12sp"))
             box.add_widget(w)
         btn = Button(text="更新", size_hint_y=None, height=dp(40), background_color=get_color_from_hex("#4CAF50"),
             on_press=lambda x: self.do_save(r["id"], site_inp.text, url_inp.text, user_inp.text, pwd_inp.text, note_inp.text))
         box.add_widget(btn)
         self.pop = Popup(title="", content=box, size_hint=(0.9, 0.9), auto_dismiss=True)
         self.pop.open()
     
     def confirm_del(self, r):
         box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
         box.add_widget(Label(text=f'确定要删除 "{r["site"]}" 的记录吗？', size_hint_y=None, height=dp(40)))
         btns = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
         btns.add_widget(Button(text="取消", on_press=lambda x: self.pop.dismiss()))
         btns.add_widget(Button(text="删除", background_color=get_color_from_hex("#F44336"), on_press=lambda x: (del_pw(r["id"]), self.pop.dismiss(), self.refresh())))
         box.add_widget(btns)
         self.pop = Popup(title="确认删除", content=box, size_hint=(0.8, 0.3), auto_dismiss=True)
         self.pop.open()
     
     def export_data(self, *a):
         items = list_pw()
         data = json.dumps([{"site": r["site"], "url": r["url"], "user": r["user"], "pwd": r["pwd"], "note": r["note"]} for r in items], ensure_ascii=False, indent=2)
         Clipboard.copy(data)
         box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
         box.add_widget(Label(text=f"已导出 {len(items)} 条记录到剪贴板", size_hint_y=None, height=dp(40)))
         box.add_widget(Button(text="确定", size_hint_y=None, height=dp(40), on_press=lambda x: self.pop.dismiss()))
         self.pop = Popup(title="导出成功", content=box, size_hint=(0.8, 0.3), auto_dismiss=True)
         self.pop.open()
 
 class PasswordApp(App):
     def build(self):
         init_db()
         self.title = "密码生成与管理器"
         sm = ScreenManager()
         sm.add_widget(GenScreen(name="gen"))
         sm.add_widget(MgrScreen(name="mgr"))
         return sm
 
 if __name__ == "__main__":
     PasswordApp().run()
