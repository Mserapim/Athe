/**
 *
 **/
Ext._define('common.siatu.chamado.reincidencia.WindowGerente', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.reincidencia.Restful',

    width: 500,

    height: 520,

    getReincidenciaPanel: function(){
        if(!this._reincidenciaPanel)
            this._reincidenciaPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                frame: true,
                border: false,
                title: 'Reincidência',
                items:[
                    {
                        xtype:'fieldset',
                        title: 'Gerente',
                        autoHeight:true,
                        items:[
                        {
                            xtype:'radiogroup',
                            fieldLabel: 'Parecer',
                            columns: 7,
                            items: [
                                {
                                    xtype:'radio',
                                    inputValue:'Yes',
                                    boxLabel: 'Sim',
                                    checked: this.parecer == 'true',
                                    name: 'parecer'
                                },
                                {
                                    xtype:'radio',
                                    inputValue:'No',
                                    boxLabel: 'Não',
                                    checked: this.parecer == 'false',
                                    name: 'parecer'
                                }
                            ]
                        },
                        {
                            xtype: 'textarea',
                            name: 'motivo_gerente',
                            width: 380,
                            fieldLabel: 'Motivo',
                            allowBlank: true,
                        }]
                    },
                    {
                        xtype:'fieldset',
                        title: 'Atendente',
                        autoHeight:true,
                        items:[
                        {
                            xtype:'radiogroup',
                            fieldLabel: 'Confirma',
                            columns: 7,
                            disabled: true,
                            items: [
                                {
                                    xtype:'radio',
                                    inputValue:'Yes',
                                    boxLabel: 'Sim',
                                    checked: this.confirm_atendente,
                                    name: 'confirm_atendente'
                                },
                                {
                                    xtype:'radio',
                                    inputValue:'No',
                                    boxLabel: 'Não',
                                    checked: !this.confirm_atendente,
                                    name: 'confirm_atendente'
                                }
                            ]
                        },
                        {
                            xtype: 'textarea',
                            name: 'opiniao_atendente',
                            width: 380,
                            fieldLabel: 'Opinião',
                            readOnly: true,
                        }]
                    }
                ]

            })
        return this._reincidenciaPanel
    },

    getGridBaseConhecimento: function() {
        if(!this._gridBaseConhecimento){
            this._gridBaseConhecimento = Ext._create('common.siatu.chamado.ItemBaseConhecimento.Grid', {
                // title: 'Itens da Base de Conhecimento',
                columnAction: false,
                boxMinHeight: 180,
                width: 450,
                height: 210,
                gridAutoLoad: false,
                allowUpdate: false,
            });
            columnModel = Ext._create(
                    'Ext.grid.ColumnModel',
                    [
                    {header: 'Codigo', dataIndex: 'base_conhecimento', width: 50, sortable:true},
                    {header: 'Objeto', dataIndex: 'objeto_string', width: 95, sortable:true},
                    {header: 'Problema', dataIndex: 'problema', width: 125},
                    {header: 'Solução', dataIndex: 'solucao', width: 125},
                    {header: 'Obs', dataIndex: 'info', id: 'autoExpandColumn'}
                ]
            );
            this._gridBaseConhecimento.reconfigure(this._gridBaseConhecimento.getStore(), columnModel)

            this._gridBaseConhecimento.getToolbar().hide()

            this._gridBaseConhecimento.getFooterbar().hide()
        }

        return this._gridBaseConhecimento;
    },

    getChamadoAnteriorPanel: function(){
        if(!this._chamadoAnteriorPanel)
            this._chamadoAnteriorPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                frame: true,
                border: false,
                title: 'Chamado anterior',
                items:[
                    {
                        xtype: 'displayfield',
                        width: 404,
                        name: 'identificacao',
                        fieldLabel: 'Código',
                    },
                    {
                        xtype: 'textfield',
                        width: 404,
                        name: 'servico_unicode',
                        fieldLabel: 'Serviço',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 404,
                        name: 'atendente_unicode',
                        fieldLabel: 'Atendente',
                        readOnly:true,
                    },
                    {
                        xtype: 'textarea',
                        width: 404,
                        height: 100,
                        name: 'problema_solicitante',
                        fieldLabel: 'Problema',
                        readOnly:true,
                    },

                    {
                        xtype: 'ckeditor',
                        width: 404,
                        height: 175,
                        toolbar: [],
                        name: 'relatorio',
                        fieldLabel: 'Relatório',
                        allowBlank: true,
                        disabled: true,
                        readOnly: true,
                    }
                    // {
                    //     xtype:'fieldset',
                    //     title: 'Base de Conhecimento',
                    //     autoHeight:true,
                    //     items:[
                    //         this.getGridBaseConhecimento()
                    //     ]
                    // }
                ]

            })
        return this._chamadoAnteriorPanel
    },

    getTabPanel: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 500,
                border: false,
                activeTab: 0,
                items: [
                    this.getReincidenciaPanel(),
                    this.getChamadoAnteriorPanel(),
                ]
            });

        return this._tabPanel;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                // frame: true,
                labelWidth: 60,
                items: [
                    this.getTabPanel(),
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        this.confirm_atendente = cfg.confirm_atendente
        this.parecer = cfg.parecer

        common.siatu.chamado.reincidencia.WindowGerente.superclass.constructor.call(this, cfg);

        if (this.chamado_anterior){
            this.getGridBaseConhecimento().setFilterProperty('chamado', this.chamado_anterior)
            var rest = Ext._create('common.siatu.chamado.Restful',{});
            rest.get(
                this.chamado_anterior,
                {
                    success: {
                                scope: this,
                                fn: function(instance) {
                                    this.getFormPanel().getForm().setValues(
                                        instance
                                    );
                                }
                            }
                }
            )
        }
    }

});
