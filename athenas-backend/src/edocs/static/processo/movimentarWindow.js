/**
 *
 **/
Ext._define('edocs.processo.movimentarWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.movimentacao.Restful',

    actionTitles: {
        create: 'Nova Movimentação',
        update: 'Editar Movimentação',
        remove: 'Remover',
        read: 'Carregar'
    },

    width: 710,

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    getAttachmentGrid: function() {
        if (!this._attachmentGrid) {
            this._attachmentGrid = Ext._create('edocs.protocolo.AttachmentGrid', {
                region: 'center',
                title: 'Anexos',
                allowRemove: false,
                configOrderToolBar: ['add', 'edit'],
                columnAction: false,
                gridAutoLoad: false,
                sm: Ext._create('Ext.grid.RowSelectionModel', {singleSelect: true}),
            });

            this._attachmentGrid.getStore().on({
                scope: this,
                load: function() {
                    this._attachmentGrid.setParam('moviment', this.getParams().movimentacao);
                    this._attachmentGrid.setParam('protocol', this.oId);
                }
            });

            this._attachmentGrid.setFilterProperty('protocol', this.oId, 1, true);
        }

        return this._attachmentGrid;
    },

    getReferenciasGrid: function() {
        if (!this._referenciasGrid) {
            this._referenciasGrid = Ext._create('edocs.processo.referencia.Grid', {
                title: 'Referências',
                gridAutoLoad: false
            });

            this._referenciasGrid.setParam('processo', this.oId);
            this._referenciasGrid.setFilterProperty('processo', this.oId, 1, true);
        }

        return this._referenciasGrid;
    },

    getPessoaField: function () {
        if(!this._pessoaField) {
            this._pessoaField = Ext._create('core.fields.AutocompleteField', {
                rest: 'rh.pessoa.Restful',
                name: 'add_interessados',
                fieldLabel: 'Interessado',
                emptyText: 'Selecione um interessado para inserir',
                allowBlank: true,
                displayField: 'identificador',
                width: 675,
                gridConfig: {
                    allowUpdate: false,
                    allowRemove: false,
                    hideItemsToolbar: ['edit', 'remove']
                },
                comboListeners: {
                    scope: this,
                    changevalid:function(cmb, id, start, valid, old) {
                        if(valid == true) {
                            idx = cmb.getStore().findExact(cmb.valueField, id);
                            record = cmb.getStore().getAt(idx);
                            this.addInteressado(record);
                            this.getPessoaField().reset();
                        }

                    },
                },
            });
        }

        return this._pessoaField;
    },

    addInteressado: function(record) {
        var items = [];
        var store1 = this.getInteressadosGrid().getStore();

        // store1.addSorted(record)

        store1.add(record);

        this.getInteressadosGrid().getView().refresh();

        var rec=store1.getRange();

        for (i=0; i<rec.length; i++) {
            items.push(rec[i].get('pk'));
        }

        this.setParam('interessados', items);
    },

    removeInteressado: function(record) {
        var items = [];
        // this == Interessados Grid
        var store1 = this.getStore();

        store1.remove(record);

        // this == Interessados Grid
        this.getView().refresh();

        var rec=store1.getRange();

        for (i=0; i<rec.length; i++) {
            items.push(rec[i].get('pk'));
        }

        this.setParam('interessados',items);
    },

    getInteressadosGrid: function() {
        if (!this._interessadosGrid) {
            this._interessadosGrid = Ext._create('rh.pessoa.Grid', {
                height: 260,
                width: 675,
                gridAutoLoad: false,
                columnAction: true,
                defaultRemoveFunction: this.removeInteressado
            });

            this._interessadosGrid.getFooterbar().hide();
            this._interessadosGrid.getToolbar().hide();

        }

        return this._interessadosGrid;
    },

    getFormPanel: function(cfg) {
        var width = 675;
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                new Ext.TabPanel({
                    activeTab: 0,
                    height: 360,
                    border: false,
                    defaults: { boxMinHeight: 320 },
                    items: [
                        {
                            xtype: "panel",
                            layout: "form",
                            frame: true,
                            title: "Destinatário",
                            border: false,
                            // labelWidth: 120,
                            labelAlign: 'top',
                            items: this.get_destinatario_fields(cfg)
                        },
                        {
                            xtype: "panel",
                            layout: "form",
                            frame: true,
                            title: "Informações",
                            border: false,
                            labelAlign: 'top',
                            items: [
                                new toolkit.plugins.CKEditor({
                                    name:'parecer',
                                    fieldLabel:'Novo parecer',
                                    autoScroll: true,
                                    height: 250
                                }),
                            ]
                        },
                        this.getAttachmentGrid(),
                        this.getReferenciasGrid(),
                    ]
                })
                ]
            });

        return this._formPanel;
    },

    get_caixa_field: function() {
        if (!this._caixa) {
            this._caixa = Ext._create('Ext.form.TextField',{
                name: 'caixa',
                fieldLabel: 'Caixa',
                width: 550,
                disabled: true,
                hidden: true
            });
        }
        return this._caixa;
    },

    get_destinatario_fields: function(cfg) {
            var width = 675;
            var items = [];
            var first_line = [];

            items.push({
                xtype:'combo',
                fieldLabel: 'Enviar para',
                hiddenName: 'tipo_envio',
                emptyText: 'Selecione um tipo de Destinatário',
                width: 550,
                store: [
                    [1, 'Enviar para Lotação'],
                    [2, 'Enviar para Pessoa']
                ],
                triggerAction: 'all',
                listeners: {
                    scope:  this,
                    select: this._manipular
                }
            });

            items.push({
                id: 'lotacao_destino',
                xtype: 'rest-autocompletefield',
                fieldLabel: "Enviar para Lotação",
                allowBlank: true,
                rest: "rh.generalorgan.Restful",
                name: "lotacao_destino",
                emptyText: 'Destinatário',
                width: 552,
                hidden:true,
                preFilter: [
                    {property: 'lotacao', value: null, stage: -1},
                    {property: 'ativo', value: true, stage: 2}
                ],
                gridConfig: {
                    columnAction: false,
                    allowCreate: false,
                    allowUpdate: false,
                    allowRemove: false,
                    configOrderToolBar: ['search', '->'],
                    hideColumns: ['habilita_protocolo']
                }
            });

            items.push({
                id: 'pessoa_destino',
                xtype: 'rest-autocompletefield',
                fieldLabel: "Enviar para Pessoa",
                allowBlank: true,
                rest: "rh.person.naturalperson.Restful",
                name: "pessoa",
                emptyText: 'Destinatário',
                width: 552,
                hidden:true,
                gridConfig: {
                    columnAction: false,
                    allowCreate: false,
                    allowUpdate: false,
                    allowRemove: false,
                    configOrderToolBar: ['search', '->'],
                    hideColumns: ['rg_unicode', 'cpf', 'data_nascimento', 'municipio_naturalidade_unicode', 'sexo_display', 'nome_mae', 'nome_pai']
                }
            });

            if (!cfg.situacao_locked) {
                items.push({
                    xtype: 'rest-combofield',
                    rest: 'edocs.processo.situacao.Restful',
                    fieldLabel: "Situação",
                    hiddenName: 'situacao',
                    triggerAction: 'all',
                    lazyRender: true,
                    lazyInit: true,
                    displayField: 'nome',
                    width: 550,
                    value: 3,
                    listeners: {
                        scope: this,
                        select: function(combo, record) {
                            if (record.id == 1) {
                                this.get_caixa_field().enable();
                                this.get_caixa_field().show();
                            }
                            else{
                                this.get_caixa_field().disable();
                                this.get_caixa_field().hide();
                            }
                        }
                    }
                });
            }
            items.push(
            this.get_caixa_field(),
            {
                name: "urgente",
                boxLabel: "Pedir urgência",
                hideLabel: true,
                xtype: "checkbox"
            },
            {
                height: 10,
                border: false,
            },
            this.getmovprocessoGrid()
            );
            return items;
    },

    _manipular: function(combo, record, index) {
        var valor = combo.getValue();
        if (valor == 1) {
            Ext.getCmp('pessoa_destino').hide();
            Ext.getCmp('lotacao_destino').enable();
            Ext.getCmp('lotacao_destino').show();
        } else {
            Ext.getCmp('lotacao_destino').hide();
            Ext.getCmp('pessoa_destino').enable();
            Ext.getCmp('pessoa_destino').show();
        }
    },

    getMovementButton: function() {
        if(!this._movementButton)
            this._movementButton = Ext._create('Ext.Button', {
                text: 'Movimentar',
                scope: this,
                handler: this.movimentar,
                listeners:{
                    scope:this,
                    click: function(btn) {
                        //FIXME: retornar
                        btn.disable();
                    }
                }
            });

        return this._movementButton;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                this.getMovementButton(),
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    movimentar: function() {
        var rest = this.factoryRestful();
        var form = this.getFormPanel().getForm();
        cfg = {
            params: Ext.applyIf(
                form.getValues(),
                this.getParams()
            ),
            scope: this,
            success: function(request) {
                var rst = Ext.decode(request.responseText);
                if(rst.success) {
                    core.invokeCallback(this.callback.success);
                    this.destroy();
                }
                else {
                    Ext.Msg.show({
                        title: 'Movimentar',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message
                    });
                }
            },
            failure: function(request) {
                console.debug('Falha na requisição');
            },
        };
        rest.doRequest(rest.getRoute('nova_movimentacao', null, 'POST', cfg));
    },

    getmovprocessoGrid:function() {
        if (!this._movprocessoGrid) {
            this._movprocessoGrid = Ext._create('edocs.processo.movprocessoGrid', {
                height: 200,
                width: 675,
                gridAutoLoad: false
            });
        }

        return this._movprocessoGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.oId = cfg.oId;

        edocs.processo.movimentarWindow.superclass.constructor.call(this, cfg);
        this.getmovprocessoGrid().setFilterProperty('pk', this.getParams().movimentacao, 1, true);
    },
});
