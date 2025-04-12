/**
 *
 **/
Ext._define('common.siatu.chamado.Manager', {
    extend: 'toolkit.widget.TabPanel',

    getGrid: function() {
        if(!this._Grid){
            this._Grid = Ext._create('common.siatu.chamado.Grid', {
                region: 'center',
                minHeight: 200,
                manager: 'adm',
                concluido: this.concluido,
                filterStatus: this.filterStatus,
                update_callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getGrid().getStore().reload();
                            this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado())
                        }
                    }
                },
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

            this._Grid.setFilterProperty('status_atual__status__in', this.filterStatus, 1000, false);

            this._Grid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.setChamado(record.get('pk'));
                    var servico_atendentes = record.get('servico_atendentes');
                    var atendentes = record.get('atendentes');

                    this.getTabInfoSolicitante().getForm().loadRecord(record)
                    
                    this.setServicoAtendentes(servico_atendentes)
                    this.setSizeAtendentesChamado(atendentes.length)
                    this.observe();
                    this.getTabHistorico().getForm().loadRecord(record)
                    this.getTabProblema().getForm().setValues({problema_solicitante: record.get('problema_solicitante')});
                }
            });

            this._Grid.getSelectionModel().on({
                scope: this,
                rowdeselect: function() {
                    this.setChamado(undefined);
                    this.setServicoAtendentes(undefined);
                    this.setSizeAtendentesChamado(0);
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

            if (this.getSizeAtendentesChamado()==0){
                this.getTabDistribuicaoManual().enable()
                this.getTabDistribuicaoManual().setChamado(this.getChamado());
                this.getTabDistribuicaoManual().getListaAtendenteGrid().setFilterProperty('chamados', this.getChamado());

                this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado())
            }
            else{
                this.getTabDistribuicaoManual().disable()
                if(this.getTabs().activeTab.title=='Distribuição Manual')
                    this.getTabPrincipal().show()
            }

            this.getTabTerceiroInterno().setChamado(this.getChamado());
            this.getTabTerceiroInterno().getListaTerceiroGrid().setFilterProperty('chamados', this.getChamado());
            this.getTabTerceiroInterno().setStoreTerceiroGrid(this.getChamado())

            this.getTabAnexo().getGrid().setFilterProperty('chamado', this.getChamado());
            this.getTabAnexo().getGrid().setParam('chamado', this.getChamado());

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

    setSizeAtendentesChamado: function(length) {
        this.SizeAtendentesChamado = length;
    },

    getSizeAtendentesChamado: function() {
        return this.SizeAtendentesChamado;
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
            this._tabTransferencia = Ext._create('common.siatu.chamado.TabTransferencia', {
                super_user:true,
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabTransferencia().getTransferenciaGrid().getStore().reload();
                            this.getGrid().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getTabPrincipal().getListaAtendenteGrid().getStore().reload();
                        }
                    }
                }
            }
            );
        }
        return this._tabTransferencia
    },

    getTabDistribuicaoManual: function(){
        if(!this._tabDistribuicao) {
            this._tabDistribuicao = Ext._create('common.siatu.chamado.TabDistribuicaoManual', {
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabDistribuicaoManual().setStoreAtendenteGrid(this.getChamado())
                            this.getTabDistribuicaoManual().getListaAtendenteGrid().getStore().reload();
                            this.getGrid().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getTabPrincipal().getListaAtendenteGrid().getStore().reload();
                        }
                    }
                }
            });
        }
        return this._tabDistribuicao
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

    getTabAnexo: function(){
        if(!this._tabAnexo) {
            this._tabAnexo = Ext._create('common.siatu.chamado.TabAnexo', {});
        }
        return this._tabAnexo
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
                region: 'south',
                height: 300,
                minHeight: 200,
                split:true,
                border: true,
                closable: false,
                region: 'south',
                disabled: true,
                activeTab: 1,
                items: [
                    this.getTabProblema(),
                    this.getTabInfoSolicitante(),
                    this.getTabPrincipal(),
                    this.getTabDistribuicaoManual(),
                    this.getTabTransferencia(),
                    this.getTabTerceiroInterno(),
                    this.getTabAnexo(),
                    this.getTabHistorico(),
                ]
            });

        return this._tabPanel;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});
        this.getTabTransferencia().getTransferenciaGrid().setParam('super_user',true);
        this.concluido = cfg.concluido
        this.all_status = cfg.all_status

        if (Ext.util.Cookies.get('siatu-chamado-filterStatus') != null)
            this.filterStatus = Ext.decode(Ext.util.Cookies.get('siatu-chamado-filterStatus'));
        else
            this.filterStatus = this.all_status;

        Ext.applyIf(
            cfg,
            {
                title: 'Gerenciador de Chamadoss',
            }
        );

        Ext.apply(
            cfg,
            {
                layout: 'border',
                items: [
                    this.getGrid(),
                    this.getTabs(),
                ]
            }
        );



        common.siatu.chamado.Manager.superclass.constructor.call(this, cfg);


    }
});

