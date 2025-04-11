/**
 *
 **/
Ext._define('common.siatu.chamado.TabPrincipal', {
    extend: 'Ext.Panel',

    getStatusGrid: function(cfg){
        if(!this._statusGrid){
            this._statusGrid = Ext._create('common.siatu.chamado.status.Grid', Ext.applyIf({
                flex: 0.7,
                border: false,
                title:'Histórico de Status',
                layout: 'fit',
                gridAutoLoad: false,
                }, cfg)
            );

            if (cfg.columnAction==false){
                var tbar = this._statusGrid.getToolbar()
                tbar.hide()
            }
        }

        return this._statusGrid
    },

    getAtendentePanel: function(cfg){
        if(!this._atendentePanel)
            this._atendentePanel = Ext._create('Ext.Panel',{
                layout: 'border',
                flex: 0.3,
                frame: false,
                border: false,
                items:[
                    this.getListaAtendenteGrid(cfg),
                ]

            })
        return this._atendentePanel
    },

    getListaAtendenteGrid: function(cfg) {
        if(!this._listaAtendenteServGrid){
            this._listaAtendenteServGrid = Ext._create('common.siatu.atendente.Grid', {
                flex: 1.0,
                border: false,
                gridAutoLoad: false,
                title:'Atendentes do chamado',
                columnAction: false,
                region: 'center',
                allowCreate: false,
                allowRemove: false,
                hideItemsToolbar: ['add', 'edit', 'remove', 'download', 'notificacao']
            });

            if (cfg.columnAction==false){
                var tbar = this._listaAtendenteServGrid.getToolbar()
                tbar.hide()
                columnModel = Ext._create(
                    'Ext.grid.ColumnModel',
                    [
                        Ext._create('Ext.grid.RowNumberer'),
                        {header: 'Nome', dataIndex: 'nome', id: 'autoExpandColumn'},
                    ]
                );
                this._listaAtendenteServGrid.reconfigure(this._listaAtendenteServGrid.getStore(), columnModel)
            }
        }

         return this._listaAtendenteServGrid;
    },

    constructor: function(cfg) {        
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
            	title: 'Principal',
                layout: 'hbox',
                region:'south',         
                split:true,
                bodyStyle: {
                    'border-left': 0,
                    'border-right': 0
                },
                layoutConfig: {
                    align: 'stretch',
                },
                items:[
                    this.getStatusGrid(cfg),
                    this.getAtendentePanel(cfg),
                ]
            }


        );

        common.siatu.chamado.TabPrincipal.superclass.constructor.call(this, cfg);
    }

});