/**
 *
 **/
Ext._define('common.siatu.chamado.Window', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.chamado.Restful',

    width: 530,

    setParam: function(key, value) {
        this.params = core.nullValue(this.params, {});
        this.params[key] = value;
    },

    getServicoField: function(){
        if(!this._servico){
            this._servico = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Servico',
                name: 'servico',
                width: 412,
                treeConfig:{
                    listeners: {
                        render: function(tree){
                            tbar = tree.getToolbar()
                            tbar.remove(tbar.getComponent(0))//Adicionar
                            tbar.remove(tbar.getComponent(0))//Editar
                            tbar.remove(tbar.getComponent(0))//Remover
                            tbar.remove(tbar.getComponent(0))//Separador
                            tbar.remove(tbar.getComponent(0))//Mover
                            tbar.remove(tbar.getComponent(0))//Separador
                        }
                    }
                }
            })
        }
        return this._servico;
    },

    getGridItemBaseConhecimento: function() {
        if(!this._gridItemBaseConhecimento){
            this._gridItemBaseConhecimento = Ext._create('common.siatu.chamado.ItemBaseConhecimento.Grid', {
                columnAction: false,
                boxMinHeight: 200,
                width: 480,
                height: 200,
                gridAutoLoad: false,
                hideItemsToolbar: ['search', 'download']
            });

            this._gridItemBaseConhecimento.getFooterbar().hide()
        }

        return this._gridItemBaseConhecimento;
    },

    getChamadoPanel: function(){
        if(!this._chamadoPanel)
            this._chamadoPanel = Ext._create('Ext.Panel',{
                layout: 'form',
                frame: true,
                border: false,
                title: 'Chamado',
                items:[
                    this.getServicoField(),
                    {
                        xtype: 'checkbox',
                        width: 295,
                        name: 'cancelado',
                        boxLabel: 'Cancelado',
                        allowBlank: true,
                        disabled: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 410,
                        name: 'motivo_cancelado',
                        fieldLabel: 'Justificativa',
                        readOnly: true,
                    },
                    {
                        xtype: 'checkbox',
                        width: 295,
                        name: 'nao_institucional',
                        boxLabel: 'Não institucional',
                        inputValue:'true',
                        allowBlank: true,
                    },
                    {
                        xtype:'fieldset',
                        title: 'Base de Conhecimento',
                        autoHeight:true,
                        items:[
                            this.getGridItemBaseConhecimento(),
                            ]
                    },
                ]
            })
        return this._chamadoPanel
    },

    getInfoPanel: function(){
        if(!this._infoPanel)
            this._infoPanel = Ext._create('Ext.Panel',{
                title: 'Solicitação',
                frame: true,
                border: false,
                layout: 'form',
                items:[
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'servico_unicode',
                        fieldLabel: 'Servico',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'solicitante_username',
                        fieldLabel: 'Solicitante',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'solicitante_lotacao',
                        fieldLabel: 'Lotação',
                        readOnly:true,
                    },
                    {
                        xtype: 'fonefield',
                        width: 419,
                        name: 'telefone',
                        fieldLabel: 'Telefone',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'tipo_display',
                        fieldLabel: 'Tipo',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'reincidencia_solicitacao',
                        fieldLabel: 'Reincidência',
                        readOnly:true,
                    },
                    {
                        xtype: 'textarea',
                        width: 420,
                        height: 239,
                        name: 'descricao_problema',
                        fieldLabel: 'Problema',
                        allowBlank: true,
                        readOnly:true,
                    }
                ]

            })

        return this._infoPanel
    },

    getAvaliacaoPanel: function(){
        if(!this._avaliacaoPanel)
            this._avaliacaoPanel = Ext._create('Ext.Panel',{
                title: 'Avaliação',
                frame: true,
                border: false,
                layout: 'form',
                labelWidth: 90,
                items:[
                    {
                        xtype: 'textfield',
                        width: 403,
                        name: 'satisfacao_display',
                        fieldLabel: 'Satisfação',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 403,
                        name: 'presteza_display',
                        fieldLabel: 'Presteza',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 403,
                        name: 'esclarecimento_display',
                        fieldLabel: 'Esclarecimento',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textfield',
                        width: 403,
                        name: 'tempo_display',
                        fieldLabel: 'Tempo',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textarea',
                        width: 404,
                        name: 'sugestao',
                        fieldLabel: 'Sugestão',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'textarea',
                        width: 404,
                        height: 168,
                        name: 'replica',
                        fieldLabel: 'Replica',
                        allowBlank: true,
                        readOnly: true,
                    }
                ]

            })

        return this._avaliacaoPanel
    },

    getReincidenciaPanel: function(){
        if(!this._reincidenciaPanel)
            this._reincidenciaPanel = Ext._create('Ext.Panel',{
                title: 'Reincidência',
                frame: true,
                border: false,
                layout: 'form',
                items:[
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'chamado_anterior_numero',
                        fieldLabel: 'Chamado Anterior',
                        readOnly:true,
                    },
                    {
                        xtype: 'textfield',
                        width: 419,
                        name: 'chamado_anterior_atendente',
                        fieldLabel: 'Atendente(s)',
                        readOnly:true,
                    },
                    {
                        xtype: 'textarea',
                        width: 404,
                        height: 100,
                        name: 'chamado_anterior_problema',
                        fieldLabel: 'Problema',
                        allowBlank: true,
                        readOnly: true,
                    },
                    {
                        xtype: 'ckeditor',
                        width: 404,
                        height: 175,
                        toolbar: [],
                        name: 'chamado_anterior_relatorio',
                        fieldLabel: 'Histórico',
                        allowBlank: true,
                        readOnly: true,
                    }
                ]

            })
        return this._reincidenciaPanel;
    },

    getTabPanel: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                height: 400,
                border: false,
                activeTab: 0,
                items: [
                    this.getChamadoPanel(),
                    this.getInfoPanel(),
                    this.getAvaliacaoPanel(),
                    this.getReincidenciaPanel()
                ],
                listeners: {
                    scope: this,
                    render: function() {
                        this.observer();
                    }
                }
            });
        return this._tabPanel;
    },

    observer: function() {
        if(this.values.reincidencia != "")
        {
            this.getReincidenciaPanel().enable();
        }else{
            this.getReincidenciaPanel().disable();
        }
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                labelWidth:74,
                items: [
                    this.getTabPanel(),
                ]
            });

        return this._formPanel;
    },

    getButtons: function(cfg) {
        if(!this._buttons) {
            this._buttons = [
                {
                    text: 'Fechar',
                    scope: this,
                    handler: this.destroy
                }
            ];

            if(!cfg.disableSave)
                this._buttons = [{
                    text: 'Salvar',
                    scope: this,
                    handler: this.save,
                    handler: function() { this.save(true) }
                }].concat(this._buttons);

            if(cfg.action == 'create' && !cfg.disableSaveAndNew)
                this._buttons = [{
                    text: 'Salvar e novo',
                    scope: this,
                    handler: function() { this.save(false) }
                }].concat(this._buttons);
        }

        return this._buttons;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        common.siatu.chamado.Window.superclass.constructor.call(this, cfg);

        if (this.oId){
            this.getGridItemBaseConhecimento().setParam('chamado', this.oId)
            this.getGridItemBaseConhecimento().setFilterProperty('chamado', this.oId)
        }

        if(this.disableSave){
            this._servico.setReadOnly(true)
            this.getGridItemBaseConhecimento().allowCreate=false
            this.getGridItemBaseConhecimento().disableSave=true
            this.getGridItemBaseConhecimento().allowRemove=false
            var tbar = this.getGridItemBaseConhecimento().getToolbar()
            tbar.remove(tbar.getComponent(0)); // Adicionar
            tbar.getComponent(0).setText('Visualizar'); // Editar/**/
            tbar.remove(tbar.getComponent(1)); // Remover
            tbar.remove(tbar.getComponent(2)); // base_conhecimento inserção facilitada
            tbar.remove(tbar.getComponent(2)); // base_conhecimento inserção facilitada
            tbar.remove(tbar.getComponent(2)); // base_conhecimento inserção facilitada
        }

        if (this.values.solicitacao){
            var rest = Ext._create('common.siatu.solicitacao.Restful',{});
            rest.get(
                this.values.solicitacao,
                {
                    success: {
                                scope: this,
                                fn: function(instance) {
                                    delete instance.servico
                                    if(instance.reincidencia)
                                        instance.reincidencia_solicitacao = 'sim'
                                    else
                                        instance.reincidencia_solicitacao = 'não'
                                    delete instance.reincidencia
                                    this.getFormPanel().getForm().setValues(
                                        instance
                                    );
                                }
                            }
                }
            )
        }
        if (this.values.avaliacao_pk){
            var rest = Ext._create('common.siatu.chamado.avaliacao.Restful',{});
            rest.get(
                this.values.avaliacao_pk,
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
