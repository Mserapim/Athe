/**
 *
 **/
Ext._define('engine.TaskSessionWindow', {
    extend: 'core.RestfulWindow',

    rest: 'engine.TaskSessionRestful',

    width: 700,

    _observe: function() {
        var gridMessages, panelMessages;
        if(this.oId) {
            panelMessages = this.getMessagesPanel();
            gridMessages = this.getMessagesGrid();
            gridMessages.setParam('session', this.oId);
            gridMessages.setFilterProperty('session', this.oId);
            gridMessages._filterTypeOf = [1, 2, 3, 4];
            gridMessages.setFilterProperty('type_of__in', gridMessages._filterTypeOf, 1000);
            gridMessages.setSortProperty('id','ASC', false);
            panelMessages.enable();
            
        }
        else {
            this.getMessagesPanel().disable();
        }
    },

    getMessagesGrid: function(cfg){
        if(!this._messagesGrid){
            this._messagesGrid = Ext._create('engine.TaskMessageGrid', {
                gridAutoLoad: false,
                region: 'center',
                layout: 'fit',
                // columnAction: false,
                hideColumns: ['session_unicode', ],
                hideItemsToolbar: ['add', 'edit', 'remove', ],
                hideActions: ['add', 'edit', 'remove', ],
            });
            this._messagesGrid.getSelectionModel().on(
                'rowselect',
                function(selModel, idx, record){
                    this.getMessageField().update(record.data.message);
                }, 
                this
            );
        }
        return this._messagesGrid;
    },

    getMessageField: function(cfg){
        if(!this._messageField){
            this._messageField = Ext._create('Ext.form.TextArea', {
                readOnly: true,
                fieldLabel: 'Mensagem'
            })
        }
        return this._messageField;
    },

    getMessagesPanel: function(cfg){
        if(!this._tabMessages)
            this._tabMessages = Ext._create('Ext.Panel', {
                border: false,
                layout: 'border',
                title: 'Messages',
                items: [
                    this.getMessagesGrid(cfg),
                    {
                        region: 'south',     // center region is required, no width/height specified
                        height: 100,
                        xtype: 'container',
                        layout: 'fit',
                        margins: '5 5 5 5',
                        items:[
                            this.getMessageField(),
                        ]
                    }
                ]
            });

        return this._tabMessages;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: (cfg.activeTab? cfg.activeTab: 0),
                height: 435,
                border: false,
                items: [
                    this.getMainPanel(cfg),
                    this.getMessagesPanel(cfg),
                ]
            });

        return this._tabPanel;
    },

    getMainPanel: function(cfg) {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                border: false,
                frame: true,
                title: 'Principal',
                items: [
                    {
                        fieldLabel: 'SSID',
                        xtype: 'displayfield',
                        name: 'sid',
                        // maxLenght: 100,
                        // readOnly: true,
                        width: 600
                    },{
                        fieldLabel: 'Descrição',
                        xtype: 'displayfield',
                        name: 'description',
                        // readOnly: true,
                        // maxLenght: 100,
                        width: 600,
                        // height: 100
                    },{
                        fieldLabel: 'Iniciado em',
                        xtype: 'displayfield',
                        readOnly: true,
                        name: 'started_task',
                    },{
                        fieldLabel: 'Finalizado em',
                        xtype: 'displayfield',
                        name: 'finished_task',
                        readOnly: true,
                    },
                ]
            });

        return this._mainPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: false,
                items: [
                    this.getTabPanel(cfg)
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            // saveAndContinue: {
            //     scope: this,
            //     fn: function(instance) {
            //         this.getFormPanel().getForm().findField('controllers').objectId(instance.pk);
            //         this.getFormPanel().getForm().findField('users').objectId(instance.pk);
            //         this.oId = instance.pk;
            //         this.action = 'update';
            //     }
            // }
        });

        engine.TaskSessionWindow.superclass.constructor.call(this, cfg);
        // this.values && this.getFormPanel().getForm().setValues(this.values);
        this._observe();        
    }
});

