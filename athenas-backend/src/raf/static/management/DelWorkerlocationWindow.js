
Ext._define('raf.management.DelWorkerlocationWindow', {
    extend: 'core.RestfulWindow',

    getWorkerLocationField: function() {
        if(!this._workerLocationField) {
            this._workerLocationField = Ext._create('core.fields.AutocompleteField', {
                xtype: "rest-autocompletefield",
                fieldLabel: "Lotação",
                allowBlank: true,
                rest: "judicial.county.ExecutionOrganRestful",
                name: "workerlocation",
                disabled: false,
                gridConfig: {
                    columnAction: false,
                    hideColumns: ['habilita_protocolo', 'ativo', 'sigla', 'general_distribution', 'replacements', 'owner_unicode', 'employee_exercise_unicode'],
                    hideItemsToolbar: ['add', 'edit', 'remove', 'download'],
                }
            });
        }
        return this._workerLocationField;
    },

    getWorkerLocationGrid: function() {
        if (!this._workerLocationGrid) {
            this._workerLocationGrid = Ext._create('raf.workerlocation.Grid', {
                region: 'north',
                // title: 'Órgãos de Execução',
                margins: '0 0 1 0',
                split: true,
                height: 300,
                minHeight: 250,
                maxHeight: 650,
                gridAutoLoad: false,
                columnAction: true,
                configOrderToolBar: [''],
                hideColumns: ['raf_unicode'],
                doubleClickHandler: function() {},
                sm: new Ext.grid.RowSelectionModel({singleSelect:true}),
            });
        }
        return this._workerLocationGrid;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                frame: true,
                labelWidth: 50,
                border: false,
                items: [
                    {
                        xtype:'fieldset',
                        title: 'RAF',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Mês/Ano',
                                name: 'month_reference',
                            },
                            {
                                xtype: 'displayfield',
                                fieldLabel: 'Membro',
                                name: 'employee',
                            },
                        ]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Órgãos de Execução',
                        collapsible: false,
                        autoHeight:true,
                        items: [
                            this.getWorkerLocationField(),
                            // this.getWorkerLocationGrid(),
                        ]
                    },
                ]
        });
        return this._formPanel;
    },

    delWorkerLocation: function() {
        var values = this.getFormPanel().getForm().getValues();
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'Removendo Órgãos de Execução...'});
        if (values.workerlocation) {
            mask.show();
            Ext.Ajax.request({
                scope: this,
                url: core.callAction('RAFFunctionalActivityReport', 'delWorkerLocation'),
                callback: function() {
                    mask.hide();
                },
                success: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Editar RAF',
                        msg: rst.message,
                        icon: Ext.Msg.INFO,
                        buttons: Ext.Msg.OK
                    });
                    this.close();
                    core.invokeCallback((this.callback || {}).success);
                },
                failure: function(request) {
                    var rst = Ext.decode(request.responseText);
                    Ext.Msg.show({
                        title: 'Editar RAF',
                        msg: rst.message,
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK
                    });
                },
                params: {
                    raf: this.raf,
                    workerlocation: values.workerlocation,
                },
            });
        } else {
            Ext.Msg.show({
              title: 'Editar RAF',
              msg: 'Selecione um Órgão de Execução para adicioná-lo.',
              icon: Ext.Msg.ERROR,
              buttons: Ext.Msg.OK
            });
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons)
            this._buttons = [
                {
                    text: 'Remover',
                    scope: this,
                    handler: function() { this.delWorkerLocation(); }
                },
                {
                    text: 'Fechar',
                    scope: this,
                    handler: function() { this.close(); }
                }
            ];
        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        Ext.applyIf(
            cfg,
            {
                title: 'Remover Órgãos de Execução',
                modal: true,
                resizable: false,
                border: false,
                width: 700,
            }
        );
        Ext.apply(
            cfg,
            {
                items: this.getFormPanel(),
                buttons: this.getButtons(cfg),
            }
        );
        raf.management.DelWorkerlocationWindow.superclass.constructor.call(this, cfg);

        this.getFormPanel().getForm().setValues(this.values !== undefined ? this.values : {});

    }
});
