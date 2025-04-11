/**
 *
 **/
Ext._define('common.siatu.solicitacao.WindowSolicitante', {
    extend: 'core.RestfulWindow',

    rest: 'common.siatu.solicitacao.Restful',

    width: 750,

    height: 480,

    getServicoField: function(){
        if(!this._servico){
            this._servico = Ext._create('core.fields.FoldedRestfulField', {
                restTree: 'common.siatu.servico.Tree',
                fieldLabel: 'Servico',
                name: 'servico',
                width: 620,
                treeConfig: {
                    listeners: {
                        render: function(tree){
                            tbar = tree.getToolbar();
                            tbar.remove(tbar.getComponent(0));
                            tbar.remove(tbar.getComponent(0));
                            tbar.remove(tbar.getComponent(0));
                            tbar.remove(tbar.getComponent(0));
                            tbar.remove(tbar.getComponent(0));
                            tbar.remove(tbar.getComponent(0));
                        },
                        scope: this,
                        load: function(node) {
                            Ext.each(
                                node.childNodes,
                                function(childNode) {
                                    if((childNode.text == 'Administrativo') ||
                                       (childNode.text == 'Almoxarifado') ||
                                       (childNode.text == 'Informática') ||
                                       (childNode.text == 'Banco de dados') ||
                                       (childNode.text == 'Manutenção de Informática') ||
                                       (childNode.text == 'Redes e comunicação') ||
                                       (childNode.text == 'Sistemas de informação') ||
                                       (childNode.text == 'Processo Eletrônico') ||
                                       (childNode.text == 'Transporte')) {
                                            childNode.disable();
                                    }
                                },
                                this
                            );
                        },
                    }
                }
            });
        }

        return this._servico;
    },

    getReincidenciaField: function(){
        if(!this._reincidencia){
            this._reincidencia = Ext._create('Ext.form.Checkbox', {
                name: 'reincidencia',
                fieldLabel: '&nbsp;',
                labelSeparator: '&nbsp;',
                boxLabel: 'Este problema já aconteceu outra vez?',
                allowBlank: true,
            });

            this._reincidencia.on({
                scope: this,
                check: function(checkbox, checked) {
                    if (checked){
                        this.getChamadoField().enable();
                        this.getChamadoField().show();
                    }
                    else{
                        this.getChamadoField().hide();
                        this.getChamadoField().disable();
                        this.getChamadoField().reset();
                    }
                }
            });

        }

        return this._reincidencia;
    },

    getChamadoField: function(){
        if (!this._chamado){
            this._chamado = Ext._create('core.fields.AutocompleteField', {
                rest: 'common.siatu.chamado.Restful',
                name: 'chamado_anterior',
                fieldLabel: 'Chamado',
                displayField: 'identificacao',
                gridColumnAction: false,
                gridListeners:{
                    render: function(grid){
                        tbar = grid.getToolbar();
                        tbar.remove(tbar.getComponent(0));
                        tbar.remove(tbar.getComponent(0));
                    }
                },
                disabled: true,
                hidden: true
            });
        }

        return this._chamado;
    },

    getArquivoGrid: function(){
        if(!this._arquivogrid) {
            this._arquivogrid = Ext._create('common.siatu.chamado.anexo.Grid', {
                height:200,
                disabled: true,
                gridAutoLoad: false,
            });
        }

        return this._arquivogrid;
    },

    getDepartmentField: function(cfg) {
        if(!this._departmentField){
            this._departmentField = Ext._create('core.fields.ComboField', {
                fieldLabel: 'Origem',
                hiddenName: 'orgao_geral_origem',
                displayField: 'description',
                store: Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        url: core.callAction('EDOCManage', 'work_locations')
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        totalProperty: 'count',
                        root: 'collection',
                        fields: [
                            {name: 'pk', type: 'int'},
                            {name: 'description', type: 'string'},
                        ]
                    })
                }),
                width: 600,
                // anchor: '100%',
                allowBlank: false
            });
        }

        return this._departmentField;
    },

    getFormPanel: function() {
        if(!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: [
                    this.getServicoField(),
                    this.getDepartmentField(),
                    {
                        xtype: 'fonefield',
                        width: 220,
                        name: 'telefone',
                        fieldLabel: 'Telefone',
                        allowBlank: false,
                    },
                    {
                        xtype: 'textarea',
                        width: 620,
                        name: 'descricao_problema',
                        fieldLabel: 'Problema',
                        allowBlank: true,
                    },
                    this.getReincidenciaField(),
                    this.getChamadoField(),
                    {
                        title: 'Deseja anexar uma foto da tela ou um arquivo pra ajudar na explicação do problema?: ',
                        flex: 1,
                        border: false,
                        items: [
                            this.getArquivoGrid(),
                        ]
                    },
                ]
            });

        return this._formPanel;
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(cfg, {
            disableSaveAndNew: true,
            saveAndContinue: {
                scope: this,
                fn: function(instance) {
                    this.getArquivoGrid().setParam('chamado', instance.chamado);
                    this.getArquivoGrid().setFilterProperty('chamado__id', instance.chamado, 1001);
                    this.getArquivoGrid().enable();
                    this.oId = instance.pk;
                    this.action = 'update';
                }
            }
        });

        common.siatu.solicitacao.WindowSolicitante.superclass.constructor.call(this, cfg);

        if(this.getParams().solicitante)
            this.getChamadoField().setPreFilter([
                    {property:'chamado_reincidente__isnull',value:true, stage: 0},
                    {property:'solicitacao__solicitante',value: this.getParams().solicitante, stage: 1},
                    {property:'status_atual__status__in',value: [this.getParams().concluido, 12], stage: 2},
                    {property:'cancelado',value: false, stage: 3},
                ]
            );
    }
});
