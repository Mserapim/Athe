/**
 *
 **/
Ext._define('edocs.processo.movimentarLoteWindow', {
    extend: 'core.RestfulWindow',

    rest: 'edocs.movimentacao.Restful',

    actionTitles: {
        create: 'Movimentação em Lote',
        update: 'Movimentação em Lote',
        remove: 'Remover',
        read: 'Carregar'
    },

    width: 720,

    getFormPanel: function(cfg) {
        var width = 690;
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                items: [
                    new Ext.TabPanel({
                        activeTab: 0,
                        width: 710,
                        height: 455,
                        border: false,
                        items: [
                        {
                            xtype: "panel",
                            layout: "form",
                            title: "Destinatário",
                            border: false,
                            style: "margin: 5pt",
                            labelWidth: 120,
                            items: this.getDestinatarioFields(cfg)
                        },
                        {
                            xtype: "panel",
                            layout: "form",
                            title: "Informações",
                            border: false,
                            style: "margin: 5pt",
                            labelWidth: 120,
                            items: [
                                new Ext.Panel({
                                    layout:'form',
                                    labelAlign: "top",
                                    border: false,
                                    items:[
                                        new toolkit.plugins.CKEditor({
                                            name:'parecer',
                                            fieldLabel:'Novo parecer',
                                            toolbar: [
                                                ['Source'], ['PasteFromWord'],
                                                ['Link','Unlink','Anchor'],
                                                ['NumberedList','BulletedList'],
                                                ['Bold','Italic','Underline', 'Styles','Format', 'TextColor','BGColor']
                                            ],
                                            autoScroll:true,
                                            width: width,
                                            height: 310
                                        })
                                    ]
                                })
                            ]
                        }]
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

    getDestinatarioFields: function(cfg) {
        var items = [];

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

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Movimentar',
                    scope: this,
                    id:'movimentar',
                    handler: this.movimentarLote,
                    listeners:{
                        scope:this,
                        click: function(btn) {
                            btn.disable();
                        }
                    }
                },

                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];
        }

        return this._buttons;
    },

    movimentarLote: function() {
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
                        title: 'Movimentação em Lote',
                        icon: Ext.Msg.ERROR,
                        buttons: Ext.Msg.OK,
                        msg: rst.message,
                    });
                }
            },
            failure: function(request) {
                console.debug('Falha na requisição');
            },
        };
        rest.doRequest(rest.getRoute('nova_movimentacao_lote', null, 'POST', cfg));
    },

    getmovprocessoGrid:function() {
        if (!this._movprocessoGrid) {
            this._movprocessoGrid = Ext._create('edocs.processo.movprocessoGrid',{
                height: 200,
                width: 690,
            });
        }

        return this._movprocessoGrid;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        edocs.processo.movimentarLoteWindow.superclass.constructor.call(this, cfg);
        this.getmovprocessoGrid().setFilterProperty('pk__in', this.getParams().selecteds, 0, false);
    },
});
