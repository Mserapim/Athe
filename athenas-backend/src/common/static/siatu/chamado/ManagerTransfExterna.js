/**
 *
 **/
Ext._define('common.siatu.chamado.ManagerTransfExterna', {
    extend: 'Ext.Window',

    getGrid: function() {
        if(!this._Grid){
            rest = Ext._create('common.siatu.chamado.Restful',{});
            this._Grid = Ext._create('common.siatu.chamado.Grid', {
                region: 'center',
                title:'Lista de chamados para decidir sobre transferência',
                minHeight: 400,
                columnAction: false,
                gridAutoLoad: false,
                disableSave: true
            });

            this._Grid.getStore().proxy.setApi({
                read: core.callAction("SiatuChamado", "action_transf_waiting")
            });

            this._Grid.on({
                scope: this,
                render: function(grid) {
                    grid.getStore().load({});
                }
            });

            this._Grid.getEditarButton().setText('+ Info');

            this._Grid.getSelectionModel().on({
                scope: this,
                rowselect: function(grid, index, record) {
                    this.setChamado(record.get('pk'));
                    this.set_transf_ativa(record.get('transf_ativa'));
                    this.observe();
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
            this.getTabPrincipal().getListaAtendenteGrid().setFilterProperty('chamados', this.getChamado());

            this.getTabTransferencia().getTransferenciaGrid().setFilterProperty('chamado', this.getChamado());

            this.getTabAnexo().getGrid().setFilterProperty('chamado', this.getChamado());


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

    set_transf_ativa: function(pk) {
        this.TransfId = pk;
    },

    get_transf_ativa: function() {
        return this.TransfId;
    },

    setSizeAtendentesChamado: function(length) {
        this.SizeAtendentesChamado = length;
    },

    getSizeAtendentesChamado: function() {
        return this.SizeAtendentesChamado;
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

    getTabTransferencia: function(){
        if(!this._tabTransferencia) {
            this._tabTransferencia = Ext._create('common.siatu.chamado.TabTransferencia', {super_user:false});
            tbar = this._tabTransferencia.getTransferenciaGrid().getToolbar()
            tbar.remove(tbar.getComponent(0))//Adicionar
            tbar.remove(tbar.getComponent(0))//Remover

            tbar.insert(4,
                    {
                        text: 'Decidir',
                        iconCls: 'icon-diarias icon-ok',
                        scope: this,
                        handler: this.decidir
                    }
            );
        }
        return this._tabTransferencia
    },

    getTabAnexo: function(){
        if(!this._tabAnexo) {
            this._tabAnexo = Ext._create('common.siatu.chamado.TabAnexo', {});
            this._tabAnexo.getGrid().disableSave = true
            tbar = this._tabAnexo.getGrid().getToolbar()
            tbar.remove(tbar.getComponent(0))//Adicionar
            tbar.remove(tbar.getComponent(1))//Remover
            tbar.getComponent(0).setText('+ Info')

        }
        return this._tabAnexo
    },

    getTabs: function() {
        if(!this._tabPanel)
            this._tabPanel = Ext._create('Ext.TabPanel', {
                border: true,
                closable: false,
                region: 'south',
                height: 400,
                minHeight: 200,
                disabled: true,
                split:true,
                activeTab: 1,
                items: [
                    this.getTabPrincipal(),
                    this.getTabTransferencia(),
                    this.getTabAnexo()
                ]
            });

        return this._tabPanel;
    },

    decidir: function() {
        if (this.get_transf_ativa() != 0)
            Ext._create('common.siatu.transferencia.WindowDecidir',{
                action: 'update',
                title: 'Decidir',
                oId: this.get_transf_ativa(),
                callback: {
                    success: {
                        scope: this,
                        fn: function() {
                            this.getTabTransferencia().getTransferenciaGrid().getStore().reload();
                            this.getGrid().getStore().reload();
                            this.getTabPrincipal().getStatusGrid().getStore().reload();
                            this.getTabPrincipal().getListaAtendenteGrid().getStore().reload();

                            this._tabTransferencia.getTransferenciaGrid().getToolbar().getComponent(4).disable()
                        }
                    }
                }
            }).show();
        else
            Ext.Msg.show({
                title: 'Decidir',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK,
                msg: 'Ocorreu um erro ao identificar a transferência ativa. Consulte o administrador do sistema'
            });

    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {
                modal: true,
                width: Ext.getBody().getBox().width * 0.9,
                height: Ext.getBody().getBox().height * 0.9,
                title: 'Gerenciador de Chamados'
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
        common.siatu.chamado.ManagerTransfExterna.superclass.constructor.call(this, cfg);
    }
});

