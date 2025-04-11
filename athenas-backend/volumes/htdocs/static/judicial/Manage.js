Ext._define('judicial.Manage', {
    extend: 'toolkit.widget.TabPanel',

    observeLawsuit: function() {
        if(this.lawsuit()) {
            this.getTilePagePanel().enable();
            this.loadLawsuitCover(this.lawsuit(), this.location());
            this.getReminderDisplayManage().lawsuitId = this.lawsuit();
            this.getReminderDisplayManage().start();
        }
        else {
            this.getTilePagePanel().disable();
            this.getTilePagePanel().setPageContent('');
        }
    },

    getReminderDisplayManage: function(attachedAt) {
      if (!this._reminderDisplayManage) {
        this._reminderDisplayManage = Ext._create('judicial.reminder.lawsuit.DisplayManage', {
            lawsuitId: 0,
            attached: attachedAt,
            callback: {
                afterNew: {
                    scope: this,
                    fn: function() {
                        this.getOutCourtLawsuitGrid().getStore().reload();
                        this.getHistoryOutCourtLawsuitGrid().getStore().reload();
                        this.getClosedOutCourtLawsuitGrid().getStore().reload();
                    }
                },
                afterChanges: {
                    scope: this,
                    fn: function() {
                        this.getOutCourtLawsuitGrid().getStore().reload();
                        this.getHistoryOutCourtLawsuitGrid().getStore().reload();
                        this.getClosedOutCourtLawsuitGrid().getStore().reload();
                    }
                },
            }
        });
      }

      return this._reminderDisplayManage;
    },

    loadLawsuitCover: function(lawsuitId, location) {
        var rest = Ext._create('judicial.OutCourtLawsuitRestful');

        rest.doRequest(
            rest.getRoute('cover', false, 'GET', {
                params: {
                    pk: lawsuitId,
                    execution_organ: location
                },
                scope: this,
                callback: function() {},
                success: function(xhr) {
                    this.getTilePagePanel().setPageContent(xhr.responseText);
                },
                failure: function() {
                    this.getTilePagePanel().setPageContent('Ocorreu um erro buscando inforações.');
                }
            })
        );
    },

    clearFilterAll: function() {
        this.getOutCourtLawsuitGrid().removeFilterProperty('location', 1000, false);
        this.getOutCourtLawsuitGrid().removeFilterProperty('type_lawsuit', 1002, false);
        this.getOutCourtLawsuitGrid().removeFilterProperty('tags', 1003, false);

        this.getHistoryOutCourtLawsuitGrid().removeFilterProperty('type_lawsuit', 1002, false);
        this.getHistoryOutCourtLawsuitGrid().removeFilterProperty('tags', 1003, false);

        this.getClosedOutCourtLawsuitGrid().removeFilterProperty('origin__movimentacoes__lotacao_destino', 1000, false);
        this.getClosedOutCourtLawsuitGrid().removeFilterProperty('type_lawsuit', 1002, false);
        this.getClosedOutCourtLawsuitGrid().removeFilterProperty('tags', 1003, false);

        this.getEntryWorkerReminderGrid().removeFilterProperty('part__lawsuit__location', 1000, false);
        this.getOutWorkerReminderGrid().removeFilterProperty('part__lawsuit__location', 1000, false);
    },

    observe: function() {
        var enable = true;
        var needLoad = false;
        var needClear = false;
        var obj;

        this.clearFilterAll();

        this.getScopeTreePanel().locationSelected(this.location());

        if(this.is_local_collaboration()) {
            obj = this.getOutCourtLawsuitGrid();
            obj.showContextMenu = false;
            obj.gridCollaboration = true;
        }else{
          obj = this.getOutCourtLawsuitGrid();
          obj.showContextMenu = true;
          obj.gridCollaboration = false;
        }

        if(this.location()) {
            enable = true;
            needLoad = true;

            obj = this.getOutCourtLawsuitGrid();
            obj.setParam('location', this.location());
            obj.setFilterProperty('location', this.location(), 1000, false);

            obj = this.getHistoryOutCourtLawsuitGrid();
            obj.forExecutionOrgan = this.location();
            obj.getStore().setBaseParam('execution_organ', this.location());

            obj = this.getClosedOutCourtLawsuitGrid();
            obj.setFilterProperty('origin__movimentacoes__lotacao_destino', this.location(), 1000, false);

            obj = this.getEntryWorkerReminderGrid();
            obj.setFilterProperty('part__lawsuit__location', this.location(), 1000, false);

            obj = this.getOutWorkerReminderGrid();
            obj.setFilterProperty('part__lawsuit__location', this.location(), 1000, false);

        }
        else {
            needClear = true;

            obj = this.getOutCourtLawsuitGrid();
            obj.setParam('location', 0);

            obj = this.getHistoryOutCourtLawsuitGrid();
            obj.forExecutionOrgan = 0;
            obj.getStore().setBaseParam('execution_organ', 0);

            obj = this.getClosedOutCourtLawsuitGrid();
            obj.setParam('origin__movimentacoes__lotacao_destino', 0);

        }

        if(this.typeLawSuit()) {
            enable = true;
            needLoad = true;

            obj = this.getOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', this.typeLawSuit());
            obj.setFilterProperty('type_lawsuit', this.typeLawSuit(), 1002, false);

            obj = this.getHistoryOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', this.typeLawSuit());
            obj.setFilterProperty('type_lawsuit', this.typeLawSuit(), 1002, false);

            obj = this.getClosedOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', this.typeLawSuit());
            obj.setFilterProperty('type_lawsuit', this.typeLawSuit(), 1002, false);
        }
        else {
            needClear = true;

            obj = this.getOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', 0);

            obj = this.getHistoryOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', 0);

            obj = this.getClosedOutCourtLawsuitGrid();
            obj.setParam('type_lawsuit', 0);
        }

        if(this.tag()) {
            enable = true;
            needLoad = true;

            obj = this.getOutCourtLawsuitGrid();
            obj.setFilterProperty('tags', this.tag(), 1003, false);

            obj = this.getHistoryOutCourtLawsuitGrid();
            obj.setFilterProperty('tags', this.tag(), 1003, false);

            obj = this.getClosedOutCourtLawsuitGrid();
            obj.setFilterProperty('tags', this.tag(), 1003, false);
        }
        else {
            needClear = true;
        }

        if(enable) {
            this.getOutCourtLawsuitGrid().enable();
            this.getHistoryOutCourtLawsuitGrid().enable();
            this.getClosedOutCourtLawsuitGrid().enable();
            this.getWorkerReminderPanel().enable();
        }
        else {
            this.getOutCourtLawsuitGrid().disable();
            this.getHistoryOutCourtLawsuitGrid().disable();
            this.getClosedOutCourtLawsuitGrid().disable();
            this.getWorkerReminderPanel().disable();
        }

        if(needLoad) {
            this.getOutCourtLawsuitGrid().getStore().load({});
            this.getHistoryOutCourtLawsuitGrid().getStore().load({});
            this.getClosedOutCourtLawsuitGrid().getStore().load({});
            this.getEntryWorkerReminderGrid().getStore().load({});
            this.getOutWorkerReminderGrid().getStore().load({});
        }
        else if(needClear){
            this.getOutCourtLawsuitGrid().getStore().removeAll();
            this.getHistoryOutCourtLawsuitGrid().getStore().removeAll();
            this.getClosedOutCourtLawsuitGrid().getStore().removeAll();
            this.getEntryWorkerReminderGrid().getStore().removeAll();
            this.getOutWorkerReminderGrid().getStore().removeAll();
        }
    },

    location: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._location = value;
            if(observe) this.observe();
        }

        return this._location;
    },

    is_local_collaboration: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._is_collaboration_node = value;
            if(observe) this.observe();
        }

        return this._is_collaboration_node;
    },

    lawsuit: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._lawsuit = value;
            if(observe) this.observeLawsuit();
        }

        return this._lawsuit;
    },

    tag: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._tag = value;
            if(observe) this.observe();
        }

        return this._tag;
    },

    typeLawSuit: function(value, observe) {
        observe = core.nullValue(observe, true);

        if(value !== undefined) {
            this._type_lawsuit = value;
            if(observe) this.observe();
        }

        return this._type_lawsuit;
    },

    getScopeTreePanel: function(cfg) {
        if(!this._scopeTreePanel)
            this._scopeTreePanel = Ext._create('judicial.ScopeTree', {
                region: 'west',
                width: 350,
                maxWidth: 450,
                minWidth: 250,
                split: true,
                autoScroll:true,
                bodyStyle: {
                    paddingBottom: '16px',
                },
                hiddenReportAction: (cfg.hiddenReportAction || false)
            });

        return this._scopeTreePanel;
    },

    openDiligence: function(){
        Ext._create('judicial.diligences.ExecutionOrganWindow', {
            modal: true,
            width: (Ext.getBody().getBox().width * 0.9),
            height: (Ext.getBody().getBox().height * 0.9),
            params: {'lawsuit': this.lawsuit(), 'type_lawsuit': this.typeLawSuit()}
        }).show();
    },

    getOutCourtLawsuitGrid: function() {
        if(!this._outCourtLawsuitGrid) {
            this._outCourtLawsuitGrid = Ext._create('judicial.OutCourtLawsuitGrid', {
                title: 'Principal',
                gridAutoLoad: false,
                showContextMenu: true,
                columnAction: false
            });

            this._outCourtLawsuitGrid.setFilterProperty('attached_lawsuit', null, 1001, false);
            this._outCourtLawsuitGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.lawsuit(selection[0].get('pk'));
                    else
                        this.lawsuit(null);
                }
            });
        }

        return this._outCourtLawsuitGrid;
    },

    getTilePagePanel: function() {
        if(!this._tilePagePanel) {
            this._tilePagePanel = Ext._create('core.TilePagePanel', {
                disabled: true
            });

            this._tilePagePanel.on({
                scope: this,
                render: function(p) {
                    var me = this;
                    setTimeout(function() { me.getReminderDisplayManage(p) }, 300);
                }
            });
        }

        return this._tilePagePanel;
    },

    getHistoryOutCourtLawsuitGrid: function(cfg) {
        if(!this._historyOutCourtLawsuit) {
            this._historyOutCourtLawsuit = Ext._create('judicial.OutCourtLawsuitGrid', {
                configOrderToolBar: ['openDocument', '-', 'search', '->', 'download'],
                title: 'Histórico',
                columnAction: false,
                storeDefaultRoute: 'historic',
                documentMode: 'historic',
                gridAutoLoad: true
            });
            this._historyOutCourtLawsuit.setFilterProperty('attached_lawsuit', null, 1001, false);
            this._historyOutCourtLawsuit.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.lawsuit(selection[0].get('pk'));
                    else
                        this.lawsuit(null);
                }
            });

            // this._historyOutCourtLawsuit.updateItem = Ext.emptyFn;
        }
        return this._historyOutCourtLawsuit;
    },

    getClosedOutCourtLawsuitGrid: function(cfg) {
        if(!this._closedOutCourtLawsuit) {
            this._closedOutCourtLawsuit = Ext._create('judicial.OutCourtLawsuitGrid', {
                configOrderToolBar: ['openDocument', '-', 'search', '->', 'download'],
                title: 'Finalizado',
                gridAutoLoad: true,
                columnAction: false,
                storeDefaultRoute: 'archived',
                documentMode: 'archived'
            });

            this._closedOutCourtLawsuit.setFilterProperty('attached_lawsuit', null, 1001, false);
            this._closedOutCourtLawsuit.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.lawsuit(selection[0].get('pk'));
                    else
                        this.lawsuit(null);
                }
            });
        }

        return this._closedOutCourtLawsuit;
    },

    workerReminder: function(value, dispatch) {
        dispatch = (dispatch === undefined ? true : dispatch);

        if(value !== undefined) {
            this._workerReminder = value;

            if(dispatch) this.observeWorkerReminder();
        }

        return this._workerReminder;
    },

    loadWorkerReminderContent: function(reminderId) {
        var rest = Ext._create('judicial.workerreminder.Restful');
        rest.rendererDocument(
            reminderId,
            {
                scope: this,
                fn: function(document) {
                    if(document.hasContent){
                        this.getTilePagePanel().setPageContent(document.content);
                        this.getTilePagePanel().addPageContent(document.appends);
                    } else {
                        this.getTilePagePanel().setPageContent(document.appends);
                    }
                }
            },
            {
                fn: function(message) {
                    this.getTilePagePanel().setPageContent(message);
                }
            },
            {fn: function() {}}
        );
    },

    observeWorkerReminder: function() {
        var value = this.workerReminder();

        if(value) {
            this.getTilePagePanel().enable();
            this.loadWorkerReminderContent(value);

        }
        else {
            this.getTilePagePanel().disable();
            this.getTilePagePanel().setPageContent('');
        }
    },

    getEntryWorkerReminderGrid: function(cfg) {
        if(!this._entryWorkerReminderGrid) {
            this._entryWorkerReminderGrid = Ext._create('judicial.workerreminder.Grid', {
                title: 'Caixa de Entrada',
                gridAutoLoad: false,
                showFinished: false,
                columnAction: false,
                border: false,
                storeDefaultRoute: 'entrybox',
                hideColumns: ['receiver_unicode']
            });


            // FIXME: a atualização do grid deveria ser via Request Push por exemplo
            this._entryWorkerReminderGrid.on(
                {
                    scope: this,
                    afterrender: function(obj){
                        setInterval(function(){
                            obj.getStore().load();
                        }, 60000);
                    }
                }
             );

            this._entryWorkerReminderGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.workerReminder(selection[0].get('pk'));
                    else
                        this.workerReminder(null);
                }
            });

            this._entryWorkerReminderGrid.setFilterProperty('resolved', 'true', -100);
        }

        return this._entryWorkerReminderGrid;
    },

    getOutWorkerReminderGrid: function(cfg) {
        if(!this._outWorkerReminderGrid) {
            this._outWorkerReminderGrid = Ext._create('judicial.workerreminder.Grid', {
                title: 'Caixa de Saída',
                gridAutoLoad: false,
                showFinished: false,
                columnAction: false,
                border: false,
                storeDefaultRoute: 'outbox',
                hideColumns: ['action_button', 'solicited_by'],
                configOrderToolBar: ['search', '->'],
            });

            // FIXME: a atualização do grid deveria ser via Request Push por exemplo
            this._outWorkerReminderGrid.on(
                {
                    scope: this,
                    afterrender: function(obj){
                        setInterval(function(){
                            obj.getStore().load();
                        }, 60000);
                    }
                }
             );

            this._outWorkerReminderGrid.getSelectionModel().on({
                scope: this,
                selectionchange: function(sel) {
                    var selection = sel.getSelections();

                    if(selection.length > 0)
                        this.workerReminder(selection[0].get('pk'));
                    else
                        this.workerReminder(null);
                }
            });

            this._outWorkerReminderGrid.setFilterProperty('resolved', 'true', -100);
        }

        return this._outWorkerReminderGrid;
    },

    getWorkerReminderPanel: function(cfg) {
        if(!this._workerReminderPanel)
            this._workerReminderPanel = Ext._create('Ext.Panel', {
                title: 'Pré-análise',
                disabled: true,
                border: false,
                frame: false,
                layout: 'fit',
                items: [
                    {
                        xtype: 'tabpanel',
                        activeTab: 0,
                        border: false,
                        items: [
                            this.getEntryWorkerReminderGrid(cfg),
                            this.getOutWorkerReminderGrid(cfg)
                        ]
                    }
                ]
            });

        return this._workerReminderPanel;
    },

    getBoxTabPanel: function(cfg) {
        if(!this._boxTabPanel)
            this._boxTabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                region: 'center',
                // split: true,
                // height: 300,
                minHeight: 250,
                // maxHeight: 650,
                tabPosition: 'bottom',
                items: [
                    this.getOutCourtLawsuitGrid(cfg),
                    this.getHistoryOutCourtLawsuitGrid(cfg),
                    this.getClosedOutCourtLawsuitGrid(cfg),
                    this.getWorkerReminderPanel(cfg)
                ]
            });

        return this._boxTabPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                title: 'Gestor de Procedimentos'
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                border: false,
                items: [
                    this.getScopeTreePanel(cfg),
                    {
                        region: 'center',
                        layout: 'border',
                        border: false,
                        items: [
                            this.getBoxTabPanel(cfg),
                            {
                                title: 'Capa do Procedimento',
                                region: 'south',
                                layout: 'fit',
                                collapsed: false,
                                maxHeight: 600,
                                height: 600,
                                split: true,
                                collapsible: true,
                                items: [
                                    this.getTilePagePanel()
                                ],
                                listeners: {
                                    scope: this,
                                    expand: function(p) {
                                        this.getReminderDisplayManage().redraw();
                                    },
                                    afterrender: function(p) {
                                        setTimeout(function() { p.collapse() }, 500)
                                    }
                                }
                            }
                        ]
                    }
                ]
            }
        );

        judicial.Manage.superclass.constructor.call(this, cfg);

        this.getScopeTreePanel().getSelectionModel().on({
            scope: this,
            beforeselect: function(sm, node) {

                this.typeLawSuit(null, false);
                this.location(null, false);
                this.tag(null, false);

                this.is_local_collaboration(node.attributes.is_collaboration);

                if(node.attributes.type == 'location') {
                    this.location(node.attributes.node);
                }
                else if(node.attributes.type == 'type_lawsuit') {
                    this.typeLawSuit(node.attributes.value, false);
                    this.location(node.parentNode.attributes.node);
                }
                else if(node.attributes.type == 'bookmark_root') {
                    this.location(node.parentNode.attributes.node);
                } else if(node.attributes.type == 'bookmark_item'){
                    if(['nao-recebido', 'urgente', 'caixa-da-secretaria', 'proc-devolvidos'].indexOf(node.attributes.node) >= 0){
                        this.tag(node.attributes.value, false);
                        this.location(node.parentNode.attributes.node);
                    }else{
                        this.tag(node.attributes.pk, false);
                        this.location(node.parentNode.parentNode.attributes.node);
                    }
                }
            }
        });

        this.observe();
    }
});
