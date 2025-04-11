/**
 *
 **/
Ext._define('adm.patrimonio.PatrimonioRestfulWindow', {
    extend: 'core.RestfulWindow',

    rest: 'adm.patrimonio.PatrimonioRestful',

    width: 650,

    observer: function() {
        var grid;

        if(this.oId) {
            grid = this.getDocumentPanel();

            grid.setParam('documentos_do_patrimonio', this.oId);
            grid.setFilterProperty('documentos_do_patrimonio__id', this.oId, 1001);

            grid = this.getMovimentacaoPanel();
            grid.setFilterProperty('itens__pk', this.oId, 1001);
        }
    },

    getHistoryPanel: function() {
        if(!this._historyPanel)
            this._historyPanel = Ext._create('Ext.Panel', {
                title: 'Observação',
                border: false,
                frame: true,
                layoutConfig: {
                    align: 'stretchmax'
                },
                items: [
                    {
                        height: 230,
                        submitValue: false,
                        xtype: 'ckeditor',
                        name: 'observacao',
                    },
                    {
                        text: 'Salvar Observação',
                        scope: this,
                        xtype: 'button',
                        handler: this.save_observation,
                    }
                ]
            });

        return this._historyPanel;
    },

    save_observation: function() {
        var rest = Ext._create('adm.patrimonio.PatrimonioRestful');
        var mask = new Ext.LoadMask(this.getEl(), {msg: 'salvando...'});
        var values = this.getHistoryPanel().getComponent(0);
        if(values.value)
            values = { "conteudo" :values.value };

        mask.show();
        rest.save_observation(
            this.oId,
            values,
            {
                scope: this,
                fn: function(rst) {
                    if(rst.success) {
                        core.invokeCallback((this.callback || {}).success);
                    }
                    else
                        Ext.Msg.show({
                            title: 'Erro',
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
                        title: 'ErrO',
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
    },

    getDocumentPanel: function() {
        if(!this._documentsPanel)
            this._documentsPanel = Ext._create('adm.patrimonio.DocumentoGrid', {
                title: 'Documentos'
            });

        return this._documentsPanel;
    },

    getMovimentacaoPanel: function(cfg) {
        if(!this._movimentacaoPanel) {
            this._movimentacaoPanel = Ext._create('adm.patrimonio.movimento.Grid', {
                title: 'Movimentações',
                gridAutoLoad: false,
                hideColumns: ['origem_unicode', 'destino_unicode']
            });

            for(var c = 0; c < 8; c++)
                this._movimentacaoPanel.getToolbar().remove(0);
        }

        return this._movimentacaoPanel;
    },

    getMainPanel: function() {
        if(!this._mainPanel)
            this._mainPanel = Ext._create('Ext.Panel', {
                layout: 'form',
                border: false,
                frame: true,
                title: 'Principal',
                items: [
                    {
                        fieldLabel: 'Plaqueta',
                        xtype: 'textfield',
                        readOnly: true,
                        submitValue: false,
                        name: 'plaqueta'
                    },
                    {
                        fieldLabel: 'Especie',
                        xtype: 'textfield',
                        width: 515,
                        readOnly: true,
                        submitValue: false,
                        name: 'especie_unicode'
                    },
                    {
                        fieldLabel: 'Localização',
                        xtype: 'textfield',
                        width: 515,
                        readOnly: true,
                        submitValue: false,
                        name: 'localizacao_unicode'
                    },
                    {
                        fieldLabel: 'Responsável',
                        xtype: 'textfield',
                        width: 515,
                        readOnly: true,
                        submitValue: false,
                        name: 'responsavel_unicode'
                    },
                    {
                        xtype: 'rest-autocompletefield',
                        fieldLabel: "Utilizado por",
                        allowBlank: true,
                        rest: "rh.employee.Restful",
                        name: "utilizado_por",
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        layoutConfig: {
                            align: 'stretchmax'
                        },
                        defaults: {
                            layout: 'form',
                            flex: 1.0
                        },
                        items: [
                            {
                                width: 208,
                                items:  {
                                    fieldLabel: 'Conservação',
                                    xtype: 'textfield',
                                    width: 95,
                                    readOnly: true,
                                    submitValue: false,
                                    name: 'conservacao_display'
                                }
                            },
                            {
                                flex: 1.0,
                                items: {
                                    fieldLabel: 'Utilização',
                                    xtype: 'combo',
                                    width: 306,
                                    hiddenName: 'utilizacao',
                                    name: 'utilizacao',
                                    store: [
                                        [1, '8 horas ao dia'],
                                        [2, '16 horas ao dia'],
                                        [3, '24 horas ao dia']
                                    ],
                                    triggerAction: 'all'
                                }
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        layoutConfig: {
                            align: 'stretchmax'
                        },
                        defaults: {
                            layout: 'form',
                            flex: 1.0
                        },
                        items: [
                            {
                                items:  {
                                    fieldLabel: 'Aquisição',
                                    xtype: 'textfield',
                                    width: 95,
                                    readOnly: true,
                                    submitValue: false,
                                    name: 'valor_aquisicao'
                                }
                            },
                            {
                                items: {
                                    fieldLabel: 'Valor atual',
                                    xtype: 'textfield',
                                    width: 95,
                                    readOnly: true,
                                    submitValue: false,
                                    name: 'valor_atual'
                                }
                            },
                            {
                                items: {
                                    fieldLabel: 'Depreciado',
                                    xtype: 'textfield',
                                    width: 98,
                                    readOnly: true,
                                    submitValue: false,
                                    name: 'depreciado'
                                }
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        layout: 'hbox',
                        layoutConfig: {
                            align: 'stretchmax'
                        },
                        defaults: {
                            layout: 'form',
                            flex: 1.0
                        },
                        items: [
                            {
                                items:  {
                                    fieldLabel: 'Data do Tombo',
                                    xtype: 'displaydatefield',
                                    readOnly: true,
                                    width: 95,
                                    submitValue: false,
                                    name: 'data_tombo'
                                }
                            },
                            {
                                items: {
                                    fieldLabel: 'Garantia ',
                                    xtype: 'displaydatefield',
                                    readOnly: true,
                                    submitValue: false,
                                    width: 95,
                                    name: 'prazo_garantia'
                                }
                            },
                            {
                                items: {
                                    fieldLabel: 'Data da baixa',
                                    xtype: 'displaydatefield',
                                    readOnly: true,
                                    submitValue: false,
                                    width: 98,
                                    name: 'data_baixa'
                                }
                            }
                        ]
                    },
                    {
                        xtype: 'panel',
                        items: [
                            {
                                width: 620,
                                height: 110,
                                submitValue: false,
                                xtype: 'ckeditor',
                                name: 'descricao'
                            }
                        ]
                    }
                ]
            });

        return this._mainPanel;
    },

    getTabPanel: function(cfg) {
        if(!this._tabPanel) {
            this._tabPanel = Ext._create('Ext.TabPanel', {
                activeTab: 0,
                border: false,
                height: 450,
                items: [
                    this.getMainPanel(),
                    this.getDocumentPanel(),
                    this.getMovimentacaoPanel(cfg),
                    this.getHistoryPanel()
                ],
                listeners: {
                    scope: this,
                    render: function() {
                        this.observer();
                    }
                }
            });
        }

        return this._tabPanel;
    },

    getFormPanel: function(cfg) {
        if(!this._formPanel) {
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: this.getTabPanel(cfg)
            });

            var form = this._formPanel.getForm();
            var fn = form.setValues;

            form.setValues = function(values) {
                values = core.nullValue(values, {});

                if(values.depreciado || values.depreciado === 0)
                    values.depreciado = Ext.util.Format.number(values.depreciado, '0.0,00/i');

                if(values.valor_atual || values.valor_atual === 0)
                    values.valor_atual = Ext.util.Format.number(values.valor_atual, '0.0,00/i');

                fn.call(form, values);
            };
        }

        return this._formPanel;
    },

    openDocumentIn: function() {
        var Klass = adm.patrimonio.entrada.Grid.getClassByName(this.values.nota_entrada_cache_type);

        if (Klass == false){
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Não consegui encontrar nenhum(a) ' + this.values.nota_entrada_cache_type
            });

        }else{

            Ext._create(Klass, {
                action: 'update',
                values: 'remote',
                oId: this.values.nota_entrada
            }).show();
        }
    },

    openDocumentOut: function() {
        var Klass = adm.patrimonio.baixa.Grid.getClassByName(this.values.nota_baixa_cache_type);

        if (Klass == false){
            Ext.Msg.show({
                title: 'Atenção',
                icon: Ext.Msg.INFO,
                buttons: Ext.Msg.OK,
                msg: 'Não consegui encontrar nenhuma nota-baixa '
            });

        }else{
            Ext._create(Klass, {
                action: 'update',
                values: 'remote',
                oId: this.values.nota_baixa
            }).show();
        }
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Documento de Entrada',
                    disabled: core.nullValue(cfg.values, {}).read_only,
                    handler: this.openDocumentIn,
                    scope: this
                },
                {
                    text: 'Documento de Baixa',
                    disabled: core.nullValue(cfg.values, {}).read_only,
                    handler: this.openDocumentOut,
                    scope: this
                },
                '-',
                '-'
            ];

            if(cfg.action == 'create' && !cfg.disableSaveAndNew)
                this._buttons.push({
                    text: 'Salvar e novo',
                    scope: this,
                    disabled: ((cfg.values || {}).read_only == true),
                    handler: function() { this.save(false); }
                });
            if(!cfg.disableSave)
                this._buttons.push({
                    text: 'Salvar',
                    scope: this,
                    disabled: ((cfg.values || {}).read_only == true),
                    handler: function() { this.save(true); }
                });

            this._buttons.push(
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            );

        }

        return this._buttons;
    },

    constructor: function(cfg) {
        adm.patrimonio.PatrimonioRestfulWindow.superclass.constructor.call(this, cfg);
        this.observer();
    }
});
