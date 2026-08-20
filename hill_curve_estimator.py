import math,re,csv,tkinter as tk
from tkinter import ttk,messagebox,filedialog
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2Tk

def num(s):
 s=s.strip().replace('%','').replace(' ','')
 if ',' in s and '.' in s: s=s.replace('.','').replace(',','.') if s.rfind(',')>s.rfind('.') else s.replace(',','')
 elif ',' in s: s=s.replace(',','.')
 return float(s)
def elong(s):
 v=num(s); return v/100 if '%' in s or v>1 else v
def hill_n(E,fy,fu,em):
 if E<=0 or fy<=0 or fu<=fy: raise ValueError('Require E > 0 and UTS > yield > 0.')
 z=(em-fu/E)/.002
 if z<=0: raise ValueError('Maximum elongation must be greater than fu/E.')
 return math.log(z)/math.log(fu/fy)
def parse(txt):
 out=[]
 for line in txt.splitlines():
  p=re.split(r'\t|;',line.strip())
  if len(p)<2:p=re.split(r'\s+',line.strip())
  try: out.append((num(p[0]),num(p[1])))
  except: pass
 return out
class App(tk.Tk):
 def __init__(self):
  super().__init__();self.title('Hill Single-Stage Stress-Strain Estimator');self.geometry('1250x780');self.test=[];self.curve=None;self.ui();self.defaults();self.calc()
 def ui(self):
  self.columnconfigure(1,weight=1);self.rowconfigure(0,weight=1)
  l=ttk.Frame(self,padding=12);l.grid(row=0,column=0,sticky='ns');r=ttk.Frame(self,padding=12);r.grid(row=0,column=1,sticky='nsew');r.rowconfigure(1,weight=1);r.columnconfigure(0,weight=1)
  ttk.Label(l,text='Hill Single-Stage Model',font=('Segoe UI',16,'bold')).grid(row=0,column=0,columnspan=2,sticky='w',pady=(0,14))
  self.e={}
  for i,(k,t) in enumerate([('E',"Young's modulus [MPa]"),('fy','Yield / 0.2% proof [MPa]'),('fu','UTS [MPa]'),('em','Maximum elongation [0.02 or 2%]'),('pts','Curve points')],2):
   ttk.Label(l,text=t).grid(row=i,column=0,sticky='w',pady=4);self.e[k]=ttk.Entry(l,width=18);self.e[k].grid(row=i,column=1,padx=8,pady=4)
  ttk.Label(l,text='Calculated parameters',font=('Segoe UI',11,'bold')).grid(row=8,column=0,columnspan=2,sticky='w',pady=(12,4))
  self.nv=tk.StringVar();self.sv=tk.StringVar()
  ttk.Label(l,text='Hill exponent n').grid(row=9,column=0,sticky='w');ttk.Label(l,textvariable=self.nv,font=('Segoe UI',10,'bold')).grid(row=9,column=1,sticky='e')
  ttk.Label(l,text='Status').grid(row=10,column=0,sticky='w');ttk.Label(l,textvariable=self.sv).grid(row=10,column=1,sticky='e')
  ttk.Button(l,text='Calculate / Update Plot',command=self.calc).grid(row=11,column=0,columnspan=2,sticky='ew',pady=8)
  ttk.Label(l,text='Paste test data',font=('Segoe UI',11,'bold')).grid(row=12,column=0,columnspan=2,sticky='w')
  ttk.Label(l,text='True strain [mm/mm]   True stress [MPa]').grid(row=13,column=0,columnspan=2,sticky='w')
  self.txt=tk.Text(l,width=42,height=17,font=('Consolas',9));self.txt.grid(row=14,column=0,columnspan=2)
  ttk.Button(l,text='Plot Test Data',command=self.loadtest).grid(row=15,column=0,columnspan=2,sticky='ew',pady=5)
  ttk.Button(l,text='Clear Test Data',command=self.clear).grid(row=16,column=0,columnspan=2,sticky='ew',pady=2)
  ttk.Button(l,text='Save Plot',command=self.save).grid(row=17,column=0,columnspan=2,sticky='ew',pady=2)
  ttk.Button(l,text='Export Estimated CSV',command=self.export).grid(row=18,column=0,columnspan=2,sticky='ew',pady=2)
  ttk.Label(r,text='True Stress–Strain Comparison',font=('Segoe UI',13,'bold')).grid(row=0,column=0,sticky='w')
  self.fig=Figure(figsize=(8.5,6),dpi=100);self.ax=self.fig.add_subplot(111);self.canvas=FigureCanvasTkAgg(self.fig,r);self.canvas.get_tk_widget().grid(row=1,column=0,sticky='nsew');NavigationToolbar2Tk(self.canvas,r,pack_toolbar=False).grid(row=2,column=0,sticky='ew')
 def defaults(self):
  for k,v in {'E':'72900','fy':'117','fu':'265','em':'0.02','pts':'200'}.items():self.e[k].insert(0,v)
 def calc(self):
  try:
   E,fy,fu,em=[num(self.e[k].get()) for k in ('E','fy','fu')]+[elong(self.e['em'].get())];pts=int(num(self.e['pts'].get()));n=hill_n(E,fy,fu,em)
   es=[fu*i/(pts-1) for i in range(pts)];ee=[s/E+.002*(s/fy)**n for s in es];ts=[s*(1+x) for s,x in zip(es,ee)];te=[math.log(1+x) for x in ee]
   self.curve=(es,ee,ts,te,n);self.nv.set(f'{n:.5f}');self.sv.set('Calculated');self.redraw()
  except Exception as ex:self.sv.set('Input error');messagebox.showerror('Calculation error',str(ex))
 def redraw(self):
  self.ax.clear();self.ax.grid(True,alpha=.25);self.ax.set_xlabel('True Strain');self.ax.set_ylabel('True Stress [MPa]')
  if self.curve:self.ax.plot(self.curve[3],self.curve[2],lw=2.5,label=f'Hill estimate (n={self.curve[4]:.3f})')
  if self.test:self.ax.plot([x for x,y in self.test],[y for x,y in self.test],lw=1.7,marker='o',markersize=3,markevery=max(1,len(self.test)//80),label=f'Test ({len(self.test)} pts)')
  if self.curve or self.test:self.ax.legend();self.fig.tight_layout();self.canvas.draw_idle()
 def loadtest(self):
  d=parse(self.txt.get('1.0','end'))
  if len(d)<2:return messagebox.showwarning('Test data','Paste two numeric columns: true strain and true stress.')
  self.test=d;self.redraw()
 def clear(self):self.test=[];self.txt.delete('1.0','end');self.redraw()
 def save(self):
  p=filedialog.asksaveasfilename(defaultextension='.png',filetypes=[('PNG','*.png'),('PDF','*.pdf'),('SVG','*.svg')])
  if p:self.fig.savefig(p,dpi=250,bbox_inches='tight')
 def export(self):
  if not self.curve:return
  p=filedialog.asksaveasfilename(defaultextension='.csv',filetypes=[('CSV','*.csv')])
  if p:
   es,ee,ts,te,n=self.curve
   with open(p,'w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['Engineering Strain','Engineering Stress [MPa]','True Strain','True Stress [MPa]'])
    w.writerows(zip(ee,es,te,ts))
if __name__=='__main__':App().mainloop()
