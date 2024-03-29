# /usr/bin/python3

import os
import tkinter as tk
from tkinter import messagebox
import tkinter.ttk as ttk
from tkinter import filedialog
from pygubu.widgets.tkscrolledframe import TkScrolledFrame
import agol
import log
import util
import logging
from datetime import datetime
import json
import webbrowser
import pathlib

# TODO: Multithreading on item load
# TODO: Remove/cleanup packages from AGOL

PROJECT_PATH = pathlib.Path(__file__).parent
CONFIG_PATH = f"{PROJECT_PATH}/config"
TITLE = "Backup Manager GUI"
CONFIG_BLANK = {"label": "Unnamed", "outdir": '', "portal": "", "pword": "", "uname": "", "admin": {"hours_diff": 168.0, "component": ['all'], "options": ["all"]}, "items": {}}
FREQUENCY_OPTIONS = {'Ignore': 0.0, 'Hourly': 1.0, 'Daily': 24.0, 'Weekly': 168.0, 'Fortnightly': 336.0, 'Montly': 730.0, 'Quarterly': 2190.0, 'Yearly': 8760.0, 'Custom': None}


class BackupMgrGUI:
    """AGOL Backup Manager GUI
    """
    _cfg = CONFIG_BLANK
    _items = {}
    _ago = None

    def __init__(self, master: tk.Tk, logger: logging):
        """Initiate the Backup Manager GUI

        Args:
            master (tk.Tk): master form class
            logger (logging): Logging object
        """
        # Build UI
        self._gui = master
        # Show loader
        self._gui.geometry('1080x720')
        self._gui.minsize(width=480, height=360)
        self._gui.iconbitmap('img/backup_cfg_mgr.ico')
        self._gui.wm_title("Backup Manager GUI")
        self._gui.columnconfigure(0, weight=1)
        self._gui.columnconfigure(1, weight=1)
        self._gui.rowconfigure(6, weight=1)
        # Capture logger
        self._logger = logger
        # Setup vars
        self._exportadmin = tk.BooleanVar(value=True)
        self._exportme = tk.BooleanVar(value=True)
        self._exportusers = tk.BooleanVar(value=True)
        self._exportgroups = tk.BooleanVar(value=True)
        self._adminoptions = tk.StringVar(value='all')
        self._adminfreq = tk.StringVar(value='Daily')
        self._adminhours = tk.DoubleVar(value=24.0)
        # Setup form variables
        self._lastrun = tk.StringVar(value='Never')
        self._label = tk.StringVar()
        self._location = tk.StringVar(value='Not set')
        self._outdir = tk.StringVar()
        self._cfgpath = tk.StringVar()
        self._pword = tk.StringVar()
        self._filter = tk.StringVar()
        self._uname = tk.StringVar()
        self._portal = tk.StringVar()
        self._usegit = tk.BooleanVar(value=True)
        self._method = tk.IntVar(value=2)
        # Setup menu
        menu_main = tk.Menu(self._gui)
        menu_file = tk.Menu(menu_main, tearoff=0)
        # Add menu commands
        menu_file.add_command(label="New", command=self.config_new)
        menu_file.add_command(label="Open", command=self.config_load)
        menu_file.add_command(label="Save", command=self.config_save)
        menu_file.add_command(label="Save As", command=self.config_saveas)
        menu_file.add_separator()
        menu_file.add_command(label="Exit", command=self._gui.quit)
        menu_main.add_cascade(label="File", menu=menu_file)
        # Add run commands
        menu_run = tk.Menu(menu_main, tearoff=0)
        menu_run.add_command(label="Run Now", command=self._runnow)
        menu_main.add_cascade(label="Run", menu=menu_run)
        # Add Menu to GUI
        self._gui.config(menu=menu_main)
        self._gui.configure()
        # Setup connection frame
        frame_settings = tk.Frame(self._gui)
        frame_settings.columnconfigure(1, weight=1)
        frame_settings.columnconfigure(4, weight=1)
        frame_settings.columnconfigure(7, weight=1)
        frame_settings.grid(column=0, row=3, padx=2, pady=2, sticky='ew', columnspan=3)
        # Setup connection header
        hdr_connection = tk.Label(frame_settings)
        hdr_connection.configure(font='{Arial} 10 {bold}', justify='left', text='Settings')
        hdr_connection.grid(column=0, row=0, sticky='w', columnspan=9)
        # Setup label prompt
        lbl_label = tk.Label(frame_settings)
        lbl_label.configure(font='{Arial} 8 {bold}', text='Label:')
        lbl_label.grid(column=0, row=1, sticky='w')
        txt_label = tk.Entry(frame_settings)
        txt_label.configure(font='{Arial} 8 {}', textvariable=self._label)
        txt_label.grid(column=1, padx=2, pady=2, row=1, sticky='ew', columnspan=2)
        # Setup lastrun data
        lbl_cfg = tk.Label(frame_settings)
        lbl_cfg.configure(font='{Arial} 8 {bold}', text='Config File:')
        lbl_cfg.grid(column=3, row=1, sticky='w')
        txt_cfg = tk.Label(frame_settings)
        txt_cfg.configure(font='{Arial} 8 {}', justify='left', textvariable=self._cfgpath)
        txt_cfg.grid(column=4, row=1, sticky='w', columnspan=3, padx=2, pady=2)
        # Setup use git flag
        chk_usegit = tk.Checkbutton(frame_settings)
        chk_usegit.configure(font='{Arial} 8 {}', justify='left', text='Use git for change tracking', variable=self._usegit)
        chk_usegit.grid(column=7, row=1, sticky='e', columnspan=2)
        # Setup outdir prompt
        lbl_outdir = tk.Label(frame_settings)
        lbl_outdir.configure(font='{Arial} 8 {bold}', text='Output Dir:')
        lbl_outdir.grid(column=0, row=2, sticky='w')
        txt_outdir = tk.Entry(frame_settings)
        txt_outdir.configure(font='{Arial} 8 {}', textvariable=self._outdir)
        txt_outdir.grid(column=1, padx=1, pady=2, row=2, sticky='ew', columnspan=7)
        btn_outdir = tk.Button(frame_settings)
        btn_outdir.configure(font='{Arial} 8 {}', text='Browse', command=self._browse)
        btn_outdir.grid(column=8, row=2, sticky='ew', padx=2, pady=2)
        # Setup portal/agol vars
        hdr_connection = tk.Label(frame_settings)
        hdr_connection.configure(font='{Arial} 10 {bold}', justify='left', text='AGOL/Portal Connection')
        hdr_connection.grid(column=0, row=4, sticky='w', columnspan=9)
        # Setup portal promt
        lbl_portal = tk.Label(frame_settings)
        lbl_portal.configure(font='{Arial} 8 {bold}', text='Portal:')
        lbl_portal.grid(column=0, row=5, sticky='w')
        self.txt_portal = tk.Entry(frame_settings)
        self.txt_portal.configure(font='{Arial} 8 {}', textvariable=self._portal)
        self.txt_portal.grid(column=1, padx=2, pady=2, row=5, sticky='ew', columnspan=2)
        # Setup username promt
        lbl_uname = tk.Label(frame_settings)
        lbl_uname.configure(font='{Arial} 8 {bold}', text='Username:')
        lbl_uname.grid(column=3, row=5, sticky='w')
        self.txt_uname = tk.Entry(frame_settings)
        self.txt_uname.configure(font='{Arial} 8 {}', textvariable=self._uname)
        self.txt_uname.grid(column=4, padx=2, pady=2, row=5, sticky='ew', columnspan=2)
        # Setup password promt
        lbl_pword = tk.Label(frame_settings)
        lbl_pword.configure(font='{Arial} 8 {bold}', text='Password:')
        lbl_pword.grid(column=6, row=5, sticky='w')
        self.txt_pword = tk.Entry(frame_settings)
        self.txt_pword.configure(font='{Arial} 8 {}', show='•', textvariable=self._pword)
        self.txt_pword.grid(column=7, padx=2, pady=2, row=5, sticky='ew')
        # Setup connect button
        btn_connect = tk.Button(frame_settings)
        btn_connect.configure(font='{Arial} 8 {}', text='Connect', command=self._agol_connect)
        btn_connect.grid(column=8, row=5, sticky='ew', padx=2, pady=2,)
        # Setup items frame
        frame_items = tk.Frame(self._gui)
        frame_items.columnconfigure(1, weight=2)
        frame_items.columnconfigure(3, weight=1)
        frame_items.grid(column=0, row=5, padx=2, pady=2, sticky='ew', columnspan=9)
        # Setup items header
        hdr_items = tk.Label(frame_items)
        hdr_items.configure(font='{Arial} 10 {bold}', justify='left', text='Item Config')
        hdr_items.grid(column=0, row=0, padx=2, pady=2, sticky='w')
        lbl_pword = tk.Label(frame_items)
        lbl_pword.configure(font='{Arial} 8 {bold}', text='Filter')
        lbl_pword.grid(column=2, row=0, sticky='e')
        self.txt_filter = tk.Entry(frame_items)
        self._filter.trace_add("write", self._filteritems)
        self.txt_filter.configure(font='{Arial} 8 {}', textvariable=self._filter)
        self.txt_filter.grid(column=3, padx=2, pady=2, row=0, sticky='ew')
        btn_refresh = tk.Button(frame_items)
        btn_refresh.configure(font='{Arial} 8 {}', text='Refresh', command=self._loaditems)
        btn_refresh.grid(column=4, row=0, sticky='e', padx=2, pady=2)
        # Setup items frame
        self.frame_items = TkScrolledFrame(self._gui, scrolltype='both')
        self.frame_items.innerframe.configure(bg='white')
        self.frame_items.innerframe.columnconfigure(0, weight=1)
        self.frame_items.configure(usemousewheel=True)
        self.frame_items.grid(column=0, row=6, padx=5, pady=5, sticky='nesw', columnspan=2)
        # Set main window
        self.mainwindow = self._gui

    def _toggleadmin(self, n, m, x):
        # Conditionally show/hide admin window
        if self._exportadmin.get():
            self.frame_admin.grid()
        else:
            self.frame_admin.grid_remove()

    def _populate_hours(self, source_var: tk.StringVar, target_var: tk.StringVar, target_ctl: tk.Entry):
        """Handler to populate hours on the form based on frequency combobox

        Args:
            source_var (tk.StringVar): Frequency combo box variable
            target_var (tk.StringVar): Hours text box variable
            target_ctl (tk.Entry): Hours entry control to update
        """
        # Update the hours of the target field if valid
        freq = source_var.get()
        hours = FREQUENCY_OPTIONS[freq]
        # Update hours
        if hours or (hours == 0.0):
            target_var.set(hours)
            target_ctl.configure(state="readonly")
        else:
            target_ctl.configure(state="normal")

    def config_new(self, e=None):
        """Sets up a new config item

        Args:
            e ([type], optional): Event info, not used. Defaults to None.
        """
        # Wipe config
        self._cfg = CONFIG_BLANK
        self._cfgpath.set(None)
        self._location.set('Not set')
        # Update title
        self._update_title('')
        # Update form
        self._load()

    def _update_title(self, info: str):
        """Update form title with config path (if supplied)
        """
        # Update title
        if info:
            self._gui.wm_title(f"{TITLE} ({info})")
        else:
            self._gui.wm_title(TITLE)

    def _config_load(self, path: str):
        """Loads config item from path

        Args:
            path (str): Path to config file to load
        """
        # Setup abs path
        path = os.path.abspath(path)
        # Open and load config
        try:
            with open(path, "r") as f:
                self._cfg = json.load(f)
        except json.decoder.JSONDecodeError as err:
            messagebox.showerror(
                "Load Failed", f"Config file is not formatted correctly.\n{str(err)}")
            self._cfgpath.set(None)
            return
        except IOError as err:
            messagebox.showerror(
                "Load Failed", f"Load was not successful.\n{str(err)}")
            self._cfgpath.set(None)
            return
        # Update loaded path
        self._cfgpath.set(path)
        # Update config path
        self._location.set(path)
        # Update form
        self._load()
        # Update page title
        msg = os.path.basename(self._cfgpath.get())
        self._update_title(msg)

    def config_load(self, e=None):
        """Prompt for a path to load config file from

        Args:
            e ([type], optional): Event info, not used. Defaults to None.
        """
        # Load config
        cfg_path = filedialog.askopenfilename(
            title='Open config file', initialdir=CONFIG_PATH, filetypes=[('Config Files', '*.json')])
        # Load data
        self._config_load(cfg_path)

    def _config_save(self, path: str):
        """Saves a config item to path

        Args:
            path (str): Path to config file to save
        """
        # Update config items
        self._cfg["label"] = self._label.get()
        self._cfg["outdir"] = self._outdir.get()
        self._cfg["pword"] = self._pword.get()
        self._cfg["uname"] = self._uname.get()
        self._cfg["portal"] = self._portal.get()
        self._cfg["usegit"] = self._usegit.get()
        # Check if admin is to be exported
        if self._exportadmin.get():
            # Update admin
            admin = {}
            # Update admin component
            comp = []
            if self._exportme.get():
                comp.append('self')
            if self._exportusers.get():
                comp.append('users')
            if self._exportgroups.get():
                comp.append('groups')
            admin['component'] = comp
            # Update admin options
            admin['options'] = self._adminoptions.get().split(',')
            # Update admin hours
            admin['hours_diff'] = self._adminhours.get()
            # Update admin items
            self._cfg['admin'] = admin
        else:
            # Set admin to blank
            self._cfg['admin'] = None
        # Process items
        for k, i in self._items.items():
            # Check if export is requested
            if i['selected'].get():
                # Get item
                try:
                    itm = self._cfg['items'][i['id']]
                except KeyError:
                    itm = {}
                    self._cfg['items'][i['id']] = itm
                # Update data
                itm['hours_diff'] = i['hours_diff'].get()
                itm['options'] = i['options'].get().split(',')
                itm['format'] = i['format'].get()
            else:
                # Remove item
                try:
                    del self._cfg['items'][i['id']]
                except KeyError:
                    pass
        # Update config items
        try:
            # Save object
            util.export_obj(path, self._cfg)
            # Update page title
            msg = os.path.basename(self._cfgpath.get())
            self._update_title(msg)
        except IOError as err:
            # Display save failed error
            messagebox.showerror(
                "Save Failed", f"Save was not successful.\n{str(err)}")

    def config_saveas(self, e=None):
        """Prompt for a path to save config file to

        Args:
            e ([type], optional): Event info, not used. Defaults to None.
        """
        # Get save path
        p = filedialog.asksaveasfilename(
            title='Save config file', initialdir=CONFIG_PATH,
            initialfile='config.json', defaultextension='.json',
            filetypes=[('Config Files', '*.json')])
        # Attempt save of file to new location
        if p:
            self._config_save(p)
            # Update path variable
            self._cfgpath.set(p)

    def config_save(self, e=None):
        """Saves config or if path not available, prompt for a path to save config file to

        Args:
            e ([type], optional): Event info, not used. Defaults to None.
        """
        # Check path has been set
        if not self._cfgpath.get():
            # If no path, use saveas
            self.config_saveas()
        else:
            # Save is path exists
            self._config_save(self._cfgpath.get())

    def _agol_connect(self, init: bool = False):
        """Connects to AGOL or Portal instance

        Args:
            init (bool, optional): Flag to indicate if this call is being made in init. Defaults to False.
        """
        # Attempt connection to AGOL
        self._ago = agol.Agol(self._portal.get(), self._uname.get(), self._pword.get(), logger)
        # Test GIS connection
        if not self._ago.gis:
            # Update text colour to indicate failure
            self.txt_portal.configure(foreground='#d7191c')
            self.txt_uname.configure(foreground='#d7191c')
            self.txt_pword.configure(foreground='#d7191c')
            # Clear items
            self._clearitems()
            # Show message if not init
            if not init:
                messagebox.showwarning('AGOL Connection Failed', 'Please check username, portal and password.')
        else:
            # Update text colour to indicate success
            self.txt_portal.configure(foreground='#1a9641')
            self.txt_uname.configure(foreground='#1a9641')
            self.txt_pword.configure(foreground='#1a9641')
            # Reload items
            self._loaditems(init=True)
            # Show message if not init (Disabled, loading of items and changing text colour implies connection successful)
            # if not init:
            #    messagebox.showinfo('AGOL Connection Success', f'Connection to {self._portal.get()} successful!')

    def _agol_disconnect(self, e=None):
        """Disconnects to AGOL or Portal instance

        Args:
            e ([type], optional): Event info, not used. Defaults to None.
        """
        # Change text colour to red for portal
        self.txt_portal.configure(foreground='#d7191c')
        self.txt_uname.configure(foreground='#d7191c')
        self.txt_pword.configure(foreground='#d7191c')
        # Get flag to reload items if required
        if self._ago is None:
            reloaditems = False
        else:
            reloaditems = True
        # Delete ago object
        self._ago = None
        # Reload items
        if reloaditems:
            self._loaditems()

    def _browse(self):
        """Function to request a directory path
        """
        # Get folder
        filename = filedialog.askdirectory()
        # Update output dir
        self._outdir.set(filename)

    def _load(self):
        """Load form
        """
        # Load data into form
        if "last" in self._cfg:
            lastrun = datetime.fromisoformat(self._cfg["last"]).strftime("%Y/%m/%d %H:%M:%S")
        else:
            lastrun = 'Never'
        self._lastrun.set(lastrun)
        if "label" in self._cfg:
            self._label.set(self._cfg["label"])
        else:
            self._label.set('Unnamed')
        if "outdir" in self._cfg:
            self._outdir.set(self._cfg["outdir"])
        else:
            self._outdir.set('')
        if "pword" in self._cfg:
            self._pword.set(self._cfg["pword"])
        else:
            self._pword.set('')
        if "uname" in self._cfg:
            self._uname.set(self._cfg["uname"])
        else:
            self._uname.set('')
        if "portal" in self._cfg:
            self._portal.set(self._cfg["portal"])
        else:
            self._portal.set('')
        if "usegit" in self._cfg:
            self._usegit.set(self._cfg["usegit"])
        else:
            self._usegit.set(True)
        # If uname, pword and portal is supplied, test connection
        if not (self._cfg["pword"] is None or self._cfg["uname"] is None or self._cfg["portal"] is None):
            self._agol_connect(init=True)
        # Load items
        self._loaditems(init=True)
        
    def _clearitems(self):
        """Clear out old items
        """
        # Remove old items
        for widget in self.frame_items.innerframe.winfo_children():
            widget.destroy()

    def _showTkObj(self, obj, show):
        if show:
            obj.grid()
        else:
            obj.grid_remove()
        

    def _filteritems(self, var, index, mode):
        """Filter Items
        
        """
        filter_value = self._filter.get()
        # Process items
        for k, itm in self._items.items():
            # Check if matches filter
            match = filter_value.lower() in itm['kwords']
            # Turn objects on or off
            self._showTkObj(itm['chk_itm'], match)
            self._showTkObj(itm['txt_itm_folder'], match)
            self._showTkObj(itm['txt_itm_type'], match)
            self._showTkObj(itm['txt_itm_id'], match)
            self._showTkObj(itm['txt_itm_lastupd'], match)
            self._showTkObj(itm['cmb_itm_freq'], match)
            self._showTkObj(itm['txt_itm_hours'], match)
            self._showTkObj(itm['txt_itm_options'], match)
            self._showTkObj(itm['cmb_itm_format'], match)
                
    def _loaditems(self, init: bool = False):
        """Load items

        Args:
            init (bool, optional): Flag to indicate if this call is being made in init. Defaults to False.
        """
        # Clear items
        self._clearitems()
        # Check GIS has been loaded
        if self._ago and self._ago.gis:
            # Setup item grid headers
            lbl_itm_name = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_name.configure(font='{Arial} 8 {bold}', text='Item')
            lbl_itm_name.grid(column=0, row=0, sticky='w')
            lbl_itm_folder = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_folder.configure(font='{Arial} 8 {bold}', text='Folder')
            lbl_itm_folder.grid(column=1, row=0, sticky='w')
            lbl_itm_type = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_type.configure(font='{Arial} 8 {bold}', text='Type')
            lbl_itm_type.grid(column=2, row=0, sticky='w')
            lbl_itm_link = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_link.configure(font='{Arial} 8 {bold}', text='ID')
            lbl_itm_link.grid(column=3, row=0, sticky='w')
            lbl_itm_lastupd = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_lastupd.configure(font='{Arial} 8 {bold}', text='Last Updated')
            lbl_itm_lastupd.grid(column=4, row=0, sticky='w')
            lbl_itm_freq = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_freq.configure(font='{Arial} 8 {bold}', text='Freq')
            lbl_itm_freq.grid(column=5, row=0, sticky='w')
            lbl_itm_hours = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_hours.configure(font='{Arial} 8 {bold}', text='Hours')
            lbl_itm_hours.grid(column=6, row=0, sticky='w')
            lbl_itm_options = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_options.configure(font='{Arial} 8 {bold}', text='Options')
            lbl_itm_options.grid(column=7, row=0, sticky='w')
            lbl_itm_format = tk.Label(self.frame_items.innerframe, bg='white')
            lbl_itm_format.configure(font='{Arial} 8 {bold}', text='Format')
            lbl_itm_format.grid(column=8, row=0, sticky='w')
            # Setup row items
            row = 1
            # Reset items
            self._items = {}
            # Setup agol items
            me = {'id': "self", 'title': 'My Details (Admin)', 'folder': '', 'type': 'Admin Item'}
            users = {'id': "users", 'title': 'Users (Admin)', 'folder': '', 'type': 'Admin Item'}
            groups = {'id': "groups", 'title': 'Groups (Admin)', 'folder': '', 'type': 'Admin Item'}
            # Add admin items
            agol_items = [me, users, groups]
            # Load agol items
            agol_items += self._ago.myitems
            # Setup admin items
            # Collect AGOL items
            for i in agol_items:
                # Setup itme
                itm = {}
                # Get cfg item if exists
                try:
                    itmcfg = self._cfg['items'][i['id']]
                except KeyError:
                    itmcfg = None
                # Setup item label
                itm['id'] = i['id']
                itm['row'] = row
                itm['kwords'] = str(row)
                itm['selected'] = tk.IntVar(value=1 if itmcfg else 0)
                itm['chk_itm'] = tk.Checkbutton(self.frame_items.innerframe, text=i['title'], variable=itm['selected'], bg='white')
                itm['chk_itm'].configure(font='{Arial} 8 {}')
                itm['chk_itm'].grid(column=0, row=row, sticky='w', padx=2, pady=2) 
                itm['selected'].trace('w', lambda name, index, mode, id=itm['id']: self._select_item(id))
                itm['kwords'] += i['title']
                itm['kwords'] += 'selected' if itmcfg else ''
                # Setup item id
                itm['txt_itm_folder'] = tk.Label(self.frame_items.innerframe, bg='white')
                itm['txt_itm_folder'].configure(font='{Arial} 8 {}', text=i['folder'])
                itm['txt_itm_folder'].grid(column=1, row=row, sticky='w', padx=2, pady=2,)
                itm['kwords'] += i['folder']
                # Setup item type
                itm['txt_itm_type'] = tk.Label(self.frame_items.innerframe, bg='white')
                itm['txt_itm_type'].configure(font='{Arial} 8 {}', text=i['type'])
                itm['txt_itm_type'].grid(column=2, row=row, sticky='w', padx=2, pady=2)
                itm['kwords'] += i['type']
                # Setup item id
                itm['txt_itm_id'] = tk.Label(self.frame_items.innerframe, bg='white')
                itm['txt_itm_id'].configure(font='{Arial} 8 {}', text=itm['id'])
                itm['txt_itm_id'].grid(column=3, row=row, sticky='w', padx=2, pady=2,)
                itm['kwords'] += itm['id']
                # Setup item last update flag
                if itmcfg and 'last' in itmcfg:
                    lastrun = datetime.fromisoformat(self._cfg["last"]).strftime("%Y/%m/%d %H:%M:%S")
                else:
                    lastrun = 'Never'
                itm['last'] = tk.StringVar(value=lastrun)
                itm['txt_itm_lastupd'] = tk.Label(self.frame_items.innerframe, bg='white')
                itm['txt_itm_lastupd'].configure(font='{Arial} 8 {}', text='NA', textvariable=itm['last'])
                itm['txt_itm_lastupd'].grid(column=4, row=row, sticky='w', padx=2, pady=2)
                # Setup item freq
                itm['hours_freq'] = tk.StringVar()
                itm['cmb_itm_freq'] = ttk.Combobox(self.frame_items.innerframe, width=6)
                itm['cmb_itm_freq'].configure(font='{Arial} 8 {}', textvariable=itm['hours_freq'], values=list(FREQUENCY_OPTIONS.keys()))
                itm['cmb_itm_freq'].grid(column=5, row=row, sticky='ew', padx=2, pady=2)
                # Load item freq
                hours = itmcfg['hours_diff'] if itmcfg else 168.0
                # Setup item hours
                itm['hours_diff'] = tk.DoubleVar(value=hours)
                itm['txt_itm_hours'] = tk.Entry(self.frame_items.innerframe, width=6, bg='white')
                itm['txt_itm_hours'].configure(font='{Arial} 8 {}', relief=tk.FLAT, textvariable=itm['hours_diff'])
                itm['txt_itm_hours'].grid(column=6, row=row, sticky='w', padx=2, pady=2)
                # Update frequency
                freq = [k for k, v in FREQUENCY_OPTIONS.items() if v == hours]
                if freq:
                    itm['hours_freq'].set(freq[0])
                    itm['txt_itm_hours'].configure(state="readonly")
                else:
                    itm['hours_freq'].set('Custom')
                    itm['txt_itm_hours'].configure(state="normal")
                # Setup freq command
                itm['cmb_itm_freq'].bind('<<ComboboxSelected>>', lambda e, source_var=itm['hours_freq'], target_ctl=itm['txt_itm_hours'], target_var=itm['hours_diff']: self._populate_hours(source_var, target_var, target_ctl))
                # Setup item Options
                itm['options'] = tk.StringVar(value=','.join(itmcfg['options']) if itmcfg else 'all')
                itm['txt_itm_options'] = tk.Entry(self.frame_items.innerframe, width=12, bg='white')
                itm['txt_itm_options'].configure(font='{Arial} 8 {}', relief=tk.FLAT, text='options', textvariable=itm['options'])
                itm['txt_itm_options'].grid(column=7, row=row, sticky='w', padx=2, pady=2)
                # Setup item format
                export_default = 'none'
                # Setup export formats
                if i['type'] == "Feature Service":
                    export_types = [f for f in agol.EXPORT_FORMATS if not f == 'spkg']
                    export_default = 'fgdb'
                elif i['type'] == "Vector Tile Service":
                    export_types = ['none', 'vtpk']
                elif i['type'] == "Scene Service":
                    export_types = ['none', 'spkg']
                else:
                    export_types = ['none']
                # Setup default
                itm['format'] = tk.StringVar(value=itmcfg['format'] if itmcfg else export_default)
                # Setup item format
                itm['cmb_itm_format'] = ttk.Combobox(self.frame_items.innerframe, width=6)
                itm['cmb_itm_format'].configure(font='{Arial} 8 {}', values=export_types, textvariable=itm['format'])
                itm['cmb_itm_format'].grid(column=8, row=row, sticky='w', padx=2, pady=2)
                itm['kwords'] += itm['format'].get()
                # Disable inputs if not selected
                if itm['selected'].get() == 0:
                    itm['txt_itm_lastupd'].configure(state='disabled')
                    itm['cmb_itm_freq'].configure(state='disabled')
                    itm['txt_itm_hours'].configure(state='disabled')
                    itm['txt_itm_options'].configure(state='disabled')
                    itm['cmb_itm_format'].configure(state='disabled')
                # Disable options and format for admin items
                if itm['id'] in ['self', 'users', 'groups']:
                    itm['txt_itm_options'].grid_remove()
                    itm['cmb_itm_format'].grid_remove()
                # Add item to list
                itm['kwords'] = itm['kwords'].lower()
                self._items[i['id']] = itm
                # Update row placeholder
                row += 1
        else:
            # Check if this is the call to load items on init or if its after init
            if not init:
                # Display message
                messagebox.showwarning('Not connected to AGOL', 'Please connect to your portal using the button in the Connection Properties section above.')

    def _select_item(self, id):
        """Helper function to select an item

        Args:
            id ([type]): Item to select
        """
        # Get item
        itm = self._items[id]
        # Determine if queued for export
        if itm['selected'].get() == 1:
            itm['txt_itm_lastupd'].configure(state='normal')
            itm['cmb_itm_freq'].configure(state='normal')
            if itm['cmb_itm_freq'].get() == 'Custom':
                itm['txt_itm_hours'].configure(state='normal')
            else:
                itm['txt_itm_hours'].configure(state='readonly')
            itm['txt_itm_options'].configure(state='normal')
            itm['cmb_itm_format'].configure(state='normal')
        else:
            itm['txt_itm_lastupd'].configure(state='disabled')
            itm['cmb_itm_freq'].configure(state='disabled')
            itm['txt_itm_hours'].configure(state='disabled')
            itm['txt_itm_options'].configure(state='disabled')
            itm['cmb_itm_format'].configure(state='disabled')

    def _openurl(self, url: str):
        """Opens URL in default browser

        Args:
            url (str): URL to open
        """
        # Open web browser
        webbrowser.open_new(url)

    def run(self, path: str = None):
        """Main function to run form

        Args:
            path (str, optional): Config file path. Defaults to None.
        """
        # Set initial config for form if specified
        if path:
            self._config_load(path)
        else:
            # Save config
            self.config_new()
        # Run main loop
        self.mainwindow.mainloop()

    def _runnow(self):
        # Prompt to confirm
        res = messagebox.askyesno("Run Backup Now", "Backup jobs may take a while, and will lock the config app while they run. There is no progress bar for this operation so you are on your own! Do you wish to proceed?")
        if res:
            # Import backups manager
            import backup_mgr
            import tempfile
            with tempfile.TemporaryDirectory() as d:
                # Setup path
                cfg_path = os.path.join(str(d), 'config.json')
                # Save config to path
                self._config_save(cfg_path)
                # Run backup file live
                backup_mgr.run([cfg_path], logger=self._logger)
                # Provide feedback
                messagebox.showinfo('Backup Complete', 'Backup job has been completed!')


if __name__ == '__main__':
    # Get file path
    app_dir = os.path.dirname(__file__)
    # Setup arg parse
    import argparse
    desc = "This tool manages backs up and ArcGIS Online item to a local folder including definitions, data and features in the requested format"
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-c', '--config', dest='config', help="Config item defining items to backup", nargs='?', default=None)
    parser.add_argument("-v", action="store_true", dest="verbose", help="Verbose, also logs debug messages")
    parser.add_argument("-q", action="store_false", dest="log", help="Do not log script progress to file")
    # Parse args
    args = parser.parse_args()
    # Setup logger
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = log.setup("backup_mgr_gui", app_dir=app_dir, active=args.log, level=log_level)
    # Update script log
    tsstart = datetime.now()
    tsstart_str = tsstart.strftime("%m/%d/%Y %H:%M:%S")
    log.post(logger, f"Script started at {tsstart_str}")
    # Setup form class
    tk_cls = tk.Tk()
    # Setup form
    app = BackupMgrGUI(tk_cls, logger)
    app.run(args.config)
    # Update log
    tsend = datetime.now()
    tsend_str = tsend.strftime("%m/%d/%Y %H:%M:%S")
    sec = int((tsend - tsstart).total_seconds())
    log.post(logger, f"Script finished at {tsend_str} after {sec} seconds")
