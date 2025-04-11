Ext._define('planning.hiring.minuteitem.MinuteItemGroupWindow', {
    extend: 'core.RestfulWindow',

    rest: 'planning.hiring.minuteitem.MinuteItemRestful',
    width: 570,

    getMainTab: function() {
        if (!this._mainTab)
            this._mainTab = Ext._create('Ext.Panel', {
                title: 'Item',
                labelAlign: 'top',
                frame: true,
                layout: 'form',
                autoHeight: true,
                items: [
                    {

                        fieldLabel: "Grupo ou Item",
                        xtype: "textfield",
                        name: "group",
                        allowBlank: true,
                        listeners: {
                            render: function(){
                                this.hide();
                            }
                        }
                    },
                    {
                        fieldLabel: "Nº Grupo/Item",
                        xtype: "textfield",
                        allowBlank: false,
                        name: "line",
                        anchor: '99%',
                        listeners: {
                            scope: this,
                            render: function(field) {
                                field.focus(false, 500);
                            
                                if (this.oId != undefined){
                                    if (this.getFormPanel().getForm().findField('line').value == '') {
                                        var setline = this.getFormPanel().getForm().findField('group').getValue();
                                        this.getFormPanel().getForm().findField('line').setValue(setline);
                                    }
                                }
                            }
                        }
                    },
                    {
                        fieldLabel: 'Descrição',
                        xtype: 'combo',
                        anchor: '99%',
                        store: [
                            ['Item', 'Item'],
                            ['Grupo', 'Grupo']
                        ],
                        editable: false,
                        triggerAction: 'all',
                        hiddenName: 'description',
                    },

                ]
            });

        return this._mainTab;
    },

    getFormPanel: function(cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    new Ext._create('Ext.TabPanel', {
                        activeTab: 0,
                        items: [
                            this.getMainTab(),
                        ]
                    })
                ]
            });

        return this._formPanel;
    },

    createNewLine: function(){
        if(!this._createNewLine){
            this._createNewLine = Ext._create('planning.hiring.minuteitem.MinuteItemWindow',{
                action: 'create',
                params: this.getParams(),
            }).show();
        }
        return this._createNewLine;
    },

    getButtons: function(cfg) {
        if(!this._buttons){
            this._buttons = [].concat(planning.hiring.minuteitem.MinuteItemGroupWindow.superclass.getButtons.call(this, cfg));
            this._buttons = [{
                text: 'Nova Linha',
                scope: this,
                handler: function() {
                    if(this.oId){
                        this.destroy();
                        this.createNewLine().getFormPanel().getForm().findField('parent').setValue(this.oId);
                        
                    } else {
                        Ext.Msg.show({
                            title: 'Atenção',
                            msg: 'Salve o item antes de criar uma linha.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                    }
                },
            }].concat(this._buttons);

        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
            
        });
        
        planning.hiring.minuteitem.MinuteItemGroupWindow.superclass.constructor.call(this, cfg);

    }
});
