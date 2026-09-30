import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

DB = 'campusflow.db'


def init_db():
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student TEXT NOT NULL,
        department TEXT NOT NULL,
        category TEXT NOT NULL,
        priority TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Open',
        created_at TEXT NOT NULL
    )''')
    con.commit(); con.close()


def add_request():
    student = student_var.get().strip()
    dept = dept_var.get().strip()
    category = category_var.get().strip()
    priority = priority_var.get().strip()
    desc = description.get('1.0', tk.END).strip()
    if not all([student, dept, category, priority, desc]):
        messagebox.showwarning('Missing details', 'Please fill all fields.')
        return
    con = sqlite3.connect(DB)
    con.execute('INSERT INTO requests(student,department,category,priority,description,created_at) VALUES(?,?,?,?,?,?)',
                (student, dept, category, priority, desc, datetime.now().strftime('%Y-%m-%d %H:%M')))
    con.commit(); con.close()
    clear_form(); refresh(); messagebox.showinfo('Submitted', 'Request added to the CampusFlow queue.')


def clear_form():
    student_var.set(''); dept_var.set('MCA'); category_var.set('Academic'); priority_var.set('Normal'); description.delete('1.0', tk.END)


def refresh():
    for item in tree.get_children(): tree.delete(item)
    con = sqlite3.connect(DB)
    rows = con.execute('SELECT id,student,department,category,priority,status,created_at FROM requests ORDER BY CASE priority WHEN "High" THEN 1 WHEN "Normal" THEN 2 ELSE 3 END, id DESC').fetchall()
    con.close()
    for row in rows: tree.insert('', tk.END, values=row)
    total = len(rows); open_count = sum(r[5] == 'Open' for r in rows); high = sum(r[4] == 'High' and r[5] == 'Open' for r in rows)
    stats_var.set(f'Total: {total}    Open: {open_count}    High Priority Open: {high}')


def update_status(status):
    selected = tree.selection()
    if not selected:
        messagebox.showwarning('Select request', 'Select a request first.')
        return
    rid = tree.item(selected[0])['values'][0]
    con = sqlite3.connect(DB); con.execute('UPDATE requests SET status=? WHERE id=?', (status, rid)); con.commit(); con.close(); refresh()


init_db()
root = tk.Tk(); root.title('CampusResolve – Student Issue Tracking and Resolution System'); root.geometry('1080x690'); root.minsize(900, 600)
root.configure(bg='#08131f')
style = ttk.Style(); style.theme_use('clam')
style.configure('Treeview', background='#0f2233', foreground='#eaf4fb', fieldbackground='#0f2233', rowheight=30, borderwidth=0)
style.configure('Treeview.Heading', background='#17344d', foreground='#ffffff', font=('Segoe UI', 10, 'bold'))
style.configure('TCombobox', padding=6)

header = tk.Frame(root, bg='#0b1d2d', height=82); header.pack(fill='x')
tk.Label(header, text='CampusResolve', bg='#0b1d2d', fg='#48e6a5', font=('Segoe UI', 25, 'bold')).pack(anchor='w', padx=28, pady=(15,0))
tk.Label(header, text='Campus Issue Queue', bg='#0b1d2d', fg='#8fa8ba', font=('Segoe UI', 10)).pack(anchor='w', padx=30)

content = tk.Frame(root, bg='#08131f'); content.pack(fill='both', expand=True, padx=25, pady=20)
form = tk.LabelFrame(content, text='  NEW REQUEST  ', bg='#0d2132', fg='#48e6a5', font=('Segoe UI', 10, 'bold'), padx=15, pady=12)
form.pack(fill='x')

student_var=tk.StringVar(); dept_var=tk.StringVar(value='MCA'); category_var=tk.StringVar(value='Academic'); priority_var=tk.StringVar(value='Normal')
fields=[('Student Name',student_var),('Department',dept_var),('Category',category_var),('Priority',priority_var)]
for i,(label,var) in enumerate(fields):
    tk.Label(form,text=label,bg='#0d2132',fg='#bcd0df').grid(row=0,column=i,padx=8,sticky='w')
    if label=='Department': w=ttk.Combobox(form,textvariable=var,values=['MCA','CSE','ECE','AI & DS','B.Sc Data Science'],state='readonly',width=18)
    elif label=='Category': w=ttk.Combobox(form,textvariable=var,values=['Academic','Lab','Infrastructure','Library','Transport','IT Support'],state='readonly',width=18)
    elif label=='Priority': w=ttk.Combobox(form,textvariable=var,values=['Low','Normal','High'],state='readonly',width=18)
    else: w=tk.Entry(form,textvariable=var,bg='#10283b',fg='white',insertbackground='white',relief='flat',width=21)
    w.grid(row=1,column=i,padx=8,pady=(5,10),sticky='ew')
tk.Label(form,text='Description',bg='#0d2132',fg='#bcd0df').grid(row=2,column=0,padx=8,sticky='w')
description=tk.Text(form,height=3,bg='#10283b',fg='white',insertbackground='white',relief='flat'); description.grid(row=3,column=0,columnspan=3,padx=8,pady=5,sticky='ew')
tk.Button(form,text='ADD TO QUEUE',command=add_request,bg='#48e6a5',fg='#04120c',font=('Segoe UI',10,'bold'),relief='flat',padx=18,pady=9).grid(row=3,column=3,padx=8)

bar=tk.Frame(content,bg='#08131f'); bar.pack(fill='x',pady=(18,8))
stats_var=tk.StringVar(value='Total: 0    Open: 0    High Priority Open: 0')
tk.Label(bar,textvariable=stats_var,bg='#08131f',fg='#8fa8ba').pack(side='left')
tk.Button(bar,text='MARK RESOLVED',command=lambda:update_status('Resolved'),bg='#17344d',fg='white',relief='flat',padx=12,pady=6).pack(side='right',padx=5)
tk.Button(bar,text='MARK IN PROGRESS',command=lambda:update_status('In Progress'),bg='#17344d',fg='white',relief='flat',padx=12,pady=6).pack(side='right',padx=5)

cols=('ID','Student','Department','Category','Priority','Status','Created')
tree=ttk.Treeview(content,columns=cols,show='headings')
widths=[45,150,100,125,80,100,130]
for c,w in zip(cols,widths): tree.heading(c,text=c); tree.column(c,width=w,anchor='center' if c in ('ID','Priority','Status') else 'w')
tree.pack(fill='both',expand=True)
refresh(); root.mainloop()
