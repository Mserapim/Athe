/**
 *
 **/
Ext._define('common.siatu.chamado.ManagerSolicitante', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.chamado.Grid', {
                region: 'center',
                columnAction: false,
                manager: 'solicitante',
                allowUpdate: false,
                allowRemove: false,
                aguardando_avaliacao: this.aguardando_avaliacao,
                solicitante: this.solicitante,
                concluido: this.concluido,
                qtde_chamados_avaliar: this.qtde_chamados_avaliar,
                avaliacao_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getGrid().getStore().reload();
                            this.getGrid().getAvaliarButton().disable()
                            this.getTabPrincipal().getStatusGrid().getStore().load()
                            this.getGrid().qtde_chamados_avaliar--;
                            if(this.getGrid().qtde_chamados_avaliar == 0){
                                this.getGrid().changeFilter(this.concluido, true)
                            }
                        }
                    }
                },
                cancelar_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getGrid().getStore().reload();
                            this.getGrid().getCancelarButton().disable()
                            this.getTabPrincipal().getStatusGrid().getStore().load()
                        }
                    }
                }
            });

            this._Grid.getColumnModel().setHidden(4,true)
            this._Grid.setFilterProperty('solicitacao__solicitante', this.solicitante, 0, false);
            this._Grid.addFilterProperty('status_atual__status__in', [this.concluido, 12], -1, false);

            this._Grid.on({
                scope: this,
                dblclick: function(grid) {
                    var selected = this._Grid.getSelectionModel().getSelected();
                    if (selected)
                    this._Grid.avaliar()
                },

            });

            this._Grid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.atualizaPanel(record)

                    this.getTabInfoSolicitante().getForm().loadRecord(record)
                    
                    this.setChamado(record.get('pk'));
                    this.observe();
                    this.getTabCfgEmail().getFormPanel().getForm().loadRecord(record);
                    this.getTabHistorico().getForm().loadRecord(record)
                    this.getTabProblema().getForm().setValues({problema_solicitante: record.get('problema_solicitante')});


                    var rest = Ext._create('common.siatu.chamado.Restful', {});
                    var mask = new Ext.LoadMask(this.getEl(), {msg: 'Carregando dados...'});
                    mask.show();
                    rest.rendererDocument(
                        record.get('pk'),
                        {
                            scope: this,
                            fn: function(document) {

                                this.getDetailChamadoTilePagePanel().enable();
                                this.getDetailChamadoTilePagePanel().setPageContent(document.content);
                            }
                        },
                        {
                            fn: function(message) {
                                Ext.Msg.show({
                                    title: 'Buscando documento',
                                    msg: message,
                                    icon: Ext.Msg.ERROR,
                                    buttons: Ext.Msg.OK
                                });
                            }
                        },
                        {fn: function() {mask.hide();}}
                    );

                    
                    if(record.get('avaliacao')!='' || record.get('status_atual')!='Aguardando avaliação')
                        this.getGrid().getAvaliarButton().disable()
                    else
                        this.getGrid().getAvaliarButton().enable()

                    if(record.get('cancelado')=='' && record.get('status_atual')=='Aberto' 
                        || record.get('status_atual')=='Aguardando atendimento')
                        this.getGrid().getCancelarButton().enable()
                    else
                        this.getGrid().getCancelarButton().disable()
                }
            });

            this._Grid.getSelectionModel().on({
                scope: this,
                rowdeselect: function() {
                    this.setChamado(undefined);
                    this.observe();
                }
            });   
        }

         return this._Grid;
    },

    observe: function() {
        if(this.ChamadoId) {
            this.getTabPrincipal().getStatusGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabPrincipal().getStatusGrid().setParam('chamado', this.getChamado());
            this.getTabPrincipal().getListaAtendenteGrid().setFilterProperty('chamados', this.getChamado());

            this.getTabCfgEmail().setChamado(this.getChamado())



            this.getTabs().enable();
        }
        else {
            this.getTabs().disable();
        }
     },

    setChamado: function(pk) {
        this.ChamadoId = pk;
    },

    getChamado: function() {
        return this.ChamadoId;
    },

    setSizeAtendentesChamado: function(length) {
        this.SizeAtendentesChamado = length;
    },

    getSizeAtendentesChamado: function() {
        return this.SizeAtendentesChamado;
    },

    getTabInfoSolicitante: function(){
        if(!this._tabInfoSolicitante) {
            this._tabInfoSolicitante = Ext._create('common.siatu.chamado.TabInfoSolicitante', {
                solicitante: this.solicitante,
            });
        }
        return this._tabInfoSolicitante
    },

    getTabProblema: function() {
        if(!this._tabProblema) {
            this._tabProblema = Ext._create('Ext.FormPanel', {
                title: 'Problema',
                layout: 'fit',
                frame: true,
                items:[
                    {
                        name:'problema_solicitante',
                        xtype: 'textarea',
                        hideLabel: true,
                        readOnly: true,
                    }
                ]
            });
        }
        return this._tabProblema
    },

    getTabPrincipal: function(){
        if(!this._tabPrincipal) {
            this._tabPrincipal = Ext._create('common.siatu.chamado.TabPrincipal', {
                columnAction: false, 
                allowCreate: false,
                allowUpdate: false,
                allowRemove: false
            });
        }
        return this._tabPrincipal
    },

    getTabCfgEmail: function(){
        if(!this._tabCfgEmail) {
            this._tabCfgEmail = Ext._create('common.siatu.chamado.TabCfgEmailSolicitante', {
                callback: {
                    success: {
                        scope: this.getGrid(),
                        fn: function() {
                            this.getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabCfgEmail
    },

    getTabHistorico: function() {
        if(!this._tabHistorico) {
            this._tabHistorico = Ext._create('Ext.FormPanel', {
                title: 'Histórico',
                layout: 'fit',
                frame: true,
                items:[
                    {
                        name:'relatorio',
                        xtype: 'ckeditor',
                        listeners: {
                            scope: this,
                            render: function(panel) {
                                panel._editor = CKEDITOR.replace(
                                panel.getEl().dom,
                                {
                                    toolbar: [],
                                    resize_enabled: false,
                                    height: this.getTabHistorico().getInnerHeight()-40,
                                }
                                );
                                var cb = function(e) { if(panel._editor.checkDirty()) panel.setValue(panel._editor.getSnapshot(), false) };
                                panel._editor.loadSnapshot(panel.value);
                                panel._editor.on('key', cb, panel);
                                panel._editor.on('blur', cb, panel);
                            },
                        }
                    }
                ]
            });
        }
        return this._tabHistorico
    },

    // getTabs: function() {
    //     if(!this._tabPanel)
    //         this._tabPanel = Ext._create('Ext.TabPanel', {
    //             region: 'south',
    //             height: 300,
    //             minHeight: 200,
    //             split:true,
    //             border: true,
    //             closable: false,
    //             disabled: true,
    //             activeTab: 0,
    //             items: [
    //                 this.getTabProblema(),
    //                 this.getTabPrincipal(),
    //                 this.getTabInfoSolicitante(),
    //                 this.getTabCfgEmail(),
    //                 this.getTabHistorico(),
    //             ]
    //         });

    //     return this._tabPanel;
    // },


    getTabs: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                region: 'center',
                // layout: 'border',
                // height: 300,
                minHeight: 200,
                split:true,
                border: true,
                closable: false,
                disabled: true,
                activeTab: 0,
                items: [
                    this.getDetailChamadoTilePagePanel(),
                    // this.getTabProblema(),
                    this.getTabPrincipal(),
                    // this.getTabInfoSolicitante(),
                    this.getTabCfgEmail(),
                    // this.getTabHistorico(),
                ]
            });

        return this._tabPanel;
    },

    atualizaPanel: function(record) {
        var rest = Ext._create('common.siatu.chamado.Restful', {});
        store = Ext._create('Ext.data.Store', {
                    proxy: Ext._create('Ext.data.HttpProxy', {
                        api: {
                            read: core.callAction("SiatuServico", "action_satisfacao_servico", [record.get('servico'), record.get('pk')])
                        },
                        disableCaching: false,
                        defaultHeaders: rest.defaultHeaders,
                    }),
                    reader: Ext._create('Ext.data.JsonReader', {
                        idProperty: 'nome',
                        root: 'result',
                        totalProperty: 'count',
                        successProperty: 'success',
                        messageProperty: 'message',
                        fields: [
                                {name: 'percentual', type: 'string'},
                                {name: 'maioria', type: 'string'},
                                {name: 'nome', type: 'string'},
                                {name: 'texto', type: 'string'},
                                {name: 'atendentes', type: 'int'},
                                {name: 'chamados_hoje', type: 'string'},
                                {name: 'chamados_abertos', type: 'string'},
                                {name: 'chamados_mes', type: 'string'},
                                ]
                    }),
                    autoLoad: false
                })

        store.load({callback: this.preenchePanelSatisfacao, scope: this})
    },

    preenchePanelSatisfacao: function(record, option, success) {
        this.getPanelSatisfacao().getForm().loadRecord(record[0])

        this.getPanelSatisfacaoQtdeChamados().getForm().loadRecord(record[0])
    },

    // getPanelSatisfacao: function() {
    //     if(!this._panelSatisfacao)
    //         this._panelSatisfacao = Ext._create('Ext.form.FormPanel', {
    //             // flex: 0.2,
    //             // width: 210,
    //             // region: 'east',
    //             // title: 'Gerencia da Área',
    //             // collapsible: true,
    //             // labelWidth: 90,
    //             // autoScroll: true,
    //             // frame: true,
    //             height: 300,
    //             region: 'south',
    //             split: true,
    //             title: 'Gerência da Área',
    //             collapsible: true,
    //             labelWidth: 90,
    //             autoScroll: true,
    //             frame: true,
    //             items:[
    //                 {
    //                     style: 'font-size:10px;',
    //                     labelStyle: 'font-size:10px;',
    //                     xtype: 'displayfield',
    //                     fieldLabel: 'Área avaliada',
    //                     name: 'nome',
    //                     hideLabel: true,
    //                 },
    //                 // {
    //                 //     style: 'font-size:10px;',
    //                 //     labelStyle: 'font-size:10px;',
    //                 //     xtype: 'displayfield',
    //                 //     fieldLabel: 'Percentual',
    //                 //     name: 'percentual',
    //                 // },
    //                 {
    //                     xtype: 'label',
    //                     style: 'font-size:10px;',
    //                     text: 'Grau de satisfação da área avaliada:',
    //                     name: 'label',
    //                 },
    //                 Ext._create('Ext.Panel',{
    //                     labelWidth: 30,
    //                     border: true,
    //                     layout: 'form',
    //                     items:[
    //                     {
    //                         xtype: 'displayfield',
    //                         name: 'maioria',
    //                     },
    //                     ]
    //                 }),
    //                 {
    //                     xtype: 'label',
    //                     style: 'font-size:10px;',
    //                     text: 'Atendentes Hoje:',
    //                     name: 'label2',
    //                 },
    //                 {
    //                     style: 'font-size:10px;',
    //                     labelStyle: 'font-size:10px;',
    //                     xtype: 'displayfield',
    //                     name: 'atendentes',
    //                 },
    //                 {
    //                     style: 'font-size:10px;',
    //                     fieldLabel: 'Chamados Abertos Hoje',
    //                     labelStyle: 'font-size:10px;',
    //                     xtype: 'displayfield',
    //                     name: 'chamados_hoje',
    //                 },
    //                 {
    //                     style: 'font-size:10px;',
    //                     fieldLabel: 'Chamados Abertos no Mês',
    //                     labelStyle: 'font-size:10px;',
    //                     xtype: 'displayfield',
    //                     name: 'chamados_mes',
    //                 },
    //                 {
    //                     style: 'font-size:10px;',
    //                     fieldLabel: 'Total Chamados Abertos',
    //                     labelStyle: 'font-size:10px;',
    //                     xtype: 'displayfield',
    //                     name: 'chamados_abertos',
    //                 },
    //                 {
    //                     xtype: 'displayfield',
    //                     hideLabel: true,
    //                     name: 'texto',
    //                 },
    //             ]
            
    //         });

    //     return this._panelSatisfacao;
    // },
    getPanelSatisfacao: function() {
        if(!this._panelSatisfacao)
            this._panelSatisfacao = Ext._create('Ext.form.FormPanel', {
                width: '50%',
                title: 'Satisfação da área',
                items:[
                    {
                        style: 'font-size:13px;',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        fieldLabel: 'Área avaliada',
                        name: 'nome',
                        hideLabel: true,
                    },
                    {
                        xtype: 'label',
                        style: 'font-size:13px;',
                        text: 'Grau de satisfação da área avaliada:',
                        name: 'label',
                    },
                    Ext._create('Ext.Panel',{
                        labelWidth: 30,
                        border: true,
                        layout: 'form',
                        items:[
                        {
                            xtype: 'displayfield',
                            name: 'maioria',
                        },
                        ]
                    }),
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Atendentes Hoje',
                        labelStyle: 'font-size:13px; ',
                        xtype: 'displayfield',
                        name: 'atendentes',
                    },
                ]

            });

        return this._panelSatisfacao;
    },

    getPanelSatisfacaoQtdeChamados: function() {
        if(!this._panelSatisfacaoQtdChamados)
            this._panelSatisfacaoQtdChamados = Ext._create('Ext.form.FormPanel', {
                width: '50%',
                height:300,
                title: 'Chamados',
                items:[
                    
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Chamados Abertos Hoje',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_hoje',
                    },
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Chamados Abertos no Mês',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_mes',
                    },
                    {
                        style: 'font-size:13px;',
                        fieldLabel: 'Total Chamados Abertos',
                        labelStyle: 'font-size:13px;',
                        xtype: 'displayfield',
                        name: 'chamados_abertos',
                    },
                    {
                        xtype: 'displayfield',
                        hideLabel: true,
                        name: 'texto',
                        style: 'font-size:13px;',
                        labelStyle: 'font-size:13px;',
                    },
                ]

            });

        return this._panelSatisfacaoQtdChamados;
    },

    getGerenciaArea: function() {
        if(!this._gridTeste)
            this._gridTeste = Ext._create('Ext.Panel', {

                title: 'Gerência da Área',
                region: 'south',
                split: true,
                border: false,
                height: 300,
                
                collapsible: true,
                // labelWidth: 90,
                autoScroll: true,
                frame: true,

                layout:{
                    type: 'hbox',
                    align: 'strech'
                },

                items: [
                    this.getPanelSatisfacao(),
                    this.getPanelSatisfacaoQtdeChamados(),
                ]
            });

        return this._gridTeste;
    },

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('Ext.Panel', {
                region: 'center',
                width: '50%',
                split: true,
                border: false,
                layout: 'border',
                items: [
                    this.getGrid(),
                    // this.getPanelSatisfacao(),
                    this.getGerenciaArea(),
                ]
            });

        return this._gridPanel;
    },

    getDetailGridPanel: function() {
        if(!this._detailProtocolPanel)
            this._detailProtocolPanel = Ext._create('Ext.Panel', {
                region: 'east',
                width: '50%',
                split: true,
                border: false,
                layout: 'fit',
                items: [
                    // this.getDetailChamadoTilePagePanel()
                    this.getTabs()
                ]
            });

        return this._detailProtocolPanel;
    },


    getDetailChamadoTilePagePanel: function() {
        if(!this._datailProtocolTilePanel)
            this._datailProtocolTilePanel = Ext._create('core.TilePagePanel', {
                title: 'Resumo',
                disabled: true,
                region: 'center',
            });

        return this._datailProtocolTilePanel;
    },

    calculateBoxPanelWidth: function() {
        var width = (Ext.getBody().getBox().width - 900);
        return (width > 525 ? width : 525);
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});
        this.solicitante = cfg.solicitante;
        this.aguardando_avaliacao = cfg.aguardando_avaliacao
        this.qtde_chamados_avaliar = cfg.qtde_chamados_avaliar
        this.concluido = cfg.concluido

        Ext.applyIf(
            cfg,
            {
                title: 'Abrir Chamado',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGridPanel(),
                    this.getDetailGridPanel(),
                    // {
                    //     layout: 'border',
                    //     region: 'center',
                    //     border: false,
                    //     minHeight: 200,
                    //     items: [
                    //         this.getGrid(),
                    //         this.getPanelSatisfacao(),
                    //     ] 
                    // },
                    // this.getTabs(),
                ]
            }
        );
        common.siatu.chamado.ManagerSolicitante.superclass.constructor.call(this, cfg);
    }
});

