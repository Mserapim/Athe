Ext._define('raf.adjustment.dataadjustment.Window', {
    extend: 'core.RestfulWindow',
    rest: 'raf.adjustment.dataadjustment.Restful',
    width: 700,

    factoryStoreClass: function(cfg) {
        if(!this._factoryStoreClass) {
            console.log(Ext.getCmp('legalclass'));
            this._factoryStoreClass = Ext._create('Ext.data.Store', {
                autoLoad: true,
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('RAFLegalClass', 'get_listclasses')
                }),
                baseParams: {
                    quiz: cfg.params.quiz,
                    // keyword: Ext.getCmp('legalclass').value,
                },
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'pk', type: 'auto'},
                        {name: 'unicode', type: 'auto'},
                        {name: 'cnmp_code', type: 'auto'},
                    ]
                }),
            });
          }
          return this._factoryStoreClass;
    },

    factoryStoreMatter: function(cfg) {
        if(!this._factoryStoreMatter) {
            this._factoryStoreMatter = Ext._create('Ext.data.Store', {
                autoLoad: true,
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('RAFLegalMatter', 'get_listmatters')
                }),
                baseParams: {
                    activity: cfg.params.activity,
                },
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'pk', type: 'auto'},
                        {name: 'unicode', type: 'auto'},
                        {name: 'cnmp_code', type: 'auto'},
                    ]
                }),
            });
          }
          return this._factoryStoreMatter;
    },

    factoryStoreMovement: function(cfg) {
        if(!this._factoryStoreMovement) {
            this._factoryStoreMovement = Ext._create('Ext.data.Store', {
                autoLoad: true,
                proxy: Ext._create('Ext.data.HttpProxy', {
                    url: core.callAction('RAFLegalMovement', 'get_listmovements')
                }),
                baseParams: {
                    activity: cfg.params.activity,
                },
                reader: Ext._create('Ext.data.JsonReader', {
                    totalProperty: 'count',
                    root: 'collection',
                    fields: [
                        {name: 'pk', type: 'auto'},
                        {name: 'unicode', type: 'auto'},
                        {name: 'cnmp_code', type: 'auto'},
                    ]
                }),
            });
          }
          return this._factoryStoreMovement;
    },

    getClassField: function(cfg) {
        if(!this._classField) {
            this._classField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Classe",
                allowBlank: true,
                rest: "raf.LegalClassRestful",
                store: this.factoryStoreClass(cfg),
                id: "legalclass",
                name: "legalclass",
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['version_unicode'],
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                }
            });
        }
        return this._classField;
    },

    getMatterField: function(cfg) {
        if(!this._matterField) {
            this._matterField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Assunto",
                allowBlank: true,
                rest: "raf.LegalMatterRestful",
                store: this.factoryStoreMatter(cfg),
                id: "legalmatter",
                name: "legalmatter",
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                }
            });
        }
        return this._matterField;
    },

    getMovementField: function(cfg) {
        if(!this._movementField) {
            this._movementField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Movimento",
                allowBlank: true,
                rest: "raf.LegalMovementRestful",
                store: this.factoryStoreMovement(cfg),
                id: "movement",
                name: "movement",
                gridConfig: {
                    columnAction: false,
                    hideItemsToolbar:['add', 'edit', 'remove', '-', 'download'],
                }
            });
        }
        return this._movementField;
    },

    verifyFields: function(){
        if (this.getFormPanel().getForm().findField('operation').getValue() != ''){
            if (this.getFormPanel().getForm().findField('operation').getValue() == 2){
                if (this.getFormPanel().getForm().findField('source').getValue() != ''){
                    if (this.getFormPanel().getForm().findField('process_number').getValue() != ''){

                    } else {
                        Ext.Msg.show({
                            title: 'Ajuste de atividades',
                            msg: 'Informe um <b>NÚMERO</b>.',
                            icon: Ext.Msg.ERROR,
                            buttons: Ext.Msg.OK
                        });
                        this.getFormPanel().getForm().findField('process_number').focus();
                    }
                } else {
                    Ext.Msg.show({
                        title: 'Ajuste de atividades',
                        msg: 'Selecione uma <b>ORIGEM</b>.',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                    this.getFormPanel().getForm().findField('source').focus();
                }
            }
        } else {
            Ext.Msg.show({
              title: 'Ajuste de atividades',
              msg: 'Selecione uma <b>OPERAÇÃO</b>.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
            this.getFormPanel().getForm().findField('operation').focus();
        }
    },

    findData_rem: function(){
        if (this.getFormPanel().getForm().findField('operation').getValue() == 2){
            if (this.getFormPanel().getForm().findField('source').getValue() != ''){
                if (this.getFormPanel().getForm().findField('process_number').getValue() != '') {
                    if (this.getFormPanel().getForm().findField('date').getValue() != '') {
                        var rest = this.factoryRestful();
                        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Pesquisando informações para solicitação de remoção...'});
                        mask.show();
                        rest.get_data_process(
                            {
                                activity: this.values.activity,
                                source: this.getFormPanel().getForm().findField('source').getValue(),
                                process_number: this.getFormPanel().getForm().findField('process_number').getValue(),
                                date: this.getFormPanel().getForm().findField('date').getValue(),
                            },
                            {
                                scope: this,
                                fn: function(rst) {
                                    if(rst.success) {
                                        if (rst.count > 0) {
                                            this.getFormPanel().getForm().findField('legalclass').setValue(rst.classe);
                                            this.getFormPanel().getForm().findField('legalmatter').setValue(rst.matter);
                                            this.getFormPanel().getForm().findField('movement').setValue(rst.movement);
                                            this.getFormPanel().getForm().findField('legalclass').value = rst.classe;
                                            this.getFormPanel().getForm().findField('legalmatter').value = rst.matter;
                                            this.getFormPanel().getForm().findField('movement').value = rst.movement;
                                        } else {
                                            Ext.Msg.show({
                                                title: 'Ajuste de atividades',
                                                msg: 'Os dados informados não correspondem a uma atividade registrada no mês.',
                                                icon: Ext.Msg.ERROR,
                                                buttons: Ext.Msg.OK
                                            });
                                            this.getFormPanel().getForm().findField('legalclass').setValue(0);
                                            this.getFormPanel().getForm().findField('legalmatter').setValue(0);
                                            this.getFormPanel().getForm().findField('movement').setValue(0);
                                            this.getFormPanel().getForm().findField('legalclass').value = rst.classe;
                                            this.getFormPanel().getForm().findField('legalmatter').value = rst.matter;
                                            this.getFormPanel().getForm().findField('movement').value = rst.movement;
                                            this.getFormPanel().getForm().findField('process_number').focus();
                                        }
                                        if (this.getFormPanel().getForm().findField('legalclass')._comboField.value) {
                                            this.getFormPanel().getForm().findField('legalclass').setReadOnly(true);
                                        } else {
                                            this.getFormPanel().getForm().findField('legalclass').setReadOnly(false);
                                        }
                                        if (this.getFormPanel().getForm().findField('legalmatter')._comboField.value) {
                                            this.getFormPanel().getForm().findField('legalmatter').setReadOnly(true);
                                        } else {
                                            this.getFormPanel().getForm().findField('legalmatter').setReadOnly(false);
                                        }
                                        if (this.getFormPanel().getForm().findField('movement')._comboField.value) {
                                            this.getFormPanel().getForm().findField('movement').setReadOnly(true);
                                        } else {
                                            this.getFormPanel().getForm().findField('movement').setReadOnly(false);
                                        }
                                    }
                                    else
                                        Ext.Msg.show({
                                            title: 'Ajuste de atividades',
                                            msg: rst.message,
                                            icon: Ext.Msg.ERROR,
                                            buttons: Ext.Msg.OK
                                        });
                                }
                            },
                            {
                                scope: this,
                                fn: function(message) {
                                    Ext.Msg.show({
                                        title: 'Ajuste de atividades',
                                        msg: message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                                }
                            },
                            {
                                scope: this,
                                fn: function() {
                                    mask.hide();
                                }
                            }
                        );
                    } else {
                        Ext.Msg.show({
                          title: 'Ajuste de atividades',
                          msg: 'Informe uma data de movimentação para verificar a possibilidade de remoção.',
                          icon: Ext.Msg.ERROR,
                          buttons: Ext.Msg.OK
                        });
                    }
                }
            }
        }
    },

    findData_add: function(){
        if (this.getFormPanel().getForm().findField('operation').getValue() == 1){
            if (this.getFormPanel().getForm().findField('source').getValue() != ''){
                if (this.getFormPanel().getForm().findField('process_number').getValue() != '') {
                    var rest = this.factoryRestful();
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Pesquisando informações para solicitação de adição...'});
                    mask.show();
                    rest.get_data_process_add(
                        {
                            activity: this.values.activity,
                            source: this.getFormPanel().getForm().findField('source').getValue(),
                            process_number: this.getFormPanel().getForm().findField('process_number').getValue(),
                        },
                        {
                            scope: this,
                            fn: function(rst) {
                                if(rst.success) {
                                    if (rst.count > 0) {
                                        this.getFormPanel().getForm().findField('legalclass').setValue(rst.classe);
                                        this.getFormPanel().getForm().findField('legalmatter').setValue(rst.matter);
                                        this.getFormPanel().getForm().findField('legalclass').value = rst.classe;
                                        this.getFormPanel().getForm().findField('legalmatter').value = rst.matter;
                                    } else {
                                        // Ext.Msg.show({
                                        //     title: 'Ajuste de atividades',
                                        //     msg: 'Os dados informados não correspondem a nenhuma atividade retgistrada no Athenas.',
                                        //     icon: Ext.Msg.INFO,
                                        //     buttons: Ext.Msg.OK
                                        // });
                                        this.getFormPanel().getForm().findField('legalclass').setValue(0);
                                        this.getFormPanel().getForm().findField('legalmatter').setValue(0);
                                        this.getFormPanel().getForm().findField('legalclass').value = rst.classe;
                                        this.getFormPanel().getForm().findField('legalmatter').value = rst.matter;
                                        this.getFormPanel().getForm().findField('date').focus();
                                    }
                                }
                                else
                                    Ext.Msg.show({
                                        title: 'Ajuste de atividades',
                                        msg: rst.message,
                                        icon: Ext.Msg.ERROR,
                                        buttons: Ext.Msg.OK
                                    });
                            }
                        },
                        {
                            scope: this,
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Ajuste de atividades',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {
                            scope: this,
                            fn: function() {
                                mask.hide();
                            }
                        }
                    );
                }
            }
        }
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 55,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Operação',
                                        id: 'operation',
                                        hiddenName: 'operation',
                                        width: 270,
                                        choiceId: 'raf.ADJUSTMENT_OPERATION',
                                        listeners: {
                                            scope: this,
                                            select: function(index, scrollIntoView){
                                                if (index.value==2) {
                                                    this.getFormPanel().getForm().findField('legalclass').setReadOnly(true);
                                                    this.getFormPanel().getForm().findField('legalmatter').setReadOnly(true);
                                                    this.getFormPanel().getForm().findField('movement').setReadOnly(true);
                                                } else {
                                                    this.getFormPanel().getForm().findField('legalclass').setReadOnly(false);
                                                    this.getFormPanel().getForm().findField('legalmatter').setReadOnly(false);
                                                    this.getFormPanel().getForm().findField('movement').setReadOnly(false);
                                                }
                                            },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 44,
                                columnWidth: 0.5,
                                items: [
                                    {
                                        xtype: 'choicefield',
                                        fieldLabel: 'Origem',
                                        hiddenName: 'source',
                                        width: 285,
                                        choiceId: 'raf.ACTIVITY_SOURCE',
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'column',
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 120,
                                columnWidth: 0.78,
                                items: [
                                    {
                                        xtype: 'textfield',
                                        fieldLabel: 'Número do Processo',
                                        id: 'process_number',
                                        name: 'process_number',
                                        hideLabel: false,
                                        width: 380,
                                        listeners: {
                                            scope: this,
                                            // focus: function() { this.verifyFields(); },
                                            blur: function(){ this.findData_add(); },
                                        },
                                    },
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 30,
                                columnWidth: 0.22,
                                items: [
                                    {
                                        xtype: 'datefield',
                                        fieldLabel: 'Data',
                                        id: 'date',
                                        name: 'date',
                                        width: 110,
                                        listeners: {
                                            scope: this,
                                            focus: function() { this.verifyFields(); },
                                            blur: function(){ this.findData_rem(); },
                                        },
                                    },
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 65,
                        items: [
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 40,
                                items: [
                                    this.getClassField(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 50,
                                items: [
                                    this.getMatterField(cfg),
                                ]
                            },
                            {
                                xtype:'panel',
                                autoHeight:true,
                                layout: 'form',
                                labelWidth: 65,
                                items: [
                                    this.getMovementField(cfg),
                                ]
                            },
                        ]
                    },
                    {
                        xtype:'panel',
                        autoHeight:true,
                        layout: 'form',
                        labelWidth: 120,
                        items: [
                            {
                                xtype: "htmleditor",
                                name: "initial_message",
                                hideLabel: true,
                                width: 670,
                                enableAlignments : false,
                                enableColors : false,
                                enableFont : false,
                                enableFontSize : false,
                                enableFormat : false,
                                enableLinks : false,
                                enableLists : false,
                                enableSourceEdit : false,
                            },
                        ]
                    },
                ]
            });
        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(cfg, {
            title: 'Ajuste de atividade',
        });
        raf.adjustment.dataadjustment.Window.superclass.constructor.call(this, cfg);
    }

});
