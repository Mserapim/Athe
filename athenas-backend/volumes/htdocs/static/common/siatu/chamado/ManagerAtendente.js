/**
 *
 **/
Ext._define('common.siatu.chamado.ManagerAtendente', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.chamado.AtendenteGrid', {
                region: 'center',
                minHeight: 200,
                concluido: this.concluido,
                manager: 'atendente',
                status_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getGrid().getStore().reload();
                        }
                    }
                }
            });
            this._Grid.getKeywordField().setWidth(190);

            this._Grid.setFilterProperty('atendentes', this.atendente, 0, false);
            // Exclude concluído
            this._Grid.addFilterProperty('status_atual__status', this.concluido, -1, false);
            //exclude Aguardando Avaliacao status==4
            this._Grid.addFilterProperty('cancelado', true, -1, false);
            this._Grid.addFilterProperty('status_atual__status', 1, -1, false);
            this._Grid.addFilterProperty('status_atual__status', 4, -1, false);
            this._Grid.addFilterProperty('status_atual__status', 5, -1, false);
            this._Grid.addFilterProperty('status_atual__status', 8, -1, false);
            this._Grid.addFilterProperty('status_atual__status', 12, -1, false);

            // this.filterStatus = [2, 3, 6, 7, 10, 11];
            
            this._Grid.setSortProperty('urgente','DESC', false);
            this._Grid.addSortProperty('data_fila_atendimento', 'ASC', false);

            this._Grid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.setChamado(record.get('pk'));
                    var servico_atendentes = record.get('servico_atendentes');
                    this.setServicoAtendentes(servico_atendentes);

                    this.getTabInfoSolicitante().getForm().loadRecord(record)
                    
                    this.observe();
                    this.getTabCfgEmail().getFormPanel().getForm().loadRecord(record);
                    this.getTabHistorico().getForm().loadRecord(record);
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


                    if( (record.get('reincidencia')!='') && (record.get('status_atual')!='Concluído') )
                        this.getGrid().getReincidenciaAtendenteButton().enable();
                    else
                        this.getGrid().getReincidenciaAtendenteButton().disable();

                    if( (record.get('avaliacao')!='') && (record.get('replicado') == false) )
                        this.getGrid().getReplicaButton().enable();
                    else
                        this.getGrid().getReplicaButton().disable();
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

            this.getTabTransferencia().getTransferenciaGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabTransferencia().getTransferenciaGrid().setParam('chamado', this.getChamado());
            this.getTabTransferencia().getTransferenciaGrid().setParam('servico_atendentes', this.getServicoAtendentes());

            this.getTabCfgEmail().setChamado(this.getChamado())

            this.getTabAnexo().getGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabAnexo().getGrid().setParam('chamado', this.getChamado());

            this.getTabTerceiroInterno().setChamado(this.getChamado());
            this.getTabTerceiroInterno().getListaTerceiroGrid().setFilterProperty('chamados', this.getChamado());
            this.getTabTerceiroInterno().setStoreTerceiroGrid(this.getChamado())

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

    setServicoAtendentes: function(atendentes){
        this.ServicoAtendentes = atendentes;
    },

    getServicoAtendentes: function(){
        return this.ServicoAtendentes;
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

    getTabInfoSolicitante: function(){
        if(!this._tabInfoSolicitante) {
            this._tabInfoSolicitante = Ext._create('common.siatu.chamado.TabInfoSolicitante', {
            });
        }
        return this._tabInfoSolicitante
    },

    getTabPrincipal: function(){
        if(!this._tabPrincipal) {
            this._tabPrincipal = Ext._create('common.siatu.chamado.TabPrincipal', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getGrid().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabPrincipal
    },

    getTabTransferencia: function(){
        if(!this._tabTransferencia) {
            this._tabTransferencia = Ext._create('common.siatu.chamado.TabTransferencia', {super_user:false});
        }
        return this._tabTransferencia
    },

    getTabCfgEmail: function(){
        if(!this._tabCfgEmail) {
            this._tabCfgEmail = Ext._create('common.siatu.chamado.TabCfgEmailAtendente', {
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

    getTabAnexo: function(){
        if(!this._tabAnexo) {
            this._tabAnexo = Ext._create('common.siatu.chamado.TabAnexo', {});
        }
        return this._tabAnexo
    },

    getTabTerceiroInterno: function(){
        if(!this._tabTerceiro) {
            this._tabTerceiro = Ext._create('common.siatu.chamado.TabTerceiroInterno', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabTerceiroInterno().getListaTerceiroGrid().getStore().reload();
                            this.getTabTerceiroInterno().setStoreTerceiroGrid(this.getChamado())
                            this.getGrid().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabTerceiro
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

    getTabs: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                // region: 'south',
                // height: 300,
                // minHeight: 200,
                // split:true,
                // border: true,
                // closable: false,
                // disabled: true,
                // activeTab: 0,
                region: 'center',
                minHeight: 200,
                split:true,
                border: true,
                closable: false,
                disabled: true,
                activeTab: 0,
                items: [
                    this.getDetailChamadoTilePagePanel(),
                    // this.getTabProblema(),
                    // this.getTabInfoSolicitante(),
                    this.getTabPrincipal(),
                    this.getTabTransferencia(),
                    this.getTabCfgEmail(),
                    this.getTabTerceiroInterno(),
                    this.getTabAnexo(),
                    // this.getTabHistorico()
                ]
            });

        return this._tabPanel;
    },

    getGridPanel: function() {
        if(!this._gridPanel)
            this._gridPanel = Ext._create('Ext.Panel', {
                region: 'center',
                width: '60%',
                split: true,
                border: false,
                layout: 'border',
                items: [
                    this.getGrid(),
                    // this.getPanelSatisfacao(),
                ]
            });

        return this._gridPanel;
    },

    getDetailGridPanel: function() {
        if(!this._detailProtocolPanel)
            this._detailProtocolPanel = Ext._create('Ext.Panel', {
                region: 'east',
                width: '40%',
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

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        this.atendente = cfg.atendente;
        this.concluido = cfg.concluido;

        Ext.applyIf(
            cfg,
            {
                title: 'Atender Chamado',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    // this.getGrid(),
                    // this.getTabs(),
                    this.getGridPanel(),
                    this.getDetailGridPanel(),
                ]
            }
        );



        common.siatu.chamado.ManagerAtendente.superclass.constructor.call(this, cfg);


    }
});

